# RTSP Video Player

A desktop application for Windows that enables users to connect to and view RTSP video streams from IP cameras and streaming sources. Built with Python, PySide6 (Qt), and PyAV (FFmpeg).

---

## Quick start (for reviewers)

To run the application with minimal setup:

1. **Prerequisites**: Windows 10+, Python 3.10+
2. Open a terminal in the project folder and run:
   ```bash
   pip install -r requirements.txt
   python src/main.py
   ```
3. **Try it without network**: Put a local video path in the URL field (e.g. `C:\path\to\video.mp4` or `test.MP4` if the file is in the project folder) and click **Start Stream**. Use **Stop Stream** to stop; the window should stay open.
4. **Run automated tests**: `pip install -r requirements-dev.txt` then `pytest tests/ -v`

---

## Features

- **Simple Interface**: Clean and intuitive UI for connecting to RTSP streams
- **Real-time Playback**: Smooth video streaming using PyAV (FFmpeg bindings)
- **Error Handling**: Clear error messages for connection issues, authentication failures, and invalid URLs
- **Status Indicators**: Real-time connection status updates (Ready / Connecting / Streaming / Error)

## System Requirements

- **Operating System**: Windows 10 or later
- **Python**: 3.10 or higher
- **Internet Connection**: Required for downloading dependencies and connecting to RTSP streams

## Installation

### Step 1: Install Python

If you don't have Python installed, download and install it from [python.org](https://www.python.org/downloads/).

Make sure to check "Add Python to PATH" during installation.

### Step 2: Clone or Download the Project

Download this project to your computer and navigate to the project directory:

```bash
cd NativeRTSP_Player
```

### Step 3: Create Virtual Environment (Recommended)

Create a virtual environment to isolate dependencies:

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
.venv\Scripts\activate.bat
```

### Step 4: Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `PySide6` - Qt framework for Python (UI)
- `av` (PyAV) - FFmpeg Python bindings (video processing)
- `pillow` - Image processing library

## Running the Application

### Method 1: Run from Command Line

Make sure your virtual environment is activated, then run:

```bash
python src/main.py
```

### Method 2: Run as Module

```bash
python -m src.main
```

## Usage

1. **Launch the Application**: Run the application using one of the methods above.

2. **Enter RTSP URL**: 
   - Type or paste your RTSP stream URL into the text field
   - Format: `rtsp://[username:password@]host[:port]/path`
   - Example: `rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4`

3. **Start Streaming**: Click the "Start Stream" button to connect and begin playback.

4. **Stop Streaming**: Click the "Stop Stream" button to disconnect from the stream.

5. **Status Monitoring**: Watch the status bar at the bottom for connection state updates:
   - **Ready**: Application is ready, no active connection
   - **Connecting...**: Attempting to connect to the stream
   - **Streaming**: Successfully connected and receiving video
   - **Error**: Connection failed (see error message for details)

## Example RTSP URLs for Testing

Here are some public RTSP test streams you can use:

```
rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4
```

**Note**: Public test streams may not always be available. The application will display an appropriate error message if the stream is unreachable.

## Error Messages

The application provides clear error messages for common issues:

- **"Invalid RTSP URL format"**: The URL doesn't match the expected RTSP format
- **"Unable to connect to stream. Check URL and network connection"**: Connection timeout or network issue
- **"Authentication failed. Check username and password"**: Invalid credentials in the URL
- **"No video data received from source"**: Stream connected but no video stream found

## Testing

### Automated tests

From the project root:

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Tests include:

- **URL validator**: valid/invalid RTSP URLs, local paths, credentials extraction
- **Smoke tests**: main module and core components import and expose expected APIs

### Manual testing checklist

- [ ] Application starts without errors
- [ ] URL field accepts input; Play button is clickable
- [ ] Local video: enter a path to a `.mp4` (or similar) file → video plays in the window
- [ ] Stop button stops playback and returns to "Start Stream"; window does not close
- [ ] Invalid or empty URL shows a clear error message
- [ ] Status bar shows: Ready → Connecting → Streaming (or Error with message)

## Building an executable (run on another PC without Python)

**Why**: On another computer you may not have Python installed. An `.exe` file contains the app and everything it needs (Python, libraries, your code), so the other person can just double‑click and run.

**How to build** (on your PC, in the project folder):

1. Activate your virtual environment, then install PyInstaller and run the build script:
   ```bash
   pip install pyinstaller
   python build_exe.py
   ```
2. When it finishes, the executable is here: **`dist/RTSP_Player.exe`**.

**How to run on another PC**:

- Copy **`dist/RTSP_Player.exe`** to the other computer (USB, cloud, etc.).
- On that PC: double‑click `RTSP_Player.exe`. No need to install Python or anything else (Windows 10 or later).
- To test without network: they can paste a path to a local video file (e.g. `C:\Users\...\video.mp4`) in the URL field and click Start Stream.

**Notes**: The first run of the exe can be a bit slow. Some antivirus programs may warn about new, unknown executables; they can allow it or add an exception. If the other person has Python, they can instead run `pip install -r requirements.txt` and `python src/main.py` from the project folder.

## Project Structure

```
NativeRTSP_Player/
├── src/
│   ├── main.py                 # Application entry point
│   ├── ui/
│   │   └── main_window.py      # Main window UI and controls
│   └── core/
│       ├── av_engine.py        # Video engine (PyAV/FFmpeg)
│       └── url_validator.py    # URL validation logic
├── tests/
│   ├── test_url_validator.py   # Unit tests for URL validation
│   └── test_app_smoke.py       # Import and smoke tests
├── build_exe.py                # Script to build dist/RTSP_Player.exe
├── requirements.txt            # Python dependencies (run app)
├── requirements-dev.txt       # Dev dependencies (run tests)
└── README.md                   # This file
```

## Troubleshooting

### Application won't start

- **Check Python version**: Run `python --version` to ensure you have Python 3.10+
- **Check dependencies**: Make sure all packages are installed: `pip install -r requirements.txt`
- **Check virtual environment**: Ensure your virtual environment is activated

### Video won't play

- **Check URL format**: Ensure the RTSP URL is correctly formatted
- **Check network**: Verify you can reach the RTSP server
- **Check credentials**: If authentication is required, verify username and password in the URL
- **Check firewall**: Windows Firewall may be blocking the connection

### FFmpeg errors

- PyAV requires FFmpeg libraries. These should be included with the `av` package, but if you encounter issues:
  - Try reinstalling: `pip uninstall av && pip install av`
  - Check PyAV documentation: https://pyav.org/docs/

## Technical Details

- **UI Framework**: PySide6 (Qt for Python)
- **Video Engine**: PyAV (FFmpeg Python bindings)
- **Threading**: Video decoding runs in a separate thread to keep UI responsive
- **Protocol**: RTSP over TCP (configurable in code)

## Development

### Code Style

The project follows PEP 8 Python style guidelines.

### Adding Features

The codebase is organized into clear modules:
- `ui/main_window.py`: UI components and user interaction
- `core/av_engine.py`: Video streaming and decoding logic
- `core/url_validator.py`: URL validation utilities

## License

This project is provided as-is for demonstration purposes.

## Support

For issues or questions, please check:
1. Error messages displayed in the application
2. This README file
3. Python and PyAV documentation

---

**Version**: 1.0  
**Last Updated**: February 2026
