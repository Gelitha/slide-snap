# Slide Snap: Automatic Screenshot Capture for Presentations

This PyQt5 application automatically captures screenshots of your screen when it detects significant visual changes, such as slide transitions during a presentation. It's designed to run in the background, minimizing distractions.

## Features

*   **Automatic Screenshot Capture:** Captures screenshots when a visual change is detected (e.g., a slide change).
*   **Adjustable Sensitivity:** Fine-tune the sensitivity threshold to control the amount of change required to trigger a screenshot.  Lower values are *more* sensitive.
*   **Adjustable Interval:** Set the time interval (in seconds) between screen checks.
*   **Video Detection:** Automatically pauses capturing when video playback is detected, preventing unnecessary screenshots. Resumes automatically when video stops.
*   **Custom Output Folder:** Select the directory where screenshots will be saved. Subfolders are created automatically for each day.
*   **Screenshot Preview:** View the last captured screenshot directly within the application.
*   **Screenshot History:** Browse past screenshots organized by date and hour in a collapsible format.
*   **Thumbnail Gallery:** Quick visual preview of recently captured screenshots. Click a thumbnail to open the full image.
*   **Dark/Light Mode:** Toggle between dark and light themes (Ctrl+D).
*   **Cross-platform:** Works on Windows, macOS, and Linux.
*   **Keyboard Shortcuts:** Control the application using hotkeys (see below).
* **Context Menu:** Right-click on the preview image for options to Open, Copy, and Delete the current screenshot.
* **Drag and Drop:** Drag and drop image files onto the application window to preview them.

## Installation

**Prerequisites:**

*   Python 3.7 or higher.

**Steps:**

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/Gelitha/slide-snap.git
    cd slide-snap
    ```

2.  **_Highly Recommended:_ Use a Virtual Environment:**

    Isolate your project's dependencies to prevent conflicts.

    ```bash
    # Create the environment (only once per project):
    python3 -m venv venv  # Or python -m venv venv

    # Activate the environment (every time you work on the project):
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**

    *Inside the activated virtual environment*, run:

    ```bash
    pip install -r requirements.txt
    ```

    This command installs the necessary Python packages (PyQt5, opencv-python, pyautogui, numpy, scikit-image, Pillow, and other PyAutoGUI dependencies).

    When finished, deactivate the environment:

    ```bash
    deactivate
    ```

## Usage

1.  **Run the Application:**

    ```bash
    python screenshot_app.py
    ```
    The application will start minimized.

2.  **Access the UI:** Double-click the application's icon in the system tray (Windows) or find the minimized window.

3.  **Configure Settings:**

    *   **Output Folder:** Click "Browse..." to choose the directory. A subfolder with the current date (YYYY.MM.DD) is created automatically.
    *   **Capture Interval:** Adjust the "Capture Interval" (seconds). Shorter intervals are more responsive but may generate more screenshots. Default: 5 seconds.
    *   **Change Sensitivity:** Controls how much the screen must change. *Lower* values are *more* sensitive. Experiment to find the best setting. Default: 0.005 (0.5%).
    *   **Adaptive Sensitivity:** Check this box to automatically adjust sensitivity based on image content.
    *   **Video Detection Interval:** How often to check for video playback.

4.  **Start/Stop Capture:**

    *   **Start:** Click "Start Capture" (or Ctrl+Shift+S). Minimizes to system tray.
    *   **Stop:** Click "Stop Capture" (or Ctrl+Shift+X).

5.  **View Screenshots:**

    *   **Preview:** The last captured screenshot is displayed.
    *   **Open Last Screenshot:** Click "Open Last Screenshot" (or Ctrl+Shift+O) to open with your default image viewer.
    *   **History:** The left sidebar shows a history, organized by date and hour. Click to open.
    *   **Thumbnail Gallery:** Shows recent captures. Click to open.

## Keyboard Shortcuts

| Shortcut          | Action                               |
| ----------------- | ------------------------------------ |
| Ctrl+Shift+S     | Start Capture                        |
| Ctrl+Shift+X     | Stop Capture                         |
| Ctrl+Shift+O     | Open Last Screenshot                |
| Ctrl+D           | Toggle Dark/Light Mode              |
| Ctrl+H           | Show/Hide Keyboard Shortcuts Dialog |
| Ctrl+Q           | Quit Application                     |

## Building an Executable (Optional)

You can create a standalone executable (.exe) using PyInstaller:

1.  **Install PyInstaller (in your virtual environment):**

    ```bash
    pip install pyinstaller
    ```

2.  **Build the Executable:**

    ```bash
    pyinstaller --onefile --windowed --icon=assets/icon.ico --add-data "assets;assets" --hidden-import PyQt5.QtWidgets --hidden-import PyQt5.QtGui --hidden-import PyQt5.QtCore --hidden-import skimage.metrics --collect-all PyQt5 screenshot_app.py
    ```
    *   **`--onefile`:** Creates a single executable file.
    *   **`--windowed`:** Hides the console window.
    *   **`--icon=assets/icon.ico`:** Sets the application icon (replace `icon.ico` with your icon file if it has a different name).  If you don't have an `.ico` file, remove this option.
    *   **`--add-data "assets;assets"`:** Includes the `assets` folder (important for icons and images used by the application).
    *   **`--hidden-import ...`:**  Specifies modules that PyInstaller might not detect automatically.
    *   **`--collect-all PyQt5`:**  This is crucial for resolving common PyQt5 DLL issues (like the "ordinal 380" error).

3.  **Find the Executable:**  The executable (`screenshot_app.exe`) will be created in the `dist` folder.

## Video Detection

The application pauses capturing when it detects video, resuming automatically.  This detection is based on rapid screen changes. Adjust the "Video Detection Interval" if needed.

## Troubleshooting

*   **`ModuleNotFoundError`:**  Install dependencies: `pip install -r requirements.txt` *in your activated virtual environment*.
*   **Screenshots not saved:**
    *   Check the "Output Folder" exists and you have write permissions.
    *   Lower the "Change Sensitivity".
    *   Ensure the application is running (system tray).
*   **Application crashes:**  Check the terminal/console for error messages.
*   **Video pause/resume issues:** Adjust the "Video Detection Interval".
*   **Too many screenshots:** Increase "Change Sensitivity" and/or "Capture Interval". Enable "Adaptive Sensitivity".
*   **Missing slide changes:** Decrease "Change Sensitivity".
* **Executable does not run (Ordinal 380 error):** Use the Pyinstaller command with `--collect-all PyQt5`

## Contributing

Contributions are welcome!

1.  Fork the repository.
2.  Create a new branch.
3.  Make changes, commit with clear messages.
4.  Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.
