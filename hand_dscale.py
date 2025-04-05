# -*- coding: utf-8 -*-
import cv2
import threading
import pygame # Need full pygame for events if we want smoother exit
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector
import sys

# -------------------------------------
# Configuration
# -------------------------------------
CAMERA_ID = 0
HAND_DETECTION_CONFIDENCE = 0.8
MAX_HANDS = 2
SUSTAIN_TIME = 1.5
MIDI_OUTPUT_DEVICE_ID = None

# -------------------------------------
# 🎹 Initialize Pygame & Pygame MIDI
# -------------------------------------
print("Initializing Pygame...")
pygame.init()
print("Initializing Pygame MIDI...")
pygame.midi.init()
print("MIDI Initialized.")

print("\nAvailable MIDI Output Devices:")
found_output = False
output_device_info = {}
try:
    for i in range(pygame.midi.get_count()):
        info = pygame.midi.get_device_info(i)
        if info and info[3] == 1: # Check info is not None and is output
            device_id = i
            device_name = info[1].decode('utf-8', errors='replace') # Safer decoding
            print(f"  ID: {device_id} | Name: {device_name}")
            output_device_info[device_id] = device_name
            found_output = True
except Exception as e:
     print(f"Error getting MIDI device info: {e}")
     pygame.midi.quit()
     pygame.quit()
     sys.exit()


if not found_output:
    print("\n❌ No MIDI output devices found. Ensure a MIDI synth (e.g., IAC Driver) is active.")
    pygame.midi.quit()
    pygame.quit()
    sys.exit()

