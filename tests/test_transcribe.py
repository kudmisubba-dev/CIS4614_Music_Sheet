import argparse
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import NOTE_EVENTS_DIR  # noqa: F401  # inserts NoteEvents on sys.path
import transcribe


class FilterNoteEventsTests(unittest.TestCase):
    def test_drops_events_below_min_amplitude(self):
        events = [
            (0.0, 1.0, 60, 0.1, []),
            (1.0, 2.0, 64, 0.5, []),
            (2.0, 3.0, 67, 0.9, []),
        ]
        kept = transcribe.filter_note_events(events, min_amplitude=0.5)
        self.assertEqual(len(kept), 2)
        self.assertEqual([e[2] for e in kept], [64, 67])

    def test_keeps_all_when_threshold_is_zero(self):
        events = [(0.0, 1.0, 60, 0.0, [])]
        self.assertEqual(transcribe.filter_note_events(events, 0.0), events)


class QuantizeNoteEventsTests(unittest.TestCase):
    def test_converts_seconds_to_beats_and_rounds_to_grid(self):
        # 60 BPM => 1 beat per second; grid 4 => quarter-note units of 1.0
        events = [(1.0, 2.0, 60, 1.0, [])]
        quantized = transcribe.quantize_note_events(events, bpm=60.0, grid=4)
        self.assertEqual(len(quantized), 1)
        self.assertEqual(quantized[0]["start_beat"], 1.0)
        self.assertEqual(quantized[0]["duration_beats"], 1.0)
        self.assertEqual(quantized[0]["pitch"], 60)
        self.assertEqual(quantized[0]["velocity"], 127)

    def test_zero_or_negative_duration_becomes_one_grid_unit(self):
        events = [(0.0, 0.01, 72, 0.5, [])]
        quantized = transcribe.quantize_note_events(events, bpm=60.0, grid=4)
        self.assertEqual(quantized[0]["duration_beats"], 1.0)

    def test_sorts_by_start_beat_then_pitch(self):
        events = [
            (1.0, 2.0, 72, 1.0, []),
            (0.0, 1.0, 64, 1.0, []),
            (0.0, 1.0, 60, 1.0, []),
        ]
        quantized = transcribe.quantize_note_events(events, bpm=60.0, grid=4)
        pitches = [e["pitch"] for e in quantized]
        self.assertEqual(pitches, [60, 64, 72])


class ExportNoteEventsTests(unittest.TestCase):
    def test_marks_same_start_beat_as_chord(self):
        events = [
            {"start_beat": 0.0, "duration_beats": 1.0, "pitch": 60, "velocity": 80},
            {"start_beat": 0.0, "duration_beats": 1.0, "pitch": 64, "velocity": 70},
            {"start_beat": 1.0, "duration_beats": 1.0, "pitch": 67, "velocity": 90},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "notes.csv"
            transcribe.export_note_events(events, str(csv_path))
            with open(csv_path, newline="") as f:
                rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["is_chord"], "True")
        self.assertEqual(rows[1]["is_chord"], "True")
        self.assertEqual(rows[2]["is_chord"], "False")


class AddCliArgsTests(unittest.TestCase):
    def test_parses_required_audio_path_and_defaults(self):
        parser = argparse.ArgumentParser()
        transcribe.add_cli_args(parser)
        args = parser.parse_args(["song.wav"])
        self.assertEqual(args.audio_path, "song.wav")
        self.assertEqual(args.bpm, 120.0)
        self.assertEqual(args.grid, 16)
        self.assertFalse(args.gate)


class TranscribePipelineTests(unittest.TestCase):
    def test_transcribe_writes_csv_using_mocked_basic_pitch(self):
        fake_events = [(0.0, 1.0, 60, 1.0, [])]
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "song.wav"
            audio.write_bytes(b"fake")
            with patch.object(transcribe, "run_basic_pitch", return_value=fake_events):
                csv_path = transcribe.transcribe(
                    str(audio),
                    output_dir=tmp,
                    bpm=60.0,
                    grid=4,
                    min_amplitude=0.0,
                    gate=False,
                )
            self.assertTrue(Path(csv_path).is_file())


if __name__ == "__main__":
    unittest.main()
