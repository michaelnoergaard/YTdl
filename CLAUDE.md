# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A YouTube downloader utility built with Python that supports both video downloads and audio extraction to MP3. Uses `uv` for package management and `yt-dlp` for downloading.

## Architecture

**ytdl.py** is the main entry point:
- `main()`: Entry point with URL validation, user prompts, and exit codes
- `download_audio_from_youtube(url)`: Downloads and converts to MP3 at 192kbps
- `download_video_from_youtube(url)`: Downloads best quality video with audio merged
- `get_user_choice()`: Interactive CLI prompt for download type selection
- `get_youtube_url()`: URL input with validation
- `is_valid_youtube_url(url)`: Validates YouTube URL patterns

Files are saved with the video title as filename. FFmpeg handles audio conversion and video merging.

## Development Commands

```bash
uv sync                    # Install dependencies
uv run python ytdl.py      # Run the application
uv add <package>           # Add a new dependency
```

## System Dependencies

- **FFmpeg**: Required by yt-dlp for audio conversion and video merging (install via system package manager)