"""
Backward compatibility wrapper for bongo_cat.py

This file maintains backward compatibility with the original bongo_cat.py
while using the new modular structure under the hood.

For new code, use: python -m bongo_cat
Or import from: from bongo_cat import BongoCatWindow
"""

# Import everything from the new modular package
from bongo_cat.main import main
from bongo_cat.ui import BongoCatWindow, SettingsPanelWidget
from bongo_cat.models import ConfigManager
from bongo_cat.input import InputManager
from bongo_cat.utils import resource_path, setup_logging

# Set up logging
logger = setup_logging()

if __name__ == "__main__":
    logger.info("Running Bongo Cat via legacy entry point")
    main()
