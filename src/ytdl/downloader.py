"""YouTube download functions using yt-dlp."""

import re
from pathlib import Path

import yt_dlp

DOWNLOAD_DIR = Path("downloads")


def download_audio(url: str) -> bool:
    """Download audio from YouTube and convert to MP3 at 192kbps.

    Returns True on success, False on failure.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s_audio_tmp.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "progress_hooks": [_progress_hook],
    }

    DOWNLOAD_DIR.mkdir(exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                return False
            # The temp suffix keeps this download from colliding with a video
            # download of the same title; rename back to the clean name here.
            tmp_path = Path(ydl.prepare_filename(info)).with_suffix(".mp3")
            final_path = tmp_path.with_name(tmp_path.name.replace("_audio_tmp", ""))
            if tmp_path.exists():
                tmp_path.rename(final_path)
                print(f"\n  Audio saved to: {final_path}")
            else:
                print(
                    f"\n  Warning: expected {tmp_path.name} after conversion but it "
                    "was not found; the file may still have its temporary name."
                )
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
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
        "progress_hooks": [_progress_hook],
    }

    DOWNLOAD_DIR.mkdir(exist_ok=True)
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


def download_transcript(url: str) -> bool:
    """Download transcript/subtitles from YouTube as a plain text file.

    Tries manual subtitles first, falls back to auto-generated captions.
    Returns True on success, False on failure.
    """
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "subtitlesformat": "vtt",
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
    }

    DOWNLOAD_DIR.mkdir(exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                print("\nError: could not extract video info.")
                return False

            # Use prepare_filename to get the sanitized base path yt-dlp actually uses
            base = Path(ydl.prepare_filename(info))
            stem = base.with_suffix("").as_posix()  # strip the .ext part
            for suffix in (".en.vtt", ".en.srt"):
                sub_path = Path(f"{stem}{suffix}")
                if sub_path.exists():
                    txt_path = base.with_suffix(".txt")
                    txt_path.write_text(
                        _strip_timestamps(sub_path.read_text(encoding="utf-8")),
                        encoding="utf-8",
                    )
                    sub_path.unlink()
                    print(f"\n  Transcript saved to: {txt_path}")
                    return True

            print("\nNo English subtitles or captions available for this video.")
            return False
    except yt_dlp.utils.DownloadError as e:
        print(f"\nError downloading: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False


def _strip_timestamps(vtt_text: str) -> str:
    """Strip VTT/SRT formatting to produce clean plain text."""
    # Remove VTT header
    text = re.sub(r"WEBVTT\n.*?\n\n", "", vtt_text, count=1, flags=re.DOTALL)
    # Remove timestamp lines (00:00:00.000 --> 00:00:00.000)
    text = re.sub(r"\d{2}:\d{2}[:\.]\d{2}[\.\d]* --> \d{2}:\d{2}[:\.\d]+.*\n", "", text)
    # Remove numeric cue identifiers
    text = re.sub(r"^\d+$", "", text, flags=re.MULTILINE)
    # Remove HTML-like tags and entities
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove duplicate consecutive lines (common in VTT)
    lines: list[str] = []
    for line in text.strip().splitlines():
        stripped = line.strip()
        if stripped and (not lines or stripped != lines[-1]):
            lines.append(stripped)
    return "\n".join(lines) + "\n"


def _progress_hook(d: dict[str, object]) -> None:
    """Display download progress."""
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "?%")
        speed = d.get("_speed_str", "?")
        print(f"\r  Downloading: {percent} at {speed}", end="", flush=True)
    elif d["status"] == "finished":
        print("\n  Download complete, processing...")
