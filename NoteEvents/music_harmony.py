import pandas as pd
import numpy as np
from pathlib import Path

# R. Hart, “Key-finding algorithm,” Aug. 19, 2012. [Online]. Available: https://rnhart.net/articles/key-finding/

NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
MAJOR_KEY = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
MINOR_KEY = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])

# NEW: Favor familiar diatonic functions over uncommon diminished chords.
MAJOR_CHORD_PRIORITY = [0.45, 0.25, 0.15, 0.40, 0.40, 0.35, -0.80]
MINOR_CHORD_PRIORITY = [0.45, -0.80, 0.35, 0.30, 0.20, 0.30, 0.10]


def _score_chord(weights, tones, degree, mode, tonic_pc):
    """Score chord membership, scale-degree popularity and root/third evidence."""
    inside = sum(weights[t] for t in tones)
    outside = sum(weights[t] for t in range(12) if t not in tones)
    score = inside - 0.65 * outside

    priority = (MAJOR_CHORD_PRIORITY if mode == 'Major'
                else MINOR_CHORD_PRIORITY)
    total_weight = float(sum(weights))
    if total_weight > 0:
        score += priority[degree] * min(total_weight, 2.0)

    active_notes = {i for i in range(12) if weights[i] > 0.05}
    matching_notes = active_notes.intersection(tones)
    if len(matching_notes) >= 2:
        score += 0.50
    if len(matching_notes) == 3:
        score += 0.75

    scale = ([0, 2, 4, 5, 7, 9, 11] if mode == 'Major'
             else [0, 2, 3, 5, 7, 8, 10])
    root = (tonic_pc + scale[degree]) % 12
    third = (tonic_pc + scale[(degree + 2) % 7]) % 12
    if root in active_notes:
        score += 0.35
    if root in active_notes and third in active_notes:
        score += 0.65
    return score


def _music(data):
    df = pd.read_csv(data) if isinstance(data, (str, bytes)) else data.copy()
    needed = {'start_beat','duration_beats','pitch'}
    if not needed.issubset(df.columns):
        raise ValueError(f'Missing columns: {needed - set(df.columns)}')
    df = df.copy()
    for c in needed:
        df[c] = pd.to_numeric(df[c], errors='raise')
    df = df[(df.duration_beats > 0) & (df.pitch.between(0,127))]
    if df.empty:
        raise ValueError('No valid note events')
    return df

def detect_key(data):
    df = _music(data)
    hist = np.zeros(12)
    for r in df.itertuples():
        hist[int(r.pitch) % 12] += float(r.duration_beats)
    if np.std(hist) < 1e-10:
        return 'Unknown'
    candidates = []
    for root in range(12):
        for mode, profile in [('Major', MAJOR_KEY), ('minor', MINOR_KEY)]:
            corr = np.corrcoef(hist, np.roll(profile, root))[0,1]
            candidates.append((corr, f'{NOTES[root]} {mode}'))
    return max(candidates)[1]

def _chord_candidates(key):
    tonic, mode = key.split(' ', 1)
    root = NOTES.index(tonic)
    # Diatonic triads, including diminished vii° or ii°.
    scale = [0,2,4,5,7,9,11] if mode == 'Major' else [0,2,3,5,7,8,10]
    notes = [(root + x) % 12 for x in scale]
    result = []
    for i in range(7):
        tones = {notes[i], notes[(i+2)%7], notes[(i+4)%7]}
        intervals = {(t - notes[i]) % 12 for t in tones}
        quality = 'Major' if intervals == {0,4,7} else 'minor' if intervals == {0,3,7} else 'diminished' if intervals == {0,3,6} else 'augmented'
        result.append((f'{NOTES[notes[i]]} {quality}', tones))
    return result

def detect_beat_chords(data, key=None, beats_per_measure=4):

    df = _music(data)
    if beats_per_measure <= 0 or int(beats_per_measure) != beats_per_measure:
        raise ValueError('beats_per_measure must be a positive integer')
    key = key or detect_key(df)
    if key == 'Unknown':
        raise ValueError('Cannot estimate a key')
    candidates = _chord_candidates(key)
    tonic_pc = NOTES.index(key.split(' ', 1)[0])  # NEW
    mode = key.split(' ', 1)[1]  # NEW
    end = int(np.ceil((df.start_beat + df.duration_beats).max()))
    # Score every beat by overlapping note duration, and prefer smoother changes.
    observations = []

    for beat in range(end):
        weights = np.zeros(12)
        for r in df.itertuples():
            overlap = max(0, min(beat+1, r.start_beat+r.duration_beats) - max(beat, r.start_beat))
            if overlap:
                weights[int(r.pitch)%12] += overlap
        # MODIFIED: use musically informed chord scoring.
        scores = []
        for degree, (name, tones) in enumerate(candidates):
            scores.append(_score_chord(weights, tones, degree, mode, tonic_pc))
        observations.append(scores)
    
    n = len(candidates)
    dp = np.full((end, n), -np.inf)
    back = np.zeros((end, n), dtype=int)
    dp[0] = observations[0]
    for beat in range(1, end):
        for j in range(n):
            # Prefer holding harmony, especially within a measure.
            change_cost = 1.2 if beat % beats_per_measure else 0.6
            transitions = dp[beat-1] - change_cost * (np.arange(n) != j)
            back[beat,j] = np.argmax(transitions)
            dp[beat,j] = transitions[back[beat,j]] + observations[beat][j]
    indices = [int(np.argmax(dp[-1]))]
    for beat in range(end-1,0,-1):
        indices.append(int(back[beat,indices[-1]]))
    indices.reverse()
    return pd.DataFrame({'beat':range(end), 'measure':[b//beats_per_measure+1 for b in range(end)], 'chord':[candidates[i][0] for i in indices]})

def detect_measure_chords(data, key=None, beats_per_measure=4):
    """Return chord on the first beat of each measure (0-based beat indexing)."""
    beat_chords = detect_beat_chords(data, key=key, beats_per_measure=beats_per_measure)
    return beat_chords.loc[beat_chords.beat % beats_per_measure == 0, ['measure','beat','chord']].reset_index(drop=True)

def export_harmony_csv(input_file, output_file, beats_per_measure=4):
    """
    Analyze note events and export harmony to a separate CSV.

    Columns:
        key, beat, measure, beat_chord, measure_chord

    Returns the output file path.
    """
    source = Path(input_file).expanduser().resolve()
    destination = Path(output_file).expanduser().resolve()

    if source == destination:
        raise ValueError("Output CSV must be different from input CSV")

    key = detect_key(str(source))

    beats = detect_beat_chords(
        str(source),
        key=key,
        beats_per_measure=beats_per_measure
    )

    result = beats.rename(columns={"chord": "beat_chord"}).copy()
    result.insert(0, "key", key)

    result["measure_chord"] = result["beat_chord"].where(
        result["beat"] % beats_per_measure == 0, ""
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(destination, index=False)

    return str(destination)
