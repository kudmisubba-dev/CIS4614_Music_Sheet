import csv
from collections import defaultdict
from typing import Dict, List


class BeatData:

    def __init__(self, beat_num: int, volumes: List[float]):
        self.beat_num: int = beat_num
        self.volumes: List[float] = volumes

    @classmethod
    def analyze_melody_from_csv(cls, file_path: str) -> Dict[int, str]:
        """Reads a CSV file, calculates a rolling 4-beat average velocity,

        and classifies each beat as 'MELODY' or 'NOT MELODY'.
        """
        # Step 1: Read CSV and collect velocities for each start_beat
        beat_velocities: Dict[int, List[float]] = defaultdict(list)

        with open(file_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Round to integer to handle grouping (e.g., 0, 1, 2, 3)
                beat = int(float(row["start_beat"]))
                velocity = float(row["velocity"])
                beat_velocities[beat].append(velocity)

        # Step 2: Average velocities per individual beat
        # (Handles cases where a beat has multiple notes/chords)
        avg_velocity_per_beat: Dict[int, float] = {}
        for beat, v_list in beat_velocities.items():
            avg_velocity_per_beat[beat] = sum(v_list) / len(v_list)

        # Step 3: Group beats into 4-beat windows to find the window average
        # Window 0: beats 0-3, Window 1: beats 4-7, etc.
        window_totals: Dict[int, float] = defaultdict(float)
        window_counts: Dict[int, int] = defaultdict(int)

        for beat, avg_v in avg_velocity_per_beat.items():
            window_id = beat // 4
            window_totals[window_id] += avg_v
            window_counts[window_id] += 1

        window_averages: Dict[int, float] = {}
        for w_id, total in window_totals.items():
            window_averages[w_id] = total / window_counts[w_id]

        # Step 4: Classify each beat against its 4-beat window average
        results: Dict[int, str] = {}
        for beat, avg_v in avg_velocity_per_beat.items():
            window_id = beat // 4
            group_avg = window_averages[window_id]

            # High compared to average -> MELODY
            # Lower than average -> NOT MELODY
            if avg_v >= group_avg:
                results[beat] = "MELODY"
            else:
                results[beat] = "NOT MELODY"

        return dict(sorted(results.items()))
