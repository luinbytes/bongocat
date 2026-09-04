import json
import os
from pathlib import Path
import struct
import tempfile
import unittest

from bongo_cat.models.skin_manager import SkinManager


BUILTIN_SKIN_IDS = ("default", "neon", "retro")
POSE_FILENAMES = ("cat-rest.png", "cat-left.png", "cat-right.png")


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


class TestBuiltInSkinAssets(unittest.TestCase):
    def test_builtin_skin_assets_are_distinct_and_keep_dimensions(self):
        repo_root = Path(__file__).resolve().parents[1]
        skin_assets = {
            skin_id: {
                pose: repo_root / "skins" / skin_id / pose
                for pose in POSE_FILENAMES
            }
            for skin_id in BUILTIN_SKIN_IDS
        }

        for skin_id in BUILTIN_SKIN_IDS[1:]:
            for pose, default_path in skin_assets["default"].items():
                with self.subTest(skin=skin_id, pose=pose):
                    self.assertNotEqual(
                        default_path.read_bytes(),
                        skin_assets[skin_id][pose].read_bytes(),
                        f"{skin_id}/{pose} must differ from default",
                    )

        for skin_id, poses in skin_assets.items():
            for pose, path in poses.items():
                with self.subTest(skin=skin_id, pose=pose):
                    header = path.read_bytes()[:29]
                    self.assertEqual(b"\x89PNG\r\n\x1a\n", header[:8])
                    self.assertEqual(13, struct.unpack(">I", header[8:12])[0])
                    self.assertEqual(b"IHDR", header[12:16])
                    width, height = struct.unpack(">II", header[16:24])
                    self.assertEqual((200, 126), (width, height))


if __name__ == "__main__":
    unittest.main()
