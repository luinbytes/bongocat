#!/usr/bin/env python3
"""Generate simple sound effects for Bongo Cat."""

import wave
import math
import struct
import os


def generate_beep(filename, frequency=800, duration=0.1, volume=0.3):
    """Generate a simple beep sound.

    Args:
        filename: Output WAV file path
        frequency: Frequency in Hz
        duration: Duration in seconds
        volume: Volume (0.0 to 1.0)
    """
    sample_rate = 44100
    num_samples = int(sample_rate * duration)

    # Generate samples
    samples = []
    for i in range(num_samples):
        # Simple sine wave
        t = float(i) / sample_rate
        value = volume * math.sin(2 * math.pi * frequency * t)

        # Add envelope (fade in/out) to avoid clicks
        envelope = min(i / (sample_rate * 0.01), 1.0)  # Fade in
        envelope *= min((num_samples - i) / (sample_rate * 0.01), 1.0)  # Fade out
        value *= envelope

        # Convert to 16-bit integer
        samples.append(int(value * 32767))

    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack('h' * len(samples), *samples))

    print(f"✓ Created {filename}")


def generate_click(filename, frequency=1200, duration=0.05, volume=0.25):
    """Generate a click sound (short, high-pitched beep)."""
    generate_beep(filename, frequency, duration, volume)


def generate_chord(filename, frequencies=[523, 659, 784], duration=0.15, volume=0.2):
    """Generate a chord sound (multiple frequencies).

    Args:
        filename: Output WAV file path
        frequencies: List of frequencies in Hz
        duration: Duration in seconds
        volume: Volume (0.0 to 1.0)
    """
    sample_rate = 44100
    num_samples = int(sample_rate * duration)

    # Generate samples
    samples = []
    for i in range(num_samples):
        t = float(i) / sample_rate
        value = 0

        # Mix multiple frequencies
        for freq in frequencies:
            value += volume * math.sin(2 * math.pi * freq * t) / len(frequencies)

        # Add envelope
        envelope = min(i / (sample_rate * 0.01), 1.0)
        envelope *= min((num_samples - i) / (sample_rate * 0.02), 1.0)
        value *= envelope

        # Convert to 16-bit integer
        samples.append(int(value * 32767))

    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack('h' * len(samples), *samples))

    print(f"✓ Created {filename}")


def main():
    """Generate all sound effects."""
    print("🔊 Generating sound effects...")
    print()

    # Create sounds directory if it doesn't exist
    sounds_dir = "sounds/default"
    os.makedirs(sounds_dir, exist_ok=True)

    # Generate slap sound (medium pitch click)
    generate_click(
        f"{sounds_dir}/slap.wav",
        frequency=1000,
        duration=0.06,
        volume=0.3
    )

    # Generate alternate slap sound (slightly higher pitch)
    generate_click(
        f"{sounds_dir}/slap_alt.wav",
        frequency=1200,
        duration=0.05,
        volume=0.28
    )

    # Generate combo sound (ascending beeps)
    generate_chord(
        f"{sounds_dir}/combo.wav",
        frequencies=[523, 659, 784],  # C, E, G (C major chord)
        duration=0.12,
        volume=0.25
    )

    # Generate high combo sound (higher chord)
    generate_chord(
        f"{sounds_dir}/combo_high.wav",
        frequencies=[659, 831, 988],  # E, G#, B (E major chord)
        duration=0.15,
        volume=0.27
    )

    # Generate achievement sound (triumphant chord)
    generate_chord(
        f"{sounds_dir}/achievement.wav",
        frequencies=[523, 659, 784, 1047],  # C major chord with octave
        duration=0.3,
        volume=0.23
    )

    print()
    print("✅ All sound effects generated successfully!")
    print(f"📁 Location: {sounds_dir}/")
    print()
    print("Note: These are simple programmatically-generated sounds.")
    print("You can replace them with your own custom sound effects.")


if __name__ == "__main__":
    main()
