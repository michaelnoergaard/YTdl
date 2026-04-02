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
