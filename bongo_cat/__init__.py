"""Bongo Cat Desktop Buddy - A reactive desktop pet application."""

from .models import ConfigManager
from .ui import BongoCatWindow, SettingsPanelWidget
from .input import InputManager
from .utils import resource_path, setup_logging
from . import animations

__version__ = "1.0.0"
__author__ = "luinbytes"
__description__ = "Interactive desktop pet that responds to keyboard, mouse, and controller inputs"

__all__ = [
    'ConfigManager',
    'BongoCatWindow',
    'SettingsPanelWidget',
    'InputManager',
    'resource_path',
    'setup_logging',
    'animations'
]
