"""Settings panel widget for configuring Bongo Cat."""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class SettingsPanelWidget(QtWidgets.QWidget):
    """Custom widget for settings panel with overridden closeEvent.

    This widget hides instead of closing when the user clicks the X button,
    allowing it to be shown again without recreating the widget.

    Attributes:
        parent_window: Reference to the parent window
    """

    def __init__(self, parent=None):
        """Initialize settings panel widget.

        Args:
            parent: Parent widget (typically the main window)
        """
        super().__init__(parent)
        self.parent_window = parent

    def closeEvent(self, event):
        """Override close event to hide panel instead of closing.

        Args:
            event: QCloseEvent
        """
        event.ignore()
        self.hide()
