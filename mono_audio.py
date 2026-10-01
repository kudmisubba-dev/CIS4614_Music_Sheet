import os
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import music21

# 1. Define your paths
audio_file = "mono.wav"  # path to your audio file
output_xml = "monophonic_sheet.musicxml"  # path to save the output sheet music

print("Processing monophonic audio...")

# 2. Run Basic Pitch Inference
# We pass the built-in model path directly to the predict function
model_output, midi_data, note_events = predict(audio_file)

# 3. Save the raw transcription data to a temporary MIDI file
temp_midi_path = "temp_mono.mid"
midi_data.write(temp_midi_path)

# 4. Convert MIDI to Readable Sheet Music using music21
# music21 automatically handles the quantization (rounding notes to the nearest beat)

# Set music21 environment variables
music21.environment.set('musicxmlPath', 'C:\\Program Files\\MuseScore 4\\bin\\MuseScore4.exe')
music21.environment.set('musescoreDirectPNGPath', 'C:\\Program Files\\MuseScore 4\\bin\\MuseScore4.exe')

parsed = music21.converter.parse(temp_midi_path)
if isinstance(parsed, music21.stream.Score):
    score = parsed
elif isinstance(parsed, music21.stream.Part):
    score = music21.stream.Score()
    score.insert(0, parsed)
else:
    score = parsed.scores[0]

# Clean up formatting for a single melody line
for part in score.parts:
    part.makeRests(inPlace=True)
    part.quantize([4], inPlace=True) # Quantize to nearest quarter/eighth note for readability

# 5. Export and View
score.write('musicxml', fp=output_xml)
print(f"Sheet music saved successfully to {output_xml}")

# This will attempt to open the sheet music automatically in MuseScore or your default XML viewer
score.show()

# Clean up temp file
if os.path.exists(temp_midi_path):
    os.remove(temp_midi_path)
