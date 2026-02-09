"""
URL Validator module for RTSP URL format validation.
Provides clear error messages for invalid URL formats.
"""
import re
from urllib.parse import urlparse


class URLValidator:
    """Validates RTSP URL format and provides user-friendly error messages."""
    
    @staticmethod
    def validate(url: str) -> tuple[bool, str]:
        """
        Validates the input as either:
        - a RTSP URL (rtsp://...) with basic format checks, or
        - a local file path / non-RTSP URL, which we allow to pass.

        This lets us use the same input field for:
        - Real RTSP streams
        - Local video files (e.g. C:\\video\\test.mp4) for debugging
        - Other protocols if needed in the future

        Args:
            url: The URL string to validate.

        Returns:
            Tuple of (is_valid: bool, error_message: str).
            If valid, error_message will be an empty string.
        """
        if not url or not url.strip():
            # Empty input is always invalid
            return False, "Invalid RTSP URL format"

        url = url.strip()

        # If this is a RTSP URL, perform basic RTSP validation.
        if url.startswith("rtsp://"):
            try:
                parsed = urlparse(url)

                # Hostname is required for a valid RTSP URL.
                if not parsed.hostname:
                    return False, "Invalid RTSP URL format"

                # Basic format validation passed.
                return True, ""

            except Exception:
                return False, "Invalid RTSP URL format"

        # For non-RTSP inputs (e.g. local file path), we accept them.
        # Detailed validation (file exists, readable, etc.) is done
        # later by the AV engine when trying to open the source.
        return True, ""
    
    @staticmethod
    def extract_credentials(url: str) -> tuple[str, str]:
        """
        Extracts username and password from RTSP URL if present.
        
        Args:
            url: RTSP URL string
            
        Returns:
            Tuple of (username, password). Both will be empty strings if not present.
        """
        try:
            parsed = urlparse(url)
            if parsed.username:
                return parsed.username, parsed.password or ""
            return "", ""
        except Exception:
            return "", ""
