import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import NOTE_EVENTS_DIR
from tests.helpers import C_MAJOR_EVENTS, write_csv


class DetectChordsScriptTests(unittest.TestCase):
    def test_script_writes_harmony_csv(self):
        script = NOTE_EVENTS_DIR / "detect_chords.py"
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = write_csv(Path(tmp) / "notes.csv", C_MAJOR_EVENTS)
            result = subprocess.run(
                [sys.executable, str(script), str(csv_path)],
                cwd=str(NOTE_EVENTS_DIR),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            harmony = Path(tmp) / "notes_harmony.csv"
            self.assertTrue(harmony.is_file())
            self.assertIn("Harmony CSV written to", result.stdout)


if __name__ == "__main__":
    unittest.main()
