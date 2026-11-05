"""
main.py

Runs the full NoteEvents pipeline on one audio file:
    1. transcribe.py     audio -> quantized MIDI + note events CSV
    2. separating.py     note events -> note events labeled melody / accompaniment
    3. music_harmony.py  separated note events -> key + chord on every beat

How to run:
    python main.py input.wav
    python main.py input.wav --output-dir output/ --bpm 120 --grid 16
    python main.py input.wav --gate --gate-ratio 4
    python main.py input.wav --accompaniment-only

Output files (in --output-dir), for input "song.wav":
    song_quantized.mid
    song_note_events.csv
    song_note_events_separated.csv
    song_note_events_separated_harmony.csv
"""
import argparse
import os
 
from transcribe import transcribe, add_cli_args
from separating import separate, BEATS_PER_MEASURE
from music_harmony import export_harmony_csv
 
 
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
 
 
if __name__ == "__main__":
    main()