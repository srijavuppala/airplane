import pygame.midi
import time

# Initialize Pygame MIDI
pygame.midi.init()

def get_midi_device():
    """Get the default MIDI output device or print available devices."""
    default_device = pygame.midi.get_default_output_id()
    if default_device == -1:
        print("⚠️ No default MIDI device found. Listing available devices:")
        for i in range(pygame.midi.get_count()):
            print(f"Device {i}: {pygame.midi.get_device_info(i)}")
        return None
    return default_device

# Get a valid MIDI output device
midi_device = get_midi_device()
if midi_device is not None:
    midi_out = pygame.midi.Output(midi_device)
    midi_out.set_instrument(0)  # 0 = Acoustic Grand Piano
else:
    midi_out = None

def play_chord(chord_notes, velocity=127):
    """Play a chord (list of MIDI note values)."""
    if midi_out:
        for note in chord_notes:
            midi_out.note_on(note, velocity)

def stop_chord(chord_notes):
    """Stop playing a chord."""
    if midi_out:
        for note in chord_notes:
            midi_out.note_off(note)

def stop_chord_after_delay(chord_notes, delay=2.0):
    """Stop the chord after a delay."""
    time.sleep(delay)
    stop_chord(chord_notes)

def cleanup():
    """Shut down MIDI when done."""
    if midi_out:
        midi_out.close()
    pygame.midi.quit()

if __name__ == "__main__":
    # Test by playing a D major chord (D, F#, A)
    print("🎹 Testing MIDI Output...")
    test_chord = [62, 66, 69]
    play_chord(test_chord)
    time.sleep(1)
    stop_chord(test_chord)
    cleanup()
    print("✅ Test completed!")
