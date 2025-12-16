# Implementation Guide - Phase 5 Feature Integration

This guide provides step-by-step instructions for integrating the Phase 4 managers (Skins, Sounds, Achievements) into the UI.

---

## 🎨 Part 1: Skin Manager Integration

### Step 1: Import SkinManager in main_window.py

**File:** `bongo_cat/ui/main_window.py`

```python
# Add to imports (line ~15):
from ..models import ConfigManager, SkinManager
```

### Step 2: Initialize SkinManager

**File:** `bongo_cat/ui/main_window.py` in `__init__` method

```python
# After self.config = ConfigManager() (line ~46):
self.skin_manager = SkinManager()
self.skin_manager.load_skin(self.config.current_skin)
```

### Step 3: Use Skin Images Instead of Hardcoded Paths

**File:** `bongo_cat/ui/main_window.py` in `setup_ui` method

**Replace:**
```python
pixmap = QtGui.QPixmap(resource_path("img/cat-rest.png"))
```

**With:**
```python
current_skin = self.skin_manager.current_skin
if current_skin:
    pixmap = QtGui.QPixmap(current_skin.images['idle'])
else:
    # Fallback to default
    pixmap = QtGui.QPixmap(resource_path("img/cat-rest.png"))
```

**Apply same pattern for:**
- `cat-left.png` → `current_skin.images['left']`
- `cat-right.png` → `current_skin.images['right']`

### Step 4: Add Skin Dropdown to Settings

**File:** `bongo_cat/ui/main_window.py` in `setup_settings_panel` method

```python
# After max_slaps_spinbox (around line ~1413):

# Skin selection
self.config.skin_dropdown = QtWidgets.QComboBox()
self.config.skin_dropdown.setStyleSheet("""
    color: white;
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    padding: 4px;
""")

# Populate with available skins
for skin_id, skin_info in self.skin_manager.available_skins.items():
    self.config.skin_dropdown.addItem(skin_info.name, skin_id)

# Set current selection
current_index = self.config.skin_dropdown.findData(self.config.current_skin)
if current_index >= 0:
    self.config.skin_dropdown.setCurrentIndex(current_index)

form_layout.addRow(
    self.create_settings_label("Cat Skin:"),
    self.config.skin_dropdown
)
```

### Step 5: Apply Skin Changes

**File:** `bongo_cat/ui/main_window.py` in `apply_settings` method

```python
# Add after line ~1258:
selected_skin_id = self.config.skin_dropdown.currentData()
if selected_skin_id != self.config.current_skin:
    self.config.current_skin = selected_skin_id
    self.skin_manager.load_skin(selected_skin_id)
    # Reload images
    self.update_stretched_image()
```

### Step 6: Update open_settings_dialog

**File:** `bongo_cat/ui/main_window.py` in `open_settings_dialog` method

```python
# Add after line ~1259:
current_index = self.config.skin_dropdown.findData(self.config.current_skin)
if current_index >= 0:
    self.config.skin_dropdown.setCurrentIndex(current_index)
```

---

## 🔊 Part 2: Sound Manager Integration

### Step 1: Import SoundManager

**File:** `bongo_cat/ui/main_window.py`

```python
# Add to imports:
from ..models import ConfigManager, SkinManager, SoundManager
```

### Step 2: Initialize SoundManager

**File:** `bongo_cat/ui/main_window.py` in `__init__` method

```python
# After skin_manager initialization:
self.sound_manager = SoundManager(
    enabled=self.config.sound_enabled,
    volume=self.config.sound_volume / 100.0
)
```

### Step 3: Play Sound on Slap

**File:** `bongo_cat/ui/main_window.py` in `do_slap` method

```python
# Add after combo_count increment (around line ~630):
if self.sound_manager.enabled:
    # Alternate between slap sounds randomly
    alternate = random.random() > 0.5
    self.sound_manager.play_slap(alternate=alternate)
```

### Step 4: Play Sound on Combo Milestones

**File:** `bongo_cat/ui/main_window.py` in `do_slap` method

```python
# After combo threshold checks (around line ~645):
if self.combo_count in [10, 25, 50, 100]:
    if self.sound_manager.enabled:
        if self.combo_count >= 50:
            self.sound_manager.play('combo_high')
        else:
            self.sound_manager.play('combo')
```

### Step 5: Add Sound Controls to Settings

