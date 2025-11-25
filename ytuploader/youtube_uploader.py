import argparse
import os
import json
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# This is the file that will store the user's access and refresh tokens.
# It will be created automatically when the authorization flow is completed
# for the first time.
TOKEN_FILE = 'token.json'

# This is the file that you downloaded from the Google Cloud Console.
CLIENT_SECRETS_FILE = 'client_secret.json'

# This is the file where we will keep track of uploaded videos.
UPLOADED_VIDEOS_FILE = 'uploaded_videos.json'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Supported video formats
VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv']


def get_authenticated_service():
    """Authenticate and return a YouTube API service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # We need to handle the case where the client_secret.json is not found
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"Error: {CLIENT_SECRETS_FILE} not found. Please follow the setup instructions.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)


def get_video_files(directory):
    """
    Get a sorted list of unique video files in a directory, excluding 'unsorted' folders.

    Args:
        directory (str): The directory to scan for video files.

    Returns:
        list: A list of unique video file paths, sorted by creation time.
    """
    video_files = set()
    for root, dirs, files in os.walk(directory):
        # Exclude 'unsorted' directories
        if 'unsorted' in dirs:
            dirs.remove('unsorted')

        for file in files:
            if any(file.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                video_files.add(os.path.join(root, file))

    # Sort files by creation time (oldest first)
    sorted_videos = sorted(list(video_files), key=lambda f: os.path.getctime(f))
    return sorted_videos


def load_uploaded_videos(tracking_file):
    """
    Load the set of already uploaded video file paths.

    Args:
        tracking_file (str): The path to the JSON file tracking uploads.

    Returns:
        set: A set of file paths of uploaded videos.
    """
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r') as f:
            return set(json.load(f))
    return set()


def save_uploaded_videos(tracking_file, uploaded_videos):
    """
    Save the set of uploaded video file paths.

    Args:
        tracking_file (str): The path to the JSON file for tracking.
        uploaded_videos (set): The set of file paths of uploaded videos.
    """
    with open(tracking_file, 'w') as f:
        json.dump(list(uploaded_videos), f, indent=4)


def main():
    """
    Main function to handle video uploads.
    """
    parser = argparse.ArgumentParser(description='Upload videos to YouTube.')
    parser.add_argument('folder', help='The folder containing videos to upload.')
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: Folder not found at '{args.folder}'")
        return

    # We will handle authentication later, for now we focus on file discovery
    # youtube = get_authenticated_service()
    # if not youtube:
    #     return
    # print("Successfully authenticated with YouTube.")

    all_videos = get_video_files(args.folder)
    uploaded_videos = load_uploaded_videos(UPLOADED_VIDEOS_FILE)

    videos_to_upload = [
        video for video in all_videos if video not in uploaded_videos
    ]

    if not videos_to_upload:
        print("No new videos to upload.")
        return

    print(f"Found {len(videos_to_upload)} new videos to upload:")
    for video in videos_to_upload:
        creation_time = datetime.fromtimestamp(os.path.getctime(video))
        print(f" - {video} (Created: {creation_time})")

    # TODO:
    # 1. Get or create a playlist with the folder name.
    # 2. For each video in videos_to_upload:
    #    a. Upload the video to YouTube.
    #    b. Add the uploaded video to the playlist.
    #    c. Add the video path to the `uploaded_videos` set.
    #    d. Save the `uploaded_videos` set to the tracking file.


if __name__ == '__main__':
    main()
