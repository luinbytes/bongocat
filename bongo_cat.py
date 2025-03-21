import sys
import os
import threading
import configparser
import random
import math
from typing import Optional, cast
from PyQt5 import QtCore, QtGui, QtWidgets
from pynput import keyboard, mouse
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QSettings, Qt

# ----------------------
#  Utility Functions
# ----------------------
def resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource."""
    if relative_path == "bongo.ini":
        appdata = os.getenv("APPDATA")
        if appdata is None:
            appdata = os.path.expanduser("~")
        appdata_path = os.path.join(appdata, "BongoCat")
        os.makedirs(appdata_path, exist_ok=True)
        return os.path.join(appdata_path, relative_path)
    if getattr(sys, '_MEIPASS', None) is not None:
        base_path = getattr(sys, '_MEIPASS')
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ----------------------
#  Main Window Class
# ----------------------
class BongoCatWindow(QtWidgets.QWidget):
    trigger_slap = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.trigger_slap.connect(self.do_slap)
        
        # Initialize configuration attributes with default values
        self.slaps = 0
        self.hidden_footer = True
        self.footer_alpha = 50
        self.always_show_points = False
        self.floating_points = True
        self.startup_with_windows = False
        self.max_slaps = 0
        self.is_paused = False
        self.is_hovering = False
        self.drag_position = None
        self.current_side = "left"
        
        self.setup_window()
        self.setup_ui()
        self.setup_animations()
        self.setup_system_tray()
        self.setup_context_menu()
        self.load_config()
        self.restore_window_position()

    # ----------------------
    #  Window Setup
    # ----------------------
    def setup_window(self):
        """Initialize window properties and flags."""
        self.setWindowTitle("Bongo Cat")
        self.settings = QSettings('BongoCat', 'BongoCat')
        self.is_paused = False
        
        flags = Qt.WindowFlags()
        flags |= Qt.WindowType.FramelessWindowHint
        flags |= Qt.WindowType.WindowStaysOnTopHint
        flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setMouseTracking(True)

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
        self.idle_pixmap = self.load_and_fix_image(resource_path("img/cat-rest.png"))
        self.slap_pixmap_left = self.load_and_fix_image(resource_path("img/cat-left.png"))
        self.slap_pixmap_right = self.load_and_fix_image(resource_path("img/cat-right.png"))
        
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
                background: rgba(40, 44, 52, {self.footer_alpha * 2.55});
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
        self.count_label.setText(f"{self.slaps}")
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
        self.slapping_timer = QtCore.QTimer()
        self.slapping_timer.setSingleShot(True)
        self.slapping_timer.timeout.connect(self.reset_image)
        self.slap_labels = []

    # ----------------------
    #  Image Handling
    # ----------------------
    def load_and_fix_image(self, path):
        """Loads an image and rotates it back -16 degrees to fix tilt."""
        try:
            pixmap = QtGui.QPixmap(resource_path(path))
            if pixmap.isNull():
                raise Exception(f"Failed to load image: {path}")
            transform = QtGui.QTransform()
            transform.rotate(-13)
            return pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
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
            
        font_size = min(13 + (self.combo_count // 3), 18)
        opacity = min(0.95, 0.7 + (self.combo_count * 0.02))
        
        if self.combo_count < 30:
            color = "255, 255, 100"
        elif self.combo_count < 60:
            color = "255, 150, 50"
        else:
            color = "255, 50, 50"
        
        self.original_color = color
        gradient_start = "rgba(40, 44, 52, 0.85)"
        gradient_end = "rgba(60, 64, 72, 0.85)"
        
        self.combo_label.setStyleSheet(f"""
            QLabel {{
                color: rgba({color}, 0.95);
                font: 500 {font_size}px 'Segoe UI';
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {gradient_start}, 
                    stop:1 {gradient_end});
                padding: 2px 8px;
                border: 1px solid rgba({color}, 0.2);
                border-radius: 2px;
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
        
        if self.always_show_points and self.total_slaps_label.isVisible():
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
        
        r, g, b = map(int, self.original_color.split(','))
        intensity = 0.6 + wave * 0.9
        r_new = min(255, int(r * intensity))
        g_new = min(255, int(g * intensity))
        b_new = min(255, int(b * intensity))
        
        border_width = 1 + wave * 3
        font_size = min(13 + (self.combo_count // 3), 18)
        
        self.combo_label.setStyleSheet(f"""
            QLabel {{
                color: rgba({r_new}, {g_new}, {b_new}, 0.95);
                font: 500 {font_size}px 'Segoe UI';
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(40, 44, 52, 0.85), 
                    stop:1 rgba(60, 64, 72, 0.85));
                padding: 2px 8px;
                border: {border_width}px solid rgba({r_new}, {g_new}, {b_new}, {0.2 + wave * 0.5});
                border-radius: 2px;
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
            
            if not self.is_hovering and self.hidden_footer:
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

    def reset_count(self):
        """Reset the slap count."""
        self.slaps = 0
        self.update_slap_count()
        self.count_label.setText(f"{self.slaps}")
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
                "max_slaps": "0"
            }
        }

        def safe_getboolean(section, key, default=False):
            try:
                value = self.config.get(section, key, fallback=str(default)).lower()
                return value in ('true', '1', 'yes', 'on')
            except:
                return default

        def safe_getint(section, key, default=0):
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
                for section, values in default_config.items():
                    if section not in self.config:
                        self.config[section] = {}
                    for key, value in values.items():
                        if key not in self.config[section]:
                            self.config[section][key] = value
                with open(config_path, "w") as config_file:
                    self.config.write(config_file)
            except Exception as e:
                print(f"Error reading config file: {e}")
                self.config.read_dict(default_config)

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
        # If the footer should always be visible
        if not self.hidden_footer:
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
        if self.footer_opacity_effect and self.footer_opacity_effect.opacity() == 0.0 and self.hidden_footer:
            self.footer_widget.hide()

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
        
        # Only update the slaps count in the config, not the entire config
        self.update_slap_count()
        self.count_label.setText(f"{self.slaps}")
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
            QLabel {
                color: rgba(255, 255, 255, 0.95);
                font: 500 13px 'Segoe UI';
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(40, 44, 52, 0.85), 
                    stop:1 rgba(60, 64, 72, 0.85));
                padding: 2px 6px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 2px;
            }
        """)
        slap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slap_label.setText("+1")
        slap_label.adjustSize()
        
        # Add subtle glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(15)
        glow.setOffset(0, 0)
        glow.setColor(QtGui.QColor(255, 255, 255, 50))
        slap_label.setGraphicsEffect(glow)
        
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

    def open_settings_dialog(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # If dialog is accepted (OK clicked), update settings
            self.hidden_footer = dialog.hidden_footer_checkbox.isChecked()
            self.footer_alpha = dialog.footer_alpha_slider.value()
            self.always_show_points = dialog.always_show_points_checkbox.isChecked()
            self.floating_points = dialog.floating_points_checkbox.isChecked()
            self.startup_with_windows = dialog.startup_with_windows_checkbox.isChecked()
            self.max_slaps = dialog.max_slaps_spinbox.value()
            
            # Apply settings
            self.save_config()
            
            # Update the footer styling with new alpha
            self.setup_footer_style()
            
            # Recreate the opacity effect to ensure it's valid
            self.footer_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.footer_widget)
            self.footer_widget.setGraphicsEffect(self.footer_opacity_effect)
            
            # Reconnect animation to the new effect
            self.footer_animation.setTargetObject(self.footer_opacity_effect)
            self.footer_animation.setPropertyName(b"opacity")
            
            # Update footer visibility based on hidden_footer setting
            if not self.hidden_footer:
                self.footer_widget.show()
                self.footer_opacity_effect.setOpacity(1.0)
            
            # Update UI based on new settings
            if self.always_show_points:
                self.show_total_slaps()
            else:
                self.total_slaps_label.hide()

    def update_slap_count(self):
        """Update only the slap count in the config file without changing other settings."""
        config_path = resource_path("bongo.ini")
        try:
            self.config["Settings"]["slaps"] = str(self.slaps)
            
            with open(config_path, "w") as config_file:
                self.config.write(config_file)
        except Exception as e:
            print(f"Error updating slap count: {e}")

# ----------------------
#  Settings Dialog
# ----------------------
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Bongo Cat Settings")
        self.setFixedSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the settings dialog UI."""
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Create form layout for settings
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Hidden footer option
        self.hidden_footer_checkbox = QtWidgets.QCheckBox()
        if self.parent_window:
            self.hidden_footer_checkbox.setChecked(self.parent_window.hidden_footer)
        form_layout.addRow("Auto-hide footer:", self.hidden_footer_checkbox)
        
        # Footer opacity
        self.footer_alpha_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.footer_alpha_slider.setRange(0, 100)
        if self.parent_window:
            self.footer_alpha_slider.setValue(self.parent_window.footer_alpha)
        self.footer_alpha_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.footer_alpha_slider.setTickInterval(10)
        
        footer_alpha_layout = QtWidgets.QHBoxLayout()
        footer_alpha_layout.addWidget(self.footer_alpha_slider)
        alpha_value = self.parent_window.footer_alpha if self.parent_window else 50
        self.footer_alpha_value = QtWidgets.QLabel(f"{alpha_value}%")
        footer_alpha_layout.addWidget(self.footer_alpha_value)
        self.footer_alpha_slider.valueChanged.connect(
            lambda value: self.footer_alpha_value.setText(f"{value}%")
        )
        
        form_layout.addRow("Footer opacity:", footer_alpha_layout)
        
        # Always show points
        self.always_show_points_checkbox = QtWidgets.QCheckBox()
        if self.parent_window:
            self.always_show_points_checkbox.setChecked(self.parent_window.always_show_points)
        form_layout.addRow("Always show total slaps:", self.always_show_points_checkbox)
        
        # Show floating points
        self.floating_points_checkbox = QtWidgets.QCheckBox()
        if self.parent_window:
            self.floating_points_checkbox.setChecked(self.parent_window.floating_points)
        form_layout.addRow("Show floating +1 animations:", self.floating_points_checkbox)
        
        # Start with Windows
        self.startup_with_windows_checkbox = QtWidgets.QCheckBox()
        if self.parent_window:
            self.startup_with_windows_checkbox.setChecked(self.parent_window.startup_with_windows)
        form_layout.addRow("Start with Windows:", self.startup_with_windows_checkbox)
        
        # Max slaps (for achievements or tracking)
        self.max_slaps_spinbox = QtWidgets.QSpinBox()
        self.max_slaps_spinbox.setRange(0, 1000000)
        if self.parent_window:
            self.max_slaps_spinbox.setValue(self.parent_window.max_slaps)
        self.max_slaps_spinbox.setSpecialValueText("No limit")
        form_layout.addRow("Max slap count:", self.max_slaps_spinbox)
        
        # Reset counter button
        reset_button = QtWidgets.QPushButton("Reset Counter")
        reset_button.clicked.connect(self.reset_counter)
        
        main_layout.addLayout(form_layout)
        main_layout.addWidget(reset_button)
        
        # Add buttons
        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        button_box.addButton(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # Apply style
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: white;
            }
            QLabel {
                color: white;
            }
            QCheckBox {
                color: white;
            }
            QSpinBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
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
    
    def reset_counter(self):
        """Reset the slap counter."""
        if not self.parent_window:
            return
            
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
            self.parent_window.reset_count()

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