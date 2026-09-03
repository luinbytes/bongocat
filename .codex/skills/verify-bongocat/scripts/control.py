#!/usr/bin/env python3

import argparse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Dict, Iterator, List, Optional, Sequence


REPO_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class VerificationRun:
    repo_root: Path
    working_dir: Path
    appdata_dir: Path
    evidence_dir: Path


@dataclass(frozen=True)
class VerificationResult:
    status: str
    revision: str
    python_version: str
    qt_version: str
    working_directory: str
    resolved_skins_dir: str
    skin_ids: List[str]
    selected_skin_id: Optional[str]
    selected_skin_type: str
    apply_error_count: int
    persisted_sound_enabled: bool
    evidence_files: List[str]
    scratch_removed: bool


@contextmanager
def isolated_environment(run: VerificationRun) -> Iterator[None]:
    previous_cwd = Path.cwd()
    previous_values: Dict[str, Optional[str]] = {
        name: os.environ.get(name)
        for name in (
            "APPDATA",
            "PYNPUT_BACKEND",
            "PYGAME_HIDE_SUPPORT_PROMPT",
            "QT_QPA_PLATFORM",
        )
    }
    os.environ.update(
        APPDATA=str(run.appdata_dir),
        PYNPUT_BACKEND="dummy",
        PYGAME_HIDE_SUPPORT_PROMPT="1",
        QT_QPA_PLATFORM="offscreen",
    )
    os.chdir(str(run.working_dir))
    sys.path.insert(0, str(run.repo_root))
    try:
        yield
    finally:
        os.chdir(str(previous_cwd))
        if sys.path and sys.path[0] == str(run.repo_root):
            sys.path.pop(0)
        for name, value in previous_values.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def revision(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_root),
        text=True,
    ).strip()


def doctor(repo_root: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="verify-bongocat-doctor-") as scratch:
        scratch_path = Path(scratch)
        run = VerificationRun(
            repo_root=repo_root,
            working_dir=scratch_path / "working",
            appdata_dir=scratch_path / "appdata",
            evidence_dir=scratch_path / "unused-evidence",
        )
        run.working_dir.mkdir()
        run.appdata_dir.mkdir()
        with isolated_environment(run):
            from PyQt5 import QtCore, QtWidgets
            from bongo_cat.models.skin_manager import SkinManager

            app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
            manager = SkinManager()
            skin_ids = sorted(manager.get_skin_ids())
            payload = {
                "status": "ok" if skin_ids == ["default", "neon", "retro"] else "error",
                "python_version": sys.version.split()[0],
                "qt_version": QtCore.QT_VERSION_STR,
                "resolved_skins_dir": manager.skins_dir,
                "skin_count": len(skin_ids),
                "skin_ids": skin_ids,
            }
            app.quit()

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" else 1


