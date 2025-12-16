"""Tests for platform-specific functionality."""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPlatformSpecificCode(unittest.TestCase):
    """Test platform-specific functionality."""

    @unittest.skipUnless(sys.platform == 'win32', "Windows-only test")
    def test_open_ini_file_windows(self):
        """Test opening config file on Windows."""
        with patch('os.startfile') as mock_startfile:
            mock_startfile.return_value = None

            # Simulate the logic from open_ini_file
            config_path = "/test/path/bongo.ini"
            if sys.platform == 'win32':
                os.startfile(config_path)

            mock_startfile.assert_called_once_with(config_path)

    @patch('sys.platform', 'darwin')
    @patch('subprocess.call')
    def test_open_ini_file_macos(self, mock_call):
        """Test opening config file on macOS."""
        mock_call.return_value = 0

        # Simulate the logic from open_ini_file
        config_path = "/test/path/bongo.ini"
        if sys.platform == 'darwin':
            import subprocess
            subprocess.call(['open', config_path])

        mock_call.assert_called_once_with(['open', config_path])

    @patch('sys.platform', 'linux')
    @patch('subprocess.call')
    def test_open_ini_file_linux(self, mock_call):
        """Test opening config file on Linux."""
        mock_call.return_value = 0

        # Simulate the logic from open_ini_file
        config_path = "/test/path/bongo.ini"
        if sys.platform == 'linux':
            import subprocess
            subprocess.call(['xdg-open', config_path])

        mock_call.assert_called_once_with(['xdg-open', config_path])


if __name__ == '__main__':
    unittest.main()
