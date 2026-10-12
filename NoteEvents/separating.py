"""
separating.py

Reads a note events CSV from transcribe.py and adds a "part" column,
labeling each note as "melody" or "accompaniment".

How to run:
    python separating.py output/twinkleTest_note_events.csv
"""
import argparse
import csv
import os
from collections import defaultdict




def assign_parts(events):
    # Starting rule: at each start_beat, the highest note is melody, everything else is accompaniment.

    # group notes on same beat
    notes_by_beat = {}
    for note in events:
        beat = float(note["start_beat"])
        if beat not in notes_by_beat:
            notes_by_beat[beat] = []
        notes_by_beat[beat].append(note)

    # in each group, highest is melody
    for notes in notes_by_beat.values():
        highest_note = notes[0]
        for note in notes:
            if int(note["pitch"]) > int(highest_note["pitch"]):
                highest_note = note

        for note in notes:
            if note is highest_note:
                note["part"] = "melody"
            else:
                note["part"] = "accompaniment"

    return events




def read_events(csv_path):
    with open(csv_path, newline="") as f:
        return list(csv.DictReader(f))

def write_events(events, csv_path):
    columns = list(events[0].keys())

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(events)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    args = parser.parse_args()

    name, path = os.path.splitext(args.csv_path)
    output_path = f"{name}_separated.csv"

    events = read_events(args.csv_path)
    events = assign_parts(events)
    write_events(events, output_path)



if __name__ == "__main__":
    main()