import sys
import time
import numpy as np
import cv2
import pyautogui
from PyQt5 import QtWidgets, QtGui, QtCore
from datetime import datetime
import os
import subprocess

class ScreenshotApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slide Change Screenshot App')
        self.setGeometry(100, 100, 800, 600)
        self.previous_screenshot = None
        self.screenshot_interval = 1  # seconds
        self.is_running = False
        self.base_output_path = r"F:\ss"  # Initial default path
        self.current_date_folder = ""
        self.last_screenshot_path = ""
        self.paused_for_video = False
        self.last_video_check_time = 0
        self.video_check_interval = 5  # seconds
        self.setup_ui()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.capture_and_compare)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # Main Label
        self.label = QtWidgets.QLabel('Ready to capture. Press Start.')
        layout.addWidget(self.label)

        # --- Control Panel ---
        control_layout = QtWidgets.QVBoxLayout() # Changed to VBoxLayout for better vertical arrangement

        # --- Row 1:  Start/Stop, Interval ---
        row1_layout = QtWidgets.QHBoxLayout()

        # Start Button
        self.start_button = QtWidgets.QPushButton('Start')
        self.start_button.clicked.connect(self.start_capture)
        row1_layout.addWidget(self.start_button)

        # Stop Button
        self.stop_button = QtWidgets.QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        row1_layout.addWidget(self.stop_button)

        # Interval Setting
        interval_label = QtWidgets.QLabel("Interval (s):")
        row1_layout.addWidget(interval_label)
        self.interval_spinbox = QtWidgets.QDoubleSpinBox()
        self.interval_spinbox.setRange(0.1, 10.0)
        self.interval_spinbox.setValue(self.screenshot_interval)
        self.interval_spinbox.valueChanged.connect(self.update_interval)
        row1_layout.addWidget(self.interval_spinbox)

        control_layout.addLayout(row1_layout)


        # --- Row 2: Sensitivity, Output Folder ---
        row2_layout = QtWidgets.QHBoxLayout()

        # Sensitivity Setting
        sensitivity_label = QtWidgets.QLabel("Sensitivity:")
        row2_layout.addWidget(sensitivity_label)
        self.sensitivity_spinbox = QtWidgets.QSpinBox()
        self.sensitivity_spinbox.setRange(1000, 50000)
        self.sensitivity_spinbox.setValue(5000)
        self.sensitivity_spinbox.setSingleStep(100)
        row2_layout.addWidget(self.sensitivity_spinbox)

        # Output Folder
        output_folder_label = QtWidgets.QLabel("Output Folder:")
        row2_layout.addWidget(output_folder_label)
        self.output_folder_edit = QtWidgets.QLineEdit(self.base_output_path)
        self.output_folder_edit.setReadOnly(True) # Make it read-only initially
        row2_layout.addWidget(self.output_folder_edit)
        self.browse_button = QtWidgets.QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_output_folder)
        row2_layout.addWidget(self.browse_button)

        control_layout.addLayout(row2_layout)
        layout.addLayout(control_layout) # Add the entire control panel


        # --- Screenshot Preview ---
        self.screenshot_label = QtWidgets.QLabel()
        self.screenshot_label.setAlignment(QtCore.Qt.AlignCenter)
        self.set_default_preview()
        layout.addWidget(self.screenshot_label)

        # Open Last Screenshot Button
        self.open_button = QtWidgets.QPushButton('Open Last Screenshot')
        self.open_button.clicked.connect(self.open_last_screenshot)
        self.open_button.setEnabled(False)
        layout.addWidget(self.open_button)

        # --- Status Area ---
        self.status_label = QtWidgets.QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def browse_output_folder(self):
        """Opens a dialog to select the output folder."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Folder", self.base_output_path)
        if folder:  # If a folder is selected (not cancelled)
            self.base_output_path = folder
            self.output_folder_edit.setText(folder)
            # No need to create the dated subfolder here; it's done in start_capture

    def set_default_preview(self):
        pixmap = QtGui.QPixmap(1, 1)
        pixmap.fill(QtCore.Qt.lightGray)
        self.screenshot_label.setPixmap(pixmap.scaled(640, 480, QtCore.Qt.KeepAspectRatio))

    def update_interval(self):
        self.screenshot_interval = self.interval_spinbox.value()
        if self.is_running:
            self.timer.setInterval(int(self.screenshot_interval * 1000))

    def start_capture(self):
        # Check if the output folder exists:
        if not os.path.exists(self.base_output_path):
            QtWidgets.QMessageBox.critical(self, "Error", "The selected output folder does not exist!")
            return


        self.is_running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.interval_spinbox.setEnabled(False)
        self.browse_button.setEnabled(False) # Disable browse during capture

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
        self.browse_button.setEnabled(True) # Re-enable browse
        self.timer.stop()
        self.status_label.setText("Status: Stopped")
        self.label.setText("Capturing stopped.")
        self.paused_for_video = False

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

            if non_zero_count > self.sensitivity_spinbox.value() * 5:
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

                if non_zero_count > self.sensitivity_spinbox.value():
                    filename = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                    filepath = os.path.join(self.current_date_folder, filename)
                    screenshot.save(filepath)
                    self.label.setText(f'Screenshot saved: {filepath}')
                    self.last_screenshot_path = filepath
                    self.update_preview(filepath)
                    self.open_button.setEnabled(True)

            self.previous_screenshot = screenshot_gray
        except Exception as e:
            self.label.setText(f"Error during capture/compare: {e}")
            self.stop_capture()

    def update_preview(self, image_path):
        pixmap = QtGui.QPixmap(image_path)
        if pixmap.isNull():
            self.label.setText(f"Error loading image: {image_path}")
            return
        self.screenshot_label.setPixmap(pixmap.scaled(640, 480, QtCore.Qt.KeepAspectRatio))

    def open_last_screenshot(self):
        if self.last_screenshot_path and os.path.exists(self.last_screenshot_path):
            try:
                if sys.platform == "win32":
                    os.startfile(self.last_screenshot_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", self.last_screenshot_path], check=True)
                else:
                    subprocess.run(["xdg-open", self.last_screenshot_path], check=True)
            except (OSError, subprocess.CalledProcessError) as e:
                self.label.setText(f"Error opening image: {e}")
        else:
            self.label.setText("No screenshot to open.")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec_())