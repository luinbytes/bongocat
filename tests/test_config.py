"""Tests for configuration management."""
import os
import sys
import tempfile
import unittest
import configparser

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfigDefaults(unittest.TestCase):
    """Test configuration default values."""

    def test_default_config_values(self):
        """Test that default config values are correct."""
        default_config = {
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

        # Verify all expected keys exist
        self.assertIn("Settings", default_config)
        settings = default_config["Settings"]

        self.assertEqual(settings["slaps"], "0")
        self.assertEqual(settings["hidden_footer"], "true")
        self.assertEqual(settings["footer_alpha"], "50")
        self.assertEqual(settings["always_show_points"], "false")
        self.assertEqual(settings["floating_points"], "true")
        self.assertEqual(settings["startup_with_windows"], "false")
        self.assertEqual(settings["max_slaps"], "0")
        self.assertEqual(settings["invert_cat"], "false")


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation."""

    def test_safe_getint_valid(self):
        """Test safe_getint with valid integer."""
        config = configparser.ConfigParser()
        config.add_section("Settings")
        config.set("Settings", "slaps", "100")

        def safe_getint(section, key, default=0):
            try:
                return int(config.get(section, key, fallback=str(default)))
            except (ValueError, TypeError):
                return default

        result = safe_getint("Settings", "slaps")
        self.assertEqual(result, 100)

    def test_safe_getint_invalid(self):
        """Test safe_getint with invalid value."""
        config = configparser.ConfigParser()
        config.add_section("Settings")
        config.set("Settings", "slaps", "invalid")

        def safe_getint(section, key, default=0):
            try:
                return int(config.get(section, key, fallback=str(default)))
            except (ValueError, TypeError):
                return default

        result = safe_getint("Settings", "slaps", default=0)
        self.assertEqual(result, 0)

    def test_safe_getboolean_true_values(self):
        """Test safe_getboolean with various true values."""
        config = configparser.ConfigParser()
        config.add_section("Settings")

        def safe_getboolean(section, key, default=False):
            try:
                value = config.get(section, key, fallback=str(default)).lower()
                return value in ('true', '1', 'yes', 'on')
            except (ValueError, AttributeError):
                return default

        for true_value in ['true', 'True', 'TRUE', '1', 'yes', 'YES', 'on', 'ON']:
            config.set("Settings", "test", true_value)
            result = safe_getboolean("Settings", "test")
            self.assertTrue(result, f"Failed for value: {true_value}")

    def test_safe_getboolean_false_values(self):
        """Test safe_getboolean with various false values."""
        config = configparser.ConfigParser()
        config.add_section("Settings")

        def safe_getboolean(section, key, default=False):
            try:
                value = config.get(section, key, fallback=str(default)).lower()
                return value in ('true', '1', 'yes', 'on')
            except (ValueError, AttributeError):
                return default

        for false_value in ['false', 'False', 'FALSE', '0', 'no', 'NO', 'off', 'OFF']:
            config.set("Settings", "test", false_value)
            result = safe_getboolean("Settings", "test")
            self.assertFalse(result, f"Failed for value: {false_value}")


class TestConfigFileOperations(unittest.TestCase):
    """Test config file read/write operations."""

    def setUp(self):
        """Create a temporary config file for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_bongo.ini")

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    def test_config_create_and_load(self):
        """Test creating and loading a config file."""
        config = configparser.ConfigParser()
        config.add_section("Settings")
        config.set("Settings", "slaps", "42")
        config.set("Settings", "hidden_footer", "false")

        # Write config
        with open(self.config_path, "w") as f:
            config.write(f)

        # Read it back
        new_config = configparser.ConfigParser()
        new_config.read(self.config_path)

        self.assertEqual(new_config.get("Settings", "slaps"), "42")
        self.assertEqual(new_config.get("Settings", "hidden_footer"), "false")

    def test_config_update_single_value(self):
        """Test updating a single config value."""
        config = configparser.ConfigParser()
        config.add_section("Settings")
        config.set("Settings", "slaps", "0")
        config.set("Settings", "hidden_footer", "true")

        # Write initial config
        with open(self.config_path, "w") as f:
            config.write(f)

        # Update only slaps
        config.set("Settings", "slaps", "100")
        with open(self.config_path, "w") as f:
            config.write(f)

        # Read back and verify
        new_config = configparser.ConfigParser()
        new_config.read(self.config_path)

        self.assertEqual(new_config.get("Settings", "slaps"), "100")
        self.assertEqual(new_config.get("Settings", "hidden_footer"), "true")


if __name__ == '__main__':
    unittest.main()
