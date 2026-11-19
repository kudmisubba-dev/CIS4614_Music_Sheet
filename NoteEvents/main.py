"""
main.py

Runs the full NoteEvents pipeline on one audio file:
    1. transcribe.py     audio -> note events CSV
    2. separating.py     note events -> note events labeled melody / accompaniment
    3. music_harmony.py  separated note events -> key + chord on every beat
    4. simplify.py       separated note events + harmony -> simplified MIDI

How to run:
    python main.py input.wav
    python main.py input.wav --output-dir output/ --bpm 120 --grid 16
    python main.py input.wav --gate --gate-ratio 4

Output files (in --output-dir), for input "song.wav":
    song_note_events.csv
    song_note_events_separated.csv
    song_note_events_separated_harmony.csv
    song_simplified.mid
"""

import argparse
import os
 
from transcribe import transcribe, add_cli_args
from separating import separate, BEATS_PER_MEASURE
from music_harmony import export_harmony_csv
from simplify import simplify
 
def main():
    parser = argparse.ArgumentParser(description="Audio -> note events -> melody/accompaniment -> chords")
    add_cli_args(parser)
    args = parser.parse_args()
 
    if not os.path.isfile(args.audio_path):
        parser.error(f"audio file not found: {args.audio_path}")
 
    print("--Transcribing")
    note_events_csv = transcribe(
        args.audio_path,
        output_dir=args.output_dir,
        bpm=args.bpm,
        grid=args.grid,
        min_amplitude=args.min_amplitude,
        gate=args.gate,
        gate_ratio=args.gate_ratio,
    )
 
    print("\n--Separating melody / accompaniment")
    separated_csv = separate(note_events_csv)
 
    print("\n-- Detecting chords ")
    harmony_csv = export_harmony_csv(
        separated_csv,
        os.path.splitext(separated_csv)[0] + "_harmony.csv",
        beats_per_measure=BEATS_PER_MEASURE,
    )
    print(f"Harmony CSV written to {harmony_csv}")
    base_name = os.path.splitext(os.path.basename(args.audio_path))[0]
    simplify(separated_csv, harmony_csv, os.path.join(args.output_dir, f"{base_name}_simplified.mid"), bpm=args.bpm)
 
 
if __name__ == "__main__":
    main()