import av
import logging
import threading
import traceback
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage

# For debugging: see logs in PyCharm Run console
logger = logging.getLogger("RTSP")
logger.setLevel(logging.DEBUG)


class AVEngine(QObject):
    """
    Video engine using PyAV (FFmpeg bindings) for high-performance
    RTSP stream decoding.
    """
    # Signal to send decoded frames to the UI thread
    new_frame_signal = Signal(QImage)
    # (user_message, technical_detail) for UI; detail shown in "Show Details"
    error_signal = Signal(str, str)
    # Signal to report connection status changes
    status_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._thread = None
        self._container = None

    def start_stream(self, url: str):
        """Initializes and starts the background decoding thread."""
        # Stop any existing stream first
        if self._is_running:
            self.stop()
            # Wait for thread to finish if it exists
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=0.5)

        # Reset state
        self._is_running = True
        self.status_signal.emit("Connecting")
        self._thread = threading.Thread(
            target=self._decode_loop,
            args=(url,),
            daemon=True
        )
        self._thread.start()

    def _decode_loop(self, url: str):
        """
        Background loop for fetching and decoding packets from a source.

        The source can be:
        - RTSP URL (rtsp://...) with low-latency RTSP-specific options.
        - Local file path (e.g. C:\\video\\test.mp4) for offline debugging.
        """

        def emit_error(user_msg: str, technical: str):
            """
            Log an error to the console (and PyCharm Run window) and notify the UI.

            user_msg   - short, user-friendly message shown in the UI.
            technical  - detailed technical info for debugging (exception type, message).
            """
            logger.error("RTSP error: %s | %s", user_msg, technical)
            traceback.print_exc()
            self.error_signal.emit(user_msg, technical)

        try:
            logger.info("Opening source: %s", url)

            # Detect if this is an RTSP URL or a local/other source.
            is_rtsp = isinstance(url, str) and url.startswith("rtsp://")

            if is_rtsp:
                # RTSP source: use FFmpeg / PyAV RTSP tuning options for stability and low latency.
                options = {
                    "rtsp_transport": "tcp",
                    "stimeout": "5000000",  # 5 seconds timeout (in microseconds for FFmpeg)
                    "buffer_size": "1024000",
                }

                try:
                    self._container = av.open(url, options=options)
                    logger.info("Connected to RTSP stream, opening video streams.")
                except (av.FFmpegError, av.OSError) as e:
                    technical = f"{type(e).__name__}: {e}"
                    error_msg = str(e).lower()
                    if "401" in error_msg or "unauthorized" in error_msg or "authentication" in error_msg:
                        emit_error("Authentication failed. Check username and password", technical)
                    elif "404" in error_msg or "not found" in error_msg:
                        emit_error("Unable to connect to stream. Check URL and network connection", technical)
                    else:
                        emit_error("Unable to connect to stream. Check URL and network connection", technical)
                    self.stop()
                    return
                except Exception as e:
                    # Any other unexpected error while opening RTSP.
                    technical = f"{type(e).__name__}: {e}"
                    error_msg = str(e).lower()
                    if "timeout" in error_msg or "connection" in error_msg:
                        emit_error("Unable to connect to stream. Check URL and network connection", technical)
                    else:
                        emit_error("Unable to connect to stream. Check URL and network connection", technical)
                    self.stop()
                    return
            else:
                # Non-RTSP source: treat as local file or generic media URL.
                try:
                    logger.info("Opening local/generic media source: %s", url)
                    self._container = av.open(url)
                except Exception as e:
                    technical = f"{type(e).__name__}: {e}"
                    emit_error("Failed to open local file or media source", technical)
                    self.stop()
                    return

            # Check if a video stream exists in the opened container.
            if not self._container.streams.video:
                emit_error("No video data received from source", "Container has no video stream.")
                self.stop()
                return

            stream = self._container.streams.video[0]

            # Setting thread count for FFmpeg decoder
            stream.thread_type = 'AUTO'

            self.status_signal.emit("Streaming")
            frame_count = 0

            for frame in self._container.decode(stream):
                if not self._is_running:
                    break

                frame_count += 1
                
                # Convert frame to RGB for Qt compatibility
                try:
                    img = frame.to_image()

                    # Convert PIL image to QImage
                    data = img.tobytes("raw", "RGB")
                    q_img = QImage(data, img.width, img.height, QImage.Format_RGB888)

                    # Emit signal to main UI thread
                    self.new_frame_signal.emit(q_img)
                except Exception:
                    # Frame decoding error - continue to next frame
                    continue

            # If we exit the loop without receiving frames
            if frame_count == 0 and self._is_running:
                emit_error("No video data received from source", "Decode loop ended with 0 frames.")

        except (av.FFmpegError, av.OSError) as e:
            technical = f"{type(e).__name__}: {e}"
            error_msg = str(e).lower()
            if '401' in error_msg or 'unauthorized' in error_msg or 'authentication' in error_msg:
                emit_error("Authentication failed. Check username and password", technical)
            elif 'timeout' in error_msg or 'connection' in error_msg:
                emit_error("Unable to connect to stream. Check URL and network connection", technical)
            else:
                emit_error("Unable to connect to stream. Check URL and network connection", technical)
            self.stop()
        except Exception as e:
            technical = f"{type(e).__name__}: {e}"
            error_msg = str(e).lower()
            if 'timeout' in error_msg or 'connection' in error_msg:
                emit_error("Unable to connect to stream. Check URL and network connection", technical)
            else:
                emit_error(f"Error: {str(e)}", technical)
            self.stop()
        finally:
            # Always close container in this (decode) thread on any exit path.
            if self._container:
                try:
                    self._container.close()
                except Exception:
                    pass
                self._container = None

    def stop(self):
        """
        Gracefully stops the decoding thread.
        Only sets _is_running = False; the decode thread closes the container
        when it exits the loop to avoid closing it from another thread (which would crash).
        """
        was_running = self._is_running
        self._is_running = False

        # Do NOT close self._container here. The decode thread is still iterating
        # over it; closing from the main thread causes a crash. The decode thread
        # will close the container when it breaks out of the loop.

        if self._thread and threading.current_thread() != self._thread:
            self._thread.join(timeout=2.0)

        if was_running:
            self.status_signal.emit("Ready")