# --- Select MIDI Device ---
while MIDI_OUTPUT_DEVICE_ID is None:
    try:
        device_id_str = input(f"➡️ Please enter the ID of the MIDI device to use ({list(output_device_info.keys())}): ")
        selected_id = int(device_id_str)
        if selected_id in output_device_info:
            # MODIFICATION 1: REMOVED the pre-check (player_test = ...)
            # We will attempt the main initialization directly.
            MIDI_OUTPUT_DEVICE_ID = selected_id
            print(f"Attempting to use selected device ID: {MIDI_OUTPUT_DEVICE_ID} ({output_device_info[MIDI_OUTPUT_DEVICE_ID]})")
        else:
            print(f"❌ Invalid ID. Please choose from {list(output_device_info.keys())}.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
    # No MidiException check here anymore, will happen in the main init block


# --- Initialize the actual MIDI Player ---
player = None # Initialize player to None
try:
    print(f"Attempting: pygame.midi.Output({MIDI_OUTPUT_DEVICE_ID})")
    player = pygame.midi.Output(MIDI_OUTPUT_DEVICE_ID)
    player.set_instrument(0) # 0 = Acoustic Grand Piano
    print("✅🎹 MIDI Output Initialized Successfully.")
except pygame.midi.MidiException as e:
    # This is where the error is happening
    print(f"❌ CRITICAL ERROR: Failed to initialize MIDI output device ID {MIDI_OUTPUT_DEVICE_ID} even after selection.")
    print(f"   Pygame MIDI Exception: {e}")
    print("   This indicates a conflict or issue within Pygame/PortMidi accessing the device in this script's context.")
    print("   Suggestions: Try the other listed IAC Bus ID, restart IAC Driver/computer, check for conflicting software.")
    pygame.midi.quit()
    pygame.quit()
    sys.exit()
except Exception as e:
    print(f"❌ An unexpected error occurred during MIDI player initialization: {e}")
    pygame.midi.quit()
    pygame.quit()
    sys.exit()

# --- If MIDI succeeded, NOW initialize Camera and Detector ---
# MODIFICATION 2: Moved Camera/Detector init AFTER successful MIDI init
cap = None
detector = None
try:
    print("Initializing Camera...")
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        raise IOError(f"Cannot open camera with ID {CAMERA_ID}.")
    print("Initializing Hand Detector...")
    detector = HandDetector(detectionCon=HAND_DETECTION_CONFIDENCE, maxHands=MAX_HANDS)
    print("🖐️ Camera and Hand Detector Initialized.")
except IOError as e:
     print(f"❌ Error initializing camera: {e}")
     if player: player.close()
     pygame.midi.quit()
     pygame.quit()
     sys.exit()
except Exception as e:
     print(f"❌ Error initializing Hand Detector: {e}")
     if cap and cap.isOpened(): cap.release()
     if player: player.close()
     pygame.midi.quit()
     pygame.quit()
     sys.exit()


# -------------------------------------
# 🎺 Chord Mapping & State Tracking (Keep as before)
# -------------------------------------
chords = {
    "Left": {
        "Thumb": [62, 66, 69], "Index": [64, 67, 71], "Middle": [66, 69, 73],
        "Ring": [67, 71, 74], "Pinky": [69, 73, 76]
    },
    "Right": {
        "Thumb": [74, 78, 81], "Index": [76, 79, 83], "Middle": [78, 81, 85],
        "Ring": [79, 83, 86], "Pinky": [81, 85, 88]
    }
}
finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
prev_states = {h: {f: 0 for f in chords[h]} for h in chords}
active_notes = {}
active_notes_lock = threading.Lock()

# -------------------------------------
# 🎵 MIDI Functions (Keep as before)
# -------------------------------------
def play_chord(chord_notes, hand_type, finger):
    with active_notes_lock:
        timestamp = time.time()
        # print(f"▶️ PLAYING: {hand_type} {finger} {chord_notes}") # Reduce console spam
        for note in chord_notes:
            if note in active_notes:
                player.note_off(note, 0)
                # time.sleep(0.001) # Tiny pause optional
            player.note_on(note, 127)
            active_notes[note] = timestamp

def stop_note_delayed(note):
    initial_play_time = active_notes.get(note, 0)
    if initial_play_time == 0: return
    time.sleep(SUSTAIN_TIME)
    with active_notes_lock:
        if note in active_notes and active_notes[note] == initial_play_time:
            player.note_off(note, 127)
            try: del active_notes[note]
            except KeyError: pass

def stop_chord_immediately(chord_notes):
     # Ensure player exists before trying to use it
     if player is None: return
     with active_notes_lock:
        for note in chord_notes:
            if note in active_notes:
                player.note_off(note, 127)
                try: del active_notes[note]
                except KeyError: pass

# -------------------------------------
# ✨ Main Loop (Keep as before)
# -------------------------------------
print("\n🚀 Air Piano Activated! Show hands. Press 'q' to quit.")
try:
    while True:
        success, img = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False, draw=True)
        current_hands_detected = {hand["type"] for hand in hands}

        for hand in hands:
            hand_type = hand["type"]
            if hand_type not in chords: continue
            fingers_up = detector.fingersUp(hand)
            for i, finger_name in enumerate(finger_names):
                if finger_name in chords[hand_type]:
                    current_state = fingers_up[i]
                    previous_state = prev_states[hand_type][finger_name]
                    chord_notes = chords[hand_type][finger_name]

                    if current_state == 1 and previous_state == 0:
                        play_chord(chord_notes, hand_type, finger_name)
                    elif current_state == 0 and previous_state == 1:
                        # print(f"➖ Down: {hand_type} {finger_name}. Sustain.") # Reduce spam
                        for note in chord_notes:
                            if note in active_notes:
                                threading.Thread(target=stop_note_delayed, args=(note,), daemon=True).start()
                    prev_states[hand_type][finger_name] = current_state

        for hand_type in chords:
            if hand_type not in current_hands_detected:
                for finger_name in chords[hand_type]:
                    if prev_states[hand_type][finger_name] == 1:
                        # print(f"🖐️ Lost: {hand_type}. Sustain {finger_name}.") # Reduce spam
                        chord_notes = chords[hand_type][finger_name]
                        for note in chord_notes:
                            if note in active_notes:
                                threading.Thread(target=stop_note_delayed, args=(note,), daemon=True).start()
                        prev_states[hand_type][finger_name] = 0

        cv2.imshow("Air Piano - Hand Tracking MIDI (Press 'q' to quit)", img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n'q' pressed, exiting.")
            break
        for event in pygame.event.get(): # Keep processing pygame events
            if event.type == pygame.QUIT:
                 print("\nPygame window closed event, exiting.")
                 # Break inner loop, outer will be broken by flag/condition check needed
                 # This part is tricky; simpler to rely on 'q' or Ctrl+C for console apps
                 # For simplicity, this example won't fully handle pygame window close gracefully
                 # TODO: Implement a shared flag for exiting from pygame events too.
                 pass # Ignore for now, focus on 'q'

finally:
    # -------------------------------------
    # 🧹 Cleanup (Keep as before, ensure player/cap checks)
    # -------------------------------------
    print("\nCleaning up resources...")
    if cap and cap.isOpened():
        cap.release()
        print("Camera released.")
    cv2.destroyAllWindows()
    # print("OpenCV windows closed.") # Less verbose

    if player is not None:
        print("Stopping all active MIDI notes...")
        notes_to_stop = []
        with active_notes_lock:
             if isinstance(active_notes, dict): notes_to_stop = list(active_notes.keys())
        if notes_to_stop: stop_chord_immediately(notes_to_stop)
        player.close()
        print("MIDI player closed.")

    if pygame.midi.get_init():
        pygame.midi.quit()
        # print("Pygame MIDI quit.")
    if pygame.get_init():
        pygame.quit()
        # print("Pygame quit.")
    print("Program finished.")