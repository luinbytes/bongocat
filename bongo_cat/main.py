"""Main entry point for Bongo Cat application."""

import sys
from PyQt5 import QtWidgets

from .utils import setup_logging
from .ui import BongoCatWindow
from .input import InputManager

# Set up logging
logger = setup_logging()


def main():
    """Initialize and run the Bongo Cat application."""
    logger.info("Starting Bongo Cat application")

    # Create Qt application
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Bongo Cat")
    app.setOrganizationName("BongoCat")

    # Create main window
    window = BongoCatWindow()
    window.show()

    # Create and start input manager
    input_manager = InputManager(window.trigger_slap.emit)
    input_manager.start()

    logger.info("Application initialized successfully")

    # Run application
    exit_code = app.exec_()

    # Cleanup
    input_manager.stop()
    logger.info("Application exiting")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
