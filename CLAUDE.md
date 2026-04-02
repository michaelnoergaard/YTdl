# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A YouTube downloader utility built with Python that supports both video downloads and audio extraction to MP3. Uses `uv` for package management and `yt-dlp` for downloading.

## Architecture

The package lives in `src/ytdl/` with three modules:

- **`validation.py`**: `is_valid_youtube_url(url)` — regex-based YouTube URL validation
- **`downloader.py`**: `download_audio(url)`, `download_video(url)` — yt-dlp wrapper functions. Downloads best quality video (merged) or extracts audio to MP3 at 192kbps. `_progress_hook()` displays live download progress.
- **`cli.py`**: `main()`, `get_youtube_url()`, `get_user_choice()` — interactive CLI prompts and orchestration. Entry point for both `ytdl` command and `python -m ytdl`.

Files are saved with the video title as filename. FFmpeg handles audio conversion and video merging.

## Development Commands

```bash
uv sync                          # Install dependencies (including dev tools)
uv run ytdl                      # Run the application
uv run pytest -v                 # Run tests
uv run ruff check src/ tests/    # Lint
uv run ruff format src/ tests/   # Format
uv run mypy src/                 # Type check
uv run pre-commit run --all-files  # Run all pre-commit hooks
uv add <package>                 # Add a new dependency
```

## System Dependencies

- **FFmpeg**: Required by yt-dlp for audio conversion and video merging (install via system package manager)