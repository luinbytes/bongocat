"""Skin management system for Bongo Cat."""

import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger("BongoCat")


@dataclass
class SkinInfo:
    """Information about a skin.

    Attributes:
        name: Display name of the skin
        author: Creator of the skin
        version: Skin version
        description: Description of the skin
        path: Path to the skin directory
        images: Dictionary mapping image types to filenames
        rotation_degrees: Image rotation in degrees
    """
    name: str
    author: str
    version: str
    description: str
    path: str
    images: Dict[str, str]
    rotation_degrees: int = -13


class SkinManager:
    """Manages loading and switching of skins.

    Skins are located in the 'skins/' directory. Each skin is a subdirectory
    containing:
    - skin.json: Metadata file
    - cat-rest.png: Idle animation image
    - cat-left.png: Left paw slap image
    - cat-right.png: Right paw slap image

    Attributes:
        skins_dir: Path to the skins directory
        available_skins: Dictionary of available skins
        current_skin: Currently loaded skin
    """

    def __init__(self, skins_dir: str = "skins"):
        """Initialize the skin manager.

        Args:
            skins_dir: Path to the skins directory
        """
        self.skins_dir = skins_dir
        self.available_skins: Dict[str, SkinInfo] = {}
        self.current_skin: Optional[SkinInfo] = None
        self._discover_skins()

    def _discover_skins(self) -> None:
        """Discover all available skins in the skins directory."""
        if not os.path.exists(self.skins_dir):
            logger.warning(f"Skins directory not found: {self.skins_dir}")
            return

        for skin_dir in os.listdir(self.skins_dir):
            skin_path = os.path.join(self.skins_dir, skin_dir)

            if not os.path.isdir(skin_path):
                continue

            metadata_path = os.path.join(skin_path, "skin.json")

            if not os.path.exists(metadata_path):
                logger.warning(f"Skin metadata not found: {metadata_path}")
                continue

            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                skin_info = SkinInfo(
                    name=metadata.get('name', skin_dir),
                    author=metadata.get('author', 'Unknown'),
                    version=metadata.get('version', '1.0.0'),
                    description=metadata.get('description', ''),
                    path=skin_path,
                    images=metadata.get('images', {
                        'idle': 'cat-rest.png',
                        'left': 'cat-left.png',
                        'right': 'cat-right.png'
                    }),
                    rotation_degrees=metadata.get('rotation_degrees', -13)
                )

                # Validate that all required images exist
                if self._validate_skin(skin_info):
                    self.available_skins[skin_dir] = skin_info
                    logger.info(f"Loaded skin: {skin_info.name} by {skin_info.author}")
                else:
                    logger.warning(f"Skin validation failed: {skin_dir}")

            except (json.JSONDecodeError, KeyError, Exception) as e:
                logger.error(f"Error loading skin {skin_dir}: {e}")

    def _validate_skin(self, skin: SkinInfo) -> bool:
        """Validate that a skin has all required images.

        Args:
            skin: Skin to validate

        Returns:
            True if skin is valid, False otherwise
        """
        required_keys = ['idle', 'left', 'right']

        for key in required_keys:
            if key not in skin.images:
                logger.error(f"Skin {skin.name} missing image key: {key}")
                return False

            image_path = os.path.join(skin.path, skin.images[key])
            if not os.path.exists(image_path):
                logger.error(f"Skin {skin.name} missing image file: {image_path}")
                return False

        return True

    def load_skin(self, skin_id: str) -> bool:
        """Load a skin by ID.

        Args:
            skin_id: Directory name of the skin to load

        Returns:
            True if skin loaded successfully, False otherwise
        """
        if skin_id not in self.available_skins:
            logger.error(f"Skin not found: {skin_id}")
            return False

        self.current_skin = self.available_skins[skin_id]
        logger.info(f"Loaded skin: {self.current_skin.name}")
        return True

    def get_skin_names(self) -> List[str]:
        """Get list of available skin names.

        Returns:
            List of skin display names
        """
        return [skin.name for skin in self.available_skins.values()]

    def get_skin_ids(self) -> List[str]:
        """Get list of available skin IDs.

        Returns:
            List of skin directory names
        """
        return list(self.available_skins.keys())

    def get_current_skin_id(self) -> str:
        """Get the ID of the currently loaded skin.

        Returns:
            Current skin ID, or 'default' if none loaded
        """
        if self.current_skin:
            # Find the ID by matching the path
            for skin_id, skin in self.available_skins.items():
                if skin.path == self.current_skin.path:
                    return skin_id
        return 'default'

    def get_image_path(self, image_type: str) -> Optional[str]:
        """Get the path to a specific image in the current skin.

        Args:
            image_type: Type of image ('idle', 'left', or 'right')

        Returns:
            Full path to the image, or None if not found
        """
        if not self.current_skin:
            return None

        if image_type not in self.current_skin.images:
            return None

        return os.path.join(self.current_skin.path, self.current_skin.images[image_type])

    def get_rotation_degrees(self) -> int:
        """Get the rotation degrees for the current skin.

        Returns:
            Rotation degrees, or -13 as default
        """
        if self.current_skin:
            return self.current_skin.rotation_degrees
        return -13
