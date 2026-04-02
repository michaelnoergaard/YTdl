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