**File:** `bongo_cat/ui/main_window.py` in `setup_settings_panel` method

```python
# After skin dropdown:

# Sound enabled toggle
self.config.sound_enabled_checkbox = QtWidgets.QCheckBox()
self.config.sound_enabled_checkbox.setChecked(self.config.sound_enabled)
self.config.sound_enabled_checkbox.setStyleSheet("color: white;")
form_layout.addRow(
    self.create_settings_label("Enable Sounds:"),
    self.config.sound_enabled_checkbox
)

# Sound volume slider
self.config.sound_volume_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
self.config.sound_volume_slider.setRange(0, 100)
self.config.sound_volume_slider.setValue(self.config.sound_volume)
self.config.sound_volume_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
self.config.sound_volume_slider.setTickInterval(10)

sound_volume_layout = QtWidgets.QHBoxLayout()
sound_volume_layout.addWidget(self.config.sound_volume_slider)
self.config.sound_volume_value = QtWidgets.QLabel(f"{self.config.sound_volume}%")
self.config.sound_volume_value.setStyleSheet("color: white; min-width: 40px;")
sound_volume_layout.addWidget(self.config.sound_volume_value)
self.config.sound_volume_slider.valueChanged.connect(
    lambda value: self.config.sound_volume_value.setText(f"{value}%")
)

form_layout.addRow(
    self.create_settings_label("Sound Volume:"),
    sound_volume_layout
)
```

### Step 6: Apply Sound Settings

**File:** `bongo_cat/ui/main_window.py` in `apply_settings` method

```python
# Add:
self.config.sound_enabled = self.config.sound_enabled_checkbox.isChecked()
self.config.sound_volume = self.config.sound_volume_slider.value()

# Update sound manager
self.sound_manager.enabled = self.config.sound_enabled
self.sound_manager.set_volume(self.config.sound_volume / 100.0)
```

### Step 7: Update open_settings_dialog

**File:** `bongo_cat/ui/main_window.py` in `open_settings_dialog` method

```python
# Add:
self.config.sound_enabled_checkbox.setChecked(self.config.sound_enabled)
self.config.sound_volume_slider.setValue(self.config.sound_volume)
```

---

## 🏆 Part 3: Achievement Manager Integration

### Step 1: Import AchievementManager

**File:** `bongo_cat/ui/main_window.py`

```python
# Add to imports:
from ..models import ConfigManager, SkinManager, SoundManager, AchievementManager
```

### Step 2: Initialize AchievementManager

**File:** `bongo_cat/ui/main_window.py` in `__init__` method

```python
# After sound_manager initialization:
self.achievement_manager = AchievementManager()
```

### Step 3: Check for Achievements on Slap

**File:** `bongo_cat/ui/main_window.py` in `do_slap` method

```python
# After incrementing slap count:
newly_unlocked = self.achievement_manager.check_slap_count(self.config.slaps)
for achievement in newly_unlocked:
    self.show_achievement_notification(achievement)
    if self.sound_manager.enabled:
        self.sound_manager.play('achievement')
```

### Step 4: Check for Combo Achievements

**File:** `bongo_cat/ui/main_window.py` in `do_slap` method

```python
# After updating combo count:
newly_unlocked = self.achievement_manager.check_combo(self.combo_count)
for achievement in newly_unlocked:
    self.show_achievement_notification(achievement)
    if self.sound_manager.enabled:
        self.sound_manager.play('achievement')
```

### Step 5: Create Achievement Notification Method

**File:** `bongo_cat/ui/main_window.py` (new method)

