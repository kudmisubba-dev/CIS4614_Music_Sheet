import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import NOTE_EVENTS_DIR  # noqa: F401
import main as pipeline_main


class MainPipelineTests(unittest.TestCase):
    def test_errors_when_audio_file_missing(self):
        with patch("sys.argv", ["main.py", "does-not-exist.wav"]):
            with self.assertRaises(SystemExit):
                pipeline_main.main()

    def test_runs_full_pipeline_with_default_args(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "song.wav"
            audio.write_bytes(b"fake")

            notes = Path(tmp) / "song_note_events.csv"
            separated = Path(tmp) / "song_note_events_separated.csv"
            harmony = Path(tmp) / "song_note_events_separated_harmony.csv"
            simplified = Path(tmp) / "song_simplified.mid"

            with patch("sys.argv", ["main.py", str(audio), "--output-dir", tmp]):
                with patch.object(
                    pipeline_main, "transcribe", return_value=str(notes)
                ) as mock_transcribe, patch.object(
                    pipeline_main, "separate", return_value=str(separated)
                ) as mock_separate, patch.object(
                    pipeline_main,
                    "export_harmony_csv",
                    return_value=str(harmony),
                ) as mock_harmony, patch.object(
                    pipeline_main, "simplify"
                ) as mock_simplify:
                    pipeline_main.main()

            mock_transcribe.assert_called_once_with(
                str(audio),
                output_dir=tmp,
                bpm=120.0,
                grid=16,
                min_amplitude=0.35,
                gate=False,
                gate_ratio=10.0,
            )
            mock_separate.assert_called_once_with(str(notes))
            mock_harmony.assert_called_once_with(
                str(separated),
                str(harmony),
                beats_per_measure=pipeline_main.BEATS_PER_MEASURE,
            )
            mock_simplify.assert_called_once_with(
                str(separated),
                str(harmony),
                str(simplified),
                bpm=120.0,
            )

    def test_forwards_custom_cli_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "track.mp3"
            audio.write_bytes(b"fake")

            notes = Path(tmp) / "track_note_events.csv"
            separated = Path(tmp) / "track_note_events_separated.csv"
            harmony = Path(tmp) / "track_note_events_separated_harmony.csv"
            simplified = Path(tmp) / "track_simplified.mid"

            argv = [
                "main.py",
                str(audio),
                "--output-dir",
                tmp,
                "--bpm",
                "95",
                "--grid",
                "8",
                "--min-amplitude",
                "0.5",
                "--gate",
                "--gate-ratio",
                "4.5",
            ]

            with patch("sys.argv", argv):
                with patch.object(
                    pipeline_main, "transcribe", return_value=str(notes)
                ) as mock_transcribe, patch.object(
                    pipeline_main, "separate", return_value=str(separated)
                ), patch.object(
                    pipeline_main,
                    "export_harmony_csv",
                    return_value=str(harmony),
                ), patch.object(
                    pipeline_main, "simplify"
                ) as mock_simplify:
                    pipeline_main.main()

            mock_transcribe.assert_called_once_with(
                str(audio),
                output_dir=tmp,
                bpm=95.0,
                grid=8,
                min_amplitude=0.5,
                gate=True,
                gate_ratio=4.5,
            )
            mock_simplify.assert_called_once_with(
                str(separated),
                str(harmony),
                str(simplified),
                bpm=95.0,
            )


if __name__ == "__main__":
    unittest.main()
