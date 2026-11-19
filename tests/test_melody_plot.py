import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")

from tests import NOTE_EVENTS_DIR  # noqa: F401
from tests.helpers import write_csv
import melody_plot


class MelodyPlotMainTests(unittest.TestCase):
    def test_exits_when_no_csv_argument(self):
        with patch.object(melody_plot.sys, "argv", ["melody_plot.py"]):
            with self.assertRaises(SystemExit) as ctx:
                melody_plot.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_when_file_missing(self):
        with patch.object(
            melody_plot.sys, "argv", ["melody_plot.py", "missing.csv"]
        ):
            with self.assertRaises(SystemExit) as ctx:
                melody_plot.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_saves_png_next_to_csv(self):
        rows = [
            {
                "start_beat": 0.0,
                "duration_beats": 1.0,
                "pitch": 72,
                "velocity": 90,
                "is_chord": False,
                "part": "melody",
            },
            {
                "start_beat": 0.0,
                "duration_beats": 1.0,
                "pitch": 60,
                "velocity": 70,
                "is_chord": True,
                "part": "accompaniment",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = write_csv(Path(tmp) / "notes.csv", rows)
            png_path = Path(tmp) / "notes.png"
            with patch.object(
                melody_plot.sys, "argv", ["melody_plot.py", str(csv_path)]
            ):
                melody_plot.main()
            self.assertTrue(png_path.is_file())


if __name__ == "__main__":
    unittest.main()
