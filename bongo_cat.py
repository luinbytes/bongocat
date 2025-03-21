import sys
import os
import threading
import configparser
from PyQt5 import QtCore, QtGui, QtWidgets
from pynput import keyboard, mouse
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QSettings, Qt
from typing import Optional, cast
import random

def resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource."""
    if relative_path == "bongo.ini":
        # Use AppData for the config file
        appdata = os.getenv("APPDATA")
        if appdata is None:
            appdata = os.path.expanduser("~")
        appdata_path = os.path.join(appdata, "BongoCat")
        os.makedirs(appdata_path, exist_ok=True)  # Ensure the directory exists
        return os.path.join(appdata_path, relative_path)
    if getattr(sys, '_MEIPASS', None) is not None:
        # If running as a PyInstaller bundle
        base_path = getattr(sys, '_MEIPASS')
    else:
        # If running as a script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class BongoCatWindow(QtWidgets.QWidget):
    trigger_slap = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        # Connect the signal to the slot
        self.trigger_slap.connect(self.do_slap)
        
        self.load_config()
        self.setWindowTitle("Bongo Cat")
        
        # Settings for window position
        self.settings = QSettings('BongoCat', 'BongoCat')
        self.restore_window_position()
        
        # System tray setup
        self.setup_system_tray()
        
        # Context menu setup
        self.setup_context_menu()
        
        # Pause state
        self.is_paused = False

        # Frameless, transparent, always on top
        flags = Qt.WindowFlags()
        flags |= Qt.WindowType.FramelessWindowHint
        flags |= Qt.WindowType.WindowStaysOnTopHint
        flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Enable mouse tracking to detect hover
        self.setMouseTracking(True)

        # Input count & tracking
        self.input_count = 0
        self.current_side = "left"

        # Load and auto-fix images (level the cat)
        self.idle_pixmap = self.load_and_fix_image(resource_path("img/cat-rest.png"))
        self.slap_pixmap_left = self.load_and_fix_image(resource_path("img/cat-left.png"))
        self.slap_pixmap_right = self.load_and_fix_image(resource_path("img/cat-right.png"))

        # Dimensions
        self.cat_width = self.idle_pixmap.width()
        self.cat_height = self.idle_pixmap.height()
        self.footer_height = 35

        # Total window size = cat + footer
        self.setFixedSize(self.cat_width, self.cat_height + self.footer_height)

        # Create a container widget for better transparency handling
        self.container = QtWidgets.QWidget(self)
        self.container.setGeometry(0, 0, self.cat_width, self.cat_height + self.footer_height)
        self.container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.container.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.container.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Create a background widget for better transparency
        self.background = QtWidgets.QWidget(self.container)
        self.background.setGeometry(0, 0, self.cat_width, self.cat_height + self.footer_height)
        self.background.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.background.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.background.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.background.setStyleSheet("background-color: transparent;")
        self.background.lower()

        # ----------------------
        #   Cat Label (Top)
        # ----------------------
        self.cat_label = QtWidgets.QLabel(self.container)
        self.cat_label.setPixmap(self.idle_pixmap)
        self.cat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cat_label.setGeometry(0, 0, self.cat_width, self.cat_height)
        self.cat_label.setMouseTracking(True)
        self.cat_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.cat_label.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.cat_label.raise_()

        # ----------------------
        #  Footer (Below Cat)
        # ----------------------
        self.footer_widget = QtWidgets.QWidget(self.container)
        self.footer_widget.setGeometry(0, self.cat_height - 60, self.cat_width, self.footer_height)
        self.footer_widget.setMouseTracking(True)
        self.footer_widget.hide()

        # Enhanced footer design
        self.footer_widget.setStyleSheet(f"""
            QWidget {{
                background: rgba(40, 44, 52, {self.footer_alpha * 2.55});
                border-radius: 12px;
                padding: 6px;
            }}
            QLabel {{
                color: white;
                font: 600 13px 'Segoe UI';
                background: transparent;
                padding: 2px 8px;
            }}
            QPushButton {{
                color: white;
                font: 500 12px 'Segoe UI';
                background: rgba(255, 255, 255, 15);
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 25);
            }}
        """)

        # Add subtle shadow to footer
        footer_shadow = QGraphicsDropShadowEffect()
        footer_shadow.setBlurRadius(12)
        footer_shadow.setOffset(0, 2)
        footer_shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        self.footer_widget.setGraphicsEffect(footer_shadow)

        # Footer fade animation
        self.footer_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.footer_widget)
        self.footer_widget.setGraphicsEffect(self.footer_opacity_effect)
        self.footer_animation = QtCore.QPropertyAnimation(self.footer_opacity_effect, b"opacity")
        self.footer_animation.setDuration(300)  # 300 ms fade
        self.footer_animation.finished.connect(self.onFooterAnimationFinished)
        self.footer_opacity_effect.setOpacity(0.0)

        # Always show footer if hidden_footer is False
        if not self.hidden_footer:
            self.footer_widget.show()
            self.footer_opacity_effect.setOpacity(1.0)

        # Layout inside the footer
        footer_layout = QtWidgets.QHBoxLayout(self.footer_widget)
        footer_layout.setContentsMargins(10, 2, 10, 2)  # Increased left/right margins
        footer_layout.setSpacing(20)

        # Label to display input count
        self.count_label = QtWidgets.QLabel(self.footer_widget)
        self.count_label.setText(f"slaps: {self.slaps}")
        self.count_label.setStyleSheet("""
            color: white;
            font: bold 14px;
            background-color: transparent;
            padding: 0px 4px;  /* Add horizontal padding */
        """)
        self.count_label.setMinimumWidth(80)  # Set minimum width
        self.count_label.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Preferred
        )
        footer_layout.addWidget(self.count_label)

        # Spacer
        footer_layout.addStretch()

        # Button to open the .ini file
        self.open_ini_button = QtWidgets.QPushButton("Open Config", self.footer_widget)
        self.open_ini_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(50, 50, 50, 200);
                border: none;
                padding: 5px 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 200);
            }
        """)
        self.open_ini_button.clicked.connect(self.open_ini_file)
        footer_layout.addWidget(self.open_ini_button)

        # Timer for reverting the slap after 100 ms
        self.slapping_timer = QtCore.QTimer()
        self.slapping_timer.setSingleShot(True)
        self.slapping_timer.timeout.connect(self.reset_image)

        # For dragging
        self.drag_position = None

        # Track if mouse is over the cat/footer
        self.is_hovering = False

        # Label for bouncing slap count
        self.slaps_label = QtWidgets.QLabel(self)
        self.slaps_label.setStyleSheet("color: white; font: bold 16px;")
        self.slaps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slaps_label.hide()

        # Track active keys to prevent repeated counts
        self.active_keys = set()

        # Container for multiple slap labels
        self.slap_labels = []

        # Label for total slaps (static when always_show_points is true)
        self.total_slaps_label = QtWidgets.QLabel(self.container)
        self.total_slaps_label.setStyleSheet("""
            color: white;
            font: 600 14px 'Segoe UI';
            background-color: rgba(40, 44, 52, 0.85);
            padding: 4px 12px;
            border-radius: 8px;
        """)
        self.total_slaps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_slaps_label.hide()  # Initially hidden

        # Add a subtle drop shadow effect to the total slaps label
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(8)
        shadow_effect.setOffset(0, 2)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 100))
        self.total_slaps_label.setGraphicsEffect(shadow_effect)

        # Show total slaps immediately if always_show_points is true
        if self.always_show_points:
            self.show_total_slaps()

        # Add combo tracking
        self.combo_count = 0
        self.last_slap_time = 0
        self.combo_timeout = 800  # Changed to 800ms for timeout
        self.combo_label = None
        self.combo_animation_group = None
        self.combo_timeout_timer = QtCore.QTimer()
        self.combo_timeout_timer.setSingleShot(True)
        self.combo_timeout_timer.timeout.connect(self.fade_out_combo)

    # ----------------------
    #  Fix Tilted Images
    # ----------------------
    def load_and_fix_image(self, path):
        """Loads an image and rotates it back -16 degrees to fix tilt."""
        try:
            pixmap = QtGui.QPixmap(resource_path(path))
            if pixmap.isNull():
                raise Exception(f"Failed to load image: {path}")
            transform = QtGui.QTransform()
            transform.rotate(-13)  # Counteract tilt
            return pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            # Create a fallback colored rectangle
            fallback = QtGui.QPixmap(100, 100)
            fallback.fill(QtGui.QColor(255, 0, 0))  # Red to indicate error
            return fallback

    # ----------------------
    #  Slap Logic
    # ----------------------
    def do_slap(self):
        """Handles slapping animation and input counting."""
        if self.is_paused:
            return
            
        self.slaps += 1
        
        # Update combo count and reset timeout
        current_time = QtCore.QTime.currentTime().msecsSinceStartOfDay()
        if current_time - self.last_slap_time < self.combo_timeout:
            self.combo_count += 1
        else:
            self.combo_count = 1
        self.last_slap_time = current_time
        
        # Reset the timeout timer
        self.combo_timeout_timer.stop()
        self.combo_timeout_timer.start(self.combo_timeout)
        
        self.save_config()
        self.count_label.setText(f"slaps: {self.slaps}")
        self.count_label.adjustSize()

        # Always update total slaps if enabled
        if self.always_show_points:
            self.show_total_slaps()
            
        # Show floating points if enabled (can work together with always_show_points)
        if self.floating_points:
            self.show_bouncing_slaps()

        # Alternate the cat's paws
        if self.current_side == "left":
            self.cat_label.setPixmap(self.slap_pixmap_left)
            self.current_side = "right"
        else:
            self.cat_label.setPixmap(self.slap_pixmap_right)
            self.current_side = "left"

        # Restart the slapping timer (100 ms)
        if self.slapping_timer.isActive():
            self.slapping_timer.stop()
        self.slapping_timer.start(100)

    def reset_image(self):
        """Revert to idle image after 100 ms."""
        self.cat_label.setPixmap(self.idle_pixmap)

    def show_total_slaps(self):
        """Display the total slaps statically."""
        self.total_slaps_label.setText(str(self.slaps))
        # Ensure the label is wide enough for the text
        self.total_slaps_label.adjustSize()
        width = max(50, self.total_slaps_label.width())  # Min width of 50px
        self.total_slaps_label.setFixedWidth(width)
        # Position in top-right corner with padding
        x = self.cat_width - width - 10  # 10px padding from right
        y = 10  # 10px from top
        self.total_slaps_label.move(x, y)
        self.total_slaps_label.show()
        self.total_slaps_label.raise_()

    def show_bouncing_slaps(self):
        """Animate a bouncing +1 that merges into a combo counter."""
        if not self.floating_points:
            return

        # Create the +1 label
        slap_label = QtWidgets.QLabel(self.container)
        slap_label.setStyleSheet("""
            color: white;
            font: 500 13px 'Segoe UI';
            background: rgba(40, 44, 52, 0.6);
            padding: 2px 4px;
            border-radius: 4px;
        """)
        slap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slap_label.setText("+1")
        slap_label.adjustSize()
        
        # Position the label with slight randomization
        x = (self.cat_width - slap_label.width()) // 2
        x += random.randint(-15, 15)
        y = self.cat_height // 2 + 10
        slap_label.move(x, y)
        slap_label.show()
        slap_label.raise_()

        # Create rise animation for +1
        rise_animation = QtCore.QPropertyAnimation(slap_label, b"pos")
        rise_animation.setDuration(400)
        rise_animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        rise_animation.setStartValue(slap_label.pos())
        
        # If we have an active combo, move towards it
        if self.combo_count > 1 and self.combo_label:
            target_pos = self.combo_label.pos()
        else:
            target_pos = QtCore.QPoint(x, y - 40)
        
        rise_animation.setEndValue(target_pos)

        # Create fade animation
        fade_effect = QtWidgets.QGraphicsOpacityEffect(slap_label)
        slap_label.setGraphicsEffect(fade_effect)
        fade_animation = QtCore.QPropertyAnimation(fade_effect, b"opacity")
        fade_animation.setDuration(400)
        fade_animation.setStartValue(1.0)
        fade_animation.setEndValue(0.0 if self.combo_count > 1 else 0.8)
        
        # Group animations
        animation_group = QtCore.QParallelAnimationGroup()
        animation_group.addAnimation(rise_animation)
        animation_group.addAnimation(fade_animation)
        
        # Handle combo display
        if self.combo_count > 1:
            animation_group.finished.connect(lambda: self.show_combo_pop(slap_label))
        else:
            animation_group.finished.connect(lambda: self.cleanup_slap_label(slap_label))
        
        animation_group.start()
        self.slap_labels.append((slap_label, animation_group))

    def show_combo_pop(self, slap_label):
        """Show or update the combo counter with a pop effect."""
        self.cleanup_slap_label(slap_label)
        
        # Don't show combo label if combo count is 0
        if self.combo_count <= 0:
            if self.combo_label:
                self.cleanup_combo()
            return
        
        # Create or update combo label
        if not self.combo_label:
            self.combo_label = QtWidgets.QLabel(self.container)
            self.combo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.combo_label.show()
            self.combo_label.raise_()
        
        # Style based on combo size
        font_size = min(13 + (self.combo_count // 3), 18)  # Smaller base size, slower growth
        opacity = min(0.85, 0.6 + (self.combo_count * 0.02))  # Start more transparent, increase slower
        self.combo_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.95);
            font: 500 {font_size}px 'Segoe UI';
            background: rgba(40, 44, 52, {opacity});
            padding: 1px 4px;
            border-radius: 3px;
        """)
        
        # Set text and adjust size
        self.combo_label.setText(f"+{self.combo_count}")
        self.combo_label.adjustSize()
        
        # Position in top-right corner of the cat, below total points if visible
        x = self.cat_width - self.combo_label.width() - 10  # 10px padding from right
        y = 10  # Default y position
        
        # If total points label is visible, position combo below it
        if self.always_show_points and self.total_slaps_label.isVisible():
            y = self.total_slaps_label.y() + self.total_slaps_label.height() + 5
        
        self.combo_label.move(x, y)
        
        # Stop existing animations if any
        if self.combo_animation_group:
            self.combo_animation_group.stop()
        
        # Create transform for pop effect
        transform_animation = QtCore.QPropertyAnimation(self.combo_label, b"geometry")
        transform_animation.setDuration(100)  # Faster animation
        
        # Calculate geometries for the pop effect
        current_geometry = self.combo_label.geometry()
        expanded_width = int(current_geometry.width() * 1.15)  # Smaller expansion
        expanded_height = int(current_geometry.height() * 1.15)
        x_offset = (expanded_width - current_geometry.width()) // 2
        y_offset = (expanded_height - current_geometry.height()) // 2
        
        expanded_geometry = QtCore.QRect(
            current_geometry.x() - x_offset,
            current_geometry.y() - y_offset,
            expanded_width,
            expanded_height
        )
        
        transform_animation.setStartValue(expanded_geometry)
        transform_animation.setEndValue(current_geometry)
        transform_animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)  # Smoother curve
        
        # Group animation
        self.combo_animation_group = QtCore.QParallelAnimationGroup()
        self.combo_animation_group.addAnimation(transform_animation)
        self.combo_animation_group.start()
        
        # Reset and start the timeout timer
        self.combo_timeout_timer.stop()
        self.combo_timeout_timer.start(self.combo_timeout)  # Start with the timeout duration

    def fade_out_combo(self):
        """Reset combo and hide label after timeout."""
        # Reset combo count
        self.combo_count = 0
        
        # Clean up the label immediately
        if self.combo_label:
            self.combo_label.hide()
            self.combo_label.deleteLater()
            self.combo_label = None
            
        if self.combo_animation_group:
            self.combo_animation_group.stop()
            self.combo_animation_group = None

    def cleanup_combo(self):
        """Clean up the combo label and animations."""
        if self.combo_label:
            self.combo_label.hide()
            self.combo_label.deleteLater()
            self.combo_label = None
            
        if self.combo_animation_group:
            self.combo_animation_group.stop()
            self.combo_animation_group = None

    def cleanup_slap_label(self, slap_label):
        """Remove slap label after animation finishes."""
        slap_label.hide()
        slap_label.deleteLater()
        self.slap_labels = [(label, anim) for label, anim in self.slap_labels if label != slap_label]

    def open_ini_file(self):
        """Open the .ini file in the default editor."""
        config_path = resource_path("bongo.ini")
        if os.path.exists(config_path):
            os.startfile(config_path)

    # ----------------------
    #  Footer Fading
    # ----------------------
    def fade_footer(self, fade_in: bool):
        """Fade the footer in or out."""
        if not self.hidden_footer:
            return  # Skip fading if footer is always visible

        if fade_in and not self.is_hovering:
            return

        if not self.footer_opacity_effect:
            return

        self.footer_animation.stop()
        start_value = self.footer_opacity_effect.opacity()
        end_value = 1.0 if fade_in else 0.0

        if fade_in:
            self.footer_widget.show()
        self.footer_animation.setStartValue(start_value)
        self.footer_animation.setEndValue(end_value)
        self.footer_animation.start()

    def onFooterAnimationFinished(self):
        """Hide footer after fade out completes."""
        if self.footer_opacity_effect and self.footer_opacity_effect.opacity() == 0.0:
            self.footer_widget.hide()

    # ----------------------
    #  Mouse / Window
    # ----------------------
    def mousePressEvent(self, event):
        """Allow dragging when clicking on the cat or footer."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.footer_widget.geometry().contains(event.pos()) or self.cat_label.geometry().contains(event.pos()):
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                # Add visual feedback
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                # Store the original opacity
                self.original_opacity = self.footer_opacity_effect.opacity()
                # Add subtle shadow effect while dragging
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(20)
                shadow.setOffset(0, 0)
                shadow.setColor(QtGui.QColor(0, 0, 0, 100))
                self.footer_widget.setGraphicsEffect(shadow)
                event.accept()

    def mouseMoveEvent(self, event):
        """Drag window & handle footer fade logic."""
        if self.drag_position and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Reset visual effects after dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            # Create a new opacity effect
            self.footer_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.footer_widget)
            self.footer_widget.setGraphicsEffect(self.footer_opacity_effect)
            # Update the animation target
            self.footer_animation.setTargetObject(self.footer_opacity_effect)
            self.footer_animation.setPropertyName(b"opacity")
            
            # Set initial opacity based on hover state
            if not self.is_hovering and self.hidden_footer:
                self.footer_opacity_effect.setOpacity(0.0)
                self.footer_widget.hide()
            elif hasattr(self, 'original_opacity'):
                self.footer_opacity_effect.setOpacity(self.original_opacity)
            
            event.accept()

    def enterEvent(self, event):
        """Detect hover over the cat or footer."""
        self.is_hovering = True
        self.fade_footer(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Detect when mouse exits both cat and footer."""
        self.is_hovering = False
        QtCore.QTimer.singleShot(200, self.check_hover)
        super().leaveEvent(event)

    def check_hover(self):
        """Delays hiding the footer in case of quick mouse movements."""
        if not self.is_hovering:
            self.fade_footer(False)

    # ----------------------
    #  Config Management
    # ----------------------
    def load_config(self):
        """Load or initialize the configuration file."""
        self.config = configparser.ConfigParser()
        config_path = resource_path("bongo.ini")

        # Default configuration
        default_config = {
            "Settings": {
                "slaps": "0",
                "hidden_footer": "true",
                "footer_alpha": "50",
                "always_show_points": "false",
                "floating_points": "true",
                "startup_with_windows": "false",
                "max_slaps": "0"  # 0 means unlimited
            }
        }

        def safe_getboolean(section, key, default=False):
            """Safely get a boolean value from config."""
            try:
                value = self.config.get(section, key, fallback=str(default)).lower()
                return value in ('true', '1', 'yes', 'on')
            except:
                return default

        def safe_getint(section, key, default=0):
            """Safely get an integer value from config."""
            try:
                return int(self.config.get(section, key, fallback=str(default)))
            except:
                return default

        if not os.path.exists(config_path):
            self.config.read_dict(default_config)
            try:
                with open(config_path, "w") as config_file:
                    self.config.write(config_file)
            except Exception as e:
                print(f"Error creating config file: {e}")
                self.config.read_dict(default_config)
        else:
            try:
                self.config.read(config_path)
                # Validate and update config with any new settings
                for section, values in default_config.items():
                    if section not in self.config:
                        self.config[section] = {}
                    for key, value in values.items():
                        if key not in self.config[section]:
                            self.config[section][key] = value
                # Save updated config
                with open(config_path, "w") as config_file:
                    self.config.write(config_file)
            except Exception as e:
                print(f"Error reading config file: {e}")
                self.config.read_dict(default_config)

        # Load settings with validation
        try:
            self.slaps = max(0, safe_getint("Settings", "slaps"))
            self.hidden_footer = safe_getboolean("Settings", "hidden_footer", True)
            self.footer_alpha = max(0, min(100, safe_getint("Settings", "footer_alpha", 50)))
            self.always_show_points = safe_getboolean("Settings", "always_show_points", False)
            self.floating_points = safe_getboolean("Settings", "floating_points", True)
            self.startup_with_windows = safe_getboolean("Settings", "startup_with_windows", False)
            self.max_slaps = max(0, safe_getint("Settings", "max_slaps"))
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Reset to defaults if there's an error
            self.slaps = 0
            self.hidden_footer = True
            self.footer_alpha = 50
            self.always_show_points = False
            self.floating_points = True
            self.startup_with_windows = False
            self.max_slaps = 0

    def save_config(self):
        """Save the current configuration to the file."""
        config_path = resource_path("bongo.ini")
        try:
            self.config["Settings"]["slaps"] = str(self.slaps)
            self.config["Settings"]["hidden_footer"] = str(self.hidden_footer).lower()
            self.config["Settings"]["footer_alpha"] = str(self.footer_alpha)
            self.config["Settings"]["always_show_points"] = str(self.always_show_points).lower()
            self.config["Settings"]["floating_points"] = str(self.floating_points).lower()
            self.config["Settings"]["startup_with_windows"] = str(self.startup_with_windows).lower()
            self.config["Settings"]["max_slaps"] = str(self.max_slaps)
            
            with open(config_path, "w") as config_file:
                self.config.write(config_file)
        except Exception as e:
            print(f"Error saving config: {e}")

    # ----------------------
    #  System Tray
    # ----------------------
    def setup_system_tray(self):
        """Setup the system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(resource_path("img/cat-rest.png")))
        self.tray_icon.setToolTip("Bongo Cat")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide action
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)
        
        # Pause/Resume action
        self.pause_action = QAction("Pause", self)
        self.pause_action.triggered.connect(self.toggle_pause)
        tray_menu.addAction(self.pause_action)
        
        # Reset count action
        reset_action = QAction("Reset Count", self)
        reset_action.triggered.connect(self.reset_count)
        tray_menu.addAction(reset_action)
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_context_menu(self):
        """Setup the context menu for the main window."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Show the context menu at the specified position."""
        menu = QMenu()
        
        # Show/Hide action
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_visibility)
        menu.addAction(show_action)
        
        # Pause/Resume action
        pause_action = QAction("Pause" if not self.is_paused else "Resume", self)
        pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(pause_action)
        
        # Reset count action
        reset_action = QAction("Reset Count", self)
        reset_action.triggered.connect(self.reset_count)
        menu.addAction(reset_action)
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        menu.addAction(quit_action)
        
        menu.exec_(self.mapToGlobal(position))

    def toggle_visibility(self):
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

    def toggle_pause(self):
        """Toggle pause state."""
        self.is_paused = not self.is_paused
        self.pause_action.setText("Resume" if self.is_paused else "Pause")
        self.tray_icon.setToolTip("Bongo Cat (Paused)" if self.is_paused else "Bongo Cat")

    def reset_count(self):
        """Reset the slap count."""
        self.slaps = 0
        self.save_config()
        self.count_label.setText(f"slaps: {self.slaps}")
        if self.always_show_points:
            self.show_total_slaps()

    def restore_window_position(self):
        """Restore the window position from settings."""
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)

    def closeEvent(self, event):
        """Handle window close event."""
        # Save window position
        self.settings.setValue('geometry', self.saveGeometry())
        # Hide instead of quit
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Bongo Cat",
            "Bongo Cat is still running in the system tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

# ----------------------
#  Global Listeners
# ----------------------
def start_listeners(trigger_callback):
    """Start global listeners for keyboard and mouse."""
    active_keys = set()

    def on_press(key):
        if key not in active_keys:
            active_keys.add(key)
            trigger_callback()

    def on_release(key):
        if key in active_keys:
            active_keys.remove(key)

    def on_click(x, y, button, pressed):
        if pressed:
            trigger_callback()

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    mouse_listener = mouse.Listener(on_click=lambda x, y, button, pressed: trigger_callback() if pressed else None)
    mouse_listener.start()

    keyboard_listener.join()
    mouse_listener.join()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = BongoCatWindow()
    window.show()

    listener_thread = threading.Thread(
        target=start_listeners,
        args=(window.trigger_slap.emit,),
        daemon=True
    )
    listener_thread.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()