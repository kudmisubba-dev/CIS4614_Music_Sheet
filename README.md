# CIS4614_Music_Sheet (Senior Project CIS4614)
This project is a python command-line application created for our Sr.Project CIS 4614. 
It takes a music file and returns a digital sheet music file (MusicXML) that you can read and edit.

To do this, the program works in two simple steps:
- It converts the audio file (like a .wav or .mp3) into a MIDI file (.mid).
- It turns that MIDI file into MusicXML sheet music (.xml).
- You can open this sheet music in programs like MuseScore or Finale to view or change the notes.

<p align="center">
<b>Steps to generate xml file:</b><br>
[ Your Music File ] (Example: .wav, .mp3)<br>
        &darr;<br>
        (Step 1: Finds the notes)<br>
  [ MIDI File ]      (.mid)<br>
        &darr;<br>
        (Step 2: Makes it readable)<br>
[ MusicXML Sheet ]   (.xml)
</p>

**How to Build the Project**<br>
1. Clone the project:
   ```bash
   git clone https://github.com/kudmisubba-dev/CIS4614_Music_Sheet.git
   cd CIS4614_Music_Sheet
   ```
2. Create a build folder:
   ```bash
   mkdir build && cd build
   ```
3. Build the code:
   ```bash
   cmake .. -DCMAKE_BUILD_TYPE=Release
   cmake --build . --config Release
   ```
## Python Setup (NoteEvents)

From the project folder:
```bash
python -m venv venv
source venv/bin/activate        # Windows PowerShell: venv\Scripts\Activate.ps1
pip install basic-pitch music21 pedalboard pandas numpy
```

Run the full pipeline:
```bash
cd NoteEvents
python main.py song.wav --bpm 120 --grid 4

**License**<br>
  This project is open-source and free to use under the MIT License

