"""Main application window for Bongo Cat."""

import os
import sys
import subprocess
import random
import math
import logging
from typing import Optional

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QSettings, Qt

from ..models import ConfigManager
from ..utils import resource_path
from .settings_panel import SettingsPanelWidget

logger = logging.getLogger("BongoCat")


class BongoCatWindow(QtWidgets.QWidget):
    """Main Bongo Cat application window.
    
    A frameless, always-on-top desktop pet that responds to keyboard,
    mouse, and controller inputs with animated slapping motions.
    
    Attributes:
        trigger_slap: Signal emitted when input is detected
        config: Configuration manager instance
        is_paused: Whether animations are paused
        is_hovering: Whether mouse is over the window
        drag_position: Position for window dragging
        current_side: Current paw side ("left" or "right")
    """
    
    trigger_slap = QtCore.pyqtSignal()

    def __init__(self):
        """Initialize the Bongo Cat window."""
        super().__init__()
        self.trigger_slap.connect(self.do_slap)
        
        # Load configuration
        self.config = ConfigManager()
        
        # Initialize state variables
        self.is_paused = False
        self.is_hovering = False
        self.drag_position = None
        self.current_side = "left"
        
        # Setup window and UI
        self.setup_window()
        self.setup_ui()
        self.setup_animations()
        self.setup_system_tray()
        self.setup_context_menu()
        self.setup_settings_panel()
        self.restore_window_position()
        
        # Show total slaps at startup if enabled
        if self.config.always_show_points:
            self.show_total_slaps()
        
        logger.info("BongoCatWindow initialized")

    # ----------------------
    #  Window Setup
    # ----------------------
    def setup_window(self):
        """Initialize window properties and flags."""
        self.setWindowTitle("Bongo Cat")
        self.settings = QSettings('BongoCat', 'BongoCat')

        flags = Qt.WindowFlags()
        flags |= Qt.WindowType.FramelessWindowHint
        flags |= Qt.WindowType.WindowStaysOnTopHint
        flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setMouseTracking(True)
        
        # Ensure the window is tall enough to show the settings panel
        self.min_height_with_settings = 450

    def setup_ui(self):
        """Initialize UI components."""
        self.setup_cat_images()
        self.setup_main_container()
        self.setup_cat_label()
        self.setup_footer()
        self.setup_combo_counter()
        self.setup_total_slaps_label()

    def setup_cat_images(self):
        """Load and prepare cat images."""
        self.idle_pixmap_original = self.load_and_fix_image(resource_path("img/cat-rest.png"))
        self.slap_pixmap_left_original = self.load_and_fix_image(resource_path("img/cat-left.png"))
        self.slap_pixmap_right_original = self.load_and_fix_image(resource_path("img/cat-right.png"))
        
        # Working copies that will be stretched
        self.idle_pixmap = QtGui.QPixmap(self.idle_pixmap_original)
        self.slap_pixmap_left = QtGui.QPixmap(self.slap_pixmap_left_original)
        self.slap_pixmap_right = QtGui.QPixmap(self.slap_pixmap_right_original)

        self.cat_width = self.idle_pixmap.width()
        self.cat_height = self.idle_pixmap.height()
        self.footer_height = 35
        self.setFixedSize(self.cat_width, self.cat_height + self.footer_height)

    def setup_main_container(self):
        """Setup the main container widget."""
        self.container = QtWidgets.QWidget(self)
        self.container.setGeometry(0, 0, self.cat_width, self.cat_height + self.footer_height)
        self.container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.container.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.container.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self.background = QtWidgets.QWidget(self.container)
        self.background.setGeometry(0, 0, self.cat_width, self.cat_height + self.footer_height)
        self.background.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.background.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.background.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.background.setStyleSheet("background-color: transparent;")
        self.background.lower()

    def setup_cat_label(self):
        """Setup the cat label."""
        self.cat_label = QtWidgets.QLabel(self.container)
        self.cat_label.setPixmap(self.idle_pixmap)
        self.cat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cat_label.setGeometry(0, 0, self.cat_width, self.cat_height)
        self.cat_label.setMouseTracking(True)
        self.cat_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.cat_label.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.cat_label.raise_()

        # Setup variables for idle animation
        self.current_image = "idle"  # Can be "idle", "left", or "right"
        self.max_stretch = 1.08  # 8% taller at maximum
        self.min_stretch = 0.98   # 2% shorter at minimum
        self.animation_time = 0   # Position in the sine wave
        self.stretch_factor = 1.0
        
        # Set up a timer for the idle animation at 60fps for smoother animation
        self.idle_timer = QtCore.QTimer(self)
        self.idle_timer.timeout.connect(self.update_idle_stretch)
        self.idle_timer.start(16)  # ~60 fps

    def update_idle_stretch(self):
        """Update the cat's stretch animation frame with smooth transitions."""
        if self.is_paused:
            return
            
        # Use sine wave for smoother animation
        angle = (self.animation_time if hasattr(self, 'animation_time') else 0) + 0.05
        self.animation_time = angle % (2 * math.pi)
        
        # Smoother sine wave oscillation
        wave = (math.sin(self.animation_time) + 1) / 2  # Range 0-1
        
        # Calculate stretch factor from wave with narrower range to reduce jitter
        self.stretch_factor = self.min_stretch + wave * (self.max_stretch - self.min_stretch)
        
        # Update the current image with the new stretch factor
        self.update_stretched_image()
    
    def update_stretched_image(self):
        """Apply the current stretch factor to the current image."""
        # Determine which source image to use
        if self.current_image == "idle":
            source_pixmap = self.idle_pixmap_original
        elif self.current_image == "left":
            source_pixmap = self.slap_pixmap_left_original
        elif self.current_image == "right":
            source_pixmap = self.slap_pixmap_right_original
        else:
            source_pixmap = self.idle_pixmap_original
        
        # Get original dimensions
        original_width = source_pixmap.width()
        original_height = source_pixmap.height()
        
        # Define fixed bottom percentage
        fixed_bottom_percent = 0.25
        fixed_bottom_height = int(original_height * fixed_bottom_percent)
        stretchable_height = original_height - fixed_bottom_height
        
        # Calculate stretched dimensions for top part
        stretched_top_height = int(stretchable_height * self.stretch_factor)
        
        # Create a new pixmap with the same dimensions as original
        new_pixmap = QtGui.QPixmap(original_width, original_height)
        new_pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        
        # Convert to QImage for direct pixel access
        original_image = source_pixmap.toImage()
        
        # Handle inversion if enabled
        if self.config.invert_cat:
            original_image = original_image.mirrored(horizontal=True, vertical=False)
        
        # Create painter
        painter = QtGui.QPainter(new_pixmap)
        
        # First draw the stretched top part
        top_source = original_image.copy(
            0, 0,
            original_width, stretchable_height
        )
        
        # Scale the top part
        scaled_top = top_source.scaled(
            original_width, stretched_top_height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Calculate where to draw the stretched top part
        top_y_position = stretchable_height - stretched_top_height
        
        # Draw the stretched top at the calculated position
        painter.drawImage(0, top_y_position, scaled_top)
        
        # Draw the fixed bottom part at its original position
        bottom_source = original_image.copy(
            0, stretchable_height, 
            original_width, fixed_bottom_height
        )
        
        # Draw the bottom part at its fixed position - always at the bottom
        painter.drawImage(0, stretchable_height, bottom_source)
        
        painter.end()
        
        # Update the appropriate pixmap based on current_image
        if self.current_image == "idle":
            self.idle_pixmap = new_pixmap
        elif self.current_image == "left":
            self.slap_pixmap_left = new_pixmap
        elif self.current_image == "right":
            self.slap_pixmap_right = new_pixmap
            
        # Update the cat label
        self.cat_label.setPixmap(new_pixmap)

    def setup_footer(self):
        """Setup the footer widget."""
        self.footer_widget = QtWidgets.QWidget(self.container)
        self.footer_widget.setGeometry(0, self.cat_height - 60, self.cat_width, self.footer_height)
        self.footer_widget.setMouseTracking(True)
        self.footer_widget.hide()

        self.setup_footer_style()
        self.setup_footer_layout()
        self.setup_footer_animation()

    def setup_footer_style(self):
        """Setup footer styling."""
        self.footer_widget.setStyleSheet(f"""
            QWidget {{
                background: rgba(40, 44, 52, {self.config.footer_alpha * 2.55});
                border-radius: 12px;
                padding: 4px;
            }}
            QLabel {{
                color: white;
                font: 600 13px 'Segoe UI';
                background: transparent;
                padding: 1px 4px;
            }}
            QPushButton {{
                color: white;
                font: 500 12px 'Segoe UI';
                background: rgba(255, 255, 255, 15);
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 25);
            }}
        """)

        footer_shadow = QGraphicsDropShadowEffect()
        footer_shadow.setBlurRadius(12)
        footer_shadow.setOffset(0, 2)
        footer_shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        self.footer_widget.setGraphicsEffect(footer_shadow)

    def setup_footer_layout(self):
        """Setup footer layout and components."""
        footer_layout = QtWidgets.QHBoxLayout(self.footer_widget)
        footer_layout.setContentsMargins(8, 2, 8, 2)
        footer_layout.setSpacing(6)  # Reduce spacing between elements

        # Use a shorter label format
        self.count_label = QtWidgets.QLabel(self.footer_widget)
        self.count_label.setText(f"{self.config.slaps}")
        self.count_label.setStyleSheet("""
            color: white;
            font: bold 14px;
            background-color: transparent;
            padding: 0px 2px;
        """)
        self.count_label.setMinimumWidth(40)
        
        # Add a tiny counter icon using Unicode
        slap_icon_label = QtWidgets.QLabel("✋")
        slap_icon_label.setStyleSheet("background: transparent; font-size: 14px;")
        
        # Create a small horizontal layout for the counter
        counter_layout = QtWidgets.QHBoxLayout()
        counter_layout.setSpacing(2)
        counter_layout.addWidget(slap_icon_label)
        counter_layout.addWidget(self.count_label)
        
        footer_layout.addLayout(counter_layout)
        footer_layout.addStretch()

        # Use more compact buttons
        self.settings_button = QtWidgets.QPushButton("⚙ Settings", self.footer_widget)
        self.settings_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(50, 50, 50, 200);
                border: none;
                padding: 3px 6px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 200);
            }
        """)
        self.settings_button.setFixedWidth(70)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        footer_layout.addWidget(self.settings_button)

        # Use an icon button for config
        self.open_ini_button = QtWidgets.QPushButton("📄", self.footer_widget)
        self.open_ini_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(50, 50, 50, 200);
                border: none;
                padding: 3px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 200);
            }
        """)
        self.open_ini_button.setFixedWidth(24)
        self.open_ini_button.setToolTip("Open Config File")
        self.open_ini_button.clicked.connect(self.open_ini_file)
        footer_layout.addWidget(self.open_ini_button)

    def setup_footer_animation(self):
        """Setup footer fade animation."""
        self.footer_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.footer_widget)
        self.footer_widget.setGraphicsEffect(self.footer_opacity_effect)
        self.footer_animation = QtCore.QPropertyAnimation(self.footer_opacity_effect, b"opacity")
        self.footer_animation.setDuration(300)
        self.footer_animation.finished.connect(self.onFooterAnimationFinished)
        self.footer_opacity_effect.setOpacity(0.0)

    def setup_combo_counter(self):
        """Initialize combo counter variables."""
        self.combo_count = 0
        self.last_slap_time = 0
        self.combo_timeout = 800
        self.combo_label: Optional[QtWidgets.QLabel] = None
        self.combo_animation_group: Optional[QtCore.QParallelAnimationGroup] = None
        self.combo_timeout_timer = QtCore.QTimer()
        self.combo_timeout_timer.setSingleShot(True)
        self.combo_timeout_timer.timeout.connect(self.fade_out_combo)

    def setup_total_slaps_label(self):
        """Setup the total slaps label."""
        self.total_slaps_label = QtWidgets.QLabel(self.container)
        self.total_slaps_label.setStyleSheet("""
            color: white;
            font: 600 14px 'Segoe UI';
            background-color: rgba(40, 44, 52, 0.85);
            padding: 4px 12px;
            border-radius: 8px;
        """)
        self.total_slaps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_slaps_label.hide()

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(8)
        shadow_effect.setOffset(0, 2)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 100))
        self.total_slaps_label.setGraphicsEffect(shadow_effect)

    def setup_animations(self):
        """Setup animation timers."""
        logger.info("Setting up animation timers")
        self.slapping_timer = QtCore.QTimer()
        self.slapping_timer.setSingleShot(True)
        self.slapping_timer.timeout.connect(self.reset_image)
        self.slap_labels = []
        logger.info("Animation setup complete")

    # ----------------------
    #  Image Handling
    # ----------------------
    def load_and_fix_image(self, path):
        """Loads an image and rotates it back -16 degrees to fix tilt."""
        try:
            pixmap = QtGui.QPixmap(resource_path(path))
            if pixmap.isNull():
                raise FileNotFoundError(f"Failed to load image: {path}")
            transform = QtGui.QTransform()
            transform.rotate(-13)
            return pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        except (FileNotFoundError, Exception) as e:
            logger.error(f"Error loading image {path}: {e}")
            fallback = QtGui.QPixmap(100, 100)
            fallback.fill(QtGui.QColor(255, 0, 0))
            return fallback

    # ----------------------
    #  Animation Methods
    # ----------------------
    def show_combo_pop(self, slap_label):
        """Show or update the combo counter with a pop effect."""
        self.cleanup_slap_label(slap_label)
        
        if self.combo_count <= 0:
            if self.combo_label:
                self.cleanup_combo()
            return
        
        if not self.combo_label:
            self.combo_label = QtWidgets.QLabel(self.container)
            self.combo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.combo_label.show()
            self.combo_label.raise_()
        
        self.update_combo_style()
        self.setup_combo_animations()
        
        # Reset and start the timeout timer
        self.combo_timeout_timer.stop()
        self.combo_timeout_timer.start(self.combo_timeout)

    def update_combo_style(self):
        """Update the combo counter style based on count."""
        if not self.combo_label:
            return
            
        font_size = min(14 + (self.combo_count // 3), 20)
        
        # Determine color based on combo count
        if self.combo_count < 30:
            color = "255, 255, 100"  # Yellow
        elif self.combo_count < 60:
            color = "255, 150, 50"   # Orange
        else:
            color = "255, 50, 50"    # Red
        
        self.original_color = color
        
        # Create a drop shadow effect for better visibility without background
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)
        shadow.setOffset(0, 0)
        shadow.setColor(QtGui.QColor(0, 0, 0, 200))
        self.combo_label.setGraphicsEffect(shadow)
        
        # Use transparent background with text-shadow for better visibility
        self.combo_label.setStyleSheet(f"""
            QLabel {{
                color: rgba({color}, 0.95);
                font: 700 {font_size}px 'Segoe UI';
                background-color: transparent;
                padding: 4px 10px;
                border: none;
            }}
        """)
        
        self.combo_label.setText(f"+{self.combo_count}")
        self.combo_label.adjustSize()
        
    def setup_combo_animations(self):
        """Setup animations for the combo counter."""
        if not self.combo_label:
            return
            
        x = self.cat_width - self.combo_label.width() - 10
        y = 10
        
        if self.config.always_show_points and self.total_slaps_label.isVisible():
            y = self.total_slaps_label.y() + self.total_slaps_label.height() + 5
        
        self.combo_label.move(x, y)
        
        if self.combo_animation_group:
            self.combo_animation_group.stop()
            self.combo_animation_group = None
        
        self.combo_animation_group = QtCore.QParallelAnimationGroup()
        
        # Initial pop effect
        current_geometry = self.combo_label.geometry()
        expanded_width = int(current_geometry.width() * 1.2)
        expanded_height = int(current_geometry.height() * 1.2)
        x_offset = (expanded_width - current_geometry.width()) // 2
        y_offset = (expanded_height - current_geometry.height()) // 2
        
        expanded_geometry = QtCore.QRect(
            current_geometry.x() - x_offset,
            current_geometry.y() - y_offset,
            expanded_width,
            expanded_height
        )
        
        pop_animation = QtCore.QPropertyAnimation(self.combo_label, b"geometry")
        pop_animation.setDuration(150)
        pop_animation.setStartValue(expanded_geometry)
        pop_animation.setEndValue(current_geometry)
        pop_animation.setEasingCurve(QtCore.QEasingCurve.OutBack)
        
        bounce_animation = QtCore.QPropertyAnimation(self.combo_label, b"pos")
        bounce_animation.setDuration(150)
        bounce_animation.setStartValue(QtCore.QPoint(x, y + 5))
        bounce_animation.setEndValue(QtCore.QPoint(x, y))
        bounce_animation.setEasingCurve(QtCore.QEasingCurve.OutBack)
        
        self.combo_animation_group.addAnimation(pop_animation)
        self.combo_animation_group.addAnimation(bounce_animation)
        
        if self.combo_count >= 60:
            self.setup_overload_animation(x, y)
        
        self.combo_animation_group.start()
        
    def setup_overload_animation(self, x: int, y: int):
        """Setup the overload animation for high combos."""
        if not self.combo_label:
            return
            
        self.combo_original_pos = QtCore.QPoint(x, y)
        self.combo_original_size = QtCore.QSize(self.combo_label.width(), self.combo_label.height())
        
        if not hasattr(self, 'overload_timer'):
            self.overload_timer = QtCore.QTimer()
            self.overload_timer.timeout.connect(self.update_overload_animation)
        else:
            self.overload_timer.stop()
        
        self.animation_time = 0
        self.pulse_direction = 1
        self.overload_timer.start(33)

    def update_overload_animation(self):
        """Update the overload animation effect for high combos."""
        if not self.combo_label or self.combo_count < 60:
            if hasattr(self, 'overload_timer'):
                self.overload_timer.stop()
            return
        
        self.animation_time += 0.08 * self.pulse_direction
        if self.animation_time >= 1.0:
            self.animation_time = 1.0
            self.pulse_direction = -1
        elif self.animation_time <= 0.0:
            self.animation_time = 0.0
            self.pulse_direction = 1
        
        wave = (math.sin(self.animation_time * math.pi) + 1) / 2
        self.update_overload_effects(wave)

    def update_overload_effects(self, wave: float):
        """Update visual effects for overload animation."""
        if not self.combo_label:
            return
            
        scale_factor = 0.9 + wave * 0.3
        new_width = int(self.combo_original_size.width() * scale_factor)
        new_height = int(self.combo_original_size.height() * scale_factor)
        
        x_offset = (new_width - self.combo_original_size.width()) // 2
        y_offset = (new_height - self.combo_original_size.height()) // 2
        
        wobble_x = int(math.sin(self.animation_time * 3 * math.pi) * 8)
        wobble_y = int(math.cos(self.animation_time * 2 * math.pi) * 5)
        
        shake_amount = 0
        if wave > 0.8 or wave < 0.2:
            shake_amount = random.randint(-2, 2)
        
        new_x = self.combo_original_pos.x() - x_offset + wobble_x + shake_amount
        new_y = self.combo_original_pos.y() - y_offset + wobble_y + shake_amount
        
        self.combo_label.setGeometry(new_x, new_y, new_width, new_height)
        
        # Parse color components
        r, g, b = map(int, self.original_color.split(','))
        intensity = 0.6 + wave * 0.9
        r_new = min(255, int(r * intensity))
        g_new = min(255, int(g * intensity))
        b_new = min(255, int(b * intensity))
        
        # Shadow gets darker with pulse
        shadow_intensity = int(100 + wave * 100)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4 + wave * 3)
        shadow.setOffset(0, 0)
        shadow.setColor(QtGui.QColor(0, 0, 0, shadow_intensity))
        self.combo_label.setGraphicsEffect(shadow)
        
        font_size = min(14 + (self.combo_count // 3), 20)
        
        self.combo_label.setStyleSheet(f"""
            QLabel {{
                color: rgba({r_new}, {g_new}, {b_new}, 0.95);
                font: 700 {font_size}px 'Segoe UI';
                background-color: transparent;
                padding: 4px 10px;
                border: none;
            }}
        """)

    def fade_out_combo(self):
        """Reset combo and fade out the label with animation."""
        if not self.combo_label:
            return
            
        self.combo_count = 0
        
        if hasattr(self, 'overload_timer') and self.overload_timer.isActive():
            self.overload_timer.stop()
            
        if self.combo_animation_group:
            self.combo_animation_group.stop()
        
        self.combo_animation_group = QtCore.QParallelAnimationGroup()
        
        fade_effect = QtWidgets.QGraphicsOpacityEffect(self.combo_label)
        self.combo_label.setGraphicsEffect(fade_effect)
        fade_effect.setOpacity(1.0)
        
        fade_animation = QtCore.QPropertyAnimation(fade_effect, b"opacity")
        fade_animation.setDuration(300)
        fade_animation.setStartValue(1.0)
        fade_animation.setEndValue(0.0)
        fade_animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        
        current_geometry = self.combo_label.geometry()
        scale_animation = QtCore.QPropertyAnimation(self.combo_label, b"geometry")
        scale_animation.setDuration(300)
        scale_animation.setStartValue(current_geometry)
        
        target_width = int(current_geometry.width() * 0.8)
        target_height = int(current_geometry.height() * 0.8)
        x_offset = (current_geometry.width() - target_width) // 2
        y_offset = (current_geometry.height() - target_height) // 2
        
        target_geometry = QtCore.QRect(
            current_geometry.x() + x_offset,
            current_geometry.y() + y_offset,
            target_width,
            target_height
        )
        
        scale_animation.setEndValue(target_geometry)
        scale_animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        
        self.combo_animation_group.addAnimation(fade_animation)
        self.combo_animation_group.addAnimation(scale_animation)
        
        self.combo_animation_group.finished.connect(self.cleanup_combo)
        self.combo_animation_group.start()

    def cleanup_combo(self):
        """Clean up the combo label and animations."""
        if hasattr(self, 'overload_timer') and self.overload_timer.isActive():
            self.overload_timer.stop()
            
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

    # ----------------------
    #  Event Handlers
    # ----------------------
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.footer_widget.geometry().contains(event.pos()) or self.cat_label.geometry().contains(event.pos()):
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.original_opacity = self.footer_opacity_effect.opacity()
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(20)
                shadow.setOffset(0, 0)
                shadow.setColor(QtGui.QColor(0, 0, 0, 100))
                self.footer_widget.setGraphicsEffect(shadow)
                event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.drag_position and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
            # Recreate the opacity effect to ensure it's valid
            self.footer_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.footer_widget)
            self.footer_widget.setGraphicsEffect(self.footer_opacity_effect)
            self.footer_animation.setTargetObject(self.footer_opacity_effect)
            self.footer_animation.setPropertyName(b"opacity")
            
            if not self.is_hovering and self.config.hidden_footer:
                self.footer_opacity_effect.setOpacity(0.0)
                self.footer_widget.hide()
            elif hasattr(self, 'original_opacity'):
                self.footer_opacity_effect.setOpacity(self.original_opacity)
            else:
                self.footer_opacity_effect.setOpacity(1.0)
            
            event.accept()

    def enterEvent(self, event):
        """Handle mouse enter events."""
        self.is_hovering = True
        self.fade_footer(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave events."""
        self.is_hovering = False
        QtCore.QTimer.singleShot(200, self.check_hover)
        super().leaveEvent(event)

    def check_hover(self):
        """Check if mouse is still hovering."""
        if not self.is_hovering:
            self.fade_footer(False)

    def closeEvent(self, event):
        """Handle window close event."""
        self.settings.setValue('geometry', self.saveGeometry())
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Bongo Cat",
            "Bongo Cat is still running in the system tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    # ----------------------
    #  System Tray
    # ----------------------
    def setup_system_tray(self):
        """Setup the system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(resource_path("img/cat-rest.png")))
        self.tray_icon.setToolTip("Bongo Cat")
        
        tray_menu = QMenu()
        
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)
        
        self.pause_action = QAction("Pause", self)
        self.pause_action.triggered.connect(self.toggle_pause)
        tray_menu.addAction(self.pause_action)
        
        reset_action = QAction("Reset Count", self)
        reset_action.triggered.connect(self.reset_count)
        tray_menu.addAction(reset_action)
        
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
        
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_visibility)
        menu.addAction(show_action)
        
        pause_action = QAction("Pause" if not self.is_paused else "Resume", self)
        pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(pause_action)
        
        reset_action = QAction("Reset Count", self)
        reset_action.triggered.connect(self.reset_count)
        menu.addAction(reset_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        menu.addAction(quit_action)
        
        menu.exec_(self.mapToGlobal(position))

    # ----------------------
    #  Window Management
    # ----------------------
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
        
        # Pause/resume idle animation
        if self.is_paused:
            self.idle_timer.stop()
        else:
            self.idle_timer.start()

    def reset_count(self):
        """Reset the slap count."""
        self.config.slaps = 0
        self.config.update_slap_count(0)
        self.count_label.setText(f"{self.config.slaps}")
        if self.config.always_show_points:
            self.show_total_slaps()

    def restore_window_position(self):
        """Restore the window position from settings."""
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)

    # ----------------------
    #  Configuration
    # ----------------------
    def load_config(self):
        """Load or initialize the configuration file."""
        self.config = configparser.ConfigParser()
        config_path = resource_path("bongo.ini")

        default_config = {
            "Settings": {
                "slaps": "0",
                "hidden_footer": "true",
                "footer_alpha": "50",
                "always_show_points": "false",
                "floating_points": "true",
                "startup_with_windows": "false",
                "max_slaps": "0",
                "invert_cat": "false"
            }
        }

        def safe_getboolean(section, key, default=False):
            try:
                value = self.config.get(section, key, fallback=str(default)).lower()
                return value in ('true', '1', 'yes', 'on')
            except (ValueError, AttributeError):
                return default

        def safe_getint(section, key, default=0):
            try:
                return int(self.config.get(section, key, fallback=str(default)))
            except (ValueError, TypeError):
                return default

        if not os.path.exists(config_path):
            self.config.read_dict(default_config)
            try:
                with open(config_path, "w") as config_file:
                    self.config.write(config_file)
            except (IOError, OSError) as e:
                logger.error(f"Error creating config file at {config_path}: {e}")
                self.config.read_dict(default_config)
        else:
            try:
                self.config.read(config_path)
                for section, values in default_config.items():
                    if section not in self.config:
                        self.config[section] = {}
                    for key, value in values.items():
                        if key not in self.config[section]:
                            self.config[section][key] = value
                with open(config_path, "w") as config_file:
                    self.config.write(config_file)
            except (IOError, OSError, configparser.Error) as e:
                logger.error(f"Error reading config file from {config_path}: {e}")
                self.config.read_dict(default_config)

        try:
            self.config.slaps = max(0, safe_getint("Settings", "slaps"))
            self.config.hidden_footer = safe_getboolean("Settings", "hidden_footer", True)
            self.config.footer_alpha = max(0, min(100, safe_getint("Settings", "footer_alpha", 50)))
            self.config.always_show_points = safe_getboolean("Settings", "always_show_points", False)
            self.config.floating_points = safe_getboolean("Settings", "floating_points", True)
            self.config.startup_with_windows = safe_getboolean("Settings", "startup_with_windows", False)
            self.config.max_slaps = max(0, safe_getint("Settings", "max_slaps"))
            self.config.invert_cat = safe_getboolean("Settings", "invert_cat", False)
            
            # Update the count label with the loaded slaps count
            if hasattr(self, 'count_label'):
                self.count_label.setText(f"{self.config.slaps}")
                
            # Show total slaps if always_show_points is enabled
            if self.config.always_show_points and hasattr(self, 'total_slaps_label'):
                self.show_total_slaps()
        except (ValueError, KeyError, AttributeError) as e:
            logger.error(f"Error loading settings: {e}")
            self.config.slaps = 0
            self.config.hidden_footer = True
            self.config.footer_alpha = 50
            self.config.always_show_points = False
            self.config.floating_points = True
            self.config.startup_with_windows = False
            self.config.max_slaps = 0
            self.config.invert_cat = False

    def save_config(self):
        """Save the current configuration to the file."""
        config_path = resource_path("bongo.ini")
        try:
            self.config["Settings"]["slaps"] = str(self.config.slaps)
            self.config["Settings"]["hidden_footer"] = str(self.config.hidden_footer).lower()
            self.config["Settings"]["footer_alpha"] = str(self.config.footer_alpha)
            self.config["Settings"]["always_show_points"] = str(self.config.always_show_points).lower()
            self.config["Settings"]["floating_points"] = str(self.config.floating_points).lower()
            self.config["Settings"]["startup_with_windows"] = str(self.config.startup_with_windows).lower()
            self.config["Settings"]["max_slaps"] = str(self.config.max_slaps)
            self.config["Settings"]["invert_cat"] = str(self.config.invert_cat).lower()

            with open(config_path, "w") as config_file:
                self.config.write(config_file)
        except (IOError, OSError) as e:
            logger.error(f"Error saving config to {config_path}: {e}")

    def open_ini_file(self):
        """Open the .ini file in the default editor."""
        config_path = resource_path("bongo.ini")
        if os.path.exists(config_path):
            try:
                if sys.platform == 'win32':
                    os.startfile(config_path)
                elif sys.platform == 'darwin':
                    subprocess.call(['open', config_path])
                else:  # Linux and other Unix-like systems
                    subprocess.call(['xdg-open', config_path])
            except Exception as e:
                logger.error(f"Failed to open config file: {e}")
                QtWidgets.QMessageBox.warning(
                    self, "Error",
                    f"Could not open config file: {e}"
                )

    # ----------------------
    #  Footer Fading
    # ----------------------
    def fade_footer(self, fade_in: bool):
        """Fade the footer in or out."""
        # If the footer should always be visible
        if not self.config.hidden_footer:
            self.footer_widget.show()
            
            # Make sure the opacity effect is valid
            if not hasattr(self, 'footer_opacity_effect') or not self.footer_opacity_effect:
                self.footer_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.footer_widget)
                self.footer_widget.setGraphicsEffect(self.footer_opacity_effect)
                self.footer_animation.setTargetObject(self.footer_opacity_effect)
                self.footer_animation.setPropertyName(b"opacity")
                
            self.footer_opacity_effect.setOpacity(1.0)
            return

        # Skip if trying to fade in but not hovering
        if fade_in and not self.is_hovering:
            return

        # Create/validate the opacity effect
        if not hasattr(self, 'footer_opacity_effect') or not self.footer_opacity_effect:
            self.footer_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.footer_widget)
            self.footer_widget.setGraphicsEffect(self.footer_opacity_effect)
            self.footer_animation.setTargetObject(self.footer_opacity_effect)
            self.footer_animation.setPropertyName(b"opacity")

        # Set up and start the animation
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
        if self.footer_opacity_effect and self.footer_opacity_effect.opacity() == 0.0 and self.config.hidden_footer:
            self.footer_widget.hide()

    # ----------------------
    #  Slap Logic
    # ----------------------
    def do_slap(self):
        """Handles slapping animation and input counting."""
        logger.debug("do_slap called")
        if self.is_paused:
            return
            
        self.config.slaps += 1
        
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

        # Only update the slaps count in the config, not the entire config
        self.config.update_slap_count(self.config.slaps)
        self.count_label.setText(f"{self.config.slaps}")
        self.count_label.adjustSize()

        # Always update total slaps if enabled
        if self.config.always_show_points:
            self.show_total_slaps()
            
        # Show floating points if enabled (can work together with always_show_points)
        if self.config.floating_points:
            self.show_bouncing_slaps()

        # Alternate the cat's paws without transition, just change the image type
        if self.current_side == "left":
            self.current_image = "left"
            self.current_side = "right"
        else:
            self.current_image = "right"
            self.current_side = "left"
            
        # Update the image with current stretch factor
        self.update_stretched_image()

        # Restart the slapping timer (100 ms)
        if self.slapping_timer.isActive():
            self.slapping_timer.stop()
        self.slapping_timer.start(100)

    def reset_image(self):
        """Revert to idle image after 100 ms."""
        self.current_image = "idle"
        self.update_stretched_image()

    def show_total_slaps(self):
        """Display the total slaps statically."""
        self.total_slaps_label.setText(str(self.config.slaps))
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
        if not self.config.floating_points:
            return

        # Create the shadow label first (will be positioned behind)
        shadow_label = QtWidgets.QLabel(self.container)
        shadow_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 0, 0, 0.85);
                font: 700 14px 'Segoe UI';
                background-color: transparent;
                padding: 4px 8px;
                border: none;
            }
        """)
        shadow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shadow_label.setText("+1")
        shadow_label.adjustSize()

        # Create the main +1 label with off-white color
        slap_label = QtWidgets.QLabel(self.container)
        slap_label.setStyleSheet("""
            QLabel {
                color: rgba(245, 245, 245, 0.95);
                font: 700 14px 'Segoe UI';
                background-color: transparent;
                padding: 4px 8px;
                border: none;
            }
        """)
        slap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slap_label.setText("+1")
        slap_label.adjustSize()
        
        # Position the labels with slight randomization
        x = (self.cat_width - slap_label.width()) // 2
        x += random.randint(-15, 15)
        y = self.cat_height // 2 + 10
        
        # Position shadow 2px offset from main label (more pronounced)
        shadow_label.move(x + 2, y + 2)
        shadow_label.show()
        shadow_label.raise_()
        
        # Position main label
        slap_label.move(x, y)
        slap_label.show()
        slap_label.raise_()  # Ensure main label is above shadow

        # Create rise animation for shadow label
        shadow_rise_animation = QtCore.QPropertyAnimation(shadow_label, b"pos")
        shadow_rise_animation.setDuration(400)
        shadow_rise_animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        shadow_rise_animation.setStartValue(shadow_label.pos())
        
        # Create rise animation for main label
        main_rise_animation = QtCore.QPropertyAnimation(slap_label, b"pos")
        main_rise_animation.setDuration(400)
        main_rise_animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        main_rise_animation.setStartValue(slap_label.pos())
        
        # If we have an active combo, move towards it
        if self.combo_count > 1 and self.combo_label:
            main_target_pos = self.combo_label.pos()
            shadow_target_pos = QtCore.QPoint(main_target_pos.x() + 2, main_target_pos.y() + 2)
        else:
            main_target_pos = QtCore.QPoint(x, y - 40)
            shadow_target_pos = QtCore.QPoint(x + 2, y - 38)  # Maintain 2px offset
        
        main_rise_animation.setEndValue(main_target_pos)
        shadow_rise_animation.setEndValue(shadow_target_pos)

        # Create fade animations
        main_fade_effect = QtWidgets.QGraphicsOpacityEffect(slap_label)
        slap_label.setGraphicsEffect(main_fade_effect)
        main_fade_animation = QtCore.QPropertyAnimation(main_fade_effect, b"opacity")
        main_fade_animation.setDuration(400)
        main_fade_animation.setStartValue(1.0)
        main_fade_animation.setEndValue(0.0 if self.combo_count > 1 else 0.8)
        
        shadow_fade_effect = QtWidgets.QGraphicsOpacityEffect(shadow_label)
        shadow_label.setGraphicsEffect(shadow_fade_effect)
        shadow_fade_animation = QtCore.QPropertyAnimation(shadow_fade_effect, b"opacity")
        shadow_fade_animation.setDuration(400)
        shadow_fade_animation.setStartValue(1.0)
        shadow_fade_animation.setEndValue(0.0 if self.combo_count > 1 else 0.8)
        
        # Group animations
        animation_group = QtCore.QParallelAnimationGroup()
        animation_group.addAnimation(main_rise_animation)
        animation_group.addAnimation(main_fade_animation)
        animation_group.addAnimation(shadow_rise_animation)
        animation_group.addAnimation(shadow_fade_animation)
        
        # Handle combo display - need to clean up both labels
        if self.combo_count > 1:
            animation_group.finished.connect(lambda: self.show_combo_pop_and_cleanup([slap_label, shadow_label]))
        else:
            animation_group.finished.connect(lambda: self.cleanup_multiple_labels([slap_label, shadow_label]))
        
        animation_group.start()
        self.slap_labels.append((slap_label, animation_group))
        self.slap_labels.append((shadow_label, animation_group))
        
    def cleanup_multiple_labels(self, labels):
        """Clean up multiple labels."""
        for label in labels:
            label.hide()
            label.deleteLater()
            self.slap_labels = [(l, anim) for l, anim in self.slap_labels if l != label]
            
    def show_combo_pop_and_cleanup(self, labels):
        """Show combo pop and clean up the temporary labels."""
        main_label = labels[0]  # Assuming the main label is first in the list
        self.cleanup_multiple_labels(labels)
        self.show_combo_pop(main_label)

    def open_settings_dialog(self):
        """Show the settings panel as a separate window."""
        if self.settings_panel.isVisible():
            self.settings_panel.activateWindow()
        else:
            # Update current values
            self.hidden_footer_checkbox.setChecked(self.config.hidden_footer)
            self.footer_alpha_slider.setValue(self.config.footer_alpha)
            self.always_show_points_checkbox.setChecked(self.config.always_show_points)
            self.floating_points_checkbox.setChecked(self.config.floating_points)
            self.startup_with_windows_checkbox.setChecked(self.config.startup_with_windows)
            self.invert_cat_checkbox.setChecked(self.config.invert_cat)
            self.max_slaps_spinbox.setValue(self.config.max_slaps)
            
            # Position the settings panel near the main window
            main_pos = self.pos()
            self.settings_panel.move(main_pos.x() + self.width() + 10, main_pos.y())
            
            # Show and activate the panel
            self.settings_panel.show()
            self.settings_panel.activateWindow()

    def apply_settings(self):
        """Apply the settings changes."""
        old_invert_cat = self.config.invert_cat

        # Update settings from UI
        self.config.hidden_footer = self.hidden_footer_checkbox.isChecked()
        self.config.footer_alpha = self.footer_alpha_slider.value()
        self.config.always_show_points = self.always_show_points_checkbox.isChecked()
        self.config.floating_points = self.floating_points_checkbox.isChecked()
        self.config.startup_with_windows = self.startup_with_windows_checkbox.isChecked()
        self.config.max_slaps = self.max_slaps_spinbox.value()
        self.config.invert_cat = self.invert_cat_checkbox.isChecked()

        # Apply settings
        self.config.save()
        
        # Update the footer styling with new alpha
        self.setup_footer_style()
        
        # Recreate the opacity effect to ensure it's valid
        self.footer_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.footer_widget)
        self.footer_widget.setGraphicsEffect(self.footer_opacity_effect)
        
        # Reconnect animation to the new effect
        self.footer_animation.setTargetObject(self.footer_opacity_effect)
        self.footer_animation.setPropertyName(b"opacity")
        
        # Update footer visibility based on hidden_footer setting
        if not self.config.hidden_footer:
            self.footer_widget.show()
            self.footer_opacity_effect.setOpacity(1.0)
        
        # Update UI based on new settings
        if self.config.always_show_points:
            self.show_total_slaps()
        else:
            self.total_slaps_label.hide()
            
        # Update cat image if invert setting changed
        if old_invert_cat != self.config.invert_cat:
            self.update_stretched_image()

    def reset_counter_confirm(self):
        """Confirm before resetting the counter."""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Reset Counter")
        msg_box.setText("Are you sure you want to reset the slap counter to 0?")
        
        # Create StandardButtons using the enum correctly
        yes_button = QtWidgets.QMessageBox.StandardButton.Yes
        no_button = QtWidgets.QMessageBox.StandardButton.No
        msg_box.addButton(yes_button)
        msg_box.addButton(no_button)
        msg_box.setDefaultButton(no_button)
        
        result = msg_box.exec_()
        
        if result == QtWidgets.QMessageBox.StandardButton.Yes:
            self.reset_count()

    def setup_settings_panel(self):
        """Set up the settings panel as a separate window."""
        # Create settings panel as a top-level window
        self.settings_panel = SettingsPanelWidget(self)
        self.settings_panel.setWindowTitle("Bongo Cat Settings")
        
        # Set window flags for a dialog-like appearance
        flags = Qt.WindowFlags()
        flags |= Qt.WindowType.Window
        flags |= Qt.WindowType.WindowStaysOnTopHint
        flags |= Qt.WindowType.CustomizeWindowHint
        flags |= Qt.WindowType.WindowTitleHint
        flags |= Qt.WindowType.WindowCloseButtonHint
        self.settings_panel.setWindowFlags(flags)
        
        # Style the panel
        self.settings_panel.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
        """)
        
        # Set panel size
        self.settings_panel.setFixedSize(300, 400)
        
        # Create layout
        main_layout = QtWidgets.QVBoxLayout(self.settings_panel)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Add title
        title_label = QtWidgets.QLabel("Settings")
        title_label.setStyleSheet("""
            color: white;
            font: bold 16px 'Segoe UI';
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 5px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create form layout for settings
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # Hidden footer option
        self.config.hidden_footer_checkbox = QtWidgets.QCheckBox()
        self.config.hidden_footer_checkbox.setChecked(self.config.hidden_footer)
        self.config.hidden_footer_checkbox.setStyleSheet("color: white;")
        form_layout.addRow(self.create_settings_label("Auto-hide footer:"), self.config.hidden_footer_checkbox)
        
        # Footer opacity
        self.config.footer_alpha_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.config.footer_alpha_slider.setRange(0, 100)
        self.config.footer_alpha_slider.setValue(self.config.footer_alpha)
        self.config.footer_alpha_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.config.footer_alpha_slider.setTickInterval(10)
        
        footer_alpha_layout = QtWidgets.QHBoxLayout()
        footer_alpha_layout.addWidget(self.config.footer_alpha_slider)
        self.config.footer_alpha_value = QtWidgets.QLabel(f"{self.config.footer_alpha}%")
        self.config.footer_alpha_value.setStyleSheet("color: white; min-width: 40px;")
        footer_alpha_layout.addWidget(self.config.footer_alpha_value)
        self.config.footer_alpha_slider.valueChanged.connect(
            lambda value: self.config.footer_alpha_value.setText(f"{value}%")
        )
        
        form_layout.addRow(self.create_settings_label("Footer opacity:"), footer_alpha_layout)
        
        # Always show points
        self.config.always_show_points_checkbox = QtWidgets.QCheckBox()
        self.config.always_show_points_checkbox.setChecked(self.config.always_show_points)
        self.config.always_show_points_checkbox.setStyleSheet("color: white;")
        form_layout.addRow(self.create_settings_label("Always show total:"), self.config.always_show_points_checkbox)
        
        # Show floating points
        self.config.floating_points_checkbox = QtWidgets.QCheckBox()
        self.config.floating_points_checkbox.setChecked(self.config.floating_points)
        self.config.floating_points_checkbox.setStyleSheet("color: white;")
        form_layout.addRow(self.create_settings_label("Floating +1 animations:"), self.config.floating_points_checkbox)
        
        # Invert cat
        self.config.invert_cat_checkbox = QtWidgets.QCheckBox()
        self.config.invert_cat_checkbox.setChecked(self.config.invert_cat)
        self.config.invert_cat_checkbox.setStyleSheet("color: white;")
        form_layout.addRow(self.create_settings_label("Invert cat:"), self.config.invert_cat_checkbox)
        
        # Start with Windows
        self.config.startup_with_windows_checkbox = QtWidgets.QCheckBox()
        self.config.startup_with_windows_checkbox.setChecked(self.config.startup_with_windows)
        self.config.startup_with_windows_checkbox.setStyleSheet("color: white;")
        form_layout.addRow(self.create_settings_label("Start with Windows:"), self.config.startup_with_windows_checkbox)
        
        # Max slaps (for achievements or tracking)
        self.config.max_slaps_spinbox = QtWidgets.QSpinBox()
        self.config.max_slaps_spinbox.setRange(0, 1000000)
        self.config.max_slaps_spinbox.setValue(self.config.max_slaps)
        self.config.max_slaps_spinbox.setSpecialValueText("No limit")
        self.config.max_slaps_spinbox.setStyleSheet("""
            color: white; 
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            padding: 2px;
        """)
        form_layout.addRow(self.create_settings_label("Max slap count:"), self.config.max_slaps_spinbox)
        
        main_layout.addLayout(form_layout)
        
        # Add buttons layout
        buttons_layout = QtWidgets.QHBoxLayout()
        
        # Reset counter button
        reset_button = QtWidgets.QPushButton("Reset Counter")
        reset_button.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
        """)
        reset_button.clicked.connect(self.reset_counter_confirm)
        
        # Apply button
        apply_button = QtWidgets.QPushButton("Apply")
        apply_button.setStyleSheet("""
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
        """)
        apply_button.clicked.connect(self.apply_settings)
        
        # Close button
        close_button = QtWidgets.QPushButton("Close")
        close_button.setStyleSheet("""
            background-color: #3498db;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
        """)
        close_button.clicked.connect(self.settings_panel.hide)
        
        buttons_layout.addWidget(reset_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(apply_button)
        buttons_layout.addWidget(close_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Apply overall styles to all widgets
        self.settings_panel.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QLabel {
                color: white;
                background: transparent;
            }
            QCheckBox {
                color: white;
                background: transparent;
            }
            QSpinBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton {
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #34495e;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
        # Style specific buttons
        reset_button.setStyleSheet("background-color: #e74c3c; color: white;")
        apply_button.setStyleSheet("background-color: #2ecc71; color: white;")
        close_button.setStyleSheet("background-color: #3498db; color: white;")

    def create_settings_label(self, text):
        """Create a styled label for settings form layout."""
        label = QtWidgets.QLabel(text)
        label.setStyleSheet("""
            color: #cccccc;
            font: 12px 'Segoe UI';
        """)
        return label
