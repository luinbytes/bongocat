# 🐱 Bongo Cat Desktop Buddy 🐱

![Bongo Cat](img/cat-rest.png)

**Bongo Cat Desktop Buddy** is an interactive desktop pet that lives on your screen and responds to *every* keystroke, mouse click, and controller button press by slapping its adorable little paws! Watch as your furry companion reacts to your inputs in real-time with customizable skins, sound effects, and an achievement system.

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/luinbytes/bongocat/releases)
[![Python](https://img.shields.io/badge/python-3.8--3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ Features

### Core Features
- 🎮 **Multi-Input Support**: Responds to keyboard, mouse, and game controllers
- 🔥 **Combo System**: Chain inputs together for escalating visual effects
- 💫 **Smooth Animations**: Breathing animation when idle, dynamic slapping
- 📊 **Slap Tracking**: Track total slaps with floating +1 animations
- 🎯 **Always-on-Top**: Stays visible while you work or game
- 📍 **Draggable**: Position anywhere on your screen

### New in Version 2.0
- 🎨 **Skins System**: Customize your cat's appearance with custom skins
- 🔊 **Sound Effects**: Optional audio feedback for slaps, combos, and achievements
- 🏆 **Achievements**: 14 unlockable achievements tracking your progress
- 📦 **Easy Distribution**: One-click installers for Windows, macOS, and Linux

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Development Setup](#-development-setup)
- [Building for Distribution](#-building-for-distribution)
- [Configuration](#️-configuration)
- [Creating Custom Skins](#-creating-custom-skins)
- [Adding Sound Effects](#-adding-sound-effects)
- [Achievements](#-achievements)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🚀 Quick Start

### For End Users (Pre-built Releases)

1. Download the latest release for your platform from [Releases](https://github.com/luinbytes/bongocat/releases)
2. Run the installer or extract the archive
3. Launch Bongo Cat!

### For Developers

```bash
# Clone the repository
git clone https://github.com/luinbytes/bongocat.git
cd bongocat

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m bongo_cat
```

---

## 🛠️ Development Setup

### Prerequisites

- **Python 3.8 - 3.12** ([Download Python](https://www.python.org/downloads/))
  - ✅ Tested on Python 3.8, 3.9, 3.10, 3.11, 3.12
  - ⚠️ Python 3.12 requires pygame 2.6.0+ (automatically installed)
- **pip** (comes with Python)
- **git** (optional, for cloning)

### Step-by-Step Installation

#### 1. Clone or Download the Repository

**Using git:**
```bash
git clone https://github.com/luinbytes/bongocat.git
cd bongocat
```

**Or download ZIP:**
- Download from GitHub
- Extract to a folder
- Open terminal/command prompt in that folder

#### 2. Create a Virtual Environment (Recommended)

**Windows:**
```batch
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (for building)
pip install -r requirements-dev.txt
```

**Dependencies Installed:**
- `PyQt5>=5.15.10` - GUI framework
- `pygame>=2.6.0` - Controller input and sound (Python 3.12 compatible)
- `pynput>=1.7.6` - Global keyboard/mouse hooks
- `pywin32>=306` - Windows-specific features (Windows only)

#### 4. Run the Application

```bash
# Run from package
python -m bongo_cat

# Or run the main script directly
python bongo_cat/main.py
```

#### 5. Verify Installation

You should see:
- Bongo Cat window appear on screen
- Cat breathing (idle animation)
- Cat slapping when you press keys/click mouse
- Footer at bottom with slap counter

### Development Commands

```bash
# Run tests
python -m unittest discover tests -v

# Check syntax
python -m py_compile bongo_cat/**/*.py

# Format code (if black installed)
black bongo_cat/

# Type checking (if mypy installed)
mypy bongo_cat/
```

---

## 📦 Building for Distribution

Build standalone executables and installers for end users.

### Prerequisites for Building

```bash
# Install build dependencies
pip install -r requirements-dev.txt
```

**Additional Platform-Specific Requirements:**

- **Windows**: [Inno Setup](https://jrsoftware.org/isdl.php) (optional, for installer)
- **macOS**: Xcode Command Line Tools (for DMG creation)
- **Linux**: [AppImageTool](https://github.com/AppImage/AppImageKit) (optional, for AppImage)

### Build Commands

#### Windows

**Option 1: Automated Build (Recommended)**
```batch
build_windows.bat
```

**Option 2: Manual Build**
```batch
python build.py
```

**Outputs:**
- `dist/BongoCat.exe` - Standalone executable
- `dist/BongoCat-Setup-Windows-x64.exe` - Installer (if Inno Setup installed)

#### macOS

**Option 1: Automated Build (Recommended)**
```bash
chmod +x build_unix.sh
./build_unix.sh
```

**Option 2: Manual Build**
```bash
python3 build.py
```

**Outputs:**
- `dist/BongoCat.app` - Application bundle
- `dist/BongoCat-arm64.dmg` - DMG installer (if hdiutil available)

#### Linux

**Option 1: Automated Build (Recommended)**
```bash
chmod +x build_unix.sh
./build_unix.sh
```

**Option 2: Manual Build**
```bash
python3 build.py
```

**Outputs:**
- `dist/BongoCat` - Standalone executable
- `BongoCat-x86_64.AppImage` - Portable app (if appimagetool installed)

### Build Process Details

The build script (`build.py`) performs these steps:

1. **Clean** - Removes previous build artifacts
2. **Install** - Ensures all dependencies are installed
3. **Build** - Runs PyInstaller with optimized settings
4. **Package** - Creates platform-specific installer (if tools available)

**Build Configuration:**
- Spec file: `bongo_cat.spec`
- Includes: All images, skins, sounds, config files
- Output: Single-file executable with bundled assets
- Console: Hidden (GUI-only application)

### Manual PyInstaller Build

If you prefer manual control:

```bash
# Clean previous builds
rm -rf build dist

# Build with PyInstaller
pyinstaller --clean --noconfirm bongo_cat.spec

# Find output in dist/ folder
```

### Distributing Your Build

**Windows:**
- Share `BongoCat-Setup-Windows-x64.exe` for easy installation
- Or share `BongoCat.exe` as portable version

**macOS:**
- Share `BongoCat-arm64.dmg` for easy installation
- Users drag to Applications folder

**Linux:**
- Share `BongoCat-x86_64.AppImage` as portable version
- Users make executable: `chmod +x BongoCat-x86_64.AppImage`
- Or package as `.deb`/`.rpm` using standard tools

---

## ⚙️ Configuration

### Settings Panel

Access settings by:
1. Hover over the cat to reveal footer
2. Click the ⚙️ Settings button

### Available Settings

| Setting | Description | Default |
|---------|-------------|---------|
| **Auto-hide footer** | Hide footer when not hovering | ✅ Enabled |
| **Footer opacity** | Transparency of footer (0-100) | 50 |
| **Always show total** | Permanent total slaps counter | ❌ Disabled |
| **Floating +1 animations** | Animated "+1" for each slap | ✅ Enabled |
| **Invert cat** | Mirror cat horizontally | ❌ Disabled |
| **Start with Windows** | Auto-launch at startup | ❌ Disabled |
| **Max slap count** | Maximum slaps (0 = unlimited) | 0 |
| **Current skin** | Selected appearance | default |
| **Sound effects** | Enable audio feedback | ✅ Enabled |
| **Sound volume** | Volume level (0-100) | 50 |

### Configuration File

Advanced settings can be edited in `bongo.ini`:

**Location:**
- **Windows**: `%APPDATA%/bongo.ini`
- **macOS**: `~/Library/Application Support/bongo.ini`
- **Linux**: `~/.config/bongo.ini`

**Example `bongo.ini`:**
```ini
[Settings]
slaps = 0
hidden_footer = true
footer_alpha = 50
always_show_points = false
floating_points = true
startup_with_windows = false
max_slaps = 0
invert_cat = false
current_skin = default
sound_enabled = true
sound_volume = 50
```

**Quick Config Access:**
- Click 📝 button in footer to open config file in editor

---

## 🎨 Creating Custom Skins

Make your Bongo Cat unique with custom skins!

### Skin Structure

Create a folder in `skins/` with this structure:

```
skins/
└── your-skin-name/
    ├── skin.json          # Metadata file
    ├── cat-rest.png       # Idle pose
    ├── cat-left.png       # Left paw slap
    └── cat-right.png      # Right paw slap
```

### skin.json Format

```json
{
  "name": "My Awesome Cat",
  "author": "Your Name",
  "version": "1.0.0",
  "description": "A custom Bongo Cat skin with cool colors",
  "images": {
    "idle": "cat-rest.png",
    "left": "cat-left.png",
    "right": "cat-right.png"
  },
  "rotation_degrees": -13
}
```

### Image Guidelines

**Requirements:**
- **Format**: PNG (with transparency)
- **Size**: Any size (original is ~200x200px)
- **Files**: All 3 images required (idle, left, right)

**Recommendations:**
- Use transparent background
- Keep consistent size across all 3 images
- Match the pose structure of original cat
- Test different rotation values for best look

### Testing Your Skin

1. Place skin folder in `skins/`
2. Restart Bongo Cat
3. Open Settings → Skin dropdown
4. Select your skin

### Sharing Your Skin

- Create a `.zip` of your skin folder
- Share on GitHub, Discord, or social media
- Tag with `#BongoCat` `#BongoCatSkin`

### Default Skin Location

The default skin is in `skins/default/` - use this as a template!

---

## 🔊 Adding Sound Effects

Enhance your experience with custom sounds!

### Sound Structure

Place audio files in `sounds/default/`:

```
sounds/
└── default/
    ├── slap.wav           # Regular slap sound
    ├── slap_alt.wav       # Alternate slap (optional)
    ├── combo.wav          # Combo achieved
    ├── combo_high.wav     # High combo (30+)
    └── achievement.wav    # Achievement unlocked
```

### Supported Formats

- **WAV** - Recommended (best compatibility)
- **OGG** - Good compression
- **MP3** - Requires additional codecs on some systems

### Sound Guidelines

**Recommendations:**
- **Duration**: 0.1-0.5 seconds (short and snappy)
- **Volume**: Normalize to consistent levels
- **Quality**: 22050 Hz sample rate is sufficient
- **Size**: Keep files small (<100KB each)

### Finding/Creating Sounds

**Free Sound Resources:**
- [Freesound.org](https://freesound.org/)
- [Zapsplat.com](https://www.zapsplat.com/)
- [Sonniss.com](https://sonniss.com/gameaudiogdc)

**Creating Your Own:**
- Use Audacity (free audio editor)
- Record short sounds
- Export as WAV
- Normalize volume

### Enabling/Disabling Sounds

- Settings → Sound Effects checkbox
- Adjust volume with slider (0-100%)
- Sounds are optional (works without pygame)

---

## 🏆 Achievements

Track your progress and unlock 14 achievements!

### Achievement Categories

#### Slap Count Achievements (6)
| Icon | Name | Requirement |
|------|------|-------------|
| 👋 | First Slap! | Perform your first slap |
| 💯 | Century Club | Reach 100 slaps |
| 🥁 | Dedicated Drummer | Reach 500 slaps |
| 🎯 | Thousand Taps | Reach 1,000 slaps |
| 🎵 | Rhythm Master | Reach 5,000 slaps |
| ⭐ | Ten Thousand Touches | Reach 10,000 slaps |

#### Combo Achievements (5)
| Icon | Name | Requirement |
|------|------|-------------|
| 🔟 | Getting Started | Achieve a 10x combo |
| 🔥 | Combo Novice | Achieve a 25x combo |
| ⚡ | Combo Expert | Achieve a 50x combo |
| 💥 | Combo Master | Achieve a 100x combo |
| 🌟 | Unstoppable | Achieve a 200x combo |

#### Special Achievements (3)
| Icon | Name | Requirement | Note |
|------|------|-------------|------|
| 🦉 | Night Owl | Slap between midnight-3AM | Hidden |
| 🐦 | Early Bird | Slap between 5AM-7AM | Hidden |
| 💫 | Overload Survivor | Achieve 60+ combo | - |

### Achievement Storage

- Saved in `achievements.json` in app directory
- Persists across sessions
- Tracks unlock time for each achievement

### Viewing Achievements

**Current Progress:**
- Check `achievements.json` file
- Future update will add in-app viewer

**Progress Calculation:**
- 14 total achievements
- Percentage = (unlocked / 14) × 100

---

## 🎮 Input Detection

Bongo Cat responds to all these inputs:

### Keyboard
- ✅ Any key press
- ✅ Works in any application
- ✅ Global hook (background detection)

### Mouse
- ✅ Left click
- ✅ Right click
- ✅ Middle click
- ✅ Extra buttons

### Game Controllers
- ✅ Xbox controllers
- ✅ PlayStation controllers
- ✅ Generic gamepads
- ✅ Buttons, triggers, D-pad, joysticks

**Note:** All inputs detected globally - Bongo Cat works even when other apps are focused!

---

## 🌈 Visual Effects

### Combo System

Chain inputs within **800ms** to build combos:

**Combo Levels:**
- **1-29 combos**: 🟡 Yellow counter
- **30-59 combos**: 🟠 Orange counter
- **60+ combos**: 🔴 Red counter with:
  - Pulsing scale effect
  - Wobble animation
  - Screen shake
  - Intensity changes

### Animations

**Idle State:**
- Subtle breathing (8% stretch)
- Smooth sine wave motion
- 60 FPS for fluidity

**Slap State:**
- Alternates left/right paws
- 100ms duration
- Returns to idle smoothly

**Floating Points:**
- "+1" animation on each slap
- Rises 40px upward
- Fades out over 400ms
- Merges into combo counter

---

## 🔧 Troubleshooting

### Application Won't Start

**Issue**: Nothing happens when launching
- **Check**: Python installed? Run `python --version`
- **Check**: Dependencies installed? Run `pip list`
- **Fix**: Reinstall dependencies: `pip install -r requirements.txt`

**Issue**: Error about PyQt5
- **Fix**: `pip install PyQt5==5.15.10`

**Issue**: pygame installation fails on Python 3.12
- **Error**: `ModuleNotFoundError: No module named 'distutils.msvccompiler'`
- **Cause**: pygame 2.5.2 doesn't support Python 3.12 (distutils removed)
- **Fix**: Update requirements: `pip install pygame>=2.6.0`
- **Or**: Use Python 3.11 or earlier
- **Note**: Our requirements.txt now uses pygame 2.6.0+ for Python 3.12 compatibility

### Input Not Detected

**Issue**: Cat doesn't respond to keyboard/mouse
- **Check**: Administrator/sudo permissions (required for global hooks)
- **Windows**: Right-click → Run as Administrator
- **macOS**: System Preferences → Security & Privacy → Accessibility
- **Linux**: Run with sudo or add user to input group

**Issue**: Controller not detected
- **Check**: pygame installed: `pip install pygame>=2.5.2`
- **Test**: Try reconnecting controller
- **Check**: Controller working in other apps?

### Sound Not Working

**Issue**: No sound effects
- **Check**: pygame installed: `pip install pygame`
- **Check**: Sound enabled in settings
- **Check**: System volume not muted
- **Check**: Sound files exist in `sounds/default/`

### Build Issues

**Issue**: PyInstaller not found
- **Fix**: `pip install pyinstaller>=5.0`

**Issue**: Build fails with import errors
- **Fix**: Reinstall all deps: `pip install -r requirements.txt`

**Issue**: Executable crashes on launch
- **Check**: Run from terminal to see error messages
- **Check**: All data files included (check bongo_cat.spec)

### Performance Issues

**Issue**: High CPU usage
- **Normal**: 1-2% idle, 5-10% with frequent inputs
- **If higher**: Close and reopen application
- **Check**: Other apps using global hooks?

**Issue**: Laggy animations
- **Check**: Enable hardware acceleration in GPU settings
- **Reduce**: Footer opacity to improve performance

### Configuration Issues

**Issue**: Settings not saving
- **Check**: Config file writable?
- **Location**: See [Configuration](#️-configuration) section
- **Fix**: Delete config file, restart to recreate

**Issue**: Can't find config file
- **Windows**: `%APPDATA%/bongo.ini`
- **macOS**: `~/Library/Application Support/bongo.ini`
- **Linux**: `~/.config/bongo.ini`

### Platform-Specific Issues

**Windows:**
- Requires pywin32: `pip install pywin32>=306`
- May need Visual C++ Redistributable

**macOS:**
- Accessibility permissions required
- System Preferences → Security & Privacy → Accessibility
- Add Terminal or Python to allowed apps

**Linux:**
- May need `python3-pyqt5` from package manager
- Some distros need `xdg-utils` for file opening
- Controller requires read permissions on `/dev/input/`

---

## 🤝 Contributing

Contributions are welcome! Here's how:

### Ways to Contribute

1. **Report Bugs**: Open an issue with details
2. **Suggest Features**: Open an issue with your idea
3. **Create Skins**: Share custom skins with community
4. **Add Sound Packs**: Create themed sound collections
5. **Code**: Submit pull requests

### Development Workflow

```bash
# 1. Fork the repository
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/bongocat.git
cd bongocat

# 3. Create a feature branch
git checkout -b feature/my-amazing-feature

# 4. Make your changes
# Edit code...

# 5. Run tests
python -m unittest discover tests -v

# 6. Commit your changes
git add .
git commit -m "Add amazing feature"

# 7. Push to your fork
git push origin feature/my-amazing-feature

# 8. Open a Pull Request
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions/classes
- Keep functions focused and small
- Comment complex logic

### Testing

- Write tests for new features
- Ensure all tests pass before PR
- Test on multiple platforms if possible

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Original Bongo Cat meme creators
- PyQt5 framework developers
- Open source community
- All contributors and skin creators

---

## 📬 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/luinbytes/bongocat/issues)
- **Discussions**: [Community discussions](https://github.com/luinbytes/bongocat/discussions)
- **Email**: [your-email@example.com]

---

## 🎯 Project Status

**Version**: 2.0.0
**Status**: ✅ Active Development
**Stability**: Stable
**Platform Support**: Windows, macOS, Linux

### Recent Updates

**v2.0.0** (Current)
- ✨ Added skins system
- 🔊 Added sound effects
- 🏆 Added achievements
- 📦 Multi-platform packaging
- 🏗️ Modular architecture refactor

**v1.0.0**
- 🎮 Multi-input support
- 🔥 Combo system
- 💫 Smooth animations
- ⚙️ Configuration panel

---

## 🚀 Roadmap

Future ideas (no timeline):
- [ ] In-app achievement viewer
- [ ] Skin editor GUI
- [ ] Online leaderboards
- [ ] Plugin system
- [ ] Animation customization
- [ ] More built-in skins
- [ ] Mobile companion app

---

<div align="center">

**⭐ Star this repo if you love Bongo Cat! ⭐**

Made with ❤️ by [luinbytes](https://github.com/luinbytes)

</div>

---

*Bongo Cat Desktop Buddy is not affiliated with the original Bongo Cat meme. This is a fan-made desktop application inspired by the beloved internet phenomenon.*
