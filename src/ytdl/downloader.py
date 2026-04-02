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
