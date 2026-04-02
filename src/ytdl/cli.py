"""Interactive CLI for YouTube downloads."""

from simple_term_menu import TerminalMenu

from ytdl.downloader import download_audio, download_transcript, download_video
from ytdl.validation import is_valid_youtube_url

OPTIONS = [
    ("Download video", download_video),
    ("Extract audio to MP3", download_audio),
    ("Download transcript", download_transcript),
]


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


def get_user_choices() -> list[int]:
    """Show interactive multi-select menu. Returns selected indices."""
    labels = [label for label, _ in OPTIONS]
    menu = TerminalMenu(
        labels,
        title="Select download options:",
        multi_select=True,
        show_multi_select_hint=True,
    )
    selected = menu.show()

    if selected is None:
        return []
    if isinstance(selected, int):
        return [selected]
    return list(selected)


def main() -> int:
    """Main entry point. Returns exit code."""
    try:
        url = get_youtube_url()
        choices = get_user_choices()

        if not choices:
            print("No options selected.")
            return 1

        all_success = True
        for idx in choices:
            label, download_fn = OPTIONS[idx]
            print(f"\n{label}...")
            if not download_fn(url):
                all_success = False

        if all_success:
            print("\nDone!")
            return 0
        else:
            print("\nSome downloads failed.")
            return 1
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        return 130
