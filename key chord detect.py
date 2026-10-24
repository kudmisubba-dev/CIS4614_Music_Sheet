from music_harmony import (
    detect_key,
    detect_beat_chords,
    detect_measure_chords,
    export_harmony_csv
)

file = "twinkleTest1_note_events.csv"

# 1. Determine the key
key = detect_key(file)
print("Key:", key)

# 2. Determine the chord on every beat
beat_chords = detect_beat_chords(
    file,
    key=key,
    beats_per_measure=4
)
print(beat_chords)

# 3. Determine the chord on the first beat of each measure
measure_chords = detect_measure_chords(
    file,
    key=key,
    beats_per_measure=4
)
print(measure_chords)

export_harmony_csv(
    "twinkleTest1_note_events.csv",
    "twinkleTest1_harmony.csv",
    beats_per_measure=4
)
