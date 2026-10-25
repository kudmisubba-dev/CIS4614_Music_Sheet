
# How to run:
# python detect_chords.py output/twinkleTest_note_events_separated.csv

import argparse
import os

import pandas as pd

from music_harmony import (
    detect_key,
    detect_beat_chords,
    detect_measure_chords,
)

parser = argparse.ArgumentParser()
parser.add_argument("csv_path")
args = parser.parse_args()

file = args.csv_path
notes = pd.read_csv(file)

# Use only accompaniment notes for chords,
# if separating.py has labeled them.

accompaniment = notes

'''
accompaniment = notes
if "part" in notes.columns:
    accompaniment = notes[
        notes["part"] == "accompaniment"
    ]
'''

# 1. Determine the key (from all notes, melody included)
key = detect_key(notes)
print("Key:", key)

# 2. Determine the chord on every beat
beat_chords = detect_beat_chords(
    accompaniment,
    key=key,
    beats_per_measure=4
)

print(beat_chords)

# 3. Determine the chord on the first beat of each measure
measure_chords = detect_measure_chords(
    accompaniment,
    key=key,
    beats_per_measure=4
)

print(measure_chords)

# 4. Export to CSV
harmony = beat_chords.rename(
    columns={"chord": "beat_chord"}
)

harmony.insert(0, "key", key)

harmony["measure_chord"] = harmony["beat_chord"].where(
    harmony["beat"] % 4 == 0,
    ""
)

output_file = os.path.splitext(file)[0] + "_harmony.csv"

harmony.to_csv(output_file, index=False)

print("Harmony CSV written to", output_file)
