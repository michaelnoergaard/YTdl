# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A YouTube downloader utility built with Python supporting video downloads, audio extraction to MP3, and transcript downloads, selectable in any combination from an interactive multi-select menu. Uses `uv` for package management and `yt-dlp` for downloading.

## Architecture

The package lives in `src/ytdl/` with three modules, in a strict one-way dependency chain (`cli` → `downloader`, `validation`; neither of the latter imports from the package):

- **`validation.py`**: `is_valid_youtube_url(url)` — regex-based YouTube URL validation
- **`downloader.py`**: `download_video(url)`, `download_audio(url)`, `download_transcript(url)` — yt-dlp wrapper functions, each returning `bool`. Downloads best quality video (merged), extracts audio to MP3 at 192kbps, or saves English subtitles as plain text. `_strip_timestamps()` converts VTT/SRT to clean prose; `_progress_hook()` displays live download progress.
- **`cli.py`**: `main()`, `get_youtube_url()`, `get_user_choices()` — interactive prompts and orchestration. `OPTIONS` is a label→function table driving a `simple-term-menu` multi-select, so several downloads can run in one invocation. Entry point for both `ytdl` command and `python -m ytdl`.

Files are saved with the video title as filename, into `DOWNLOAD_DIR` (`downloads/`). Note this path is **relative to the current working directory**, so running `ytdl` from elsewhere writes there instead. FFmpeg handles audio conversion and video merging.

Audio downloads use a `_audio_tmp` filename suffix that is renamed away afterwards — this keeps an MP3 extraction from colliding with a video download of the same title in the same run.

`download_transcript()` requests English only (`subtitleslangs: ["en"]`) and probes for `.en.vtt`/`.en.srt`; non-English videos yield no transcript.

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