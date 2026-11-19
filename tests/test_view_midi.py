import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from music21 import note, stream, tempo

from tests import NOTE_EVENTS_DIR  # noqa: F401
import viewMidi


class InspectMidiTests(unittest.TestCase):
    def test_prints_note_and_rest_table(self):
        s = stream.Stream()
        s.insert(0, tempo.MetronomeMark(number=120))
        n = note.Note("C4")
        n.duration.quarterLength = 1.0
        s.insert(0, n)
        s.insert(1, note.Rest(quarterLength=1.0))

        with tempfile.TemporaryDirectory() as tmp:
            midi_path = Path(tmp) / "sample.mid"
            s.write("midi", fp=str(midi_path))
            buf = io.StringIO()
            with redirect_stdout(buf):
                viewMidi.inspect_midi(str(midi_path))
            output = buf.getvalue()

        self.assertIn("Notes", output)
        self.assertTrue("C4" in output or "Rest" in output)


if __name__ == "__main__":
    unittest.main()
