"""Tests for CLI interaction."""

from unittest.mock import MagicMock, patch

from ytdl.cli import get_user_choices, get_youtube_url, main


class TestGetUserChoices:
    """Tests for get_user_choices()."""

    @patch("ytdl.cli.TerminalMenu")
    def test_single_selection(self, mock_menu_cls: MagicMock) -> None:
        mock_menu_cls.return_value.show.return_value = 0
        assert get_user_choices() == [0]

    @patch("ytdl.cli.TerminalMenu")
    def test_multiple_selections(self, mock_menu_cls: MagicMock) -> None:
        mock_menu_cls.return_value.show.return_value = (0, 2)
        assert get_user_choices() == [0, 2]

    @patch("ytdl.cli.TerminalMenu")
    def test_no_selection_returns_empty(self, mock_menu_cls: MagicMock) -> None:
        mock_menu_cls.return_value.show.return_value = None
        assert get_user_choices() == []

    @patch("ytdl.cli.TerminalMenu")
    def test_all_three_selected(self, mock_menu_cls: MagicMock) -> None:
        mock_menu_cls.return_value.show.return_value = (0, 1, 2)
        assert get_user_choices() == [0, 1, 2]


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

    @patch("ytdl.cli.OPTIONS", [("Download video", MagicMock(return_value=True))])
    @patch("ytdl.cli.get_user_choices", return_value=[0])
    @patch("ytdl.cli.get_youtube_url", return_value="https://youtu.be/test")
    def test_success_returns_0(self, *_mocks: object) -> None:
        assert main() == 0

    @patch("ytdl.cli.OPTIONS", [("Extract audio", MagicMock(return_value=False))])
    @patch("ytdl.cli.get_user_choices", return_value=[0])
    @patch("ytdl.cli.get_youtube_url", return_value="https://youtu.be/test")
    def test_failure_returns_1(self, *_mocks: object) -> None:
        assert main() == 1

    @patch(
        "ytdl.cli.OPTIONS",
        [
            ("Download video", MagicMock(return_value=True)),
            ("Extract audio", MagicMock(return_value=True)),
        ],
    )
    @patch("ytdl.cli.get_user_choices", return_value=[0, 1])
    @patch("ytdl.cli.get_youtube_url", return_value="https://youtu.be/test")
    def test_multiple_choices_all_succeed(self, *_mocks: object) -> None:
        assert main() == 0

    @patch(
        "ytdl.cli.OPTIONS",
        [
            ("Download video", MagicMock(return_value=True)),
            ("Extract audio", MagicMock(return_value=False)),
        ],
    )
    @patch("ytdl.cli.get_user_choices", return_value=[0, 1])
    @patch("ytdl.cli.get_youtube_url", return_value="https://youtu.be/test")
    def test_partial_failure_returns_1(self, *_mocks: object) -> None:
        assert main() == 1

    @patch("ytdl.cli.get_user_choices", return_value=[])
    @patch("ytdl.cli.get_youtube_url", return_value="https://youtu.be/test")
    def test_no_selection_returns_1(self, *_mocks: object) -> None:
        assert main() == 1

    @patch("ytdl.cli.get_youtube_url", side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt_returns_130(self, _mock: object) -> None:
        assert main() == 130
