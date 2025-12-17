"""Mouse input listener using pynput."""

import logging
from typing import Callable
from pynput import mouse

logger = logging.getLogger("BongoCat")


class MouseListener:
    """Listens for global mouse events.

    Uses pynput to monitor mouse clicks globally, triggering
    callbacks on button press events.

    Attributes:
        callback: Function to call on mouse click
        listener: pynput mouse listener instance
    """

    def __init__(self, callback: Callable[[], None]):
        """Initialize mouse listener.

        Args:
            callback: Function to call when mouse is clicked
        """
        self.callback = callback
        self.listener: mouse.Listener = None

    def on_click(self, x: int, y: int, button, pressed: bool) -> None:
        """Handle mouse click events.

        Args:
            x: X coordinate of click
            y: Y coordinate of click
            button: Mouse button that was clicked
            pressed: True if pressed, False if released
        """
        if pressed:
            self.callback()

    def start(self) -> None:
        """Start listening for mouse events."""
        if self.listener is None or not self.listener.is_alive():
            self.listener = mouse.Listener(on_click=self.on_click)
            self.listener.start()
            logger.info("Mouse listener started")

    def stop(self) -> None:
        """Stop listening for mouse events."""
        if self.listener and self.listener.is_alive():
            self.listener.stop()
            logger.info("Mouse listener stopped")

    def is_running(self) -> bool:
        """Check if listener is currently running.

        Returns:
            True if listener is active, False otherwise
        """
        return self.listener is not None and self.listener.is_alive()
