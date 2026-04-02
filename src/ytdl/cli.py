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
