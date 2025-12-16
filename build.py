#!/usr/bin/env python
"""Cross-platform build script for Bongo Cat."""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path


class BongoCatBuilder:
    """Build Bongo Cat for the current platform."""

    def __init__(self):
        """Initialize the builder."""
        self.platform = sys.platform
        self.arch = platform.machine()
        self.dist_dir = Path("dist")
        self.build_dir = Path("build")

    def clean(self):
        """Clean previous build artifacts."""
        print("🧹 Cleaning previous build artifacts...")

        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            print(f"  Removed {self.dist_dir}")

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print(f"  Removed {self.build_dir}")

        # Remove spec file build artifacts
        for file in Path(".").glob("*.spec~"):
            file.unlink()

        print("✓ Clean complete\n")

    def install_dependencies(self):
        """Install build dependencies."""
        print("📦 Installing build dependencies...")

        requirements = [
            "pyinstaller>=5.0",
            "PyQt5>=5.15.10",
            "pygame>=2.5.2",
            "pynput>=1.7.6",
        ]

        if self.platform == "win32":
            requirements.append("pywin32>=306")

        for req in requirements:
            subprocess.run([sys.executable, "-m", "pip", "install", req], check=False)

        print("✓ Dependencies installed\n")

    def build_executable(self):
        """Build the executable using PyInstaller."""
        print(f"🔨 Building Bongo Cat for {self.platform} ({self.arch})...")

        # Build using spec file
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "bongo_cat.spec"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Build failed:")
            print(result.stderr)
            return False

        print("✓ Build complete\n")
        return True

    def create_installer_windows(self):
        """Create Windows installer using Inno Setup (if available)."""
        print("📦 Creating Windows installer...")

        # Check if Inno Setup is available
        inno_setup = shutil.which("iscc")

        if not inno_setup:
            print("⚠️  Inno Setup not found. Skipping installer creation.")
            print("   Download from: https://jrsoftware.org/isdl.php")
            return

        # Create Inno Setup script
        iss_content = f"""
[Setup]
AppName=Bongo Cat
AppVersion=2.0.0
AppPublisher=luinbytes
DefaultDirName={{autopf}}\\BongoCat
DefaultGroupName=Bongo Cat
OutputDir=dist
OutputBaseFilename=BongoCat-Setup-Windows-{self.arch}
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\\BongoCat.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "img\\*"; DestDir: "{{app}}\\img"; Flags: ignoreversion recursesubdirs
Source: "skins\\*"; DestDir: "{{app}}\\skins"; Flags: ignoreversion recursesubdirs
Source: "sounds\\*"; DestDir: "{{app}}\\sounds"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{{group}}\\Bongo Cat"; Filename: "{{app}}\\BongoCat.exe"
Name: "{{autodesktop}}\\Bongo Cat"; Filename: "{{app}}\\BongoCat.exe"

[Run]
Filename: "{{app}}\\BongoCat.exe"; Description: "Launch Bongo Cat"; Flags: nowait postinstall skipifsilent
"""

        iss_file = Path("installer.iss")
        iss_file.write_text(iss_content)

        # Run Inno Setup
        subprocess.run([inno_setup, str(iss_file)], check=False)

        # Clean up
        iss_file.unlink()

        print("✓ Installer created\n")

    def create_dmg_macos(self):
        """Create macOS DMG file."""
        print("📦 Creating macOS DMG...")

        if not shutil.which("hdiutil"):
            print("⚠️  hdiutil not found. Skipping DMG creation.")
            return

        dmg_name = f"BongoCat-{self.arch}.dmg"
        app_path = self.dist_dir / "BongoCat.app"

        if not app_path.exists():
            print(f"❌ {app_path} not found")
            return

        # Create DMG
        cmd = [
            "hdiutil",
            "create",
            "-volname", "Bongo Cat",
            "-srcfolder", str(app_path),
            "-ov",
            "-format", "UDZO",
            str(self.dist_dir / dmg_name)
        ]

        subprocess.run(cmd, check=False)

        print("✓ DMG created\n")

    def create_appimage_linux(self):
        """Create Linux AppImage."""
        print("📦 Creating Linux AppImage...")

        # Check if AppImage tools are available
        if not shutil.which("appimagetool"):
            print("⚠️  appimagetool not found. Skipping AppImage creation.")
            print("   Install from: https://github.com/AppImage/AppImageKit")
            return

        # Create AppDir structure
        appdir = Path("BongoCat.AppDir")
        appdir.mkdir(exist_ok=True)

        # Copy executable
        (appdir / "usr" / "bin").mkdir(parents=True, exist_ok=True)
        shutil.copy(self.dist_dir / "BongoCat", appdir / "usr" / "bin" / "bongocat")

        # Create desktop file
        desktop_content = """[Desktop Entry]
Name=Bongo Cat
Exec=bongocat
Icon=bongocat
Type=Application
Categories=Game;
"""
        (appdir / "bongocat.desktop").write_text(desktop_content)

        # Copy icon (if PNG, convert to compatible format)
        if Path("img/cat-rest.png").exists():
            shutil.copy("img/cat-rest.png", appdir / "bongocat.png")

        # Create AppRun script
        apprun_content = """#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/bongocat" "$@"
"""
        apprun = appdir / "AppRun"
        apprun.write_text(apprun_content)
        apprun.chmod(0o755)

        # Build AppImage
        subprocess.run(["appimagetool", str(appdir)], check=False)

        # Clean up
        shutil.rmtree(appdir)

        print("✓ AppImage created\n")

    def build(self):
        """Run the full build process."""
        print("=" * 60)
        print("🐱 Bongo Cat Build System")
        print("=" * 60)
        print()

        # Clean
        self.clean()

        # Install dependencies
        self.install_dependencies()

        # Build executable
        if not self.build_executable():
            print("❌ Build failed!")
            return 1

        # Create platform-specific installer
        if self.platform == "win32":
            self.create_installer_windows()
        elif self.platform == "darwin":
            self.create_dmg_macos()
        elif self.platform == "linux":
            self.create_appimage_linux()

        print("=" * 60)
        print("✅ Build process complete!")
        print("=" * 60)
        print()
        print(f"📁 Output directory: {self.dist_dir.absolute()}")

        return 0


def main():
    """Main entry point."""
    builder = BongoCatBuilder()
    return builder.build()


if __name__ == "__main__":
    sys.exit(main())
