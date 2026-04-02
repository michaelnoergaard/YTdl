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