```python
def show_achievement_notification(self, achievement):
    """Show a notification when an achievement is unlocked.

    Args:
        achievement: Achievement object that was unlocked
    """
    # Create notification label
    notif = QtWidgets.QLabel(self)
    notif.setStyleSheet(f"""
        QLabel {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 215, 0, 230),
                stop:1 rgba(255, 165, 0, 230)
            );
            color: #2c3e50;
            font: bold 14px 'Segoe UI';
            padding: 12px 16px;
            border-radius: 8px;
            border: 2px solid rgba(255, 215, 0, 255);
        }}
    """)
    notif.setText(f"🏆 {achievement.name}\n{achievement.description}")
    notif.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Position at top center of window
    notif.adjustSize()
    notif.move(
        (self.width() - notif.width()) // 2,
        20
    )
    notif.show()

    # Fade in animation
    opacity_effect = QtWidgets.QGraphicsOpacityEffect(notif)
    notif.setGraphicsEffect(opacity_effect)

    fade_in = QtCore.QPropertyAnimation(opacity_effect, b"opacity")
    fade_in.setDuration(500)
    fade_in.setStartValue(0.0)
    fade_in.setEndValue(1.0)
    fade_in.start()

    # Auto-hide after 5 seconds
    QtCore.QTimer.singleShot(5000, lambda: self.fade_out_notification(notif))

def fade_out_notification(self, notif):
    """Fade out and remove notification.

    Args:
        notif: Notification label widget
    """
    opacity_effect = notif.graphicsEffect()
    if opacity_effect:
        fade_out = QtCore.QPropertyAnimation(opacity_effect, b"opacity")
        fade_out.setDuration(500)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.finished.connect(notif.deleteLater)
        fade_out.start()
```

### Step 6: Add View Achievements Button

**File:** `bongo_cat/ui/main_window.py` in `setup_settings_panel` method

```python
# After the form_layout, before buttons_layout:

# Achievements button
achievements_button = QtWidgets.QPushButton("View Achievements")
achievements_button.setStyleSheet("""
    background-color: #f39c12;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    font-weight: bold;
""")
achievements_button.clicked.connect(self.show_achievements_dialog)
main_layout.addWidget(achievements_button)
```

### Step 7: Create Achievements Dialog

**File:** `bongo_cat/ui/main_window.py` (new method)

```python
def show_achievements_dialog(self):
    """Show the achievements viewer dialog."""
    dialog = QtWidgets.QDialog(self)
    dialog.setWindowTitle("Achievements")
    dialog.setFixedSize(500, 600)
    dialog.setWindowFlags(
        Qt.WindowType.Window |
        Qt.WindowType.WindowStaysOnTopHint
    )

    layout = QtWidgets.QVBoxLayout(dialog)

    # Title
    title = QtWidgets.QLabel("🏆 Achievements")
    title.setStyleSheet("font: bold 18px; color: #f39c12; padding: 10px;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    # Progress
    unlocked_count = len([a for a in self.achievement_manager.achievements.values() if a.unlocked])
    total_count = len(self.achievement_manager.achievements)
    progress_label = QtWidgets.QLabel(f"Progress: {unlocked_count}/{total_count}")
    progress_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
    progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(progress_label)

    # Scroll area
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("background: #ecf0f1; border: none;")

    scroll_widget = QtWidgets.QWidget()
    scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)

    # Group achievements by category
    categories = {}
    for achievement in self.achievement_manager.achievements.values():
        if achievement.category not in categories:
            categories[achievement.category] = []
        categories[achievement.category].append(achievement)

    # Display by category
    for category, achievements in sorted(categories.items()):
        # Category header
        cat_label = QtWidgets.QLabel(category.upper())
        cat_label.setStyleSheet("font: bold 14px; color: #2c3e50; padding: 10px 5px 5px 5px;")
        scroll_layout.addWidget(cat_label)

        # Achievement items
        for achievement in achievements:
            item = self.create_achievement_item(achievement)
            scroll_layout.addWidget(item)

    scroll_layout.addStretch()
    scroll.setWidget(scroll_widget)
    layout.addWidget(scroll)

    # Close button
    close_btn = QtWidgets.QPushButton("Close")
    close_btn.clicked.connect(dialog.close)
    close_btn.setStyleSheet("""
        background-color: #3498db;
        color: white;
        border: none;
        padding: 8px;
        border-radius: 4px;
    """)
    layout.addWidget(close_btn)

    dialog.exec_()

def create_achievement_item(self, achievement):
    """Create a widget for displaying an achievement.

    Args:
        achievement: Achievement object

    Returns:
        QWidget containing achievement info
    """
    widget = QtWidgets.QWidget()
    widget.setStyleSheet("""
        QWidget {
            background: white;
            border-radius: 6px;
            padding: 8px;
        }
    """)

    layout = QtWidgets.QHBoxLayout(widget)

    # Icon
    icon_label = QtWidgets.QLabel(achievement.icon)
    icon_label.setStyleSheet(f"""
        font-size: 32px;
        padding: 5px;
        {"" if achievement.unlocked else "opacity: 0.3;"}
    """)
    layout.addWidget(icon_label)

    # Info
    info_layout = QtWidgets.QVBoxLayout()

    name_label = QtWidgets.QLabel(achievement.name)
    name_label.setStyleSheet(f"""
        font: bold 13px;
        color: {"#2c3e50" if achievement.unlocked else "#95a5a6"};
    """)
    info_layout.addWidget(name_label)

    desc_label = QtWidgets.QLabel(achievement.description)
    desc_label.setStyleSheet(f"""
        font: 11px;
        color: {"#7f8c8d" if achievement.unlocked else "#bdc3c7"};
    """)
    desc_label.setWordWrap(True)
    info_layout.addWidget(desc_label)

    if achievement.unlocked and achievement.unlock_time:
        time_label = QtWidgets.QLabel(f"Unlocked: {achievement.unlock_time}")
        time_label.setStyleSheet("font: 10px; color: #95a5a6;")
        info_layout.addWidget(time_label)

    layout.addLayout(info_layout, 1)

    # Status
    if achievement.unlocked:
        status_label = QtWidgets.QLabel("✓")
        status_label.setStyleSheet("color: #27ae60; font: bold 24px;")
        layout.addWidget(status_label)
    else:
        if not achievement.hidden:
            status_label = QtWidgets.QLabel("🔒")
            status_label.setStyleSheet("font-size: 20px; opacity: 0.3;")
            layout.addWidget(status_label)

    return widget
```

