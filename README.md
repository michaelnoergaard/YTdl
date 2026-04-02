# ytdl

A YouTube downloader CLI that supports video downloads, audio extraction to MP3, and transcript downloads.

## Features

- **Video download** — best quality video + audio, merged automatically
- **Audio extraction** — converts to MP3 at 192kbps
- **Transcript download** — grabs subtitles (manual or auto-generated) as clean plain text
- **Multi-select** — download any combination in one run
- Interactive prompts with URL validation

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (package manager)
- [FFmpeg](https://ffmpeg.org/) (for audio conversion and video merging)

## Installation

```bash
git clone https://github.com/your-username/YTdl.git
cd YTdl
uv sync
```

## Usage

```bash
uv run ytdl
```

You'll be prompted for a YouTube URL, then choose what to download:

```
Enter YouTube URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Select download options (toggle with number, press Enter when done):
  [x] 1. Download video
  [ ] 2. Extract audio to MP3
  [x] 3. Download transcript

Toggle option (1-3) or press Enter to confirm:
```

Files are saved to the `downloads/` directory.

## Development

```bash
uv run pytest -v                   # Run tests
uv run ruff check src/ tests/      # Lint
uv run ruff format src/ tests/     # Format
uv run mypy src/                   # Type check
uv run pre-commit run --all-files  # Run all pre-commit hooks
```

## Project Structure

```
src/ytdl/
├── __init__.py       # Package version
├── __main__.py       # python -m ytdl entry point
├── validation.py     # YouTube URL validation
├── downloader.py     # yt-dlp wrappers (video, audio, transcript)
└── cli.py            # Interactive multi-select menu
tests/
├── test_validation.py
├── test_downloader.py
└── test_cli.py
```

## License

MIT
