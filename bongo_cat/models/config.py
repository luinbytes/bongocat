"""Configuration management for Bongo Cat application."""

import os
import configparser
import logging
from typing import Any, Dict
from ..utils import resource_path

logger = logging.getLogger("BongoCat")


class ConfigManager:
    """Manages application configuration using INI files.

    Handles loading, saving, and validating configuration values with
    sensible defaults and type coercion.

    Attributes:
        config_path: Path to the configuration file
        config: ConfigParser instance
        slaps: Number of slaps recorded
        hidden_footer: Whether footer should auto-hide
        footer_alpha: Footer transparency (0-100)
        always_show_points: Show total slaps permanently
        floating_points: Show animated +1 popups
        startup_with_windows: Launch on system startup
        max_slaps: Maximum slap count (0 = unlimited)
        invert_cat: Mirror cat horizontally
    """

    DEFAULT_CONFIG = {
        "Settings": {
            "slaps": "0",
            "hidden_footer": "true",
            "footer_alpha": "50",
            "always_show_points": "false",
            "floating_points": "true",
            "startup_with_windows": "false",
            "max_slaps": "0",
            "invert_cat": "false"
        }
    }

    def __init__(self, config_path: str = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            config_path = resource_path("bongo.ini")

        self.config_path = config_path
        self.config = configparser.ConfigParser()

        # Initialize with defaults
        self.slaps = 0
        self.hidden_footer = True
        self.footer_alpha = 50
        self.always_show_points = False
        self.floating_points = True
        self.startup_with_windows = False
        self.max_slaps = 0
        self.invert_cat = False

        self.load()

    def load(self) -> None:
        """Load configuration from file or create with defaults."""
        if not os.path.exists(self.config_path):
            self._create_default_config()
        else:
            self._load_existing_config()

        self._apply_config_values()

    def _create_default_config(self) -> None:
        """Create a new configuration file with default values."""
        self.config.read_dict(self.DEFAULT_CONFIG)
        try:
            with open(self.config_path, "w") as config_file:
                self.config.write(config_file)
            logger.info(f"Created default config at {self.config_path}")
        except (IOError, OSError) as e:
            logger.error(f"Error creating config file at {self.config_path}: {e}")
            self.config.read_dict(self.DEFAULT_CONFIG)

    def _load_existing_config(self) -> None:
        """Load existing configuration and merge with defaults."""
        try:
            self.config.read(self.config_path)

            # Merge defaults for any missing keys
            for section, values in self.DEFAULT_CONFIG.items():
                if section not in self.config:
                    self.config[section] = {}
                for key, value in values.items():
                    if key not in self.config[section]:
                        self.config[section][key] = value

            # Write back merged config
            with open(self.config_path, "w") as config_file:
                self.config.write(config_file)

        except (IOError, OSError, configparser.Error) as e:
            logger.error(f"Error reading config file from {self.config_path}: {e}")
            self.config.read_dict(self.DEFAULT_CONFIG)

    def _apply_config_values(self) -> None:
        """Apply loaded configuration values to instance attributes."""
        try:
            self.slaps = max(0, self._safe_getint("Settings", "slaps"))
            self.hidden_footer = self._safe_getboolean("Settings", "hidden_footer", True)
            self.footer_alpha = max(0, min(100, self._safe_getint("Settings", "footer_alpha", 50)))
            self.always_show_points = self._safe_getboolean("Settings", "always_show_points", False)
            self.floating_points = self._safe_getboolean("Settings", "floating_points", True)
            self.startup_with_windows = self._safe_getboolean("Settings", "startup_with_windows", False)
            self.max_slaps = max(0, self._safe_getint("Settings", "max_slaps"))
            self.invert_cat = self._safe_getboolean("Settings", "invert_cat", False)

        except (ValueError, KeyError, AttributeError) as e:
            logger.error(f"Error loading settings: {e}")
            # Reset to defaults on error
            self._reset_to_defaults()

    def _reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self.slaps = 0
        self.hidden_footer = True
        self.footer_alpha = 50
        self.always_show_points = False
        self.floating_points = True
        self.startup_with_windows = False
        self.max_slaps = 0
        self.invert_cat = False

    def _safe_getboolean(self, section: str, key: str, default: bool = False) -> bool:
        """Safely get a boolean value from config.

        Args:
            section: Config section name
            key: Config key name
            default: Default value if parsing fails

        Returns:
            Boolean value from config or default
        """
        try:
            value = self.config.get(section, key, fallback=str(default)).lower()
            return value in ('true', '1', 'yes', 'on')
        except (ValueError, AttributeError):
            return default

    def _safe_getint(self, section: str, key: str, default: int = 0) -> int:
        """Safely get an integer value from config.

        Args:
            section: Config section name
            key: Config key name
            default: Default value if parsing fails

        Returns:
            Integer value from config or default
        """
        try:
            return int(self.config.get(section, key, fallback=str(default)))
        except (ValueError, TypeError):
            return default

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self.config["Settings"]["slaps"] = str(self.slaps)
            self.config["Settings"]["hidden_footer"] = str(self.hidden_footer).lower()
            self.config["Settings"]["footer_alpha"] = str(self.footer_alpha)
            self.config["Settings"]["always_show_points"] = str(self.always_show_points).lower()
            self.config["Settings"]["floating_points"] = str(self.floating_points).lower()
            self.config["Settings"]["startup_with_windows"] = str(self.startup_with_windows).lower()
            self.config["Settings"]["max_slaps"] = str(self.max_slaps)
            self.config["Settings"]["invert_cat"] = str(self.invert_cat).lower()

            with open(self.config_path, "w") as config_file:
                self.config.write(config_file)

            logger.debug("Configuration saved successfully")

        except (IOError, OSError) as e:
            logger.error(f"Error saving config to {self.config_path}: {e}")

    def update_slap_count(self, count: int) -> None:
        """Efficiently update only the slap count.

        This is called frequently so it only updates the slap count
        without touching other settings.

        Args:
            count: New slap count value
        """
        self.slaps = count
        try:
            self.config["Settings"]["slaps"] = str(count)

            with open(self.config_path, "w") as config_file:
                self.config.write(config_file)

        except (IOError, OSError) as e:
            logger.error(f"Error updating slap count in {self.config_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by attribute name.

        Args:
            key: Attribute name
            default: Default value if attribute doesn't exist

        Returns:
            Configuration value or default

        Example:
            >>> config.get('slaps', 0)
            42
        """
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by attribute name.

        Args:
            key: Attribute name
            value: Value to set

        Example:
            >>> config.set('slaps', 100)
        """
        setattr(self, key, value)

    def as_dict(self) -> Dict[str, Any]:
        """Return configuration as a dictionary.

        Returns:
            Dictionary of configuration values

        Example:
            >>> config.as_dict()
            {'slaps': 42, 'hidden_footer': True, ...}
        """
        return {
            'slaps': self.slaps,
            'hidden_footer': self.hidden_footer,
            'footer_alpha': self.footer_alpha,
            'always_show_points': self.always_show_points,
            'floating_points': self.floating_points,
            'startup_with_windows': self.startup_with_windows,
            'max_slaps': self.max_slaps,
            'invert_cat': self.invert_cat
        }

    def __repr__(self) -> str:
        """Return string representation of configuration."""
        return f"ConfigManager({self.as_dict()})"
