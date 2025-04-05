import cv2
import threading
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector
from midi_controller import play_chord, stop_chord, stop_chord_after_delay

# 🎐 Initialize Hand Detector
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)

# 🎺 Chord Mapping for Fingers (D Major Scale)
chords = {
    "left": {
        "thumb": [62, 66, 69],   # D Major (D, F#, A)
        "index": [64, 67, 71],   # E Minor (E, G, B)
        "middle": [66, 69, 73],  # F# Minor (F#, A, C#)
        "ring": [67, 71, 74],    # G Major (G, B, D)
        "pinky": [69, 73, 76]    # A Major (A, C#, E)
    },
    "right": {
        "thumb": [62, 66, 69],   # D Major (D, F#, A)
        "index": [64, 67, 71],   # E Minor (E, G, B)
        "middle": [66, 69, 73],  # F# Minor (F#, A, C#)
        "ring": [67, 71, 74],    # G Major (G, B, D)
        "pinky": [69, 73, 76]    # A Major (A, C#, E)
    }
}

# Sustain time (in seconds) after the finger is lowered
SUSTAIN_TIME = 2.0

# Track previous states to stop chords
prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

while True:
    success, img = cap.read()
    if not success:
        print("❌ Camera not capturing frames")
        break

    hands, img = detector.findHands(img, draw=True)

    if hands:
        for hand in hands:
            hand_type = hand["type"].lower()  # Get "left" or "right"
            fingers = detector.fingersUp(hand)
            finger_names = ["thumb", "index", "middle", "ring", "pinky"]

            for i, finger in enumerate(finger_names):
                if finger in chords[hand_type]:  # Only check assigned chords
                    if fingers[i] == 1 and prev_states[hand_type][finger] == 0:
                        play_chord(chords[hand_type][finger])  # Play chord
                    elif fingers[i] == 0 and prev_states[hand_type][finger] == 1:
                        threading.Thread(target=stop_chord_after_delay, args=(chords[hand_type][finger], SUSTAIN_TIME), daemon=True).start()
                    prev_states[hand_type][finger] = fingers[i]  # Update state

    else:
        # If no hands detected, stop all chords after delay
        for hand in chords:
            for finger in chords[hand]:
                threading.Thread(target=stop_chord_after_delay, args=(chords[hand][finger], SUSTAIN_TIME), daemon=True).start()
        prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

    cv2.imshow("Hand Tracking MIDI Chords", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

cap.release()  # Release camera
cv2.destroyAllWindows()  # Close all OpenCV windows
cleanup()  # Quit MIDI properly
