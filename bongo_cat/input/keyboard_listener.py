"""Keyboard input listener using pynput."""

import logging
from typing import Callable, Set
from pynput import keyboard

logger = logging.getLogger("BongoCat")


class KeyboardListener:
    """Listens for global keyboard events.

    Uses pynput to monitor keyboard input globally, triggering
    callbacks on key press events while avoiding duplicates.

    Attributes:
        callback: Function to call on key press
        active_keys: Set of currently pressed keys
        listener: pynput keyboard listener instance
    """

    def __init__(self, callback: Callable[[], None]):
        """Initialize keyboard listener.

        Args:
            callback: Function to call when a key is pressed
        """
        self.callback = callback
        self.active_keys: Set = set()
        self.listener: keyboard.Listener = None

    def on_press(self, key) -> None:
        """Handle key press events.

        Args:
            key: The key that was pressed
        """
        if key not in self.active_keys:
            self.active_keys.add(key)
            self.callback()

    def on_release(self, key) -> None:
        """Handle key release events.

        Args:
            key: The key that was released
        """
        if key in self.active_keys:
            self.active_keys.remove(key)

    def start(self) -> None:
        """Start listening for keyboard events."""
        if self.listener is None or not self.listener.is_alive():
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.listener.start()
            logger.info("Keyboard listener started")

    def stop(self) -> None:
        """Stop listening for keyboard events."""
        if self.listener and self.listener.is_alive():
            self.listener.stop()
            logger.info("Keyboard listener stopped")

    def is_running(self) -> bool:
        """Check if listener is currently running.

        Returns:
            True if listener is active, False otherwise
        """
        return self.listener is not None and self.listener.is_alive()
