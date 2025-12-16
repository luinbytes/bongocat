"""Sound effects system for Bongo Cat."""

import os
import logging
from typing import Dict, Optional

logger = logging.getLogger("BongoCat")

# Try to import pygame mixer for sound support
try:
    import pygame.mixer as mixer
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    logger.warning("pygame.mixer not available, sound effects disabled")


class SoundManager:
    """Manages loading and playing of sound effects.

    Sounds are located in the 'sounds/' directory. The manager supports:
    - Slap sounds (played on keyboard/mouse/controller input)
    - Combo sounds (played on combo milestones)
    - Achievement sounds (played when achievements are unlocked)

    Attributes:
        sounds_dir: Path to the sounds directory
        sounds: Dictionary of loaded sounds
        enabled: Whether sound is enabled
        volume: Master volume (0.0 to 1.0)
    """

    def __init__(self, sounds_dir: str = "sounds/default", enabled: bool = True, volume: float = 0.5):
        """Initialize the sound manager.

        Args:
            sounds_dir: Path to the sounds directory
            enabled: Whether sounds are enabled
            volume: Master volume level (0.0 to 1.0)
        """
        self.sounds_dir = sounds_dir
        self.sounds: Dict[str, any] = {}
        self.enabled = enabled and SOUND_AVAILABLE
        self.volume = max(0.0, min(1.0, volume))

        if self.enabled:
            self._init_mixer()
            self._load_sounds()
        else:
            logger.info("Sound system disabled")

    def _init_mixer(self) -> None:
        """Initialize the pygame mixer."""
        if not SOUND_AVAILABLE:
            return

        try:
            # Initialize mixer with reasonable defaults
            mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            logger.info("Sound mixer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize sound mixer: {e}")
            self.enabled = False

    def _load_sounds(self) -> None:
        """Load all available sound files from the sounds directory."""
        if not self.enabled or not os.path.exists(self.sounds_dir):
            return

        sound_files = {
            'slap': 'slap.wav',
            'slap_alt': 'slap_alt.wav',
            'combo': 'combo.wav',
            'combo_high': 'combo_high.wav',
            'achievement': 'achievement.wav'
        }

        for sound_name, filename in sound_files.items():
            sound_path = os.path.join(self.sounds_dir, filename)

            if os.path.exists(sound_path):
                try:
                    sound = mixer.Sound(sound_path)
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                    logger.info(f"Loaded sound: {sound_name}")
                except Exception as e:
                    logger.error(f"Failed to load sound {sound_name}: {e}")

    def play(self, sound_name: str, volume_override: Optional[float] = None) -> None:
        """Play a sound effect.

        Args:
            sound_name: Name of the sound to play
            volume_override: Optional volume override for this playback
        """
        if not self.enabled:
            return

        if sound_name not in self.sounds:
            return

        try:
            sound = self.sounds[sound_name]

            if volume_override is not None:
                original_volume = sound.get_volume()
                sound.set_volume(max(0.0, min(1.0, volume_override)))
                sound.play()
                sound.set_volume(original_volume)
            else:
                sound.play()

        except Exception as e:
            logger.error(f"Failed to play sound {sound_name}: {e}")

    def play_slap(self, alternate: bool = False) -> None:
        """Play a slap sound effect.

        Args:
            alternate: Whether to use alternate slap sound
        """
        sound_name = 'slap_alt' if alternate and 'slap_alt' in self.sounds else 'slap'
        self.play(sound_name)

    def play_combo(self, combo_count: int) -> None:
        """Play a combo sound effect.

        Args:
            combo_count: Current combo count
        """
        # Play high combo sound for combos >= 30
        if combo_count >= 30 and 'combo_high' in self.sounds:
            self.play('combo_high')
        elif 'combo' in self.sounds:
            self.play('combo')

    def play_achievement(self) -> None:
        """Play an achievement unlock sound."""
        self.play('achievement')

    def set_volume(self, volume: float) -> None:
        """Set the master volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))

        for sound in self.sounds.values():
            sound.set_volume(self.volume)

        logger.info(f"Volume set to {self.volume:.2f}")

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable sound effects.

        Args:
            enabled: Whether to enable sounds
        """
        if not SOUND_AVAILABLE:
            self.enabled = False
            return

        self.enabled = enabled
        logger.info(f"Sounds {'enabled' if enabled else 'disabled'}")

    def stop_all(self) -> None:
        """Stop all currently playing sounds."""
        if not self.enabled:
            return

        try:
            mixer.stop()
        except Exception as e:
            logger.error(f"Failed to stop sounds: {e}")

    def cleanup(self) -> None:
        """Clean up sound resources."""
        if not SOUND_AVAILABLE:
            return

        try:
            self.stop_all()
            mixer.quit()
            logger.info("Sound system cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up sound system: {e}")
