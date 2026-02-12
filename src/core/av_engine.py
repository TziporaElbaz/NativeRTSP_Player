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
    RTSP stream decoding and local webcam support.
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
        """

        def emit_error(user_msg: str, technical: str):
            logger.error("RTSP error: %s | %s", user_msg, technical)
            traceback.print_exc()
            self.error_signal.emit(user_msg, technical)

        try:
            logger.info("Opening source: %s", url)

            # --- החלק ששינינו מתחיל כאן ---
            url_str = str(url).strip()
            is_rtsp = url_str.startswith("rtsp://")
            is_webcam = url_str.isdigit() or url_str.startswith("video=")

            if is_rtsp:
                # RTSP source
                options = {
                    "rtsp_transport": "tcp",
                    "stimeout": "5000000",
                    "buffer_size": "1024000",
                }
                self._container = av.open(url_str, options=options)

            elif is_webcam:
                # Webcam source for Windows (DirectShow)
                camera_src = f"video={url_str}" if url_str.isdigit() else url_str
                logger.info(f"Attempting to open webcam via dshow: {camera_src}")
                self._container = av.open(camera_src, format='dshow')

            else:
                # Local file source
                self._container = av.open(url_str)
            # --- החלק ששינינו נגמר כאן ---

            if not self._container.streams.video:
                emit_error("No video data received from source", "Container has no video stream.")
                self.stop()
                return

            stream = self._container.streams.video[0]
            stream.thread_type = 'AUTO'

            self.status_signal.emit("Streaming")
            frame_count = 0

            for frame in self._container.decode(stream):
                if not self._is_running:
                    break

                frame_count += 1

                try:
                    img = frame.to_image()
                    data = img.tobytes("raw", "RGB")
                    q_img = QImage(data, img.width, img.height, QImage.Format_RGB888)
                    self.new_frame_signal.emit(q_img)
                except Exception:
                    continue

            if frame_count == 0 and self._is_running:
                emit_error("No video data received from source", "Decode loop ended with 0 frames.")

        except (av.FFmpegError, av.OSError) as e:
            technical = f"{type(e).__name__}: {e}"
            error_msg = str(e).lower()
            if '401' in error_msg or 'unauthorized' in error_msg:
                emit_error("Authentication failed. Check credentials", technical)
            else:
                emit_error("Connection failed. Check source and network", technical)
            self.stop()
        except Exception as e:
            technical = f"{type(e).__name__}: {e}"
            emit_error(f"Error: {str(e)}", technical)
            self.stop()
        finally:
            if self._container:
                try:
                    self._container.close()
                except Exception:
                    pass
                self._container = None

    def stop(self):
        was_running = self._is_running
        self._is_running = False
        if self._thread and threading.current_thread() != self._thread:
            self._thread.join(timeout=2.0)
        if was_running:
            self.status_signal.emit("Ready")