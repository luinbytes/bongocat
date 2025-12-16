"""Resource path management for bundled and development environments."""

import os
import sys


def resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource.

    Handles both development (file system) and PyInstaller bundled environments.
    Special handling for bongo.ini which goes to APPDATA directory.

    Args:
        relative_path: Relative path to the resource

    Returns:
        Absolute path to the resource

    Examples:
        >>> resource_path("img/cat-rest.png")
        '/path/to/bongocat/img/cat-rest.png'

        >>> resource_path("bongo.ini")
        '/home/user/.config/BongoCat/bongo.ini'  # or %APPDATA%/BongoCat on Windows
    """
    if relative_path == "bongo.ini":
        appdata = os.getenv("APPDATA")
        if appdata is None:
            appdata = os.path.expanduser("~/.config")
        appdata_path = os.path.join(appdata, "BongoCat")
        os.makedirs(appdata_path, exist_ok=True)
        return os.path.join(appdata_path, relative_path)

    if getattr(sys, '_MEIPASS', None) is not None:
        base_path = getattr(sys, '_MEIPASS')
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)
