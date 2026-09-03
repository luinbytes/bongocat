import json
import os
from pathlib import Path
import tempfile
import unittest

from bongo_cat.models.skin_manager import SkinManager


class TestSkinManagerPaths(unittest.TestCase):
    def test_explicit_relative_skin_directory_stays_authoritative(self):
        with tempfile.TemporaryDirectory() as working_dir:
            skin_root = Path(working_dir, "custom-skins")
            skin_dir = skin_root / "fixture"
            skin_dir.mkdir(parents=True)
            (skin_dir / "skin.json").write_text(
                json.dumps(
                    {
                        "name": "Fixture",
                        "images": {
                            "idle": "cat-rest.png",
                            "left": "cat-left.png",
                            "right": "cat-right.png",
                        },
                    }
                ),
                encoding="utf-8",
            )
            for image_name in ("cat-rest.png", "cat-left.png", "cat-right.png"):
                (skin_dir / image_name).write_bytes(b"fixture")

            original_cwd = os.getcwd()
            try:
                os.chdir(working_dir)
                manager = SkinManager("custom-skins")
            finally:
                os.chdir(original_cwd)

        self.assertEqual("custom-skins", manager.skins_dir)
        self.assertEqual(["fixture"], manager.get_skin_ids())


if __name__ == "__main__":
    unittest.main()
