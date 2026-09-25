"""
inspect_midi.py

View a MIDI file's contents as a readable table of note events
(pitch name, start offset, duration) instead of playing it as audio.

Usage:
    python inspect_midi.py output/twinkleTest_raw.mid
    python inspect_midi.py output/twinkleTest_quantized.mid
"""

import argparse

from music21 import converter


def inspect_midi(midi_path: str):
    score = converter.parse(midi_path)
    flat = score.flatten()

    print(f"\n{'Offset':>8}  {'Duration':>8}  {'Notes'}")
    print("-" * 40)

    for element in flat.notesAndRests:
        offset = float(element.offset)
        duration = float(element.duration.quarterLength)

        if element.isRest:
            label = "Rest"
        elif element.isChord:
            label = ", ".join(p.nameWithOctave for p in element.pitches)
        else:
            label = element.pitch.nameWithOctave

        print(f"{offset:8.3f}  {duration:8.3f}  {label}")


def main():
    parser = argparse.ArgumentParser(description="Inspect a MIDI file as note events")
    parser.add_argument("midi_path", help="Path to the MIDI file to inspect")
    args = parser.parse_args()

    inspect_midi(args.midi_path)


if __name__ == "__main__":
    main()