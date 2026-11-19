import csv
from pathlib import Path

NOTE_COLUMNS = ["start_beat", "duration_beats", "pitch", "velocity", "is_chord"]
SEPARATED_COLUMNS = NOTE_COLUMNS + ["part"]

C_MAJOR_EVENTS = [
    {"start_beat": 0.0, "duration_beats": 1.0, "pitch": 60, "velocity": 90, "is_chord": True},
    {"start_beat": 0.0, "duration_beats": 1.0, "pitch": 64, "velocity": 70, "is_chord": True},
    {"start_beat": 0.0, "duration_beats": 1.0, "pitch": 67, "velocity": 65, "is_chord": True},
    {"start_beat": 1.0, "duration_beats": 1.0, "pitch": 72, "velocity": 95, "is_chord": False},
    {"start_beat": 2.0, "duration_beats": 1.0, "pitch": 67, "velocity": 80, "is_chord": False},
    {"start_beat": 3.0, "duration_beats": 1.0, "pitch": 64, "velocity": 75, "is_chord": False},
]


def write_csv(path: Path, rows, fieldnames=None):
    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path
