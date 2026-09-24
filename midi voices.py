from mido import MidiFile
from collections import defaultdict

# Load file
mid = MidiFile('Mary Had a Little Lamb.mid')

# notes grouped by Track and Channel)
voices = defaultdict(list)

# Track note time
absolute_time = 0

for i, track in enumerate(mid.tracks):
    absolute_time = 0
    for msg in track:
        absolute_time += msg.time  # progress by length of note
        
        # if note has pitch and length...
        if msg.type == 'note_on' and msg.velocity > 0:
            voice_key = f"Track_{i}_Channel_{msg.channel}"
            voices[voice_key].append({
                'note': msg.note,
                'start_time': absolute_time,
                'velocity': msg.velocity
            })

# print out how many different voices there are
for voice_name, notes in voices.items():
    print(f"Identified Voice: {voice_name} ({len(notes)} notes found)")

# print out individual notes and lengths
for notes in voices.items():
    print(notes)

