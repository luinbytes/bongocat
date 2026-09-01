"""Runtime regression test for exceptions raised while applying settings."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


@unittest.skipUnless(importlib.util.find_spec("PyQt5"), "PyQt5 is not installed")
class TestSettingsApplyRuntime(unittest.TestCase):
    def test_apply_exception_does_not_abort_qt_process(self):
        script = textwrap.dedent(
            """
            from PyQt5 import QtCore, QtWidgets
            from bongo_cat.ui.main_window import BongoCatWindow

            app = QtWidgets.QApplication([])
            window = BongoCatWindow()
            apply_button = next(
                button
                for button in window.settings_panel.findChildren(QtWidgets.QPushButton)
                if button.text() == "Apply"
            )
            window.sound_manager.set_volume = lambda _volume: (_ for _ in ()).throw(
                RuntimeError("injected Apply failure")
            )
            window.config.sound_enabled_checkbox.setChecked(False)
            QtWidgets.QMessageBox.critical = lambda *_args: print(
                "apply-error-dialog", flush=True
            )
            QtCore.QTimer.singleShot(0, apply_button.click)
            QtCore.QTimer.singleShot(500, app.quit)
            app.exec_()
            print("after-apply-click", flush=True)
            print(f"saved-sound-enabled={window.config.__class__().sound_enabled}", flush=True)
            """
        )

        with tempfile.TemporaryDirectory() as appdata:
            env = os.environ.copy()
            env.update(
                APPDATA=appdata,
                PYNPUT_BACKEND="dummy",
                QT_QPA_PLATFORM="offscreen",
            )
            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=Path(__file__).parents[1],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("apply-error-dialog", result.stdout)
        self.assertIn("after-apply-click", result.stdout)
        self.assertIn("saved-sound-enabled=False", result.stdout)
        self.assertIn("injected Apply failure", result.stderr)


if __name__ == "__main__":
    unittest.main()
