import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from music21 import converter

import simplify as simplify_mod


class SimplifyTests(unittest.TestCase):
    def test_chord_spans_merges_consecutive_chords(self):
        harmony = pd.DataFrame(
            {
                "beat": list(range(5)),
                "beat_chord": ["C Major", "C Major", "G Major", "C Major", "C Major"],
            }
        )
        spans = simplify_mod.chord_spans(harmony)
        self.assertEqual(
            spans,
            [
                (0, 2, "C Major"),
                (2, 1, "G Major"),
                (3, 2, "C Major"),
            ],
        )

    def test_two_note_chord_uses_third_when_melody_lacks_third(self):
        # C Major root between F2 (41) and E3 (52) is C3 (48); major third is E3 (52)
        pitches = simplify_mod.two_note_chord("C Major", melody_pitch_classes={0, 7})
        self.assertEqual(tuple(pitches), (48, 52))

    def test_two_note_chord_uses_fifth_when_melody_plays_third(self):
        # Melody plays E (pitch class 4), so accompaniment switches to root + fifth (G3 = 55)
        pitches = simplify_mod.two_note_chord("C Major", melody_pitch_classes={4})
        self.assertEqual(tuple(pitches), (48, 55))

    def test_melody_during_detects_overlapping_notes(self):
        melody = pd.DataFrame(
            {
                "start_beat": [0.0, 1.5, 4.0],
                "duration_beats": [1.0, 2.0, 1.0],
                "pitch": (60, 64, 67),
            }
        )
        # Span [1.0, 3.0) overlaps only with note starting at 1.5 (pitch 64 -> pitch class 4)
        active = simplify_mod.melody_during(melody, start=1.0, end=3.0)
        self.assertEqual(active, {4})

    def test_simplify_writes_midi_and_musicxml(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            separated_csv = tmp_path / "song_note_events_separated.csv"
            harmony_csv = tmp_path / "song_note_events_separated_harmony.csv"
            output_midi = tmp_path / "song_simplified.mid"
            expected_xml = tmp_path / "song_simplified.musicxml"

            separated_csv.write_text(
                "start_beat,duration_beats,pitch,velocity,is_chord,part\n"
                "0.0,2.0,60,80,False,melody\n"
                "1.0,1.0,64,80,False,melody\n"
                "0.0,2.0,48,70,True,accompaniment\n"
            )
            harmony_csv.write_text(
                "beat,key,beat_chord\n"
                "0,C Major,C Major\n"
                "1,C Major,C Major\n"
            )

            with patch.object(
                simplify_mod,
                "export_pdf",
                return_value=str(tmp_path / "song_simplified.pdf"),
            ) as mock_pdf:
                result = simplify_mod.simplify(
                    str(separated_csv),
                    str(harmony_csv),
                    str(output_midi),
                    bpm=110.0,
                )

            self.assertEqual(result, str(output_midi))
            self.assertTrue(output_midi.is_file())
            self.assertTrue(expected_xml.is_file())
            mock_pdf.assert_called_once_with(str(expected_xml))

            # Verify parsed MIDI has two parts (right-hand melody + left-hand accompaniment)
            parsed = converter.parse(str(output_midi))
            self.assertEqual(len(parsed.parts), 2)

            # First melody note at beat 0.0 was truncated from 2.0 to 1.0 when second note entered at 1.0
            melody_part = next(iter(parsed.parts))
            melody_notes = tuple(melody_part.flatten().notes)
            self.assertEqual(tuple(n.pitch.midi for n in melody_notes), (60, 64))
            self.assertEqual(
                tuple(float(n.duration.quarterLength) for n in melody_notes),
                (1.0, 1.0),
            )

    def test_cli_builds_default_output_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            separated_csv = tmp_path / "twinkle_note_events_separated.csv"
            harmony_csv = tmp_path / "twinkle_note_events_separated_harmony.csv"
            expected_midi = tmp_path / "twinkle_simplified.mid"

            argv = ["simplify.py", str(separated_csv), str(harmony_csv), "--bpm", "90"]
            with patch("sys.argv", argv), patch.object(
                simplify_mod, "simplify"
            ) as mock_simplify:
                simplify_mod.main()

            mock_simplify.assert_called_once_with(
                str(separated_csv),
                str(harmony_csv),
                str(expected_midi),
                bpm=90.0,
            )


if __name__ == "__main__":
    unittest.main()
