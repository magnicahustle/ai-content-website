# YouTube Video Uploader

This project is an automated script to upload videos from a local network-attached storage (NAS) to YouTube. It continuously monitors a specified folder for new video files and uploads them automatically.

## Features

*   **Automated Monitoring:** Continuously watches a designated folder for new video files.
*   **Smart Uploads:** Uploads new videos, avoiding duplicates.
*   **Playlist Management:** Creates a YouTube playlist with the same name as the monitored folder if one doesn't exist, and adds uploaded videos to it.
*   **Ordered Uploads:** Processes videos from oldest to newest based on file creation date.
*   **API Quota Handling:** Gracefully pauses uploads and retries after 24 hours if YouTube's daily API quota is exceeded.
*   **Configurable:** Settings are easily adjustable via a `config.ini` file.
*   **Detailed Logging:** All activities and errors are logged to `uploader.log`.

## Setup and Usage

### 1. Google Cloud Project and YouTube API Credentials

Before running the uploader, you need to set up a Google Cloud Project and obtain OAuth 2.0 credentials. This involves:

*   Creating a Google Cloud Project.
*   Enabling the YouTube Data API v3.
*   Configuring the OAuth consent screen.
*   Creating an OAuth client ID for a "Desktop app".
*   Downloading the `client_secret.json` file.

**Place the downloaded `client_secret.json` file in the root directory of this project.**

### 2. Install Dependencies

Ensure you have Python 3 installed. Then, install the required libraries:

```bash
pip install -r requirements.txt
```

### 3. Configure the Uploader

Edit the `config.ini` file to customize the uploader's behavior:

*   **`[Paths]`**:
    *   `watch_folder`: **Crucially, set this to the absolute path of the folder you want to monitor for new videos (e.g., `/mnt/d/Media/Videos 2/`).**
    *   `log_file`: The name of the log file (default: `uploader.log`).
*   **`[YouTube]`**:
    *   `privacy_status`: Set to `private`, `public`, or `unlisted` for uploaded videos and new playlists.
    *   `category_id`: The YouTube category ID for your videos (default: `22` for 'People & Blogs').
*   **`[Uploader]`**:
    *   `upload_delay_seconds`: Time to wait after detecting a new file before attempting upload (default: `10`).
    *   `quota_sleep_hours`: How long to sleep if the YouTube API quota is exceeded (default: `24`).

### 4. Run the Uploader

Once configured, start the uploader from your terminal:

```bash
python youtube_uploader.py
```

The script will run continuously, watching your specified folder. You can stop it at any time by pressing `Ctrl+C`.

## Project Plan (Completed & Current)

1.  **Set up Google Cloud Project and YouTube API Credentials.** (User's responsibility)
2.  **Develop the core uploader script.** (Completed)
    *   Implement YouTube API authentication.
    *   Implement file discovery and filtering.
    *   Implement video upload logic.
    *   Implement playlist creation and management.
    *   Implement duplicate checking mechanism.
    *   Implement rate limit handling.
    *   **Automated folder monitoring.**
    *   **Configuration via `config.ini`.**
    *   **File-based logging.**
3.  **Refine and Test.** (Next steps)
    *   Test with a sample folder of videos.
    *   Ensure videos are ordered correctly in the playlist.
    *   Verify that duplicate uploads are skipped.
    *   Verify API quota handling.

## Decisions Made

*   **Programming Language**: Python
*   **Authentication Flow**: Guided setup of OAuth 2.0 credentials.
*   **Video Date for Ordering**: File creation date.
*   **Handling of non-video files**: Ignore them.
*   **Automation Method**: File system watcher (`watchdog`).
*   **Configuration**: `config.ini` file.
*   **Logging**: Python's `logging` module to `uploader.log`.
*   **API Quota Handling**: Pause for 24 hours on quota exceedance.