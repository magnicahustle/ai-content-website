import os
import json
import time
import logging
import configparser
from queue import Queue
from threading import Thread

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Globals ---
CONFIG = None
VIDEO_QUEUE = Queue()
UPLOADED_DB = set()

# Supported video formats
VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv']


def setup_logging():
    """Sets up logging to file and console."""
    log_file = CONFIG.get('Paths', 'log_file', fallback='uploader.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ])
    logging.info("Logger initialized.")


def load_config(file='config.ini'):
    """Loads the configuration file."""
    global CONFIG
    CONFIG = configparser.ConfigParser()
    if not os.path.exists(file):
        raise FileNotFoundError(f"Configuration file '{file}' not found.")
    CONFIG.read(file)
    logging.info("Configuration loaded successfully.")


def load_uploaded_db():
    """Loads the database of uploaded videos."""
    global UPLOADED_DB
    db_path = CONFIG.get('Files', 'uploaded_videos_db')
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            UPLOADED_DB = set(json.load(f))
    logging.info(f"Loaded {len(UPLOADED_DB)} entries from the uploaded videos database.")


def save_uploaded_db():
    """Saves the database of uploaded videos."""
    db_path = CONFIG.get('Files', 'uploaded_videos_db')
    with open(db_path, 'w') as f:
        json.dump(list(UPLOADED_DB), f, indent=4)
    logging.info(f"Saved {len(UPLOADED_DB)} entries to the uploaded videos database.")


def get_authenticated_service():
    """Authenticate and return a YouTube API service object."""
    creds = None
    token_file = CONFIG.get('Files', 'token')
    client_secrets_file = CONFIG.get('Files', 'client_secrets')
    scopes = ['https://www.googleapis.com/auth/youtube.upload']

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Refreshing expired credentials.")
            creds.refresh(Request())
        else:
            logging.info("No valid credentials found. Starting OAuth flow.")
            if not os.path.exists(client_secrets_file):
                logging.error(f"'{client_secrets_file}' not found. Please follow setup instructions.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            creds = flow.run_local_server(port=0)
        
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        logging.info("Credentials saved.")

    return build('youtube', 'v3', credentials=creds)


class NewVideoHandler(FileSystemEventHandler):
    """Handles new video file events."""
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        if any(file_path.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            if file_path not in UPLOADED_DB:
                logging.info(f"New video detected: {file_path}")
                VIDEO_QUEUE.put(file_path)
            else:
                logging.info(f"Ignoring already uploaded video: {file_path}")


def get_or_create_playlist(youtube, title, privacy_status):
    """Gets or creates a YouTube playlist."""
    playlists_response = youtube.playlists().list(part='snippet', mine=True).execute()
    for playlist in playlists_response['items']:
        if playlist['snippet']['title'] == title:
            logging.info(f"Found existing playlist: '{title}' (ID: {playlist['id']})")
            return playlist['id']

    logging.info(f"Creating new playlist: '{title}'")
    playlist_body = {
        'snippet': {'title': title, 'description': f'A playlist for {title}'},
        'status': {'privacyStatus': privacy_status}
    }
    new_playlist = youtube.playlists().insert(part='snippet,status', body=playlist_body).execute()
    logging.info(f"Successfully created playlist: '{title}' (ID: {new_playlist['id']})")
    return new_playlist['id']


def upload_video(youtube, file_path, playlist_id):
    """Uploads a single video to YouTube."""
    file_name = os.path.basename(file_path)
    video_title = os.path.splitext(file_name)[0]
    privacy_status = CONFIG.get('YouTube', 'privacy_status', fallback='private')
    category_id = CONFIG.get('YouTube', 'category_id', fallback='22')

    body = {
        'snippet': {
            'title': video_title,
            'description': f'Uploaded from {file_path}',
            'tags': [os.path.basename(os.path.dirname(file_path))],
            'categoryId': category_id
        },
        'status': {'privacyStatus': privacy_status}
    }

    logging.info(f"Starting upload for '{file_name}'...")
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                logging.info(f"Uploaded {int(status.progress() * 100)}% for '{file_name}'")
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in e.content.decode():
                logging.error("YouTube API quota exceeded. Pausing uploads.")
                raise  # Re-raise the exception to be caught by the main loop
            else:
                logging.error(f"An HTTP error occurred during upload: {e}")
                return None
        except Exception as e:
            logging.error(f"A non-HTTP error occurred during upload: {e}")
            return None

    video_id = response['id']
    logging.info(f"Successfully uploaded video: '{video_title}' (ID: {video_id})")

    # Add to playlist
    playlist_item_body = {
        'snippet': {
            'playlistId': playlist_id,
            'resourceId': {'kind': 'youtube#video', 'videoId': video_id}
        }
    }
    youtube.playlistItems().insert(part='snippet', body=playlist_item_body).execute()
    logging.info(f"Added video '{video_title}' to playlist.")
    
    return video_id


def initial_scan(watch_folder):
    """Scans the watch folder on startup for any videos not yet uploaded."""
    logging.info(f"Performing initial scan of '{watch_folder}'...")
    video_files = set()
    for root, dirs, files in os.walk(watch_folder):
        if 'unsorted' in dirs:
            dirs.remove('unsorted')
        for file in files:
            if any(file.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                video_files.add(os.path.join(root, file))
    
    new_videos = sorted(list(video_files - UPLOADED_DB), key=lambda f: os.path.getctime(f))
    
    if new_videos:
        logging.info(f"Found {len(new_videos)} new videos during initial scan.")
        for video in new_videos:
            VIDEO_QUEUE.put(video)
    else:
        logging.info("No new videos found during initial scan.")


def main():
    """Main function to run the uploader service."""
    try:
        load_config()
        setup_logging()
        load_uploaded_db()
    except FileNotFoundError as e:
        print(f"FATAL: {e}. Please ensure config.ini is set up correctly.")
        return

    watch_folder = CONFIG.get('Paths', 'watch_folder')
    if not os.path.isdir(watch_folder):
        logging.fatal(f"Watch folder '{watch_folder}' does not exist. Exiting.")
        return

    # --- Start Watchdog Observer ---
    event_handler = NewVideoHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=True)
    observer.start()
    logging.info(f"Started watching folder: {watch_folder}")

    # --- Perform Initial Scan ---
    initial_scan(watch_folder)

    # --- Main Processing Loop ---
    try:
        youtube = get_authenticated_service()
        if not youtube:
            raise Exception("Failed to authenticate with YouTube.")
        
        playlist_title = os.path.basename(os.path.normpath(watch_folder))
        privacy = CONFIG.get('YouTube', 'privacy_status', fallback='private')
        playlist_id = get_or_create_playlist(youtube, playlist_title, privacy)

        while True:
            try:
                video_path = VIDEO_QUEUE.get()
                logging.info(f"Processing '{video_path}' from queue.")
                
                # Wait for the file to be fully copied
                upload_delay = CONFIG.getint('Uploader', 'upload_delay_seconds', fallback=10)
                time.sleep(upload_delay)

                video_id = upload_video(youtube, video_path, playlist_id)
                if video_id:
                    UPLOADED_DB.add(video_path)
                    save_uploaded_db()
                    logging.info(f"Successfully processed and logged '{video_path}'.")
                else:
                    logging.warning(f"Failed to upload '{video_path}'. It will be retried on next run.")
                
                VIDEO_QUEUE.task_done()

            except HttpError: # Specifically for quota errors
                quota_sleep_hours = CONFIG.getint('Uploader', 'quota_sleep_hours', fallback=24)
                sleep_seconds = quota_sleep_hours * 3600
                logging.info(f"Sleeping for {quota_sleep_hours} hours due to API quota limit.")
                time.sleep(sleep_seconds)
                logging.info("Waking up after quota sleep. Re-authenticating...")
                youtube = get_authenticated_service() # Re-auth after long sleep
                if not youtube:
                    raise Exception("Failed to re-authenticate with YouTube after quota sleep.")
                # Put the video back in the queue to be re-processed
                VIDEO_QUEUE.put(video_path)

    except KeyboardInterrupt:
        logging.info("Shutdown signal received. Saving state and exiting.")
    except Exception as e:
        logging.fatal(f"A fatal error occurred in the main loop: {e}", exc_info=True)
    finally:
        observer.stop()
        observer.join()
        save_uploaded_db()
        logging.info("Uploader has shut down.")


if __name__ == '__main__':
    main()