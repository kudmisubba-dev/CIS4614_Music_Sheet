# CIS4614_Music_Sheet (Senior Project CIS4614)
This project is a C++ command-line application created for our Sr.Project CIS 4614. 
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

**To build and run this project:**<br>
A modern C++ compiler (GCC, Clang, or MSVC)
CMake (version 3.15 or newer)

**How to Build the Project**<br>
Bash Terminal
- Open a bash terminal and run these commands to set up the project
- Run:
  - Clone the project:
    git clone https://github.com/kudmisubba-dev/CIS4614_Music_Sheet.git
  - Create a folder for the build:
      cd CIS4614_Music_Sheet
      mkdir build && cd build
  - Build the code:
      cmake ..
      cmake --build . --config Release

**How to run the program**<br>
  ./CIS4614_Music_Sheet --input <path to your audio file> --output <path to your sheet name>

**License**<br>
  This project is open-source and free to use under the MIT License

