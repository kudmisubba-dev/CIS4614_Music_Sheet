"""
separating.py
-> adds part column to note events, labeling each note as "melody" or "accompaniment".

Rules applied:
  1. Notes significantly quieter 9below quiet_ratio) than the measure's average volume are not melody.
  2. Then highest pitch note is labelled melody
  3. If another note is MUCH louder than the measure average according to loud_ratio, it overwrites highest pitch as melody.
The relative-volume idea comes from Sri's beatdata.py.

How to run:
    python separating.py output/twinkleTest_note_events.csv
"""
import argparse
import csv
import os
from collections import defaultdict

BEATS_PER_MEASURE = 4
QUIET_RATIO = 0.75   # below 75% of the measure average -> can't be melody
LOUD_RATIO = 1.2     # above 120% of the measure average -> overrides highest note


def read_events(csv_path):
    with open(csv_path, newline="") as f:
        return list(csv.DictReader(f))


def measure_of(e):
    return int(float(e["start_beat"]) // BEATS_PER_MEASURE)


def measure_averages(events):
    # Average velocity of all notes in each measure
    velocities = defaultdict(list)
    for e in events:
        velocities[measure_of(e)].append(int(e["velocity"]))

    return {m: sum(v) / len(v) for m, v in velocities.items()}


def assign_parts(events):
    averages = measure_averages(events)

    notes_by_beat = defaultdict(list)
    for e in events:
        notes_by_beat[float(e["start_beat"])].append(e)

    for notes in notes_by_beat.values():
        avg = averages[measure_of(notes[0])]

        # Rule 1: drop notes that are too quiet to be melody
        contenders = [e for e in notes if int(e["velocity"]) >= QUIET_RATIO * avg]

        melody = None
        if contenders:
            # Rule 2: highest remaining note
            melody = max(contenders, key=lambda e: int(e["pitch"]))

            # Rule 3: a much louder note overrides the highest note
            loud = [e for e in contenders if int(e["velocity"]) >= LOUD_RATIO * avg]
            if loud and melody not in loud:
                melody = max(loud, key=lambda e: int(e["velocity"]))

        for e in notes:
            e["part"] = "melody" if e is melody else "accompaniment"

    return events


def write_events(events, csv_path):
    columns = list(events[0].keys())

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(events)


def separate(csv_path):
    # Label a note events CSV and write <name>_separated.csv. Returns the output path.
    base, _ = os.path.splitext(csv_path)
    output_path = f"{base}_separated.csv"

    events = read_events(csv_path)
    events = assign_parts(events)
    write_events(events, output_path)

    print(f"Separated CSV written to {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    args = parser.parse_args()

    separate(args.csv_path)


if __name__ == "__main__":
    main()