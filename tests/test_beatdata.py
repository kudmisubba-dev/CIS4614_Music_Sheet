import tempfile
import unittest
from pathlib import Path

from tests import NOTE_EVENTS_DIR  # noqa: F401
from tests.helpers import write_csv
from beatdata import BeatData


class AnalyzeMelodyFromCsvTests(unittest.TestCase):
    def test_labels_beats_above_window_average_as_melody(self):
        rows = [
            {"start_beat": 0, "velocity": 100},
            {"start_beat": 1, "velocity": 40},
            {"start_beat": 2, "velocity": 40},
            {"start_beat": 3, "velocity": 40},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(Path(tmp) / "notes.csv", rows)
            results = BeatData.analyze_melody_from_csv(str(path))
        self.assertEqual(results[0], "MELODY")
        self.assertEqual(results[1], "NOT MELODY")
        self.assertEqual(results[2], "NOT MELODY")
        self.assertEqual(results[3], "NOT MELODY")

    def test_uses_integer_beat_and_averages_multiple_notes(self):
        rows = [
            {"start_beat": 0.2, "velocity": 90},
            {"start_beat": 0.8, "velocity": 110},
            {"start_beat": 1.0, "velocity": 50},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(Path(tmp) / "notes.csv", rows)
            results = BeatData.analyze_melody_from_csv(str(path))
        self.assertIn(0, results)
        self.assertIn(1, results)
        self.assertEqual(results[0], "MELODY")
        self.assertEqual(results[1], "NOT MELODY")


if __name__ == "__main__":
    unittest.main()
