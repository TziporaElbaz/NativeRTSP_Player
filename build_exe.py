r"""
Build a standalone Windows .exe so the app can run on another PC without Python.

Run from project root (use the venv's Python so PyInstaller is found):

    .venv\Scripts\python.exe -m pip install pyinstaller
    .venv\Scripts\python.exe build_exe.py

Output: dist/RTSP_Player.exe (copy this file to any Windows 10+ PC and run it).
"""
import subprocess
import sys
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent
    src_dir = project_root / "src"
    main_script = src_dir / "main.py"
    venv_scripts = project_root / ".venv" / "Scripts"
    pyinstaller_exe = venv_scripts / "pyinstaller.exe"

    if not main_script.exists():
        print("Error: src/main.py not found. Run this script from the project root.")
        sys.exit(1)

    # Prefer pyinstaller.exe from venv so we don't depend on -m PyInstaller module name
    if pyinstaller_exe.exists():
        cmd = [str(pyinstaller_exe)]
    else:
        cmd = [sys.executable, "-m", "PyInstaller"]

    cmd += [
        "--onefile",           # Single .exe file
        "--windowed",          # No console window (GUI app)
        "--name", "RTSP_Player",
        "--paths", str(src_dir),  # So PyInstaller finds ui/ and core/
        str(main_script),
    ]

    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=project_root)
    if result.returncode != 0:
        sys.exit(result.returncode)

    exe_path = project_root / "dist" / "RTSP_Player.exe"
    if exe_path.exists():
        print("\nDone. Executable created:")
        print("  ", exe_path)
        print("\nCopy RTSP_Player.exe to another Windows PC and run it (no Python needed).")
    else:
        print("\nBuild finished but dist/RTSP_Player.exe not found. Check PyInstaller output.")
        sys.exit(1)

if __name__ == "__main__":
    main()
