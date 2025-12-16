"""Controller/gamepad input listener using pygame."""

import logging
import time
import threading
from typing import Callable, Set, Dict
from collections import deque

logger = logging.getLogger("BongoCat")

# Try to import pygame
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("pygame not available - controller support disabled")


class ControllerListener:
    """Listens for controller/gamepad input events.

    Uses pygame to monitor joystick/controller inputs including buttons,
    axes (analog sticks and triggers), and D-pad inputs.

    Attributes:
        callback: Function to call on controller input
        running: Whether the listener is actively running
        thread: Background thread for polling
        active_buttons: Set of currently pressed button IDs
        active_axes: Set of currently active axis IDs
        active_hats: Set of currently active hat (D-pad) IDs
        input_queue: Queue of pending input events
    """

    def __init__(self, callback: Callable[[], None]):
        """Initialize controller listener.

        Args:
            callback: Function to call when controller input detected
        """
        self.callback = callback
        self.running = False
        self.thread: threading.Thread = None

        # Track active inputs to prevent duplicates
        self.active_buttons: Set[str] = set()
        self.active_axes: Set[str] = set()
        self.active_hats: Set[str] = set()
        self.last_axes_values: Dict[str, float] = {}

        # Input queue to ensure no inputs are missed
        self.input_queue = deque(maxlen=100)

    def _check_controller(self) -> None:
        """Main controller polling loop (runs in background thread)."""
        if not PYGAME_AVAILABLE:
            logger.warning("pygame not available - controller listener exiting")
            return

        try:
            pygame.init()
            pygame.joystick.init()
            logger.info("Controller listener initialized")

            while self.running:
                # Process all waiting events
                for event in pygame.event.get():
                    self._process_event(event)

                # Fallback polling for controllers that don't generate events
                self._poll_joysticks()

                # Process input queue
                while self.input_queue:
                    self.input_queue.popleft()
                    self.callback()

                # Short sleep to prevent CPU overload
                time.sleep(0.001)  # 1ms polling interval

        except (pygame.error, Exception) as e:
            logger.error(f"Controller listener error: {e}")

    def _process_event(self, event) -> None:
        """Process a pygame event.

        Args:
            event: pygame event object
        """
        if event.type == pygame.JOYBUTTONDOWN:
            self._handle_button_down(event)
        elif event.type == pygame.JOYBUTTONUP:
            self._handle_button_up(event)
        elif event.type == pygame.JOYAXISMOTION:
            self._handle_axis_motion(event)
        elif event.type == pygame.JOYHATMOTION:
            self._handle_hat_motion(event)

    def _handle_button_down(self, event) -> None:
        """Handle button press event.

        Args:
            event: pygame JOYBUTTONDOWN event
        """
        button_id = f"joy{event.joy}_button{event.button}"
        if button_id not in self.active_buttons:
            self.active_buttons.add(button_id)
            self.input_queue.append(1)

    def _handle_button_up(self, event) -> None:
        """Handle button release event.

        Args:
            event: pygame JOYBUTTONUP event
        """
        button_id = f"joy{event.joy}_button{event.button}"
        if button_id in self.active_buttons:
            self.active_buttons.remove(button_id)

    def _handle_axis_motion(self, event) -> None:
        """Handle analog stick/trigger motion.

        Args:
            event: pygame JOYAXISMOTION event
        """
        axis_id = f"joy{event.joy}_axis{event.axis}"
        axis_value = event.value
        prev_value = self.last_axes_values.get(axis_id, 0)

        # Check if this is a trigger (axes 2 and 5 on Xbox controllers)
        is_trigger = event.axis in (2, 5)

        if is_trigger:
            # Trigger: detect initial press and full release
            trigger_active_key = f"{axis_id}_active"
            if axis_value > 0.5 and trigger_active_key not in self.active_axes:
                # Trigger pressed past halfway
                self.active_axes.add(trigger_active_key)
                self.input_queue.append(1)
            elif axis_value < 0.1 and trigger_active_key in self.active_axes:
                # Trigger released
                self.active_axes.remove(trigger_active_key)
        else:
            # Regular axis: detect crossing from center to edge
            axis_key = f"{axis_id}_{1 if axis_value > 0 else -1}"
            if abs(axis_value) > 0.7 and abs(prev_value) < 0.3:
                if axis_key not in self.active_axes:
                    self.active_axes.add(axis_key)
                    self.input_queue.append(1)
            elif abs(axis_value) < 0.3 and axis_key in self.active_axes:
                self.active_axes.remove(axis_key)

        # Update last value
        self.last_axes_values[axis_id] = axis_value

    def _handle_hat_motion(self, event) -> None:
        """Handle D-pad motion.

        Args:
            event: pygame JOYHATMOTION event
        """
        hat_id = f"joy{event.joy}_hat{event.hat}"
        hat_value = event.value
        hat_key = f"{hat_id}_{hat_value[0]},{hat_value[1]}"

        # Only trigger on non-zero hat values
        if hat_value != (0, 0):
            if hat_key not in self.active_hats:
                self.active_hats.add(hat_key)
                self.input_queue.append(1)
        else:
            # Remove any active hat entries for this hat
            for key in list(self.active_hats):
                if key.startswith(f"{hat_id}_"):
                    self.active_hats.remove(key)

    def _poll_joysticks(self) -> None:
        """Fallback polling for controllers that don't generate events."""
        for i in range(pygame.joystick.get_count()):
            try:
                joystick = pygame.joystick.Joystick(i)
                joystick.init()

                # Check buttons
                for button_idx in range(joystick.get_numbuttons()):
                    button_state = joystick.get_button(button_idx)
                    button_id = f"joy{i}_button{button_idx}"

                    if button_state and button_id not in self.active_buttons:
                        self.active_buttons.add(button_id)
                        self.input_queue.append(1)
                    elif not button_state and button_id in self.active_buttons:
                        self.active_buttons.remove(button_id)

            except pygame.error as e:
                logger.debug(f"Skipping joystick {i} due to error: {e}")
                continue

    def start(self) -> None:
        """Start the controller listener in a background thread."""
        if not PYGAME_AVAILABLE:
            logger.warning("Cannot start controller listener - pygame not available")
            return

        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._check_controller, daemon=True)
            self.thread.start()
            logger.info("Controller listener started")

    def stop(self) -> None:
        """Stop the controller listener."""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=1.0)
            logger.info("Controller listener stopped")

    def is_running(self) -> bool:
        """Check if listener is currently running.

        Returns:
            True if listener is active, False otherwise
        """
        return self.running
