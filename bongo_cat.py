import sys
import os
import threading
import configparser
from PyQt5 import QtCore, QtGui, QtWidgets
from pynput import keyboard, mouse
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

def resource_path(relative_path):
    """Get the absolute path to a resource, works for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class BongoCatWindow(QtWidgets.QWidget):
    trigger_slap = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.load_config()
        self.setWindowTitle("Bongo Cat")

        # Frameless, transparent, always on top
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |  # Ensure the window stays above all others
            QtCore.Qt.Tool  # Ensure it stays above the taskbar
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

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
        self.footer_height = 35  # Increased footer size for better visibility

        # Total window size = cat + footer
        self.setFixedSize(self.cat_width, self.cat_height + self.footer_height)

        # ----------------------
        #   Cat Label (Top)
        # ----------------------
        self.cat_label = QtWidgets.QLabel(self)
        self.cat_label.setPixmap(self.idle_pixmap)
        self.cat_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cat_label.setGeometry(0, 0, self.cat_width, self.cat_height)
        self.cat_label.setMouseTracking(True)

        # Ensure the cat label is drawn above the footer
        self.cat_label.raise_()

        # ----------------------
        #  Footer (Below Cat)
        # ----------------------
        self.footer_widget = QtWidgets.QWidget(self)
        self.footer_widget.setGeometry(0, self.cat_height - 60, self.cat_width, self.footer_height)
        self.footer_widget.setMouseTracking(True)
        self.footer_widget.hide()  # Hidden until hovered

        # Remove the footer_widget.lower() call to keep it interactive
        # self.footer_widget.lower()

        # Apply footer alpha from config
        self.footer_widget.setStyleSheet(f"""
            background-color: rgba(30, 30, 30, {self.footer_alpha * 2.55});
            border-radius: 12px;
            padding: 10px;
        """)

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
        footer_layout.setContentsMargins(4, 2, 4, 2)
        footer_layout.setSpacing(20)

        # Label to display input count
        self.count_label = QtWidgets.QLabel(self.footer_widget)
        self.count_label.setText(f"slaps: {self.slaps}")
        self.count_label.setStyleSheet("""
            color: white;
            font: bold 14px;
            background-color: transparent;
        """)
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

        # Connect global input signal → do_slap()
        self.trigger_slap.connect(self.do_slap)

        # For dragging
        self.drag_position = None

        # Track if mouse is over the cat/footer
        self.is_hovering = False

        # Label for bouncing slap count
        self.slaps_label = QtWidgets.QLabel(self)
        self.slaps_label.setStyleSheet("color: white; font: bold 16px;")
        self.slaps_label.setAlignment(QtCore.Qt.AlignCenter)
        self.slaps_label.hide()

        # Track active keys to prevent repeated counts
        self.active_keys = set()

        # Container for multiple slap labels
        self.slap_labels = []

        # Label for total slaps (static when always_show_points is true)
        self.total_slaps_label = QtWidgets.QLabel(self)
        self.total_slaps_label.setStyleSheet("""
            color: white;
            font: bold 16px;
            background-color: rgba(0, 0, 0, 150);  /* Semi-transparent black background */
            padding: 2px;
            border-radius: 4px;
        """)
        self.total_slaps_label.setAlignment(QtCore.Qt.AlignCenter)
        self.total_slaps_label.hide()  # Initially hidden

        # Add a more prominent drop shadow effect to the total slaps label
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setOffset(3, 3)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 200))  # More opaque black
        self.total_slaps_label.setGraphicsEffect(shadow_effect)

        # Show total slaps immediately if always_show_points is true
        if self.always_show_points:
            self.show_total_slaps()

    # ----------------------
    #  Fix Tilted Images
    # ----------------------
    def load_and_fix_image(self, path):
        """Loads an image and rotates it back -16 degrees to fix tilt."""
        pixmap = QtGui.QPixmap(resource_path(path))
        transform = QtGui.QTransform()
        transform.rotate(-13)  # Counteract tilt
        return pixmap.transformed(transform, QtCore.Qt.SmoothTransformation)

    # ----------------------
    #  Slap Logic
    # ----------------------
    def do_slap(self):
        """Handles slapping animation and input counting."""
        self.slaps += 1
        self.save_config()
        self.count_label.setText(f"slaps: {self.slaps}")  # Ensure label text is updated

        # Show total slaps or animate +1
        if self.always_show_points:
            self.show_total_slaps()
        else:
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
        self.total_slaps_label.setText(f"{self.slaps}")
        self.total_slaps_label.move(self.cat_width // 2 - 20, self.cat_height // 2 - 50)
        self.total_slaps_label.show()
        self.total_slaps_label.raise_()  # Ensure it's on top

    def show_bouncing_slaps(self):
        """Animate a bouncing +1 near the cat if floating_points is enabled."""
        if not self.floating_points:
            return

        slap_label = QtWidgets.QLabel(self)
        slap_label.setStyleSheet(f"""
            color: white;
            font: bold 16px;
            background-color: rgba(0, 0, 0, {self.floating_points_alpha * 2.55});  /* Semi-transparent black */
            padding: 2px;
            border-radius: 4px;
        """)
        slap_label.setAlignment(QtCore.Qt.AlignCenter)
        slap_label.setText("+1")
        slap_label.move(self.cat_width // 2 - 20, self.cat_height // 2 - 50)
        slap_label.show()
        slap_label.raise_()  # Ensure the label is on top

        # Add a drop shadow effect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(5)
        shadow_effect.setOffset(2, 2)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 160))  # Semi-transparent black
        slap_label.setGraphicsEffect(shadow_effect)

        # Animate the label upwards
        slap_animation = QtCore.QPropertyAnimation(slap_label, b"pos")
        slap_animation.setDuration(500)
        slap_animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        slap_animation.setStartValue(slap_label.pos())
        slap_animation.setEndValue(QtCore.QPoint(slap_label.x(), slap_label.y() - 30))
        slap_animation.finished.connect(lambda: self.cleanup_slap_label(slap_label))
        slap_animation.start()

        # Store the animation reference to prevent garbage collection
        self.slap_labels.append((slap_label, slap_animation))

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
        if self.footer_opacity_effect.opacity() == 0.0:
            self.footer_widget.hide()

    # ----------------------
    #  Mouse / Window
    # ----------------------
    def mousePressEvent(self, event):
        """Allow dragging when clicking on the cat or footer."""
        if event.button() == QtCore.Qt.LeftButton:
            if self.footer_widget.geometry().contains(event.pos()) or self.cat_label.geometry().contains(event.pos()):
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Drag window & handle footer fade logic."""
        if self.drag_position and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
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

        if not os.path.exists(config_path):
            # Initialize default config
            self.config["Settings"] = {
                "slaps": "0",
                "hidden_footer": "true",
                "footer_alpha": "50",
                "always_show_points": "false",
                "floating_points": "true",
                "floating_points_alpha": "50"
            }
            with open(config_path, "w") as config_file:
                self.config.write(config_file)

        self.config.read(config_path)
        # Load settings
        self.slaps = int(self.config["Settings"]["slaps"])
        self.hidden_footer = self.config["Settings"].getboolean("hidden_footer")
        self.footer_alpha = int(self.config["Settings"]["footer_alpha"])
        self.always_show_points = self.config["Settings"].getboolean("always_show_points")
        self.floating_points = self.config["Settings"].getboolean("floating_points")
        self.floating_points_alpha = int(self.config["Settings"]["floating_points_alpha"])

    def save_config(self):
        """Save the current configuration to the file."""
        self.config["Settings"]["slaps"] = str(self.slaps)
        with open(resource_path("bongo.ini"), "w") as config_file:
            self.config.write(config_file)


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