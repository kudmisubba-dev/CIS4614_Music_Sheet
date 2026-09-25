"""
transcribe.py

Takes in audio files (wav/mp3) --> Basic Pitch library to get midi version --> Music21 library to get quantized midi (rounds timing to nearest note) and CSV note events

How to run:
    python transcribe.py input.wav --output-dir output/ --bpm 120 --grid 16
    python transcribe.py input.wav --gate --gate-ratio 4
*grid 4 for quarter notes, 8 for eight notes, etc
*The noise gate step is optional (--gate) and to cuts off sustained note tails

"""
from operator import itemgetter
import argparse
import csv
import os
from collections import Counter

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

from music21 import stream, tempo, meter, note

from pedalboard import Pedalboard, NoiseGate
from pedalboard.io import AudioFile


def apply_noise_gate(
    input_path: str,
    output_path: str,
    threshold_db: float,
    ratio: float,
    attack_ms: float,
    release_ms: float,
):
    """
    Run the audio through a noise gate before it ever reaches Basic Pitch.
    Once the signal drops below threshold_db, the gate shortens it instead of letting the note sustain.
    """

    with AudioFile(input_path) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate
        num_channels = f.num_channels

    board = Pedalboard([
        NoiseGate(threshold_db=threshold_db, ratio=ratio, attack_ms=attack_ms, release_ms=release_ms)
    ])
    gated = board(audio, samplerate)

    with AudioFile(output_path, "w", samplerate, num_channels) as f:
        f.write(gated)

    print(f"Gated written to {output_path}")


def run_basic_pitch(
    audio_path: str,
    onset_threshold: float = 0.5,
    frame_threshold: float = 0.3,
    minimum_note_length: float = 127.70,
):
    #CREATING NOTE EVENTS ! 
    #onset_threshold / frame_threshold: raise these (default 0.5 / 0.3) to require a stronger signal to start or continue a note. 
    # minimum_note_length: notes shorter than this (in ms) are discarded

    print(f"[1/4] Running basic pitch")

    _, _, note_events = predict(
        audio_path=audio_path,
        model_or_model_path=ICASSP_2022_MODEL_PATH,
        onset_threshold=onset_threshold,
        frame_threshold=frame_threshold,
        minimum_note_length=minimum_note_length,
    )

    print(f"      Basic Pitch detected {len(note_events)} raw note events")
    return note_events


def filter_note_events(note_events, min_amplitude: float):
    #Drop note with amplitude below min_amplitude.
    filtered = [e for e in note_events if e[3] >= min_amplitude]
    return filtered


def quantize_note_events(note_events, bpm: float, grid: int):
    # Rounds notes to nearest 1/grid value of a beat. grid = 32, 16, 8, or 4, grid = 4 is only quarter notes, etc

    print(f"[2/4] Rounding note events ")

    bps = bpm / 60.0
    note_unit = 4.0 / grid

    quantized = []
    for start_s, end_s, pitch, amplitude, _bends in note_events:
        
        start = start_s * bps
        end = end_s * bps

        q_start = round(start / note_unit) * note_unit
        q_end = round(end / note_unit) * note_unit

        dur = q_end - q_start
        if dur <= 0:
            dur = note_unit

        quantized.append(
            {
                "start_beat": round(q_start, 6),
                "duration_beats": round(dur, 6),
                "pitch": int(pitch),
                "velocity": int(round(127 * amplitude)),
            }
        )

    quantized.sort(key=itemgetter("start_beat", "pitch"))
    print(f" -  Note eents rounded")
    return quantized


def export_note_events(events, csv_path: str):
    #Write the quantized note events to CSV

    print(f"[3/4] Write note events to CSV")

    notes_per_beat = Counter(e["start_beat"] for e in events)
    columns = ["start_beat", "duration_beats", "pitch", "velocity", "is_chord"]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for e in events:
            is_chord = notes_per_beat[e["start_beat"]] > 1 #bool for is chord

            writer.writerow({
                "start_beat": e["start_beat"],
                "duration_beats": e["duration_beats"],
                "pitch": e["pitch"],
                "velocity": e["velocity"],
                "is_chord": is_chord,
            })

    print(f" - Note events saved")


def build_quantized_midi(events, midi_path: str, bpm: float):
    # create a MIDI file from note events above

    print(f"[4/4] Writing quantized MIDI ")

    output_stream = stream.Stream()
    output_stream.insert(0, tempo.MetronomeMark(number=bpm))
    output_stream.insert(0, meter.TimeSignature("4/4"))

    for e in events:
        n = note.Note()
        n.pitch.midi = e["pitch"]
        n.duration.quarterLength = e["duration_beats"]
        output_stream.insert(e["start_beat"], n)

    output_stream.write("midi", fp=midi_path)
    print(f"  - quantized midi")



def main():
    # Basic Pitch settings (fixed)
    ONSET_THRESHOLD = 0.5
    FRAME_THRESHOLD = 0.3
    MIN_NOTE_LENGTH_MS = 127.70

    # Noise gate settings (fixed, except ratio which is a CLI arg)
    GATE_THRESHOLD_DB = -30.0
    GATE_ATTACK_MS = 2.0
    GATE_RELEASE_MS = 100.0

    parser = argparse.ArgumentParser(description="Audio -> quantized MIDI + note events")
    parser.add_argument("audio_path")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--bpm", type=float, default=120.0)
    parser.add_argument("--grid", type=int, default=16, choices=[4, 8, 16, 32])                         
    parser.add_argument("--min-amplitude", type=float, default=0.0)
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--gate-ratio", type=float, default=10.0)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(args.audio_path))[0]
    quantized_midi_path = os.path.join(args.output_dir, f"{base_name}_quantized.mid")
    csv_path = os.path.join(args.output_dir, f"{base_name}_note_events.csv")

    audio_for_basic_pitch = args.audio_path
    if args.gate:
        gated_path = os.path.join(args.output_dir, f"{base_name}_gated.wav")
        apply_noise_gate(
            args.audio_path,
            gated_path,
            threshold_db=GATE_THRESHOLD_DB,
            ratio=args.gate_ratio,
            attack_ms=GATE_ATTACK_MS,
            release_ms=GATE_RELEASE_MS,
        )
        audio_for_basic_pitch = gated_path

    note_events = run_basic_pitch(
        audio_for_basic_pitch,
        onset_threshold=ONSET_THRESHOLD,
        frame_threshold=FRAME_THRESHOLD,
        minimum_note_length=MIN_NOTE_LENGTH_MS,
    )
    note_events = filter_note_events(note_events, args.min_amplitude)
    quantized_events = quantize_note_events(note_events, args.bpm, args.grid)
    export_note_events(quantized_events, csv_path)
    build_quantized_midi(quantized_events, quantized_midi_path, args.bpm)

    print("Success")


if __name__ == "__main__":
    main()