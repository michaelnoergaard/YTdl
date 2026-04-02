# Python Best Practices Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure YTdl from a single-script YouTube downloader into a properly packaged Python project with src layout, full tooling (Ruff, mypy, pytest), pre-commit hooks, and GitHub Actions CI.

**Architecture:** Split `ytdl.py` into three modules under `src/ytdl/` — `validation.py` (URL checking), `downloader.py` (yt-dlp wrappers), `cli.py` (interactive prompts + orchestration). All tooling config lives in `pyproject.toml`. Tests mock yt-dlp and `input()` so they run without network or FFmpeg.

**Tech Stack:** Python 3.13, uv, yt-dlp, hatchling, Ruff, mypy, pytest, pre-commit, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-04-02-python-best-practices-refactor-design.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `src/ytdl/__init__.py` | Dynamic version from package metadata |
| Create | `src/ytdl/__main__.py` | `python -m ytdl` entry point |
| Create | `src/ytdl/validation.py` | `is_valid_youtube_url()` |
| Create | `src/ytdl/downloader.py` | `download_audio()`, `download_video()`, `_progress_hook()` |
| Create | `src/ytdl/cli.py` | `get_youtube_url()`, `get_user_choice()`, `main()` |
| Create | `tests/test_validation.py` | URL validation unit tests |
| Create | `tests/test_downloader.py` | Download function tests (mocked yt-dlp) |
| Create | `tests/test_cli.py` | CLI interaction tests (mocked input) |
| Modify | `pyproject.toml` | Build system, entry point, dev deps, tool configs |
| Create | `.pre-commit-config.yaml` | Ruff + mypy hooks |
| Create | `.github/workflows/ci.yml` | CI pipeline |
| Delete | `ytdl.py` | Replaced by `src/ytdl/` package |

---

### Task 1: Project scaffolding — pyproject.toml and package skeleton

**Files:**
- Modify: `pyproject.toml`
- Create: `src/ytdl/__init__.py`
- Create: `src/ytdl/__main__.py`

- [ ] **Step 1: Update `pyproject.toml`**

Replace the entire file with the new configuration:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ytdl"
version = "0.1.0"
description = "YouTube downloader utility for video downloads and audio extraction"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "yt-dlp>=2025.6.30",
]

[project.scripts]
ytdl = "ytdl.cli:main"

[dependency-groups]
dev = [
    "mypy>=1.15",
    "pytest>=8.0",
    "ruff>=0.11",
    "pre-commit>=4.0",
]

[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "RUF"]

[tool.mypy]
strict = true
python_version = "3.13"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create `src/ytdl/__init__.py`**

```python
"""YouTube downloader utility for video downloads and audio extraction."""

from importlib.metadata import version

__version__ = version("ytdl")
```

- [ ] **Step 3: Create `src/ytdl/__main__.py`**

```python
"""Allow running as `python -m ytdl`."""

import sys

from ytdl.cli import main

sys.exit(main())
```

- [ ] **Step 4: Install dependencies and verify package resolves**

Run: `cd /home/michael/projects/Python/YTdl && uv sync`
Expected: Dependencies install successfully including dev group.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/ytdl/__init__.py src/ytdl/__main__.py
git commit -m "feat: scaffold src layout with hatchling build system"
```

---

### Task 2: Validation module (TDD)

**Files:**
- Create: `src/ytdl/validation.py`
- Create: `tests/test_validation.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_validation.py`:

```python
"""Tests for YouTube URL validation."""

import pytest

from ytdl.validation import is_valid_youtube_url


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120",
        "https://youtu.be/dQw4w9WgXcQ?t=30",
    ],
)
def test_valid_urls(url: str) -> None:
    assert is_valid_youtube_url(url) is True


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not a url",
        "https://vimeo.com/123456",
        "https://www.google.com",
        "https://youtube.com/",
        "https://youtube.com/channel/UCxxxxxxx",
    ],
)
def test_invalid_urls(url: str) -> None:
    assert is_valid_youtube_url(url) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/michael/projects/Python/YTdl && uv run pytest tests/test_validation.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ytdl.validation'`

- [ ] **Step 3: Write the implementation**

Create `src/ytdl/validation.py`:

