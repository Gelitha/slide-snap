import sys
import time
import numpy as np
import cv2
import pyautogui
from PyQt5 import QtWidgets, QtGui, QtCore
from datetime import datetime
import os
import subprocess
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QSettings, QPoint, QEasingCurve, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPalette, QPainter, QBrush, QCursor, QImage
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDoubleSpinBox, QSpinBox, QLineEdit, QFileDialog, QGroupBox,
                             QScrollArea, QListWidget, QListWidgetItem, QMessageBox, QToolTip,
                             QStyleFactory, QFrame, QSplitter, QGridLayout, QSlider, QMenu, QAction)

class NotificationBanner(QWidget):
    def __init__(self, parent=None):
        super(NotificationBanner, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.layout.addWidget(self.icon_label)

        self.message_label = QLabel()
        self.message_label.setStyleSheet("color: white; font-size: 14px;")
        self.layout.addWidget(self.message_label)

        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ccc;
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        self.layout.addWidget(self.close_btn)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide)

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.finished.connect(self.onAnimationFinished)

        self.setStyleSheet("""
            NotificationBanner {
                background-color: rgba(60, 60, 60, 220);
                border-radius: 6px;
            }
        """)

    def showMessage(self, message, icon_data=None, timeout=3000):
        if icon_data:
            pixmap = QPixmap()
            pixmap.loadFromData(icon_data)
            pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
            self.icon_label.show()
        else:
            self.icon_label.hide()

        self.message_label.setText(message)

        # Position at bottom right of screen
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry(desktop.primaryScreen())
        self.adjustSize()
        x = screen_rect.width() - self.width() - 20
        y = screen_rect.height() - self.height() - 20
        self.move(x, y)

        self.setWindowOpacity(0.0)
        self.show()

        # Fade in animation
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

        # Set timeout
        self.timer.start(timeout)

    def onAnimationFinished(self):
        if self.windowOpacity() == 0.0:
            self.hide()

    def hideEvent(self, event):
        self.timer.stop()
        super(NotificationBanner, self).hideEvent(event)

class ModernSlider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(ModernSlider, self).__init__(orientation, parent)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #d0d0d0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 1px solid #2196F3;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #1976D2;
            }
            QSlider::sub-page:horizontal {
                background: #2196F3;
                border-radius: 4px;
            }
        """)

class HoverButton(QPushButton):
    def __init__(self, icon_data=None, text="", parent=None):
        super(HoverButton, self).__init__(parent)
        self.default_text = text

        if icon_data:
            pixmap = QPixmap()
            pixmap.loadFromData(icon_data)
            self.setIcon(QIcon(pixmap))
        if text:
            self.setText(text)

        self.setMouseTracking(True)
        self.installEventFilter(self)

        # Default style
        self.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                color: #3c4043;
                font-weight: 500;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
                border-color: #d2d4d7;
            }
            QPushButton:pressed {
                background-color: #e8eaed;
            }
            QPushButton:disabled {
                background-color: #f1f3f4;
                border-color: #f1f3f4;
                color: #9aa0a6;
            }
        """)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Enter:
                self.setCursor(QCursor(Qt.PointingHandCursor))
            elif event.type() == QEvent.Leave:
                self.setCursor(QCursor(Qt.ArrowCursor))
        return super(HoverButton, self).eventFilter(obj, event)

