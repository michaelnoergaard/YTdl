# Python Best Practices Refactor — Design Spec

## Goal

Reorganize the YTdl project from a single-script layout into a properly packaged Python project following modern best practices, while preserving the existing interactive CLI behavior.

## Constraints

- Keep it lean — this remains a focused YouTube downloader, not an extensible platform
- Interactive prompt-based CLI stays as-is (no CLI argument parsing)
- Python >= 3.13, `uv` for package management

## Package Structure

```
YTdl/
├── src/ytdl/
│   ├── __init__.py          # dynamic version from package metadata
│   ├── __main__.py          # `python -m ytdl` support, calls cli.main()
│   ├── cli.py               # get_youtube_url(), get_user_choice(), main()
│   ├── downloader.py        # download_audio(), download_video(), _progress_hook()
│   └── validation.py        # is_valid_youtube_url()
├── tests/
│   ├── test_validation.py
│   ├── test_downloader.py
│   └── test_cli.py
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── pyproject.toml
├── .gitignore
└── README.md
```

### Module responsibilities

- **`validation.py`**: `is_valid_youtube_url(url: str) -> bool` — regex-based YouTube URL validation.
- **`downloader.py`**: `download_audio(url: str) -> bool`, `download_video(url: str) -> bool`, `_progress_hook(d: dict) -> None` — yt-dlp wrapper functions.
- **`cli.py`**: `get_youtube_url() -> str`, `get_user_choice() -> str`, `main() -> int` — interactive prompts and orchestration. Imports from `validation` and `downloader`. `get_youtube_url()` loops until a valid URL is provided (never returns `None`). `main()` wraps the entire flow in a `KeyboardInterrupt`/`EOFError` handler so Ctrl+C exits cleanly with code 130.
- **`__main__.py`**: `from ytdl.cli import main; sys.exit(main())` — enables `python -m ytdl`.
- **`__init__.py`**: Version is read dynamically from package metadata via `importlib.metadata.version("ytdl")`. No hardcoded `__version__` — the single source of truth is `pyproject.toml`.

### Entry point

```toml
[project.scripts]
ytdl = "ytdl.cli:main"
```

After `uv pip install -e .`, running `ytdl` in the shell invokes `cli.main()`. `python -m ytdl` also works.

## Tooling Configuration

All config in `pyproject.toml` unless the tool requires its own file.

### Build system

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Hatchling handles `src/` layout automatically without extra configuration.

### Ruff (linter + formatter)

```toml
[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "RUF"]
```

Rule sets: pyflakes, pycodestyle, isort, naming, pyupgrade, bugbear, simplify, ruff-specific.

### Mypy (type checking)

```toml
[tool.mypy]
strict = true
python_version = "3.13"
```

### Pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Pre-commit hooks (`.pre-commit-config.yaml`)

1. `ruff check --fix` — lint with auto-fix
2. `ruff format` — format
3. `mypy` — type check (using `mirrors-mypy`)

### GitHub Actions CI (`.github/workflows/ci.yml`)

- Triggers: push and PR to `main`
- Runtime: Python 3.13
- Steps: checkout, install uv, `uv sync --dev`, `ruff check`, `ruff format --check`, `mypy src`, `pytest`

## Test Strategy

### `test_validation.py` — pure unit tests

- Valid URLs: standard `youtube.com/watch?v=`, `youtu.be/` short links, `/shorts/`, `/embed/`
- Invalid URLs: random strings, other domains, empty strings
- Edge cases: URLs with extra query params, timestamps

### `test_downloader.py` — mock `yt_dlp.YoutubeDL`

- Verify audio options: MP3 codec, 192kbps quality, FFmpegExtractAudio postprocessor
- Verify video options: `bv+ba/b` format string
- `DownloadError` returns `False`
- Unexpected exceptions return `False`
- Progress hook prints correct output for "downloading" and "finished" statuses (tested via direct import of `_progress_hook`)

### `test_cli.py` — mock `input()` and download functions

- `get_user_choice()`: accepts "1"/"2", rejects invalid input
- `get_youtube_url()`: valid URL accepted, invalid URL + retry flow
- `main()`: returns 0 on success, 1 on failure, 130 on KeyboardInterrupt

All tests run without network access or FFmpeg.

## What changes from current code

- `ytdl.py` is deleted and split into `src/ytdl/{cli,downloader,validation}.py`
- `pyproject.toml` gains: `[build-system]` with `hatchling` backend, `[project.scripts]`, tool configs, dev dependencies (pytest, mypy, ruff)
- New files: `__init__.py`, `__main__.py`, test files, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `.gitignore`
- Function names stay the same except dropping `_from_youtube` suffix on downloader functions (`download_audio`, `download_video`) since the module context makes it redundant
- No behavioral changes to the CLI
