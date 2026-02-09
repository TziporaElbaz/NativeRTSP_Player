"""
Smoke tests: verify that core components can be imported and basic logic runs.
Run from project root: pytest tests/ -v
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
# main.py uses "from ui.main_window" so it must be run with src on path
_src = _root / "src"
sys.path.insert(0, str(_src))


def test_import_main_module():
    """Application entry point can be imported without error."""
    import main as main_mod
    assert hasattr(main_mod, "main")
    assert callable(main_mod.main)


def test_import_av_engine():
    """AV engine module and class can be imported."""
    from core.av_engine import AVEngine
    assert AVEngine is not None
    engine = AVEngine()
    assert hasattr(engine, "start_stream")
    assert hasattr(engine, "stop")
    assert hasattr(engine, "new_frame_signal")
    assert hasattr(engine, "error_signal")
    assert hasattr(engine, "status_signal")


def test_import_main_window():
    """UI module can be imported (requires Qt)."""
    from ui.main_window import MainWindow, VideoDisplay
    assert MainWindow is not None
    assert VideoDisplay is not None
