"""Tests for footer effect handling in settings updates."""

import ast
from pathlib import Path
import unittest


class TestFooterSettings(unittest.TestCase):
    """Settings changes should not leave dangling footer effects."""

    def _main_window_method(self, method_name):
        source = Path("bongo_cat/ui/main_window.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        return next(
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == method_name
        )

    def test_apply_settings_stops_animation_before_replacing_footer_style(self):
        apply_settings = self._main_window_method("apply_settings")

        call_lines = {}
        for node in ast.walk(apply_settings):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr == "setup_footer_style":
                    call_lines["style"] = node.lineno
                elif func.attr == "stop" and isinstance(func.value, ast.Attribute):
                    if func.value.attr == "footer_animation":
                        call_lines["stop"] = node.lineno

        self.assertLess(call_lines["stop"], call_lines["style"])

    def test_footer_style_does_not_replace_footer_graphics_effect(self):
        setup_footer_style = self._main_window_method("setup_footer_style")

        calls_set_graphics_effect = [
            node for node in ast.walk(setup_footer_style)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "setGraphicsEffect"
            )
        ]

        self.assertEqual([], calls_set_graphics_effect)

    def test_drag_press_does_not_replace_footer_graphics_effect(self):
        mouse_press = self._main_window_method("mousePressEvent")

        calls_set_graphics_effect = [
            node for node in ast.walk(mouse_press)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "setGraphicsEffect"
            )
        ]

        self.assertEqual([], calls_set_graphics_effect)

    def test_drag_release_does_not_replace_footer_graphics_effect(self):
        mouse_release = self._main_window_method("mouseReleaseEvent")

        calls_set_graphics_effect = [
            node for node in ast.walk(mouse_release)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "setGraphicsEffect"
            )
        ]

        self.assertEqual([], calls_set_graphics_effect)


if __name__ == "__main__":
    unittest.main()
