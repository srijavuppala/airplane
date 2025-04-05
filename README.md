# Air-Piano 🎹

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Libraries](https://img.shields.io/badge/libraries-OpenCV%2C%20Pygame%2C%20cvzone%2C%20MediaPipe-orange)](requirements.txt)

Turn your hand gestures into music! Air-Piano is a Python-based application that uses your webcam to track your hand and fingers, translating specific finger raises into MIDI chord signals in the D Major scale.

<!-- Add a GIF or screenshot of the project in action here! -->
<!-- E.g., <p align="center"><img src="docs/air_piano_demo.gif" width="600"></p> -->

## Features

*   **Real-time Hand Tracking:** Uses OpenCV and MediaPipe (via cvzone) to detect hands and finger positions.
*   **Gesture-based Chord Triggering:** Maps specific raised fingers on left and right hands to chords in the D Major scale.
*   **MIDI Output:** Sends standard MIDI messages compatible with software and hardware synthesizers.
*   **Automatic Sustain:** Notes are automatically sustained for a short period after a finger is lowered or a hand disappears, creating a smoother sound.
*   **Configurable MIDI Device:** Allows selection of the desired MIDI output device at runtime.

## Technology Stack

*   **Python 3:** The core programming language.
*   **OpenCV (`opencv-python`):** For capturing webcam feed and basic image processing/display.
*   **MediaPipe:** Google's framework for real-time perception pipelines (used for hand landmark detection).
*   **cvzone:** A helper library simplifying the use of MediaPipe for hand tracking and providing utility functions like `fingersUp()`.
*   **Pygame (`pygame`):** Used for its `pygame.midi` module to handle MIDI output communication.

## Setup and Installation

Follow these steps to get Air-Piano running on your system:

**1. Prerequisites:**
    *   Python 3.8 or later installed.
    *   A webcam connected to your computer.

**2. Clone or Download:**        
       *    git clone https://github.com/srijavuppala/airplane.git
**3. Install Dependencies:**

    *    pip install -r requirements.txt

**4. Configure MIDI Output (Crucial Step, especially on macOS):**

    *   Air-Piano sends MIDI signals, it doesn't produce sound itself. You need another application (a software synthesizer or DAW) running to receive these MIDI signals and generate audio.
    *   On macOS:
        *  Enable IAC Driver:
            1.  Open Audio MIDI Setup** (Applications > Utilities).
            2.  Go to `Window > Show MIDI Studio`.
            3.  Double-click the **IAC Driver** icon.
            4.  Ensure **"Device is online"** is **checked**.
            5.  Make note of the available bus names (e.g., "Bus 1"). You'll select this later. Click Apply.
        *  Run a Synthesizer: You *must* have a synth app running and configured to *listen* to the IAC Driver bus your script will output to. Examples:
            *   GarageBand: Create a new "Software Instrument" track. It usually listens to all MIDI inputs by default if the IAC Driver is online.
            *   SimpleSynth (Free):** Launch it and in the "MIDI Source" dropdown, select the specific IAC Driver bus (e.g., "IAC Driver Bus 1").
            *   Other DAWs (Logic, Ableton): Configure a software instrument track's MIDI input to receive from the IAC Driver bus.
    *  On Windows: You might need a virtual MIDI cable (like [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)) and a software synth (like [VirtualMIDISynth](http://coolsoft.altervista.org/en/virtualmidisynth)). Configure VirtualMIDISynth to use a SoundFont and set its MIDI input to the loopMIDI port. Run the Python script and select the loopMIDI port as output.
    *  On Linux: You typically need `FluidSynth` with `Qsynth` (GUI) or similar. Start `Qsynth`, load a SoundFont (`.sf2`), ensure it's connected to ALSA or JACK, and make note of its MIDI input port name. Run the Python script and select the Qsynth MIDI input port.

## How to Use

1.  **Ensure your MIDI Synthesizer is running** and configured to listen (as described in Step 4 of Setup).
2.  **Navigate to the project directory** in your terminal.
3.  **Run the script:**
    ```bash
    python your_script_name.py # Replace with the actual name of your python file
    ```
4.  **Select MIDI Output:** The script will list available MIDI output devices. Enter the **ID number** corresponding to the device your synthesizer is listening to (e.g., the ID for "IAC Driver Bus 1").
5.  **Camera Window:** An OpenCV window will appear showing your webcam feed with hand tracking overlays.
6.  **Play!**
    *   Hold your hand(s) in front of the camera so they are clearly visible.
    *   Raise individual fingers to trigger the corresponding chords (see Chord Mapping below). The script detects finger-up transitions.
    *   Lowering a finger (or if the hand disappears) will stop the chord after the configured sustain duration.
7.  **Quit:** Press the **'q'** key while the OpenCV window is active.

## Chord Mapping

Chords from the D Major scale are mapped to fingers:

*   **Left Hand:**
    *   Thumb: D Major (`D, F#, A`)
    *   Index: E Minor (`E, G, B`)
    *   Middle: F# Minor (`F#, A, C#`)
    *   Ring: G Major (`G, B, D`)
    *   Pinky: A Major (`A, C#, E`)
*   **Right Hand:** (Plays chords one octave higher)
    *   Thumb: D Major High (`D, F#, A`)
    *   Index: E Minor High (`E, G, B`)
    *   Middle: F# Minor High (`F#, A, C#`)
    *   Ring: G Major High (`G, B, D`)
    *   Pinky: A Major High (`A, C#, E`)

*Note: The exact MIDI note numbers are defined in the `chords` dictionary within the script.*

## Configuration

You can adjust some parameters directly in the Python script:

*   `CAMERA_ID`: Change if your webcam is not device 0.
*   `HAND_DETECTION_CONFIDENCE`: Adjust sensitivity (0.0 to 1.0). Higher values require clearer hands.
*   `MAX_HANDS`: Set to 1 or 2 depending on how many hands you want to track.
*   `SUSTAIN_TIME`: Duration (in seconds) notes sustain after finger down/hand loss.
*   `chords` dictionary: Modify the MIDI note numbers to change the chords played.

## Troubleshooting

*   **No Sound:**
    *   Is a software synthesizer (GarageBand, SimpleSynth, etc.) running?
    *   Is the synthesizer configured to listen to the *exact same MIDI device/bus ID* that you selected when running the Python script?
    *   Check system volume and the synthesizer's own volume levels.
    *   On macOS, double-check the IAC Driver is "online" in Audio MIDI Setup.
*   **MIDI Error on Startup (`Invalid device ID` or similar):**
    *   Ensure you entered the correct ID number from the list provided by the script.
    *   Make sure the selected MIDI device (e.g., IAC Driver bus) is active and available *before* running the script.
    *   Try restarting the MIDI synth application, or even restarting your computer.
    *   Ensure no other application is exclusively using the MIDI port.
*   **Poor Hand Tracking:**
    *   Ensure good, consistent lighting on your hands.
    *   Avoid cluttered backgrounds.
    *   Try adjusting `HAND_DETECTION_CONFIDENCE`.

