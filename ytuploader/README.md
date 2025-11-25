# YouTube Video Uploader

This project is a script to upload videos from a local network-attached storage (NAS) to YouTube.

## Features

*   Uploads all videos from a specified folder.
*   Creates a YouTube playlist with the same name as the folder.
*   Orders videos in the playlist from oldest to newest based on file date.
*   Avoids uploading duplicate videos.
*   Handles YouTube's API upload limits.

## Project Plan

1.  **Set up Google Cloud Project and YouTube API Credentials.**
2.  **Develop the core uploader script.**
    *   Implement YouTube API authentication.
    *   Implement file discovery and filtering.
    *   Implement video upload logic.
    *   Implement playlist creation and management.
    *   Implement duplicate checking mechanism.
    *   Implement rate limit handling.
3.  **Refine and Test.**
    *   Test with a sample folder of videos.
    *   Ensure videos are ordered correctly in the playlist.
    *   Verify that duplicate uploads are skipped.

## Decisions Made

*   **Programming Language**: Python
*   **Authentication Flow**: Guided setup of OAuth 2.0 credentials.
*   **Video Date for Ordering**: File creation date.
*   **Handling of non-video files**: Ignore them.
*   **NAS Video Path**: `/mnt/d/Media/Videos 2/`
