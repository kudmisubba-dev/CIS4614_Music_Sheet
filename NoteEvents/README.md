Create VENV:
py -3.10 -m venv venv

run to install dependencies:
pip install -r requirements.txt


Run for each session:
windows: venv\Scripts\activate
macOS: source venv/bin/activate

Run program examples:
**make sure to run from NoteEvents fodler:
cd NoteEvents
python transcribe.py input.wav
python transcribe.py input.wav --bpm 120 --grid 8
python transcribe.py input.wav --gate --gate-ratio 4