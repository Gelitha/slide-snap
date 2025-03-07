import sys
import time
import numpy as np
import cv2
import pyautogui
from PyQt5 import QtWidgets, QtGui, QtCore
from datetime import datetime
import os
import subprocess
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QSettings, QPoint, QEasingCurve
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPalette
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDoubleSpinBox, QSpinBox, QLineEdit, QFileDialog, QGroupBox,
                             QScrollArea, QListWidget, QListWidgetItem, QMessageBox, QToolTip,
                             QStyleFactory, QFrame)

class ModernCollapsibleBox(QtWidgets.QWidget):
    def __init__(self, title="", parent=None):
        super(ModernCollapsibleBox, self).__init__(parent)

        self.toggle_button = QtWidgets.QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("""
            QToolButton {
                border: none;
                font-size: 14px;
                font-weight: bold;
                color: #444; /* Adjust text color */
                text-align: left;
                padding: 5px;
            }
            QToolButton:checked {
                background-color: #e0e0e0; /* Light background when expanded */
            }
        """)
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setIcon(QIcon("right_arrow.png"))  # Initial arrow icon
        self.toggle_button.setIconSize(QtCore.QSize(16, 16)) # Icon size
        self.toggle_button.clicked.connect(self.on_clicked)

        self.content_area = QtWidgets.QScrollArea(maximumHeight=0, minimumHeight=0)
        self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.content_area.setWidgetResizable(True)  # Important for proper resizing

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)

        self.animation = QPropertyAnimation(self, b"minimumHeight")
        self.animation.setDuration(250)  #  ms, slightly faster
        self.animation.setEasingCurve(QEasingCurve.InOutCubic) # Smoother animation
        self.animation_2 = QPropertyAnimation(self, b"maximumHeight")
        self.animation_2.setDuration(250)
        self.animation_2.setEasingCurve(QEasingCurve.InOutCubic)

    @QtCore.pyqtSlot()
    def on_clicked(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setIcon(QIcon("down_arrow.png" if checked else "right_arrow.png"))
        start_val = 0 if checked else self.content_area.maximumHeight()
        end_val = self.content_area.maximumHeight() if checked else 0
        self.animation.setStartValue(start_val)
        self.animation.setEndValue(end_val)
        self.animation.start()
        self.animation_2.setStartValue(start_val)
        self.animation_2.setEndValue(end_val)
        self.animation_2.start()


    def setContentLayout(self, layout):
        # Make sure any existing layout is removed first
        old_layout = self.content_area.layout()
        if old_layout:
            QWidget().setLayout(old_layout)  # Transfer ownership

        # Set the new layout to the content area
        layout_widget = QWidget()
        layout_widget.setLayout(layout)
        self.content_area.setWidget(layout_widget)

        # Calculate the proper height
        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        content_height = layout.sizeHint().height()

        # Set animation end values
        self.animation.setEndValue(collapsed_height + content_height)
        self.animation_2.setEndValue(collapsed_height + content_height)
        self.content_area.setMaximumHeight(content_height)

class ScreenshotApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slide Change Screenshot App')
        self.setGeometry(100, 100, 1000, 700)  # Increased size for better layout
        self.previous_screenshot = None
        self.screenshot_interval = 1
        self.is_running = False
        self.base_output_path = r"F:\ss"
        self.current_date_folder = ""
        self.last_screenshot_path = ""
        self.paused_for_video = False
        self.last_video_check_time = 0
        self.video_check_interval = 5
        self.sensitivity = 5000

        # --- Settings ---
        self.settings = QSettings("MyCompany", "ScreenshotApp")

        # Initialize UI elements *BEFORE* calling setup_ui()
        self.progress_spinner = QtWidgets.QLabel()
        self.thumbnail_gallery = QListWidget()
        #self.history_list = QListWidget() # Remove QListWidget
        self.history_layout = QVBoxLayout() # Add history layout

        self.is_dark_mode = False
        self.mode_toggle_button = QPushButton("Toggle Mode")  # Create button here

        self.load_settings()  # load settings after creating UI elements used in settings

        # --- UI Setup ---
        self.setup_ui()  # Now setup_ui can access all UI elements
        #self.apply_stylesheet() # Remove to set style in one function
        self.set_modern_style()  # Apply the modern style


        # --- Timer ---
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.capture_and_compare)

        # --- Progress Indicator ---
        movie = QtGui.QMovie("spinner.gif")  # Make sure you have spinner.gif
        self.progress_spinner.setMovie(movie)
        movie.start()
        self.progress_spinner.hide()

        # --- Thumbnail Gallery ---
        self.thumbnail_gallery.setIconSize(QtCore.QSize(120, 90)) # Slightly larger
        self.thumbnail_gallery.setFlow(QListWidget.LeftToRight)  # Horizontal flow
        self.thumbnail_gallery.setSpacing(5) # Add spacing between thumbnails
        self.thumbnail_gallery.itemClicked.connect(self.thumbnail_clicked)

        # --- Screenshot History ---
        #self.history_list.itemClicked.connect(self.history_item_clicked) # Remove itemClicked
        self.update_history_list()

        # --- Hotkeys ---
        self.start_hotkey = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+S"), self)
        self.start_hotkey.activated.connect(self.start_capture)
        self.stop_hotkey = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+X"), self)
        self.stop_hotkey.activated.connect(self.stop_capture)
        self.open_hotkey = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+O"), self)
        self.open_hotkey.activated.connect(self.open_last_screenshot)

        # --- Mode Toggle Button ---
        self.mode_toggle_button.clicked.connect(self.toggle_mode)  # Connect signal after button is created



    def setup_ui(self):
        main_layout = QHBoxLayout(self)  # Main layout: History | Main Content

        # --- Screenshot History (Sidebar) ---
        history_group = QGroupBox("Screenshot History")
        #history_layout = QVBoxLayout() # Already declared in __init__
        history_group.setLayout(self.history_layout)  # Use self.history_layout
        history_group.setFixedWidth(250)  # Wider sidebar
        main_layout.addWidget(history_group)

        # --- Main Content Area ---
        content_layout = QVBoxLayout()


        # --- Main Label ---
        self.label = QLabel('Ready to capture. Press Start.')
        self.label.setStyleSheet("font-size: 16px;") # Larger font
        content_layout.addWidget(self.label)

        # --- Control Panel (Grouped) ---
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout()

        # --- Row 1: Start/Stop, Interval ---
        row1_layout = QHBoxLayout()

        self.start_button = QPushButton(QIcon("start.png"), "Start")
        self.start_button.clicked.connect(self.start_capture)
        self.set_button_style(self.start_button)
        row1_layout.addWidget(self.start_button)

        self.stop_button = QPushButton(QIcon("stop.png"), "Stop")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        self.set_button_style(self.stop_button)
        row1_layout.addWidget(self.stop_button)


        interval_label = QLabel("Interval (s):")
        interval_label.setToolTip("Set the time interval between screenshots.")
        row1_layout.addWidget(interval_label)
        self.interval_spinbox = QDoubleSpinBox()
        self.interval_spinbox.setRange(0.1, 10.0)
        self.interval_spinbox.setDecimals(1) # Limit decimals
        self.interval_spinbox.setValue(self.screenshot_interval)
        self.interval_spinbox.valueChanged.connect(self.update_interval)
        row1_layout.addWidget(self.interval_spinbox)
        row1_layout.addStretch()
        control_layout.addLayout(row1_layout)


        # --- Row 2: Sensitivity, Output Folder ---
        row2_layout = QHBoxLayout()

        sensitivity_label = QLabel("Sensitivity:")
        sensitivity_label.setToolTip("Set the sensitivity for change detection (higher = more sensitive).")
        row2_layout.addWidget(sensitivity_label)
        self.sensitivity_spinbox = QSpinBox()
        self.sensitivity_spinbox.setRange(1000, 50000)
        self.sensitivity_spinbox.setValue(self.sensitivity)
        self.sensitivity_spinbox.setSingleStep(100)
        self.sensitivity_spinbox.valueChanged.connect(self.update_sensitivity)
        row2_layout.addWidget(self.sensitivity_spinbox)


        output_folder_label = QLabel("Output Folder:")
        output_folder_label.setToolTip("Set the directory to save screenshots.")
        row2_layout.addWidget(output_folder_label)
        self.output_folder_edit = QLineEdit(self.base_output_path)
        self.output_folder_edit.setReadOnly(True)
        row2_layout.addWidget(self.output_folder_edit)
        self.browse_button = QPushButton(QIcon("browse.png"), "Browse...")
        self.browse_button.clicked.connect(self.browse_output_folder)
        self.set_button_style(self.browse_button)
        row2_layout.addWidget(self.browse_button)
        row2_layout.addStretch()
        control_layout.addLayout(row2_layout)
        control_group.setLayout(control_layout)
        content_layout.addWidget(control_group)


        # --- Advanced Settings (Collapsible) ---
        self.advanced_settings_box = ModernCollapsibleBox("Advanced Settings")
        advanced_layout = QHBoxLayout()
        video_check_label = QLabel("Video Check Interval (s):")
        video_check_label.setToolTip("Set the interval for video detection.")
        self.video_check_spinbox = QSpinBox()
        self.video_check_spinbox.setRange(1, 60)
        self.video_check_spinbox.setValue(self.video_check_interval)
        self.video_check_spinbox.valueChanged.connect(self.update_video_check_interval)
        advanced_layout.addWidget(video_check_label)
        advanced_layout.addWidget(self.video_check_spinbox)
        advanced_layout.addStretch()
        self.advanced_settings_box.setContentLayout(advanced_layout)
        content_layout.addWidget(self.advanced_settings_box)


        # --- Screenshot Preview (Resizable) ---
        preview_group = QGroupBox("Screenshot Preview")
        preview_layout = QVBoxLayout()
        self.screenshot_label = QLabel()
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.set_default_preview()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.screenshot_label)
        preview_layout.addWidget(scroll_area)
        preview_group.setLayout(preview_layout)
        content_layout.addWidget(preview_group)

        # --- Thumbnail Gallery ---
        thumbnail_group = QGroupBox("Recent Screenshots")
        thumbnail_layout = QVBoxLayout()
        thumbnail_layout.addWidget(self.thumbnail_gallery)
        thumbnail_group.setLayout(thumbnail_layout)
        content_layout.addWidget(thumbnail_group)


        # --- Open Last Screenshot and Spinner ---
        action_layout = QHBoxLayout()
        self.open_button = QPushButton(QIcon("open.png"), 'Open Last Screenshot')
        self.open_button.clicked.connect(self.open_last_screenshot)
        self.open_button.setEnabled(False)
        self.set_button_style(self.open_button)
        action_layout.addWidget(self.open_button)
        action_layout.addWidget(self.progress_spinner)
        action_layout.addStretch()
        content_layout.addLayout(action_layout)

        # --- Status Area ---
        self.status_label = QLabel("Status: Idle")
        content_layout.addWidget(self.status_label)

        content_layout.addWidget(self.mode_toggle_button)

        main_layout.addLayout(content_layout)
        main_layout.setStretch(0, 0)  # History sidebar no stretch
        main_layout.setStretch(1, 1)  # Main content area takes up remaining space

        QToolTip.setFont(QtGui.QFont('Arial', 10))

    def set_button_style(self, button):
        button.setFixedWidth(150)
        button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #ddd;
                color: #999;
            }
        """)
    def set_modern_style(self):
        """Applies a more modern, platform-adaptive style."""

        # Use a platform-specific style as the base
        app.setStyle(QStyleFactory.create("Fusion"))  # A good cross-platform choice

        # Create a palette for more fine-grained control
        palette = QPalette()

        # --- Base Colors (adjust these to your preference) ---
        if self.is_dark_mode:
            base_color = QColor(45, 45, 45)          # Dark gray
            text_color = QColor(220, 220, 220)      # Light gray
            highlight_color = QColor(70, 130, 180)    # Steel blue
            button_color = QColor(65, 65, 65)         # Slightly lighter gray
            disabled_color = QColor(120, 120, 120)  # Medium gray (for disabled text)

        else: # Light mode
            base_color = QColor(240, 240, 240)     # Light gray
            text_color = QColor(50, 50, 50)        # Dark gray
            highlight_color = QColor(0, 120, 215)    # A standard blue
            button_color = QColor(230, 230, 230)     # Slightly lighter than base
            disabled_color = QColor(160,160,160)

        # --- Set Palette Colors ---
        palette.setColor(QPalette.Window, base_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, base_color.darker(110))  # Slightly darker for input fields
        palette.setColor(QPalette.AlternateBase, base_color)
        palette.setColor(QPalette.ToolTipBase, base_color.darker(150)) # Darker tooltip
        palette.setColor(QPalette.ToolTipText, text_color)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, button_color)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.BrightText, Qt.red)  # For errors, etc.
        palette.setColor(QPalette.Link, highlight_color)
        palette.setColor(QPalette.Highlight, highlight_color)
        palette.setColor(QPalette.HighlightedText, Qt.white) # Text color when highlighted
        palette.setColor(QPalette.Disabled, QPalette.Text, disabled_color)  # Disabled text
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_color)

        app.setPalette(palette)  # Apply the palette to the entire application

        # --- General Stylesheet (for elements not fully controlled by Palette) ---
        widget_stylesheet = f"""
            QGroupBox {{
                border: 1px solid {base_color.darker(120).name()};
                border-radius: 5px;
                margin-top: 1ex; /* Make room for title */
                font-size: 14px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left; /* Position at the top-left */
                padding: 0 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            QSpinBox, QDoubleSpinBox, QLineEdit {{
                border: 1px solid {base_color.darker(120).name()};
                border-radius: 4px;
                padding: 3px;
                font-size: 13px;
                background-color: {base_color.darker(110).name()};
            }}

            QToolTip {{
                border: 1px solid {base_color.darker(150).name()};
                padding: 2px;
                font-size: 12px;
                background-color: {base_color.darker(150).name()};
                color: {text_color.name()};
            }}
            QListWidget {{
                border: 1px solid {base_color.darker(120).name()};
                font-size: 13px;
            }}
            QListWidget::item:selected {{
                background: {highlight_color.name()};
                color: white;
            }}
            QScrollArea {{
                border: none;
            }}
            /* Style for the file buttons in the history */
            QPushButton#fileButton {{
                text-align: left;
                padding: 4px;
                border: none;
                border-bottom: 1px solid {base_color.darker(110).name()}; /* subtle separator */
                background-color: transparent;
                font-size: 12px;
            }}
            QPushButton#fileButton:hover {{
                background-color: {base_color.darker(115).name()};
            }}

        """
        self.setStyleSheet(widget_stylesheet)
        self.mode_toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 13px;
                    margin-top: 5px
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.base_output_path)
        if folder:
            self.base_output_path = folder
            self.output_folder_edit.setText(folder)


    def set_default_preview(self):
        pixmap = QPixmap(1, 1)
        pixmap.fill(Qt.lightGray)  # Or any placeholder color
        self.screenshot_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))


    def update_interval(self):
        self.screenshot_interval = self.interval_spinbox.value()
        if self.is_running:
            self.timer.setInterval(int(self.screenshot_interval * 1000))

    def update_sensitivity(self):
        self.sensitivity = self.sensitivity_spinbox.value()

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
        self.progress_spinner.show()

        today_str = datetime.now().strftime("%Y.%m.%d")
        self.current_date_folder = os.path.join(self.base_output_path, today_str)
        if not os.path.exists(self.current_date_folder):
            os.makedirs(self.current_date_folder)

        self.timer.start(int(self.screenshot_interval * 1000))
        self.status_label.setText("Status: Capturing...")
        self.label.setText("Capturing started.")


    def stop_capture(self):
        self.is_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.interval_spinbox.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.timer.stop()
        self.status_label.setText("Status: Stopped")
        self.label.setText("Capturing stopped.")
        self.paused_for_video = False
        self.progress_spinner.hide()



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

    def capture_and_compare(self):
        if not self.is_running:
            return

        if self.is_video_playing():
            self.status_label.setText("Status: Paused (video detected)")
            self.label.setText("Video detected. Capture paused.")
            return
        elif self.paused_for_video:
            self.status_label.setText("Status: Capturing...")
            self.label.setText("Capturing resumed.")


        try:
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

            if self.previous_screenshot is not None:
                diff = cv2.absdiff(self.previous_screenshot, screenshot_gray)
                _, diff = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                non_zero_count = np.count_nonzero(diff)

                if non_zero_count > self.sensitivity:
                    filename = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                    filepath = os.path.join(self.current_date_folder, filename)
                    screenshot.save(filepath)
                    self.label.setText(f'Screenshot saved: {filepath}')
                    self.last_screenshot_path = filepath
                    self.update_preview(filepath)
                    self.open_button.setEnabled(True)
                    self.add_to_history(filepath)
                    self.add_thumbnail(filepath)

            self.previous_screenshot = screenshot_gray

        except Exception as e:
            self.label.setText(f"Error during capture/compare: {e}")
            self.stop_capture()


    def update_preview(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.label.setText(f"Error loading image: {image_path}")
            return
        self.screenshot_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))

    def add_thumbnail(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return

        item = QListWidgetItem(QIcon(pixmap.scaled(120, 90, Qt.KeepAspectRatio)), "")
        item.setData(Qt.UserRole, image_path)
        self.thumbnail_gallery.addItem(item)

    def thumbnail_clicked(self, item):
        image_path = item.data(Qt.UserRole)
        self.update_preview(image_path)
        self.open_image(image_path)


    def open_last_screenshot(self):
        if self.last_screenshot_path:
            self.open_image(self.last_screenshot_path)
        else:
            self.label.setText("No screenshot to open.")
            QMessageBox.information(self, "Information", "No screenshot to open.")

    def open_image(self, image_path):
        if os.path.exists(image_path):
            try:
                if sys.platform == "win32":
                    os.startfile(image_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", image_path], check=True)
                else:
                    subprocess.run(["xdg-open", image_path], check=True)
            except (OSError, subprocess.CalledProcessError) as e:
                self.label.setText(f"Error opening image: {e}")
                QMessageBox.critical(self, "Error", f"Could not open image: {e}")
        else:
             QMessageBox.critical(self, "Error", f"File does not exist: {image_path}")

    def add_to_history(self, filepath):
        filename = os.path.basename(filepath)
        # No need to add to a list widget directly, just store the path

    def update_history_list(self):
        for i in reversed(range(self.history_layout.count())):
            widget = self.history_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()


        if not os.path.exists(self.base_output_path):
            return

        dated_files = {}

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

        for date_str in sorted(dated_files.keys(), reverse=True):
            date_box = ModernCollapsibleBox(title=date_str)
            date_layout = QVBoxLayout()

            for hour_str in sorted(dated_files[date_str].keys(), reverse=True):
                hour_box = ModernCollapsibleBox(title=f"Hour: {hour_str}")
                hour_layout = QVBoxLayout()

                for filepath, filename in sorted(dated_files[date_str][hour_str], key=lambda x: x[1], reverse=True):
                    file_button = QPushButton(filename)
                    file_button.setObjectName("fileButton") # Set object name for styling
                    file_button.clicked.connect(lambda checked, fp=filepath: self.open_image(fp))
                    #self.set_button_style(file_button) # Use stylesheet instead
                    hour_layout.addWidget(file_button)
                hour_box.setContentLayout(hour_layout)
                date_layout.addWidget(hour_box)

            date_box.setContentLayout(date_layout)
            self.history_layout.addWidget(date_box)
        self.history_layout.addStretch()



    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def load_settings(self):
            self.base_output_path = self.settings.value("output_folder", self.base_output_path)
            self.screenshot_interval = float(self.settings.value("interval", self.screenshot_interval))
            self.sensitivity = int(self.settings.value("sensitivity", self.sensitivity))
            self.video_check_interval = int(self.settings.value("video_check_interval", self.video_check_interval))

            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)

            window_state = self.settings.value("windowState")
            if window_state:
                self.restoreState(window_state)

            # Load dark/light mode setting
            self.is_dark_mode = self.settings.value("dark_mode", False, type=bool)

    def save_settings(self):
        self.settings.setValue("output_folder", self.base_output_path)
        self.settings.setValue("interval", self.screenshot_interval)
        self.settings.setValue("sensitivity", self.sensitivity)
        self.settings.setValue("video_check_interval", self.video_check_interval)
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("dark_mode", self.is_dark_mode) # Save dark mode


    def toggle_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.set_modern_style() # Re-apply the style


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScreenshotApp()

    # Load resources (icons).  Make sure these files exist!
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    icon_path_right = os.path.join(application_path, "right_arrow.png")
    icon_path_down = os.path.join(application_path, "down_arrow.png")

    # Check for the existence of icon files
    if not (os.path.exists(icon_path_right) and os.path.exists(icon_path_down)):
        print("Error: Icon files (right_arrow.png, down_arrow.png) not found.")
        # You could show a message box here to inform the user.
        # And potentially exit the application, or fall back to default icons.
        # sys.exit(1)  # Or handle the error more gracefully

    window.show()
    sys.exit(app.exec_())