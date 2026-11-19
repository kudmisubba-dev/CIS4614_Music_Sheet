import sys
from pathlib import Path

NOTE_EVENTS_DIR = Path(__file__).resolve().parent.parent / "NoteEvents"
if str(NOTE_EVENTS_DIR) not in sys.path:
    sys.path.insert(0, str(NOTE_EVENTS_DIR))