def drive_settings_apply(run: VerificationRun) -> VerificationResult:
    run.evidence_dir.mkdir(parents=True, exist_ok=True)
    before_path = run.evidence_dir / "settings-before.png"
    after_path = run.evidence_dir / "settings-after.png"
    config_copy_path = run.evidence_dir / "bongo.ini"
    result_path = run.evidence_dir / "result.json"
    window = None
    app = None
    result_values = None

    with isolated_environment(run):
        from PyQt5 import QtCore, QtTest, QtWidgets
        from bongo_cat.models.config import ConfigManager
        from bongo_cat.ui.main_window import BongoCatWindow

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        try:
            window = BongoCatWindow()
            window.show()
            window.open_settings_dialog()
            app.processEvents()

            settings_panel = window.findChild(QtWidgets.QWidget, "settingsPanel")
            skin_dropdown = window.findChild(QtWidgets.QComboBox, "skinDropdown")
            sound_checkbox = window.findChild(
                QtWidgets.QCheckBox,
                "soundEnabledCheckbox",
            )
            apply_button = window.findChild(
                QtWidgets.QPushButton,
                "applySettingsButton",
            )
            if None in (settings_panel, skin_dropdown, sound_checkbox, apply_button):
                raise RuntimeError("The settings UI is missing a verification handle")
            if not settings_panel.grab().save(str(before_path), "PNG"):
                raise RuntimeError(f"Could not save {before_path}")

            selected_skin = skin_dropdown.currentData()
            apply_errors = []
            original_critical = QtWidgets.QMessageBox.critical
            QtWidgets.QMessageBox.critical = lambda *_args: apply_errors.append(
                "apply-error"
            )
            try:
                sound_checkbox.setChecked(False)
                QtTest.QTest.mouseClick(apply_button, QtCore.Qt.LeftButton)
                app.processEvents()
            finally:
                QtWidgets.QMessageBox.critical = original_critical

            if not settings_panel.grab().save(str(after_path), "PNG"):
                raise RuntimeError(f"Could not save {after_path}")

            persisted = ConfigManager(window.config.config_path)
            shutil.copy2(window.config.config_path, config_copy_path)
            skin_ids = sorted(window.skin_manager.get_skin_ids())
            failures = []
            if skin_ids != ["default", "neon", "retro"]:
                failures.append("bundled skin discovery did not return three skins")
            if not isinstance(selected_skin, str):
                failures.append("the selected skin ID is not a string")
            if apply_errors:
                failures.append("Apply requested an error dialog")
            if persisted.sound_enabled:
                failures.append("sound_enabled did not persist as false")

            result_values = {
                "status": "ok" if not failures else "error",
                "revision": revision(run.repo_root),
                "python_version": sys.version.split()[0],
                "qt_version": QtCore.QT_VERSION_STR,
                "working_directory": str(run.working_dir),
                "resolved_skins_dir": str(window.skin_manager.skins_dir),
                "skin_ids": skin_ids,
                "selected_skin_id": selected_skin if isinstance(selected_skin, str) else None,
                "selected_skin_type": type(selected_skin).__name__,
                "apply_error_count": len(apply_errors),
                "persisted_sound_enabled": persisted.sound_enabled,
                "evidence_files": [
                    str(before_path),
                    str(after_path),
                    str(config_copy_path),
                    str(result_path),
                ],
                "scratch_removed": False,
            }
        finally:
            if window is not None:
                window.tray_icon.hide()
                window.settings_panel.hide()
                window.hide()
                window.deleteLater()
            if app is not None:
                app.processEvents()
                app.quit()

    if result_values is None:
        raise RuntimeError("The settings drive did not produce a result")
    result_values["scratch_removed"] = not run.working_dir.parent.exists()
    result = VerificationResult(**result_values)
    result_path.write_text(
        json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Drive Bongo Cat's real Qt settings path in isolated state."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="Check Qt and bundled skin discovery.")
    settings_parser = subparsers.add_parser(
        "settings-apply",
        help="Click Apply and preserve rendered and persisted evidence.",
    )
    settings_parser.add_argument(
        "--evidence-dir",
        type=Path,
        required=True,
        help="Absolute directory for PNG, JSON, and config evidence.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.command == "doctor":
        return doctor(REPO_ROOT)

    evidence_dir = args.evidence_dir.expanduser()
    if not evidence_dir.is_absolute():
        raise SystemExit("--evidence-dir must be absolute")

    with tempfile.TemporaryDirectory(prefix="verify-bongocat-") as scratch:
        scratch_path = Path(scratch)
        working_dir = scratch_path / "working"
        appdata_dir = scratch_path / "appdata"
        working_dir.mkdir()
        appdata_dir.mkdir()
        run = VerificationRun(
            repo_root=REPO_ROOT,
            working_dir=working_dir,
            appdata_dir=appdata_dir,
            evidence_dir=evidence_dir,
        )
        result = drive_settings_apply(run)

    result_path = evidence_dir / "result.json"
    result_values = asdict(result)
    result_values["scratch_removed"] = not scratch_path.exists()
    result = VerificationResult(**result_values)
    result_path.write_text(
        json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0 if result.status == "ok" and result.scratch_removed else 1


if __name__ == "__main__":
    raise SystemExit(main())
