"""
Unit tests for URLValidator.
Run from project root: pytest tests/ -v
"""
import pytest
import sys
from pathlib import Path

# Ensure src is on path when running tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.core.url_validator import URLValidator


class TestURLValidatorValidate:
    """Tests for URLValidator.validate()."""

    def test_empty_string_invalid(self):
        assert URLValidator.validate("") == (False, "Invalid RTSP URL format")
        assert URLValidator.validate("   ") == (False, "Invalid RTSP URL format")

    def test_rtsp_valid_with_host(self):
        valid, msg = URLValidator.validate("rtsp://192.168.1.1:554/stream")
        assert valid is True
        assert msg == ""

    def test_rtsp_valid_with_host_and_path(self):
        valid, msg = URLValidator.validate("rtsp://example.com:8554/live/channel1")
        assert valid is True
        assert msg == ""

    def test_rtsp_valid_with_credentials(self):
        valid, msg = URLValidator.validate("rtsp://user:pass@host/path")
        assert valid is True
        assert msg == ""

    def test_rtsp_no_hostname_invalid(self):
        # rtsp:// with no host (malformed) - urlparse might still return something
        valid, msg = URLValidator.validate("rtsp://")
        assert valid is False
        assert "Invalid RTSP URL format" in msg

    def test_non_rtsp_local_path_accepted(self):
        """Local file paths are accepted (validation done later by AV engine)."""
        valid, msg = URLValidator.validate("C:\\Users\\test\\video.mp4")
        assert valid is True
        assert msg == ""

    def test_non_rtsp_relative_path_accepted(self):
        valid, msg = URLValidator.validate("test.MP4")
        assert valid is True
        assert msg == ""

    def test_http_rejected_as_rtsp_but_accepted_as_non_rtsp(self):
        """HTTP URL is not RTSP; we accept it as generic input (AV engine may fail later)."""
        valid, msg = URLValidator.validate("http://example.com/video.mp4")
        assert valid is True
        assert msg == ""

    def test_whitespace_stripped(self):
        valid, msg = URLValidator.validate("  rtsp://host/path  ")
        assert valid is True
        assert msg == ""


class TestURLValidatorExtractCredentials:
    """Tests for URLValidator.extract_credentials()."""

    def test_no_credentials(self):
        assert URLValidator.extract_credentials("rtsp://host/path") == ("", "")

    def test_with_username_only(self):
        user, pw = URLValidator.extract_credentials("rtsp://admin@host/path")
        assert user == "admin"
        assert pw == ""

    def test_with_username_and_password(self):
        user, pw = URLValidator.extract_credentials("rtsp://user:password@host/path")
        assert user == "user"
        assert pw == "password"

    def test_invalid_url_returns_empty(self):
        assert URLValidator.extract_credentials("not-a-url") == ("", "")
