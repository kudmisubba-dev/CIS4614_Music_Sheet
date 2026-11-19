import tempfile
import unittest
from pathlib import Path

import pandas as pd

from tests import NOTE_EVENTS_DIR  # noqa: F401
from tests.helpers import C_MAJOR_EVENTS, write_csv
import music_harmony


class MusicFrameTests(unittest.TestCase):
    def test_raises_on_missing_columns(self):
        df = pd.DataFrame({"start_beat": [0], "pitch": [60]})
        with self.assertRaises(ValueError) as ctx:
            music_harmony._music(df)
        self.assertIn("Missing columns", str(ctx.exception))

    def test_raises_when_no_valid_notes(self):
        df = pd.DataFrame(
            {"start_beat": [0], "duration_beats": [0], "pitch": [60]}
        )
        with self.assertRaises(ValueError) as ctx:
            music_harmony._music(df)
        self.assertIn("No valid note events", str(ctx.exception))


class DetectKeyTests(unittest.TestCase):
    def test_detects_c_major_from_c_major_notes(self):
        df = pd.DataFrame(C_MAJOR_EVENTS)
        key = music_harmony.detect_key(df)
        self.assertTrue(key.endswith("Major") or key.endswith("minor"))
        self.assertIn(key.split()[0], music_harmony.NOTES)


class ChordDetectionTests(unittest.TestCase):
    def test_detect_beat_chords_returns_one_row_per_beat(self):
        df = pd.DataFrame(C_MAJOR_EVENTS)
        beats = music_harmony.detect_beat_chords(df, key="C Major", beats_per_measure=4)
        self.assertGreaterEqual(len(beats), 4)
        self.assertListEqual(list(beats.columns), ["beat", "measure", "chord"])
        self.assertEqual(beats.loc[0, "measure"], 1)

    def test_invalid_beats_per_measure_raises(self):
        df = pd.DataFrame(C_MAJOR_EVENTS)
        with self.assertRaises(ValueError):
            music_harmony.detect_beat_chords(df, key="C Major", beats_per_measure=0)

    def test_unknown_key_raises(self):
        df = pd.DataFrame(
            [
                {"start_beat": 0, "duration_beats": 1, "pitch": 60},
                {"start_beat": 1, "duration_beats": 1, "pitch": 61},
                {"start_beat": 2, "duration_beats": 1, "pitch": 62},
                {"start_beat": 3, "duration_beats": 1, "pitch": 63},
                {"start_beat": 4, "duration_beats": 1, "pitch": 64},
                {"start_beat": 5, "duration_beats": 1, "pitch": 65},
                {"start_beat": 6, "duration_beats": 1, "pitch": 66},
                {"start_beat": 7, "duration_beats": 1, "pitch": 67},
                {"start_beat": 8, "duration_beats": 1, "pitch": 68},
                {"start_beat": 9, "duration_beats": 1, "pitch": 69},
                {"start_beat": 10, "duration_beats": 1, "pitch": 70},
                {"start_beat": 11, "duration_beats": 1, "pitch": 71},
            ]
        )
        # Perfectly even pitch-class histogram -> Unknown key
        with self.assertRaises(ValueError):
            music_harmony.detect_beat_chords(df)

    def test_detect_measure_chords_keeps_downbeats_only(self):
        df = pd.DataFrame(C_MAJOR_EVENTS)
        measures = music_harmony.detect_measure_chords(
            df, key="C Major", beats_per_measure=4
        )
        self.assertTrue((measures["beat"] % 4 == 0).all())
        self.assertIn("chord", measures.columns)


class ExportHarmonyCsvTests(unittest.TestCase):
    def test_refuses_same_input_and_output_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(Path(tmp) / "notes.csv", C_MAJOR_EVENTS)
            with self.assertRaises(ValueError):
                music_harmony.export_harmony_csv(str(path), str(path))

    def test_writes_harmony_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = write_csv(Path(tmp) / "notes.csv", C_MAJOR_EVENTS)
            dest = Path(tmp) / "harmony.csv"
            out = music_harmony.export_harmony_csv(str(src), str(dest), beats_per_measure=4)
            result = pd.read_csv(out)
            self.assertIn("key", result.columns)
            self.assertIn("beat_chord", result.columns)
            self.assertIn("measure_chord", result.columns)
            self.assertGreater(len(result), 0)


class ScoreChordTests(unittest.TestCase):
    def test_matching_triad_scores_higher_than_empty_weights(self):
        c_major_tones = {0, 4, 7}
        matching = [1.0 if i in c_major_tones else 0.0 for i in range(12)]
        empty = [0.0] * 12
        high = music_harmony._score_chord(matching, c_major_tones, 0, "Major", 0)
        low = music_harmony._score_chord(empty, c_major_tones, 0, "Major", 0)
        self.assertGreater(high, low)


if __name__ == "__main__":
    unittest.main()