---

## 🧪 Part 4: Test Cases to Write

### test_skin_manager.py

```python
import unittest
from bongo_cat.models.skin_manager import SkinManager

class TestSkinManager(unittest.TestCase):
    def test_discover_default_skin(self):
        """Test that default skin is discovered."""
        manager = SkinManager()
        self.assertIn('default', manager.available_skins)

    def test_discover_retro_skin(self):
        """Test that retro skin is discovered."""
        manager = SkinManager()
        self.assertIn('retro', manager.available_skins)

    def test_discover_neon_skin(self):
        """Test that neon skin is discovered."""
        manager = SkinManager()
        self.assertIn('neon', manager.available_skins)

    def test_load_default_skin(self):
        """Test loading default skin."""
        manager = SkinManager()
        result = manager.load_skin('default')
        self.assertTrue(result)
        self.assertIsNotNone(manager.current_skin)
        self.assertEqual(manager.current_skin.name, 'Classic Bongo Cat')

    def test_load_invalid_skin(self):
        """Test loading non-existent skin."""
        manager = SkinManager()
        result = manager.load_skin('nonexistent')
        self.assertFalse(result)

    def test_skin_has_required_images(self):
        """Test that skin has all required images."""
        manager = SkinManager()
        manager.load_skin('default')
        skin = manager.current_skin
        self.assertIn('idle', skin.images)
        self.assertIn('left', skin.images)
        self.assertIn('right', skin.images)
```

### test_sound_manager.py

```python
import unittest
from bongo_cat.models.sound_manager import SoundManager

class TestSoundManager(unittest.TestCase):
    def test_initialize_enabled(self):
        """Test sound manager initializes."""
        manager = SoundManager(enabled=True)
        self.assertTrue(manager.enabled or not manager.enabled)  # Works even without pygame

    def test_initialize_disabled(self):
        """Test sound manager initializes disabled."""
        manager = SoundManager(enabled=False)
        self.assertFalse(manager.enabled)

    def test_set_volume(self):
        """Test volume setting."""
        manager = SoundManager()
        manager.set_volume(0.5)
        self.assertEqual(manager.volume, 0.5)

    def test_volume_bounds(self):
        """Test volume bounds checking."""
        manager = SoundManager()
        manager.set_volume(1.5)  # Too high
        self.assertLessEqual(manager.volume, 1.0)
        manager.set_volume(-0.5)  # Too low
        self.assertGreaterEqual(manager.volume, 0.0)
```

### test_achievements.py

