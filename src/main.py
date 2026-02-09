import logging
import sys
import os
from PySide6.QtWidgets import QApplication
# Importing our own modules from the src folder
from ui.main_window import MainWindow
from core.av_engine import AVEngine

# Debug: show RTSP logs in PyCharm Run console
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logging.getLogger("RTSP").setLevel(logging.DEBUG)


def main():
    """
    Main entry point of the VisionGrid application.
    Connects the Video Engine (PyAV) to the User Interface (PySide6).
    """
    app = QApplication(sys.argv)
    app.setApplicationName("VisionGrid RTSP Player")

    # Initialize components
    window = MainWindow()
    engine = AVEngine()

    # Communication Bridge: Using Qt Signals & Slots
    # This is where PyAV's power shines - it pushes frames to the UI thread
    engine.new_frame_signal.connect(window.video_display.update_frame)
    
    # Connect error and status signals from engine to UI
    engine.error_signal.connect(window._handle_error)
    engine.status_signal.connect(window._handle_status_change)

    # Connecting UI events to Engine actions
    window.connect_requested.connect(engine.start_stream)
    window.stop_requested.connect(engine.stop)

    window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()