"""
simplify.py

Creates  MIDI file so that melody is kept, and accompaniment is replaced by a two note chord: 
      root + fifth, or root + third if the melody doesn't play the chord's third during that chord [so we hear diff between major and minor chord]

How to run:
    python simplify.py output/twinkleTest_note_events_separated.csv output/twinkleTest_note_events_separated_harmony.csv
    python simplify.py <separated.csv> <harmony.csv> --bpm 120 --output output/song_simplified.mid
"""
import argparse
import os

import pandas as pd
from music21 import stream, tempo, meter, note, chord, instrument

from music_harmony import NOTES

# interval notes above root for given chord
INTERVALS = {
    "Major": (4, 7),
    "minor": (3, 7),
    "diminished": (3, 6),
    "augmented": (4, 8),
}

#keeping root between f2 and e3
LOWEST_ROOT = 41

#increments length of previous chord OR makes new chord with duration staring at 1
def chord_spans(harmony):
    spans = []
    for row in harmony.itertuples():
        if spans and spans[-1][2] == row.beat_chord:
            start, dur, name = spans[-1]
            spans[-1] = (start, dur + 1, name)
        else:
            spans.append((row.beat, 1, row.beat_chord))
    return spans

#find notes for chord
def two_note_chord(chord_name, melody_pitch_classes):
    root_name, quality = chord_name.split(" ", 1)
    root = LOWEST_ROOT + (NOTES.index(root_name) - LOWEST_ROOT) % 12
    third, fifth = INTERVALS[quality]

    if (root + third) % 12 in melody_pitch_classes:
        return [root, root + fifth]
    return [root, root + third]

#pick between root + fifth or root and third based on melody notes
def melody_during(melody, start, end):
    sounding = melody[(melody.start_beat < end) &
                      (melody.start_beat + melody.duration_beats > start)]
    return {int(p) % 12 for p in sounding.pitch}


def simplify(separated_csv, harmony_csv, output_midi, bpm=120.0):
    notes = pd.read_csv(separated_csv)
    harmony = pd.read_csv(harmony_csv)

    #save melody and insert into midi as 'right hand' 
    melody = notes[notes["part"] == "melody"]

    right = stream.Part()
    right.insert(0, instrument.Piano())
    right.insert(0, tempo.MetronomeMark(number=bpm))
    right.insert(0, meter.TimeSignature("4/4"))
    for r in melody.itertuples():
        n = note.Note()
        n.pitch.midi = int(r.pitch)
        n.duration.quarterLength = float(r.duration_beats)
        right.insert(float(r.start_beat), n)

    # insert 'left hand' two note chords
    left = stream.Part()
    left.insert(0, instrument.Piano())
    left.insert(0, meter.TimeSignature("4/4"))
    for start, dur, name in chord_spans(harmony):
        pitches = two_note_chord(name, melody_during(melody, start, start + dur))
        c = chord.Chord(pitches)
        c.duration.quarterLength = dur
        left.insert(start, c)

    score = stream.Score([right, left])
    score.write("midi", fp=output_midi)
    return output_midi

def main():
    parser = argparse.ArgumentParser(description="Melody + two-note accompaniment -> MIDI")
    parser.add_argument("separated_csv")
    parser.add_argument("harmony_csv")
    parser.add_argument("--bpm", type=float, default=120.0)
    parser.add_argument("--output", default=None,
                        help="default: <separated csv name>_simplified.mid next to the input")
    args = parser.parse_args()

    output = args.output or os.path.splitext(args.separated_csv)[0] + "_simplified.mid"
    simplify(args.separated_csv, args.harmony_csv, output, bpm=args.bpm)


if __name__ == "__main__":
    main()