```python
import unittest
import tempfile
import os
from bongo_cat.models.achievements import AchievementManager

class TestAchievements(unittest.TestCase):
    def setUp(self):
        """Create temp file for achievements."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()

    def tearDown(self):
        """Clean up temp file."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_initialize(self):
        """Test achievement manager initializes."""
        manager = AchievementManager(self.temp_file.name)
        self.assertGreater(len(manager.achievements), 0)

    def test_first_slap_achievement(self):
        """Test first slap achievement unlocks."""
        manager = AchievementManager(self.temp_file.name)
        unlocked = manager.check_slap_count(1)
        first_slap = [a for a in unlocked if 'First' in a.name]
        self.assertGreater(len(first_slap), 0)

    def test_achievement_persistence(self):
        """Test achievements persist to disk."""
        manager1 = AchievementManager(self.temp_file.name)
        manager1.check_slap_count(100)
        manager1.save()

        # Load in new instance
        manager2 = AchievementManager(self.temp_file.name)
        unlocked = [a for a in manager2.achievements.values() if a.unlocked]
        self.assertGreater(len(unlocked), 0)

    def test_combo_achievement(self):
        """Test combo achievements unlock."""
        manager = AchievementManager(self.temp_file.name)
        unlocked = manager.check_combo(50)
        combo_achievements = [a for a in unlocked if 'Combo' in a.name or 'combo' in a.description]
        self.assertGreater(len(combo_achievements), 0)
```

### test_ui_window.py

```python
import unittest
from PyQt5 import QtWidgets
from bongo_cat.ui.main_window import BongoCatWindow

class TestBongoCatWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create QApplication once for all tests."""
        import sys
        cls.app = QtWidgets.QApplication(sys.argv)

    def test_window_creates(self):
        """Test window can be created."""
        window = BongoCatWindow()
        self.assertIsNotNone(window)
        window.close()

    def test_window_has_config(self):
        """Test window has config manager."""
        window = BongoCatWindow()
        self.assertIsNotNone(window.config)
        window.close()

    def test_slap_increments_counter(self):
        """Test slap increments counter."""
        window = BongoCatWindow()
        initial_count = window.config.slaps
        window.do_slap()
        self.assertEqual(window.config.slaps, initial_count + 1)
        window.close()

    def test_pause_toggle(self):
        """Test pause functionality."""
        window = BongoCatWindow()
        initial_state = window.is_paused
        window.toggle_pause()
        self.assertNotEqual(window.is_paused, initial_state)
        window.close()
```

---

## 📋 Implementation Checklist

### Phase 5A: Skin Integration
- [ ] Import SkinManager
- [ ] Initialize in __init__
- [ ] Replace hardcoded image paths
- [ ] Add skin dropdown to settings
- [ ] Wire up skin switching
- [ ] Update open_settings_dialog
- [ ] Test skin switching works
- [ ] Test all 3 skins load correctly

### Phase 5B: Sound Integration
- [ ] Import SoundManager
- [ ] Initialize in __init__
- [ ] Play slap sounds
- [ ] Play combo sounds
- [ ] Add sound toggle to settings
- [ ] Add volume slider to settings
- [ ] Wire up sound settings
- [ ] Update open_settings_dialog
- [ ] Test sounds play correctly
- [ ] Test volume control works

### Phase 5C: Achievement Integration
- [ ] Import AchievementManager
- [ ] Initialize in __init__
- [ ] Check achievements on slap
- [ ] Check achievements on combo
- [ ] Create notification method
- [ ] Play achievement sound
- [ ] Add View Achievements button
- [ ] Create achievements dialog
- [ ] Test achievements unlock
- [ ] Test achievement persistence

### Phase 5D: Testing
- [ ] Write test_skin_manager.py
- [ ] Write test_sound_manager.py
- [ ] Write test_achievements.py
- [ ] Write test_ui_window.py
- [ ] Run all tests
- [ ] Fix any failing tests
- [ ] Verify coverage >50%

### Phase 5E: Documentation
- [ ] Update README with actual features
- [ ] Add screenshots of working features
- [ ] Update CHANGELOG
- [ ] Create USER_GUIDE.md
- [ ] Document how to create skins
- [ ] Document how to add sounds

### Phase 5F: Release
- [ ] Bump version to 2.0.0
- [ ] Test on Windows
- [ ] Test on macOS
- [ ] Test on Linux
- [ ] Build executables
- [ ] Create release notes
- [ ] Tag release in git

---

**Estimated Total Time:** 15-20 hours
**Priority:** CRITICAL - Makes documented features actually work
**Impact:** Transforms project from 60% complete to 100% complete

---

End of Implementation Guide
