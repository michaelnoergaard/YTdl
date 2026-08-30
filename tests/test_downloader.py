"""Tests for download functions."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ytdl.downloader import (
    _progress_hook,
    _strip_timestamps,
    download_audio,
    download_transcript,
    download_video,
)


def _wire_ydl(
    mock_ydl_class: MagicMock,
    *,
    prepared: Path | None = None,
    info: object = "default",
) -> MagicMock:
    """Wire a mocked YoutubeDL context manager and return the inner mock.

    `prepared` is the path yt-dlp would report via prepare_filename(); without
    it the mock returns a synthetic path that never exists on disk.
    """
    mock_ydl = MagicMock()
    if prepared is not None:
        mock_ydl.prepare_filename.return_value = str(prepared)
    mock_ydl.extract_info.return_value = (
        {"title": "Video"} if info == "default" else info
    )
    mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
    return mock_ydl


class TestDownloadAudio:
    """Tests for download_audio()."""

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_success_returns_true(
        self, mock_ydl_class: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("ytdl.downloader.DOWNLOAD_DIR", tmp_path)
        (tmp_path / "Video_audio_tmp.mp3").touch()
        _wire_ydl(mock_ydl_class, prepared=tmp_path / "Video_audio_tmp.webm")
        assert download_audio("https://youtu.be/test") is True

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_passes_mp3_options(self, mock_ydl_class: MagicMock) -> None:
        _wire_ydl(mock_ydl_class)
        download_audio("https://youtu.be/test")
        opts = mock_ydl_class.call_args[0][0]
        assert opts["format"] == "bestaudio/best"
        assert "downloads" in opts["outtmpl"]
        pp = opts["postprocessors"][0]
        assert pp["key"] == "FFmpegExtractAudio"
        assert pp["preferredcodec"] == "mp3"
        assert pp["preferredquality"] == "192"

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_renames_temp_file_to_clean_name(
        self, mock_ydl_class: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("ytdl.downloader.DOWNLOAD_DIR", tmp_path)
        tmp_file = tmp_path / "Video_audio_tmp.mp3"
        tmp_file.touch()
        _wire_ydl(mock_ydl_class, prepared=tmp_path / "Video_audio_tmp.webm")

        assert download_audio("https://youtu.be/test") is True
        assert (tmp_path / "Video.mp3").exists()
        assert not tmp_file.exists()

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_warns_when_converted_file_missing(
        self,
        mock_ydl_class: MagicMock,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr("ytdl.downloader.DOWNLOAD_DIR", tmp_path)
        _wire_ydl(mock_ydl_class, prepared=tmp_path / "Video_audio_tmp.webm")

        assert download_audio("https://youtu.be/test") is True
        assert "Warning" in capsys.readouterr().out

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_info_none_returns_false(self, mock_ydl_class: MagicMock) -> None:
        _wire_ydl(mock_ydl_class, info=None)
        assert download_audio("https://youtu.be/test") is False

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
        _wire_ydl(mock_ydl_class)
        assert download_video("https://youtu.be/test") is True

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_passes_video_format(self, mock_ydl_class: MagicMock) -> None:
        _wire_ydl(mock_ydl_class)
        download_video("https://youtu.be/test")
        opts = mock_ydl_class.call_args[0][0]
        assert opts["format"] == "bv+ba/b"
        assert "downloads" in opts["outtmpl"]


class TestDownloadTranscript:
    """Tests for download_transcript()."""

    VTT = (
        "WEBVTT\nKind: captions\n\n"
        "00:00:00.000 --> 00:00:02.000\n"
        "Hello world\n\n"
        "00:00:02.000 --> 00:00:04.000\n"
        "Second line\n\n"
    )

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_passes_subtitle_options(self, mock_ydl_class: MagicMock) -> None:
        _wire_ydl(mock_ydl_class)
        download_transcript("https://youtu.be/test")
        opts = mock_ydl_class.call_args[0][0]
        assert opts["skip_download"] is True
        assert opts["writesubtitles"] is True
        assert opts["writeautomaticsub"] is True
        assert opts["subtitleslangs"] == ["en"]
        assert opts["subtitlesformat"] == "vtt"

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_converts_vtt_to_text(
        self, mock_ydl_class: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("ytdl.downloader.DOWNLOAD_DIR", tmp_path)
        vtt = tmp_path / "Video.en.vtt"
        vtt.write_text(self.VTT, encoding="utf-8")
        _wire_ydl(mock_ydl_class, prepared=tmp_path / "Video.mp4")

        assert download_transcript("https://youtu.be/test") is True
        txt = tmp_path / "Video.txt"
        assert txt.exists()
        content = txt.read_text(encoding="utf-8")
        assert "Hello world" in content
        assert "Second line" in content
        assert "-->" not in content
        assert not vtt.exists(), "source subtitle file should be cleaned up"

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_falls_back_to_srt(
        self, mock_ydl_class: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("ytdl.downloader.DOWNLOAD_DIR", tmp_path)
        (tmp_path / "Video.en.srt").write_text(self.VTT, encoding="utf-8")
        _wire_ydl(mock_ydl_class, prepared=tmp_path / "Video.mp4")

        assert download_transcript("https://youtu.be/test") is True
        assert (tmp_path / "Video.txt").exists()

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_no_subtitles_returns_false(
        self,
        mock_ydl_class: MagicMock,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr("ytdl.downloader.DOWNLOAD_DIR", tmp_path)
        _wire_ydl(mock_ydl_class, prepared=tmp_path / "Video.mp4")

        assert download_transcript("https://youtu.be/test") is False
        assert "No English subtitles" in capsys.readouterr().out

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_info_none_returns_false(self, mock_ydl_class: MagicMock) -> None:
        _wire_ydl(mock_ydl_class, info=None)
        assert download_transcript("https://youtu.be/test") is False

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_download_error_returns_false(self, mock_ydl_class: MagicMock) -> None:
        import yt_dlp

        mock_ydl_class.return_value.__enter__ = MagicMock(
            side_effect=yt_dlp.utils.DownloadError("fail")
        )
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        assert download_transcript("https://youtu.be/test") is False

    @patch("ytdl.downloader.yt_dlp.YoutubeDL")
    def test_unexpected_error_returns_false(self, mock_ydl_class: MagicMock) -> None:
        mock_ydl_class.return_value.__enter__ = MagicMock(
            side_effect=RuntimeError("boom")
        )
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        assert download_transcript("https://youtu.be/test") is False


class TestProgressHook:
    """Tests for _progress_hook()."""

    def test_downloading_status(self, capsys: pytest.CaptureFixture[str]) -> None:
        _progress_hook(
            {
                "status": "downloading",
                "_percent_str": "50.0%",
                "_speed_str": "1.5MiB/s",
            }
        )
        captured = capsys.readouterr()
        assert "50.0%" in captured.out
        assert "1.5MiB/s" in captured.out

    def test_finished_status(self, capsys: pytest.CaptureFixture[str]) -> None:
        _progress_hook({"status": "finished"})
        captured = capsys.readouterr()
        assert "complete" in captured.out.lower()


class TestStripTimestamps:
    """Tests for _strip_timestamps()."""

    def test_strips_vtt_format(self) -> None:
        vtt = (
            "WEBVTT\nKind: captions\nLanguage: en\n\n"
            "00:00:00.000 --> 00:00:02.000\n"
            "Hello world\n\n"
            "00:00:02.000 --> 00:00:04.000\n"
            "This is a test\n\n"
        )
        result = _strip_timestamps(vtt)
        assert "Hello world" in result
        assert "This is a test" in result
        assert "-->" not in result
        assert "WEBVTT" not in result

    def test_removes_duplicate_lines(self) -> None:
        vtt = (
            "WEBVTT\n\n"
            "00:00:00.000 --> 00:00:02.000\n"
            "Same line\n\n"
            "00:00:02.000 --> 00:00:04.000\n"
            "Same line\n\n"
            "00:00:04.000 --> 00:00:06.000\n"
            "Different line\n\n"
        )
        result = _strip_timestamps(vtt)
        assert result.count("Same line") == 1
        assert "Different line" in result
