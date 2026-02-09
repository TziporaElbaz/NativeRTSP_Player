from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLineEdit, QPushButton, QLabel,
                               QMessageBox)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPixmap, QImage
import sys
import os

# Add parent directory to path to import from core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.url_validator import URLValidator


class VideoDisplay(QLabel):
    """Custom Label for rendering video frames with scaling."""

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText("No Stream Connected")
        self.setStyleSheet("background-color: #1a1a1a; color: #444; border: 1px solid #333;")
        self.setMinimumSize(640, 360)

    @Slot(QImage)
    def update_frame(self, q_img: QImage):
        """Updates the label with a new video frame."""
        # Scale image to fit the label size while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)


class MainWindow(QMainWindow):
    # Signals for communicating with the Engine
    connect_requested = Signal(str)
    stop_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisionGrid | Professional RTSP Suite")
        self.resize(1024, 768)
        self._is_connecting = False
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Control Bar
        controls = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter RTSP URL...")
        # Default test stream (Big Buck Bunny)
        self.url_input.setText("rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov")

        self.btn_toggle = QPushButton("Start Stream")
        self.btn_toggle.clicked.connect(self._handle_button_click)
        self.btn_toggle.setFixedWidth(120)

        controls.addWidget(self.url_input)
        controls.addWidget(self.btn_toggle)
        layout.addLayout(controls)

        # Video Area
        self.video_display = VideoDisplay()
        layout.addWidget(self.video_display, stretch=1)

        # Status Bar
        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

    def _handle_button_click(self):
        if self.btn_toggle.text() == "Start Stream":
            # Prevent double-clicking
            if self._is_connecting:
                return
                
            url = self.url_input.text().strip()
            if not url:
                self._show_error("Invalid RTSP URL format")
                return
            
            # Validate URL format
            is_valid, error_msg = URLValidator.validate(url)
            if not is_valid:
                self._show_error(error_msg)
                return
            
            # URL is valid, attempt connection
            self._is_connecting = True
            self.connect_requested.emit(url)
            self.btn_toggle.setText("Stop Stream")
            self.status_label.setText("Status: Connecting...")
        else:
            self._is_connecting = False
            self.stop_requested.emit()
            self.btn_toggle.setText("Start Stream")
            self.status_label.setText("Status: Ready")
           # self.video_display.clear()
            #self.video_display.setText("No Stream Connected")
    
    def _show_error(self, message: str, detail: str | None = None):
        """Displays an error message to the user. Use detail for debugging."""
        self.status_label.setText(f"Status: Error - {message}")
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Error")
        box.setText(message)
        if detail:
            box.setDetailedText(detail)
        box.exec()

    def _handle_error(self, error_message: str, technical_detail: str = ""):
        """Handles error signals from the video engine."""
        # Reset connection state
        self._is_connecting = False
        # Reset button state first
        self.btn_toggle.setText("Start Stream")
        self.video_display.clear()
        self.video_display.setText("Connection Failed")
        # Show error message with optional technical details (for debugging)
        self._show_error(error_message, technical_detail if technical_detail else None)
    
    def _handle_status_change(self, status: str):
        """Handles status change signals from the video engine."""
        self.status_label.setText(f"Status: {status}")
        # If status changed to Ready or Streaming, update connection state
        if status == "Ready":
            self._is_connecting = False
            self.btn_toggle.setText("Start Stream")
        elif status == "Streaming":
            self._is_connecting = False