```python
"""YouTube URL validation."""

import re


def is_valid_youtube_url(url: str) -> bool:
    """Check if URL appears to be a valid YouTube URL."""
    patterns = [
        r"youtube\.com/watch\?v=",
        r"youtu\.be/",
        r"youtube\.com/shorts/",
        r"youtube\.com/embed/",
    ]
    return any(re.search(pattern, url) for pattern in patterns)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/michael/projects/Python/YTdl && uv run pytest tests/test_validation.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Run mypy**

Run: `cd /home/michael/projects/Python/YTdl && uv run mypy src/ytdl/validation.py`
Expected: `Success: no issues found`

- [ ] **Step 6: Commit**

```bash
git add src/ytdl/validation.py tests/test_validation.py
git commit -m "feat: add validation module with URL pattern checking"
```

---

### Task 3: Downloader module (TDD)

**Files:**
- Create: `src/ytdl/downloader.py`
- Create: `tests/test_downloader.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_downloader.py`:

```python
"""Tests for download functions."""

from unittest.mock import MagicMock, patch

import pytest

from ytdl.downloader import _progress_hook, download_audio, download_video


class TestDownloadAudio:
    """Tests for download_audio()."""

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_success_returns_true(self, mock_ydl_class: MagicMock) -> None:
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        assert download_audio("https://youtu.be/test") is True

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_passes_mp3_options(self, mock_ydl_class: MagicMock) -> None:
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        download_audio("https://youtu.be/test")
        opts = mock_ydl_class.call_args[0][0]
        assert opts["format"] == "bestaudio/best"
        pp = opts["postprocessors"][0]
        assert pp["key"] == "FFmpegExtractAudio"
        assert pp["preferredcodec"] == "mp3"
        assert pp["preferredquality"] == "192"

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_download_error_returns_false(self, mock_ydl_class: MagicMock) -> None:
        import yt_dlp

        mock_ydl_class.return_value.__enter__ = MagicMock(
            side_effect=yt_dlp.utils.DownloadError("fail")
        )
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        assert download_audio("https://youtu.be/test") is False

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_unexpected_error_returns_false(self, mock_ydl_class: MagicMock) -> None:
        mock_ydl_class.return_value.__enter__ = MagicMock(
            side_effect=RuntimeError("boom")
        )
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        assert download_audio("https://youtu.be/test") is False


class TestDownloadVideo:
    """Tests for download_video()."""

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_success_returns_true(self, mock_ydl_class: MagicMock) -> None:
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        assert download_video("https://youtu.be/test") is True

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_passes_video_format(self, mock_ydl_class: MagicMock) -> None:
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        download_video("https://youtu.be/test")
        opts = mock_ydl_class.call_args[0][0]
        assert opts["format"] == "bv+ba/b"


class TestProgressHook:
    """Tests for _progress_hook()."""

    def test_downloading_status(self, capsys: pytest.CaptureFixture[str]) -> None:
        _progress_hook({
            "status": "downloading",
            "_percent_str": "50.0%",
            "_speed_str": "1.5MiB/s",
        })
        captured = capsys.readouterr()
        assert "50.0%" in captured.out
        assert "1.5MiB/s" in captured.out

    def test_finished_status(self, capsys: pytest.CaptureFixture[str]) -> None:
        _progress_hook({"status": "finished"})
        captured = capsys.readouterr()
        assert "complete" in captured.out.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/michael/projects/Python/YTdl && uv run pytest tests/test_downloader.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ytdl.downloader'`

- [ ] **Step 3: Write the implementation**

Create `src/ytdl/downloader.py`:

```python
"""YouTube download functions using yt-dlp."""

import yt_dlp


def download_audio(url: str) -> bool:
    """Download audio from YouTube and convert to MP3 at 192kbps.

    Returns True on success, False on failure.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "progress_hooks": [_progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except yt_dlp.utils.DownloadError as e:
        print(f"\nError downloading: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False


def download_video(url: str) -> bool:
    """Download video from YouTube with best quality.

    Returns True on success, False on failure.
    """
    ydl_opts = {
        "format": "bv+ba/b",
        "outtmpl": "%(title)s.%(ext)s",
        "progress_hooks": [_progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except yt_dlp.utils.DownloadError as e:
        print(f"\nError downloading: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False


def _progress_hook(d: dict[str, object]) -> None:
    """Display download progress."""
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "?%")
        speed = d.get("_speed_str", "?")
        print(f"\r  Downloading: {percent} at {speed}", end="", flush=True)
    elif d["status"] == "finished":
        print("\n  Download complete, processing...")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/michael/projects/Python/YTdl && uv run pytest tests/test_downloader.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Run mypy**

Run: `cd /home/michael/projects/Python/YTdl && uv run mypy src/ytdl/downloader.py`
Expected: `Success: no issues found`

- [ ] **Step 6: Commit**

```bash
git add src/ytdl/downloader.py tests/test_downloader.py
git commit -m "feat: add downloader module with audio/video download functions"
```

---

### Task 4: CLI module (TDD)

**Files:**
- Create: `src/ytdl/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cli.py`:

```python
"""Tests for CLI interaction."""

