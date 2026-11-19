import csv
import tempfile
import unittest
from pathlib import Path

from tests import NOTE_EVENTS_DIR  # noqa: F401
from tests.helpers import write_csv
import separating


class MeasureHelpersTests(unittest.TestCase):
    def test_measure_of_uses_four_beats(self):
        self.assertEqual(separating.measure_of({"start_beat": "0"}), 0)
        self.assertEqual(separating.measure_of({"start_beat": "3.9"}), 0)
        self.assertEqual(separating.measure_of({"start_beat": "4"}), 1)

    def test_measure_averages_groups_by_measure(self):
        events = [
            {"start_beat": "0", "velocity": "100"},
            {"start_beat": "1", "velocity": "50"},
            {"start_beat": "4", "velocity": "80"},
        ]
        averages = separating.measure_averages(events)
        self.assertEqual(averages[0], 75.0)
        self.assertEqual(averages[1], 80.0)


class AssignPartsTests(unittest.TestCase):
    def test_highest_pitch_is_melody_when_loud_enough(self):
        events = [
            {"start_beat": "0", "pitch": "60", "velocity": "80"},
            {"start_beat": "0", "pitch": "72", "velocity": "80"},
        ]
        labeled = separating.assign_parts(events)
        parts = {int(e["pitch"]): e["part"] for e in labeled}
        self.assertEqual(parts[72], "melody")
        self.assertEqual(parts[60], "accompaniment")

    def test_quiet_notes_cannot_be_melody(self):
        events = [
            {"start_beat": "0", "pitch": "80", "velocity": "20"},
            {"start_beat": "0", "pitch": "60", "velocity": "100"},
        ]
        labeled = separating.assign_parts(events)
        parts = {int(e["pitch"]): e["part"] for e in labeled}
        self.assertEqual(parts[80], "accompaniment")
        self.assertEqual(parts[60], "melody")

    def test_much_louder_note_overrides_highest_pitch(self):
        events = [
            {"start_beat": "0", "pitch": "80", "velocity": "80"},
            {"start_beat": "0", "pitch": "60", "velocity": "120"},
        ]
        labeled = separating.assign_parts(events)
        parts = {int(e["pitch"]): e["part"] for e in labeled}
        self.assertEqual(parts[60], "melody")
        self.assertEqual(parts[80], "accompaniment")


class SeparateFileTests(unittest.TestCase):
    def test_separate_writes_part_column(self):
        rows = [
            {
                "start_beat": 0.0,
                "duration_beats": 1.0,
                "pitch": 72,
                "velocity": 90,
                "is_chord": False,
            },
            {
                "start_beat": 0.0,
                "duration_beats": 1.0,
                "pitch": 60,
                "velocity": 70,
                "is_chord": True,
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            src = write_csv(Path(tmp) / "notes.csv", rows)
            out = separating.separate(str(src))
            self.assertTrue(out.endswith("_separated.csv"))
            with open(out, newline="") as f:
                result = list(csv.DictReader(f))
            self.assertIn("part", result[0])
            self.assertEqual({r["pitch"]: r["part"] for r in result}["72"], "melody")


if __name__ == "__main__":
    unittest.main()
