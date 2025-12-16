"""Tests for utility functions."""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import bongo_cat
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies if not installed to allow tests to run
for module in ['pygame', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
               'PyQt5.QtWidgets.QGraphicsDropShadowEffect', 'pynput', 'pynput.keyboard', 'pynput.mouse']:
    try:
        __import__(module)
    except ImportError:
        sys.modules[module] = MagicMock()

from bongo_cat import resource_path


class TestResourcePath(unittest.TestCase):
    """Test the resource_path utility function."""

    def test_resource_path_bongo_ini(self):
        """Test that bongo.ini goes to APPDATA directory."""
        path = resource_path("bongo.ini")
        # Should include BongoCat directory
        self.assertIn("BongoCat", path)
        self.assertTrue(path.endswith("bongo.ini"))

    @patch.dict(os.environ, {'APPDATA': '/test/appdata'})
    def test_resource_path_bongo_ini_custom_appdata(self):
        """Test bongo.ini path with custom APPDATA."""
        path = resource_path("bongo.ini")
        self.assertTrue(path.startswith("/test/appdata"))
        self.assertIn("BongoCat", path)

    def test_resource_path_regular_file(self):
        """Test resource path for regular files."""
        path = resource_path("img/cat-rest.png")
        self.assertTrue(path.endswith("cat-rest.png"))

    @unittest.skip("Bundled executable testing requires PyInstaller environment")
    def test_resource_path_bundled(self):
        """Test resource path when running as bundled executable.

        This test is skipped because it requires a PyInstaller environment
        to properly test sys._MEIPASS behavior.
        """
        pass


class TestLoggingSetup(unittest.TestCase):
    """Test logging setup."""

    def test_logger_exists(self):
        """Test that logger is created."""
        from bongo_cat import logger
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "BongoCat")


if __name__ == '__main__':
    unittest.main()