from unittest.mock import patch

import pytest

from ytdl.cli import get_user_choice, get_youtube_url, main


class TestGetUserChoice:
    """Tests for get_user_choice()."""

    @patch("builtins.input", return_value="1")
    def test_choice_1(self, _mock: object) -> None:
        assert get_user_choice() == "1"

    @patch("builtins.input", return_value="2")
    def test_choice_2(self, _mock: object) -> None:
        assert get_user_choice() == "2"

    @patch("builtins.input", side_effect=["3", "abc", "1"])
    def test_rejects_invalid_then_accepts(self, _mock: object) -> None:
        assert get_user_choice() == "1"


class TestGetYoutubeUrl:
    """Tests for get_youtube_url()."""

    @patch("builtins.input", return_value="https://youtu.be/dQw4w9WgXcQ")
    def test_valid_url_accepted(self, _mock: object) -> None:
        assert get_youtube_url() == "https://youtu.be/dQw4w9WgXcQ"

    @patch("builtins.input", side_effect=["not-a-url", "n", "https://youtu.be/abc"])
    def test_invalid_url_retry(self, _mock: object) -> None:
        assert get_youtube_url() == "https://youtu.be/abc"

    @patch("builtins.input", side_effect=["not-a-url", "y"])
    def test_invalid_url_forced(self, _mock: object) -> None:
        assert get_youtube_url() == "not-a-url"


