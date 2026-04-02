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