class ThumbnailCard(QWidget):
    clicked = QtCore.pyqtSignal(str)

    def __init__(self, image_path, parent=None):
        super(ThumbnailCard, self).__init__(parent)
        self.image_path = image_path  # Keep the path for deletion
        self.setFixedSize(150, 120)
        self.setMouseTracking(True)
        self.hover = False

        self.setStyleSheet("""
            QToolTip {
                background-color: white;
                color: black;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        filename = os.path.basename(image_path)
        self.setToolTip(filename)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw card background
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.NoPen)

        if self.hover:
            # Draw shadow
            painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
            shadow_rect = self.rect().adjusted(3, 3, 3, 3)
            painter.drawRoundedRect(shadow_rect, 6, 6)

            # Draw highlighted border
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QColor(33, 150, 243))  # Blue highlight
            card_rect = self.rect().adjusted(0, 0, -1, -1)
        else:
            painter.setPen(QColor(220, 220, 220))
            card_rect = self.rect().adjusted(0, 0, -1, -1)

        painter.drawRoundedRect(card_rect, 6, 6)

        # Draw image
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            # Calculate scaled size for the thumbnail
            img_rect = QtCore.QRect(5, 5, self.width() - 10, self.height() - 30)
            scaled_pixmap = pixmap.scaled(img_rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Center the image in the thumbnail area
            img_x = img_rect.x() + (img_rect.width() - scaled_pixmap.width()) // 2
            img_y = img_rect.y() + (img_rect.height() - scaled_pixmap.height()) // 2

            painter.drawPixmap(img_x, img_y, scaled_pixmap)

            # Draw filename truncated
            painter.setPen(QColor(70, 70, 70))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)

            filename = os.path.basename(self.image_path)
            if len(filename) > 20:
                filename = filename[:17] + "..."

            text_rect = QtCore.QRect(5, self.height() - 25, self.width() - 10, 20)
            painter.drawText(text_rect, Qt.AlignCenter, filename)

    def enterEvent(self, event):
        self.hover = True
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.update()
        super(ThumbnailCard, self).enterEvent(event)

    def leaveEvent(self, event):
        self.hover = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.update()
        super(ThumbnailCard, self).leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path)
        super(ThumbnailCard, self).mousePressEvent(event)

class ModernCollapsibleBox(QtWidgets.QWidget):
    def __init__(self, title="", parent=None):
        super(ModernCollapsibleBox, self).__init__(parent)

        self.toggle_button = QtWidgets.QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("""
            QToolButton {
                border: none;
                font-size: 14px;
                font-weight: bold;
                color: #444;
                text-align: left;
                padding: 5px;
            }
            QToolButton:checked {
                background-color: #e0e0e0;
            }
            QToolButton:hover {
                color: #1976D2;
            }
        """)
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        # Use in-memory icon data
        self.right_arrow_icon = self.load_icon_data("right_arrow.png")
        self.down_arrow_icon = self.load_icon_data("down_arrow.png")
        self.toggle_button.setIcon(QIcon(QPixmap.fromImage(QImage.fromData(self.right_arrow_icon))))

        self.toggle_button.setIconSize(QtCore.QSize(16, 16))
        self.toggle_button.clicked.connect(self.on_clicked)

        self.content_area = QtWidgets.QScrollArea(maximumHeight=0, minimumHeight=0)
        self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.content_area.setWidgetResizable(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)

        self.animation = QPropertyAnimation(self, b"minimumHeight")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation_2 = QPropertyAnimation(self, b"maximumHeight")
        self.animation_2.setDuration(250)
        self.animation_2.setEasingCurve(QEasingCurve.InOutCubic)

    def load_icon_data(self, filename):
        """Loads icon data from a file."""
        with open(filename, "rb") as f:
            return f.read()

    @QtCore.pyqtSlot()
    def on_clicked(self):
        checked = self.toggle_button.isChecked()
        icon = QIcon(QPixmap.fromImage(QImage.fromData(self.down_arrow_icon if checked else self.right_arrow_icon)))
        self.toggle_button.setIcon(icon)
        start_val = 0 if checked else self.content_area.maximumHeight()
        end_val = self.content_area.maximumHeight() if checked else 0
        self.animation.setStartValue(start_val)
        self.animation.setEndValue(end_val)
        self.animation.start()
        self.animation_2.setStartValue(start_val)
        self.animation_2.setEndValue(end_val)
        self.animation_2.start()

    def setContentLayout(self, layout):
        if self.content_area.widget():
            self.content_area.widget().deleteLater()

        layout_widget = QWidget()
        layout_widget.setLayout(layout)
        self.content_area.setWidget(layout_widget)

        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        content_height = layout.sizeHint().height()

        self.animation.setEndValue(collapsed_height + content_height)
        self.animation_2.setEndValue(collapsed_height + content_height)
        self.content_area.setMaximumHeight(content_height)

class KeyboardShortcutsDialog(QWidget):
    def __init__(self, parent=None):
        super(KeyboardShortcutsDialog, self).__init__(parent, Qt.Dialog)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        title_label = QLabel("Keyboard Shortcuts")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Shortcuts info
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(10)

        shortcuts = [
            ("Ctrl+Shift+S", "Start Capture"),
            ("Ctrl+Shift+X", "Stop Capture"),
            ("Ctrl+Shift+O", "Open Last Screenshot"),
            ("Ctrl+D", "Toggle Dark/Light Mode"),
            ("Ctrl+H", "Show/Hide Keyboard Shortcuts"),
            ("Ctrl+Q", "Quit Application")
        ]

        for row, (key, desc) in enumerate(shortcuts):
            key_label = QLabel(key)
            key_label.setStyleSheet("""
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-family: monospace;
            """)
            desc_label = QLabel(desc)

            grid.addWidget(key_label, row, 0)
            grid.addWidget(desc_label, row, 1)

        layout.addLayout(grid)
        layout.addStretch()

        close_button = HoverButton(text="Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, 0, Qt.AlignRight)

class ScreenshotApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slide Change Screenshot App')
        self.setGeometry(100, 100, 1000, 700)
        self.previous_screenshot = None
        self.screenshot_interval = 1
        self.is_running = False
        self.base_output_path = str(Path.home() / "Screenshots")
        self.current_date_folder = ""
        self.last_screenshot_path = ""
        self.paused_for_video = False
        self.last_video_check_time = 0
        self.video_check_interval = 5
        # --- Sensitivity ---
        self.sensitivity = 0.02  # Initial sensitivity (2% change)
        self.adaptive_sensitivity = True  # Enable adaptive sensitivity
        self.min_diff_pixels = 5000 # Minimum changed pixels to trigger

        # Load icon data
        self.start_icon_data = self.load_icon_data("start.png")
        self.stop_icon_data = self.load_icon_data("stop.png")
        self.pause_icon_data = self.load_icon_data("pause.png")
        self.save_icon_data = self.load_icon_data("save.png")
        self.error_icon_data = self.load_icon_data("error.png")
        self.browse_icon_data = self.load_icon_data("browse.png")
        self.open_icon_data = self.load_icon_data("open.png")
        self.copy_icon_data = self.load_icon_data("copy.png")
        self.delete_icon_data = self.load_icon_data("delete.png")

        self.notification = NotificationBanner()
        self.keyboard_shortcuts_dialog = None

        # --- Settings ---
        self.settings = QSettings("MyCompany", "ScreenshotApp")

        # Initialize UI elements
        self.progress_spinner = QtWidgets.QLabel()
        self.thumbnail_gallery = QScrollArea()
        self.thumbnail_widget = QWidget()
        self.thumbnail_gallery.setWidget(self.thumbnail_widget)
        self.thumbnail_gallery.setWidgetResizable(True)
        self.thumbnail_layout = QHBoxLayout(self.thumbnail_widget)


        self.history_layout = QVBoxLayout()
        self.thumbnail_area = QWidget()

        self.is_dark_mode = False
        self.mode_toggle_button = HoverButton(text="Toggle Light/Dark Mode")

        self.load_settings()

        # --- UI Setup ---
        self.setup_ui()
        self.apply_stylesheet(self.is_dark_mode)

        # --- Timer ---
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.capture_and_compare)

        # --- Progress Indicator ---
        movie = QtGui.QMovie("spinner.gif")
        self.progress_spinner.setMovie(movie)
        movie.start()
        self.progress_spinner.hide()

        # --- Thumbnail Gallery ---
        self.thumbnail_layout.setAlignment(Qt.AlignLeft)
        self.thumbnail_layout.setSpacing(10)
        self.thumbnail_layout.setContentsMargins(5, 5, 5, 5)

        # --- Screenshot History ---
        self.update_history_list()

        # --- Hotkeys ---
        self.start_hotkey = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+S"), self)
        self.start_hotkey.activated.connect(self.start_capture)
        self.stop_hotkey = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+X"), self)
        self.stop_hotkey.activated.connect(self.stop_capture)
        self.open_hotkey = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+O"), self)
        self.open_hotkey.activated.connect(self.open_last_screenshot)

        # Add new hotkeys
        self.dark_mode_hotkey = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self)
        self.dark_mode_hotkey.activated.connect(self.toggle_mode)
        self.help_hotkey = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+H"), self)
        self.help_hotkey.activated.connect(self.show_keyboard_shortcuts)
        self.quit_hotkey = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self)
        self.quit_hotkey.activated.connect(self.close)

        # --- Mode Toggle Button ---
        self.mode_toggle_button.clicked.connect(self.toggle_mode)

        # Setup drag & drop
        self.setAcceptDrops(True)

        # Context menu for preview
        self.screenshot_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.screenshot_label.customContextMenuRequested.connect(self.show_context_menu)

    def load_icon_data(self, filename):
        """Loads icon data from a file."""
        try:
            with open(filename, "rb") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Icon file '{filename}' not found.")
            return None

    def setup_ui(self):
        # Main layout with splitter
        main_layout = QHBoxLayout(self)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        # --- Screenshot History (Sidebar) ---
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(10, 10, 10, 10)

        # Use a QListWidget for the history
        self.history_list_widget = QListWidget()
        self.history_list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                margin-bottom: 5px;
            }

        """)

        history_layout.addWidget(self.history_list_widget)

        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setWidget(self.history_list_widget)
        history_layout.addWidget(history_scroll)


        self.splitter.addWidget(history_widget)


        # --- Main Content Area ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        self.splitter.addWidget(content_widget)

        # Set initial splitter sizes - 1:3 ratio
        self.splitter.setSizes([250, 750])

        # --- Header with app title and status ---
        header_layout = QHBoxLayout()

        app_title = QLabel("Slide Change Screenshot")
        app_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(app_title)

        header_layout.addStretch()

        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(self.status_label)

        content_layout.addLayout(header_layout)

        # --- Control Panel ---
        control_group = QGroupBox("Capture Controls")
        control_group.setStyleSheet("QGroupBox { padding-top: 15px; }")
        control_layout = QGridLayout()
        control_layout.setColumnStretch(2, 1)
        control_layout.setVerticalSpacing(15)
        control_layout.setHorizontalSpacing(10)

        # Start/Stop buttons with better alignment
        button_layout = QHBoxLayout()

        self.start_button = HoverButton(self.start_icon_data, "Start Capture")
        self.start_button.clicked.connect(self.start_capture)
        button_layout.addWidget(self.start_button)

        self.stop_button = HoverButton(self.stop_icon_data, "Stop Capture")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        button_layout.addStretch()

        control_layout.addLayout(button_layout, 0, 0, 1, 3)

        # Interval settings
        interval_label = QLabel("Capture Interval:")
        interval_label.setToolTip("Set the time interval between screenshots (seconds)")
        control_layout.addWidget(interval_label, 1, 0)

        self.interval_spinbox = QDoubleSpinBox()
        self.interval_spinbox.setRange(0.1, 10.0)
        self.interval_spinbox.setDecimals(1)
        self.interval_spinbox.setValue(self.screenshot_interval)
        self.interval_spinbox.valueChanged.connect(self.update_interval)
        self.interval_spinbox.setStyleSheet("""
            QDoubleSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        control_layout.addWidget(self.interval_spinbox, 1, 1)

        interval_slider = ModernSlider(Qt.Horizontal)
        interval_slider.setRange(1, 100)
        interval_slider.setValue(int(self.screenshot_interval * 10))
        interval_slider.valueChanged.connect(lambda v: self.interval_spinbox.setValue(v / 10))
        control_layout.addWidget(interval_slider, 1, 2)

        # --- Sensitivity Controls (Modified) ---
        sensitivity_label = QLabel("Change Sensitivity:")
        sensitivity_label.setToolTip("Set how sensitive the detector is to changes (lower = more sensitive)")
        control_layout.addWidget(sensitivity_label, 2, 0)

        self.sensitivity_spinbox = QDoubleSpinBox() # Changed to QDoubleSpinBox
        self.sensitivity_spinbox.setRange(0.001, 0.1)  # Range for percentage (0.1% to 10%)
        self.sensitivity_spinbox.setDecimals(3) # Three decimal places for finer control
        self.sensitivity_spinbox.setSingleStep(0.001) # Step by 0.1%
        self.sensitivity_spinbox.setValue(self.sensitivity) # Use self.sensitivity
        self.sensitivity_spinbox.valueChanged.connect(self.update_sensitivity)
        self.sensitivity_spinbox.setStyleSheet("""
            QDoubleSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        control_layout.addWidget(self.sensitivity_spinbox, 2, 1)

        sensitivity_slider = ModernSlider(Qt.Horizontal)
        sensitivity_slider.setRange(1, 100)  # Slider from 0.1% to 10%
        sensitivity_slider.setValue(int(self.sensitivity * 1000))  # Initial slider value
        sensitivity_slider.valueChanged.connect(lambda v: self.sensitivity_spinbox.setValue(v / 1000))
        control_layout.addWidget(sensitivity_slider, 2, 2)



        # Output folder
        output_folder_label = QLabel("Output Folder:")
        output_folder_label.setToolTip("Set the directory where screenshots will be saved")
        control_layout.addWidget(output_folder_label, 3, 0)

        folder_layout = QHBoxLayout()
        self.output_folder_edit = QLineEdit(self.base_output_path)
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f5f5f5;
            }
        """)
        folder_layout.addWidget(self.output_folder_edit)

        self.browse_button = HoverButton(self.browse_icon_data, "Browse...")
        self.browse_button.clicked.connect(self.browse_output_folder)
        folder_layout.addWidget(self.browse_button)

        control_layout.addLayout(folder_layout, 3, 1, 1, 2)

        control_group.setLayout(control_layout)
        content_layout.addWidget(control_group)

        # --- Advanced Settings (Collapsible) ---
        self.advanced_settings_box = ModernCollapsibleBox("Advanced Settings")
        advanced_layout = QHBoxLayout()
        advanced_layout.setContentsMargins(5, 10, 5, 10)

        video_check_label = QLabel("Video Detection Interval (s):")
        video_check_label.setToolTip("Set how often to check for playing video")
        advanced_layout.addWidget(video_check_label)

        self.video_check_spinbox = QSpinBox()
        self.video_check_spinbox.setRange(1, 60)
        self.video_check_spinbox.setValue(self.video_check_interval)
        self.video_check_spinbox.valueChanged.connect(self.update_video_check_interval)
        self.video_check_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        advanced_layout.addWidget(self.video_check_spinbox)

        # Adaptive sensitivity checkbox
        self.adaptive_sensitivity_checkbox = QtWidgets.QCheckBox("Adaptive Sensitivity")
        self.adaptive_sensitivity_checkbox.setChecked(self.adaptive_sensitivity)
        self.adaptive_sensitivity_checkbox.setToolTip("Automatically adjust sensitivity based on image content.")
        self.adaptive_sensitivity_checkbox.stateChanged.connect(self.update_adaptive_sensitivity)
        advanced_layout.addWidget(self.adaptive_sensitivity_checkbox)


        advanced_layout.addStretch()

        # Add keyboard shortcuts button
        self.shortcuts_button = HoverButton(text="Keyboard Shortcuts")
        self.shortcuts_button.clicked.connect(self.show_keyboard_shortcuts)
        advanced_layout.addWidget(self.shortcuts_button)

        self.advanced_settings_box.setContentLayout(advanced_layout)
        content_layout.addWidget(self.advanced_settings_box)

        # --- Screenshot Preview ---
        preview_group = QGroupBox("Screenshot Preview")
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(5, 15, 5, 5)

        self.screenshot_label = QLabel()
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_label.setMinimumHeight(300)
        self.set_default_preview()

       # Use QScrollArea for resizable preview
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.screenshot_label)
        preview_layout.addWidget(scroll_area)
        preview_group.setLayout(preview_layout)
        content_layout.addWidget(preview_group)

        # --- Thumbnail Gallery ---
        thumbnail_group = QGroupBox("Recent Screenshots")
        thumbnail_layout_outer = QVBoxLayout()
        thumbnail_layout_outer.addWidget(self.thumbnail_gallery)
        thumbnail_group.setLayout(thumbnail_layout_outer)
        content_layout.addWidget(thumbnail_group)

        # --- Open Last Screenshot and Spinner ---
        action_layout = QHBoxLayout()
        self.open_button = HoverButton(self.open_icon_data, 'Open Last Screenshot')
        self.open_button.clicked.connect(self.open_last_screenshot)
        self.open_button.setEnabled(False)
        action_layout.addWidget(self.open_button)
        action_layout.addWidget(self.progress_spinner)
        action_layout.addStretch()
        content_layout.addLayout(action_layout)

        # --- Status Area ---
        self.status_label = QLabel("Status: Idle")
        content_layout.addWidget(self.status_label)

        content_layout.addWidget(self.mode_toggle_button)

        # --- Credits ---
        credits_label = QLabel(f"Developed by Gelitha Jayawickrama - {datetime.now().year} - Version 1.1")
        credits_label.setAlignment(Qt.AlignCenter)
        credits_label.setStyleSheet("font-size: 10px; color: #777;")
        content_layout.addWidget(credits_label)


        QToolTip.setFont(QtGui.QFont('Arial', 10))  # Set a global tooltip font



    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.base_output_path)
        if folder:
            self.base_output_path = folder
            self.output_folder_edit.setText(folder)
            self.update_history_list()


    def set_default_preview(self):
        pixmap = QPixmap(1, 1)
        pixmap.fill(Qt.lightGray)
        self.screenshot_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))


    def update_interval(self):
        self.screenshot_interval = self.interval_spinbox.value()
        if self.is_running:
            self.timer.setInterval(int(self.screenshot_interval * 1000))

    def update_sensitivity(self):
        self.sensitivity = self.sensitivity_spinbox.value()

    def update_adaptive_sensitivity(self):
        self.adaptive_sensitivity = self.adaptive_sensitivity_checkbox.isChecked()

    def update_video_check_interval(self):
        self.video_check_interval = self.video_check_spinbox.value()


    def start_capture(self):
        if not os.path.exists(self.base_output_path):
            QMessageBox.critical(self, "Error", "The selected output folder does not exist!")
            return

        self.is_running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.interval_spinbox.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.progress_spinner.show() # Show spinner

        today_str = datetime.now().strftime("%Y.%m.%d")
        self.current_date_folder = os.path.join(self.base_output_path, today_str)
        if not os.path.exists(self.current_date_folder):
            os.makedirs(self.current_date_folder)

        self.timer.start(int(self.screenshot_interval * 1000))
        self.status_label.setText("Status: Capturing...")
        self.notification.showMessage("Capturing started.", self.start_icon_data)



    def stop_capture(self):
        self.is_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.interval_spinbox.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.timer.stop()
        self.status_label.setText("Status: Stopped")
        self.notification.showMessage("Capturing stopped.", self.stop_icon_data)
        self.paused_for_video = False
        self.progress_spinner.hide()  # Hide spinner



    def is_video_playing(self):
        current_time = time.time()
        if current_time - self.last_video_check_time < self.video_check_interval:
            return self.paused_for_video

        self.last_video_check_time = current_time

        try:
            screenshot1 = pyautogui.screenshot()
            screenshot1_np = np.array(screenshot1)
            screenshot1_gray = cv2.cvtColor(screenshot1_np, cv2.COLOR_BGR2GRAY)

            time.sleep(0.5)

            screenshot2 = pyautogui.screenshot()
            screenshot2_np = np.array(screenshot2)
            screenshot2_gray = cv2.cvtColor(screenshot2_np, cv2.COLOR_BGR2GRAY)

            diff = cv2.absdiff(screenshot1_gray, screenshot2_gray)
            _, diff = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            non_zero_count = np.count_nonzero(diff)

            if non_zero_count > self.sensitivity * 5:
                self.paused_for_video = True
                return True
            else:
                self.paused_for_video = False
                return False
        except Exception as e:
            print(f"Error in video detection: {e}")
            self.paused_for_video = False
            return False
    def _calculate_adaptive_sensitivity(self, image):
        """Calculates an adaptive sensitivity based on image content."""
        # Convert the image to grayscale if it's not already
        if len(image.shape) == 3:  # Check if it's a color image (3 channels)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image  # Already grayscale

        # Calculate the standard deviation of the pixel intensities
        std_dev = np.std(gray)

        #  sensitivity based on the standard deviation.
        #  Higher std_dev (more variation) -> lower sensitivity
        #  Lower std_dev (less variation) -> higher sensitivity
        adaptive_sensitivity = max(0.001, min(0.05, 0.03 - (std_dev / 255) * 0.02 )) # scale and clamp

        return adaptive_sensitivity

    def capture_and_compare(self):
        if not self.is_running:
            return

        if self.is_video_playing():
            self.status_label.setText("Status: Paused (video detected)")
            self.notification.showMessage("Video detected. Capture paused.", self.pause_icon_data)
            return
        elif self.paused_for_video:
            self.status_label.setText("Status: Capturing...")
            self.notification.showMessage("Capturing resumed.", self.start_icon_data)


        try:
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

            if self.previous_screenshot is not None:
                diff = cv2.absdiff(self.previous_screenshot, screenshot_gray)
                _, diff_binary = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                non_zero_count = np.count_nonzero(diff_binary)

                # Get the dimensions of the screenshot
                height, width = screenshot_gray.shape
                total_pixels = height * width

                # Calculate the percentage of changed pixels
                percent_changed = (non_zero_count / total_pixels) * 100

                # --- Adaptive Sensitivity Logic ---
                if self.adaptive_sensitivity:
                    current_sensitivity = self._calculate_adaptive_sensitivity(screenshot_gray)
                    self.sensitivity_spinbox.setValue(current_sensitivity) # Update the spinbox
                else:
                    current_sensitivity = self.sensitivity

                # Check if the change is significant
                if percent_changed > current_sensitivity and non_zero_count > self.min_diff_pixels :
                    filename = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                    filepath = os.path.join(self.current_date_folder, filename)
                    screenshot.save(filepath)
                    self.notification.showMessage(f'Screenshot saved: {filename}', self.save_icon_data)
                    self.last_screenshot_path = filepath
                    self.update_preview(filepath)
                    self.open_button.setEnabled(True)
                    self.add_to_history(filepath)
                    self.add_thumbnail(filepath)

            self.previous_screenshot = screenshot_gray

        except Exception as e:
            self.notification.showMessage(f"Error: {e}", self.error_icon_data)
            self.stop_capture()


    def update_preview(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.notification.showMessage(f"Error loading image: {os.path.basename(image_path)}", self.error_icon_data)
            return
        self.screenshot_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))

    def add_thumbnail(self, image_path):
        """Adds a thumbnail to the gallery."""
        thumbnail_card = ThumbnailCard(image_path)
        thumbnail_card.clicked.connect(self.thumbnail_clicked_card)
        self.thumbnail_layout.addWidget(thumbnail_card)


    def thumbnail_clicked_card(self, image_path):
        """Opens the full image when a thumbnail card is clicked."""
        self.update_preview(image_path)
        self.open_image(image_path)

    def open_last_screenshot(self):
        if self.last_screenshot_path:
            self.open_image(self.last_screenshot_path)
        else:
            QMessageBox.information(self, "Information", "No screenshot to open.")

    def open_image(self, image_path):
        """Opens the image using the default system viewer."""
        if os.path.exists(image_path):
            try:
                if sys.platform == "win32":
                    os.startfile(image_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", image_path], check=True)
                else:
                    subprocess.run(["xdg-open", image_path], check=True)
            except (OSError, subprocess.CalledProcessError) as e:
                self.notification.showMessage(f"Error opening image: {e}", self.error_icon_data)
                QMessageBox.critical(self, "Error", f"Could not open image: {e}")
        else:
             QMessageBox.critical(self, "Error", f"File does not exist: {image_path}")

    def add_to_history(self, filepath):
        pass

    def update_history_list(self):
        """Updates the history list with collapsible date and hour sections."""

        # Clear existing items from the QListWidget
        self.history_list_widget.clear()

        if not os.path.exists(self.base_output_path):
            return

        dated_files = {}

        # Gather files and group them by date and hour
        for date_folder in sorted(os.listdir(self.base_output_path), reverse=True):
            date_path = os.path.join(self.base_output_path, date_folder)
            if os.path.isdir(date_path):
                for filename in os.listdir(date_path):
                    if filename.endswith(".png"):
                        filepath = os.path.join(date_path, filename)
                        try:
                            dt = datetime.strptime(filename, "screenshot_%Y%m%d_%H%M%S.png")
                            date_str = dt.strftime("%Y.%m.%d")
                            hour_str = dt.strftime("%H")
                            if date_str not in dated_files:
                                dated_files[date_str] = {}
                            if hour_str not in dated_files[date_str]:
                                dated_files[date_str][hour_str] = []
                            dated_files[date_str][hour_str].append((filepath, filename))
                        except ValueError:
                            print(f"Skipping file with unexpected name format: {filename}")
                            continue

        # Create QListWidgetItems
        for date_str in sorted(dated_files.keys(), reverse=True):
            date_item = QListWidgetItem(date_str)
            date_item.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
            self.history_list_widget.addItem(date_item)

            for hour_str in sorted(dated_files[date_str].keys(), reverse=True):
                hour_item = QListWidgetItem(f"  Hour: {hour_str}")
                hour_item.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Bold))
                self.history_list_widget.addItem(hour_item)

                for filepath, filename in sorted(dated_files[date_str][hour_str], key=lambda x: x[1], reverse=True):
                    file_item = QListWidgetItem(f"    {filename}")
                    file_item.setData(Qt.UserRole, filepath)
                    file_item.setFont(QtGui.QFont("Arial", 10))
                    file_item.setToolTip(filepath)
                    self.history_list_widget.addItem(file_item)

        self.history_list_widget.itemClicked.connect(self.history_item_clicked)

    def history_item_clicked(self, item):
        filepath = item.data(Qt.UserRole)
        if filepath:
            self.open_image(filepath)


    def closeEvent(self, event):
        """Saves settings before closing the application."""
        self.save_settings()
        super().closeEvent(event)

    def load_settings(self):
        """Loads application settings."""
        self.base_output_path = self.settings.value("output_folder", self.base_output_path)
        self.screenshot_interval = float(self.settings.value("interval", self.screenshot_interval))
        self.sensitivity = float(self.settings.value("sensitivity", self.sensitivity))  # Load as float
        self.video_check_interval = int(self.settings.value("video_check_interval", self.video_check_interval))
        self.adaptive_sensitivity = self.settings.value("adaptive_sensitivity", self.adaptive_sensitivity, type=bool)


        # Load window geometry and state
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

    def save_settings(self):
        """Saves application settings."""
        self.settings.setValue("output_folder", self.base_output_path)
        self.settings.setValue("interval", self.screenshot_interval)
        self.settings.setValue("sensitivity", self.sensitivity)  # Save as float
        self.settings.setValue("video_check_interval", self.video_check_interval)
        self.settings.setValue("adaptive_sensitivity", self.adaptive_sensitivity)
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    def show_keyboard_shortcuts(self):
        """Shows the keyboard shortcuts dialog."""
        if self.keyboard_shortcuts_dialog is None:
            self.keyboard_shortcuts_dialog = KeyboardShortcutsDialog(self)
        self.keyboard_shortcuts_dialog.show()

    def show_context_menu(self, position):
        """Displays a context menu for the screenshot preview."""
        menu = QMenu(self)

        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self.open_image(self.last_screenshot_path))
        menu.addAction(open_action)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_image_to_clipboard)
        menu.addAction(copy_action)

        if self.last_screenshot_path:
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(self.delete_current_screenshot)
            menu.addAction(delete_action)


        menu.exec_(self.screenshot_label.mapToGlobal(position))

    def copy_image_to_clipboard(self):
        """Copies the currently displayed screenshot to the clipboard."""
        if self.screenshot_label.pixmap():
            QApplication.clipboard().setPixmap(self.screenshot_label.pixmap())
            self.notification.showMessage("Image copied to clipboard.", self.copy_icon_data)
        else:
            QMessageBox.information(self, "Information", "No image to copy.")


    def delete_current_screenshot(self):
        """Deletes the currently displayed screenshot."""
        if self.last_screenshot_path and os.path.exists(self.last_screenshot_path):
            reply = QMessageBox.question(self, "Delete Screenshot",
                                         "Are you sure you want to delete this screenshot?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    os.remove(self.last_screenshot_path)
                    self.notification.showMessage("Screenshot deleted.", self.delete_icon_data)
                    self.last_screenshot_path = ""
                    self.set_default_preview()
                    self.open_button.setEnabled(False)
                    self.update_history_list()
                    self.remove_thumbnail(self.last_screenshot_path)

                except OSError as e:
                    QMessageBox.critical(self, "Error", f"Could not delete file: {e}")
        else:
            QMessageBox.information(self, "Information", "No screenshot to delete.")

    def remove_thumbnail(self, image_path):
        """Removes the corresponding thumbnail from the gallery."""
        for i in range(self.thumbnail_layout.count()):
            widget = self.thumbnail_layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailCard) and widget.image_path == image_path:
                widget.deleteLater()
                break


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.update_preview(file_path)
                self.last_screenshot_path = file_path
                self.open_button.setEnabled(True)
            else:
                QMessageBox.warning(self, "Unsupported File", "Only image files are supported.")


    def apply_stylesheet(self, dark_mode=False):
        if dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #333;
                    color: #eee;
                }
                QGroupBox {
                    border: 1px solid #555;
                    border-radius: 5px;
                    margin-top: 1ex; /* Make room for title */
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left; /* Position at the top-left */
                    padding: 0 5px;
                    background-color: #444;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;

                }

                QPushButton {
                    background-color: #444;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
                QPushButton:pressed {
                    background-color: #666;
                }
                QPushButton:disabled {
                    background-color: #222;
                    color: #777;
                }
                QSpinBox, QDoubleSpinBox, QLineEdit {
                    background-color: #444;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 2px;
                }

               QToolTip {
                    background-color: #2a2a2a;
                    color: white;
                    border: 1px solid #767676;
                }
                QListWidget {
                    background-color: #444;
                    border: 1px solid #555;
                }

                QListWidget::item:selected {
                    background: #666;
                    color: white;
                }
                QScrollArea {
                    border: none;
                }
            """)
        else:
              self.setStyleSheet("""
                QWidget {
                    background-color: #eee;
                    color: #333;
                }
                QGroupBox {
                    border: 1px solid #aaa;
                    border-radius: 5px;
                    margin-top: 1ex; /* Make room for title */
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left; /* Position at the top-left */
                    padding: 0 5px;
                    background-color: #ddd;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }

                QPushButton {
                    background-color: #ddd;
                    border: 1px solid #aaa;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #ccc;
                }
                QPushButton:pressed {
                    background-color: #bbb;
                }

                QPushButton:disabled {
                    background-color: #ccc;
                    color: #888
                }
                QSpinBox, QDoubleSpinBox, QLineEdit {
                    background-color: #fff;
                    border: 1px solid #aaa;
                    border-radius: 4px;
                    padding: 2px;
                }
                QToolTip {
                    background-color: #ffffe0;
                    color: black;
                    border: black 1px solid;
                }
                QListWidget{
                   background-color: #fff;
                   border: 1px solid #aaa;
                }
                QListWidget::item:selected {
                    background: #bbb;
                    color: black;
                }
                QScrollArea {
                    border: none;
                }

              """)
    def toggle_mode(self):
        """Toggles between dark and light mode."""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_stylesheet(self.is_dark_mode)
        # Update icons for the notification banner
        if self.is_dark_mode:
            self.notification.close_btn.setStyleSheet("""
                QPushButton {
                    color: #eee;
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #ccc;
                }
            """)
        else:
             self.notification.close_btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #ccc;
                }
            """)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec_())