class TestMain:
    """Tests for main()."""

    @patch("ytdl.cli.download_video", return_value=True)
    @patch("ytdl.cli.get_user_choice", return_value="1")
    @patch("ytdl.cli.get_youtube_url", return_value="https://youtu.be/test")
    def test_success_returns_0(self, *_mocks: object) -> None:
        assert main() == 0

    @patch("ytdl.cli.download_audio", return_value=False)
    @patch("ytdl.cli.get_user_choice", return_value="2")
    @patch("ytdl.cli.get_youtube_url", return_value="https://youtu.be/test")
    def test_failure_returns_1(self, *_mocks: object) -> None:
        assert main() == 1

    @patch("ytdl.cli.get_youtube_url", side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt_returns_130(self, _mock: object) -> None:
        assert main() == 130
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/michael/projects/Python/YTdl && uv run pytest tests/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ytdl.cli'`

- [ ] **Step 3: Write the implementation**

Create `src/ytdl/cli.py`:

```python
"""Interactive CLI for YouTube downloads."""

from ytdl.downloader import download_audio, download_video
from ytdl.validation import is_valid_youtube_url


def get_youtube_url() -> str:
    """Prompt user for YouTube URL with validation."""
    while True:
        url = input("Enter YouTube URL: ").strip()
        if not url:
            print("URL cannot be empty. Please try again.")
            continue
        if not is_valid_youtube_url(url):
            print("That doesn't look like a valid YouTube URL.")
            retry = input("Try anyway? (y/n): ").strip().lower()
            if retry != "y":
                continue
        return url


def get_user_choice() -> str:
    """Prompt user for download type choice."""
    print("\nChoose download option:")
    print("1. Download video")
    print("2. Extract audio to MP3")

    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice in ("1", "2"):
            return choice
        print("Invalid choice. Please enter 1 or 2.")


def main() -> int:
    """Main entry point. Returns exit code."""
    try:
        url = get_youtube_url()
        choice = get_user_choice()

        if choice == "1":
            print("\nDownloading video...")
            success = download_video(url)
        else:
            print("\nExtracting audio to MP3...")
            success = download_audio(url)

        if success:
            print("\nDone!")
            return 0
        else:
            print("\nDownload failed.")
            return 1
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        return 130
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/michael/projects/Python/YTdl && uv run pytest tests/test_cli.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Run mypy on all source**

Run: `cd /home/michael/projects/Python/YTdl && uv run mypy src/`
Expected: `Success: no issues found`

- [ ] **Step 6: Run full test suite**

Run: `cd /home/michael/projects/Python/YTdl && uv run pytest -v`
Expected: All tests PASS across all three test files.

- [ ] **Step 7: Commit**

```bash
git add src/ytdl/cli.py tests/test_cli.py
git commit -m "feat: add CLI module with interactive prompts and KeyboardInterrupt handling"
```

---

### Task 5: Delete old script and verify entry points

**Files:**
- Delete: `ytdl.py`

- [ ] **Step 1: Delete the old single-file script**

```bash
rm /home/michael/projects/Python/YTdl/ytdl.py
```

- [ ] **Step 2: Verify `python -m ytdl` loads (Ctrl+C to exit the prompt)**

Run: `cd /home/michael/projects/Python/YTdl && echo "" | uv run python -m ytdl`
Expected: Shows "Enter YouTube URL:" prompt (then exits on empty input / EOFError).

- [ ] **Step 3: Run full test suite to confirm nothing broke**

Run: `cd /home/michael/projects/Python/YTdl && uv run pytest -v`
Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git rm ytdl.py
git add -A
git commit -m "refactor: remove old single-file script in favor of src/ytdl package"
```

---

### Task 6: Pre-commit hooks

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Create `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run mypy
        language: system
        types: [python]
        args: [--strict]
```

Note: Using a local hook with `uv run mypy` ensures mypy runs in the project's venv with all dependencies (including `yt-dlp`) available. The `mirrors-mypy` approach would fail because it runs in an isolated venv without project dependencies.

- [ ] **Step 2: Install pre-commit hooks**

Run: `cd /home/michael/projects/Python/YTdl && uv run pre-commit install`
Expected: `pre-commit installed at .git/hooks/pre-commit`

- [ ] **Step 3: Run pre-commit on all files to verify**

Run: `cd /home/michael/projects/Python/YTdl && uv run pre-commit run --all-files`
Expected: All hooks pass (ruff, ruff-format, mypy).

- [ ] **Step 4: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "chore: add pre-commit hooks for ruff and mypy"
```

---

### Task 7: GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Set up Python
        run: uv python install 3.13

      - name: Install dependencies
        run: uv sync

      - name: Lint
        run: uv run ruff check src/ tests/

      - name: Format check
        run: uv run ruff format --check src/ tests/

      - name: Type check
        run: uv run mypy src/

      - name: Test
        run: uv run pytest -v
```

- [ ] **Step 2: Validate YAML syntax**

Run: `cd /home/michael/projects/Python/YTdl && python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`
Expected: No error (exits cleanly). If `yaml` is not available, use: `python -c "import json, re; print('YAML looks valid')"` and visually confirm indentation.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow for lint, typecheck, and test"
```

---

### Task 8: Update .gitignore and CLAUDE.md

**Files:**
- Modify: `.gitignore`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update `.gitignore`**

Ensure `.gitignore` contains standard Python entries:

```gitignore
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.mypy_cache/
.pytest_cache/
.ruff_cache/
*.mp3
*.mp4
*.mkv
*.webm
.venv/
```

- [ ] **Step 2: Update `CLAUDE.md`**

Replace the Architecture and Development Commands sections with:

**Architecture section:**
```markdown
## Architecture

The package lives in `src/ytdl/` with three modules:

- **`validation.py`**: `is_valid_youtube_url(url)` — regex-based YouTube URL validation
- **`downloader.py`**: `download_audio(url)`, `download_video(url)` — yt-dlp wrapper functions. Downloads best quality video (merged) or extracts audio to MP3 at 192kbps. `_progress_hook()` displays live download progress.
- **`cli.py`**: `main()`, `get_youtube_url()`, `get_user_choice()` — interactive CLI prompts and orchestration. Entry point for both `ytdl` command and `python -m ytdl`.

Files are saved with the video title as filename. FFmpeg handles audio conversion and video merging.
```

**Development Commands section:**
```markdown
## Development Commands

\`\`\`bash
uv sync                          # Install dependencies (including dev tools)
uv run python -m ytdl            # Run the application
uv run pytest -v                 # Run tests
uv run ruff check src/ tests/    # Lint
uv run ruff format src/ tests/   # Format
uv run mypy src/                 # Type check
uv run pre-commit run --all-files  # Run all pre-commit hooks
uv add <package>                 # Add a new dependency
\`\`\`
```

- [ ] **Step 3: Run full test suite one final time**

Run: `cd /home/michael/projects/Python/YTdl && uv run pytest -v && uv run ruff check src/ tests/ && uv run mypy src/`
Expected: All tests pass, no lint errors, no type errors.

- [ ] **Step 4: Commit**

```bash
git add .gitignore CLAUDE.md
git commit -m "chore: update gitignore and CLAUDE.md for new project structure"
```
