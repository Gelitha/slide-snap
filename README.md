# Slide Change Screenshot App

This PyQt5 application automatically captures screenshots of your screen when it detects significant visual changes, such as slide transitions during a presentation. It's designed to run in the background, minimizing distractions.

## Features

*   **Automatic Screenshot Capture:**  Captures screenshots when a visual change is detected (e.g., a slide change).
*   **Adjustable Sensitivity:** Fine-tune the sensitivity threshold to control the amount of change required to trigger a screenshot.
*   **Adjustable Interval:** Set the time interval (in seconds) between screen checks.
*   **Video Detection:** Automatically pauses capturing when video playback is detected, preventing unnecessary screenshots. Resumes automatically when video stops.
*   **Custom Output Folder:** Select the directory where screenshots will be saved. Subfolders are created automatically for each day.
*   **Screenshot Preview:** View the last captured screenshot directly within the application.
*   **Screenshot History:** Browse past screenshots organized by date and time.
*   **Thumbnail Gallery:** Quick visual preview of recently captured screenshots.
*   **Dark/Light Mode:** Toggle between dark and light themes.
*   **Cross-platform:** Works on Windows, macOS, and Linux.
*   **Keyboard Shortcuts:** Control the application using hotkeys (see below).

## Installation

**Prerequisites:**

*   Python 3.7 or higher.

**Steps:**

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/Gelitha/Zoom-presentation-screenshot-App.git
    cd Zoom-presentation-screenshot-App
    ```

2.  **_Highly Recommended:_ Use a Virtual Environment:**

    It's *strongly* recommended to use a virtual environment to isolate your project's dependencies.  This prevents conflicts with other Python projects.

    ```bash
    # Create the environment (only needed once per project):
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

    This command installs all the necessary Python packages (PyQt5, opencv-python, pyautogui, numpy).

    When you're finished, deactivate the environment:

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

    *   **Output Folder:** Click "Browse..." to choose the directory where screenshots will be saved.  A subfolder named with the current date (YYYY.MM.DD) will be created automatically within this directory.
    *   **Capture Interval:** Adjust the "Capture Interval" (in seconds) to set the time between screen checks.  A shorter interval is more responsive but may generate more screenshots.  The default is 5 seconds.
    *   **Change Sensitivity:**  The "Change Sensitivity" setting controls how much the screen must change to trigger a screenshot.  *Lower* values are *more* sensitive (smaller changes trigger a screenshot).  *Higher* values are *less* sensitive.  Experiment to find the best setting for your presentations.  The default is 1.5%.
     * **Adaptive Sensitivity:** Check this box to automatically adjust the change sensitivity, very useful to get screenshots in any environment
    *   **Video Detection Interval:** This controls how often the application checks for video playback.

4.  **Start/Stop Capture:**

    *   **Start:**  Click the "Start Capture" button (or use the `Ctrl+Shift+S` hotkey). The application will minimize to the system tray.
    *   **Stop:** Click the "Stop Capture" button (or use the `Ctrl+Shift+X` hotkey).

5.  **View Screenshots:**

    *   **Preview:** The last captured screenshot is displayed in the main window.
    *   **Open Last Screenshot:** Click "Open Last Screenshot" (or use `Ctrl+Shift+O`) to open the image with your default image viewer.
    *   **History:** The left sidebar shows a history of captured screenshots, organized by date and time.  Click on an entry to open it.
    * **Thumbnail Gallery:** Shows a quick gallery of recent captures.

## Keyboard Shortcuts

| Shortcut          | Action                               |
| ----------------- | ------------------------------------ |
| Ctrl+Shift+S     | Start Capture                        |
| Ctrl+Shift+X     | Stop Capture                         |
| Ctrl+Shift+O     | Open Last Screenshot                |
| Ctrl+D           | Toggle Dark/Light Mode              |
| Ctrl+H           | Show/Hide Keyboard Shortcuts Dialog |
| Ctrl+Q           | Quit Application                     |

## Video Detection

The application automatically pauses capturing when it detects video playback to avoid generating many unnecessary screenshots.  It resumes automatically when the video stops. This detection is based on rapid changes in the screen content and is generally reliable, but you may need to adjust the "Video Detection Interval" setting if you encounter issues.

## Troubleshooting

*   **`ModuleNotFoundError: No module named '...'`:**  This means you haven't installed the required Python packages.  Make sure you have run `pip install -r requirements.txt` *within your activated virtual environment* (see Installation).
*   **Screenshots are not being saved:**
    *   Confirm that the selected "Output Folder" exists and that you have write permissions to it.
    *   Check the "Change Sensitivity" setting. If it's too high, the application might not detect enough change to trigger a screenshot. Try lowering the sensitivity.
    *  Make sure the application is running (check the system tray).
*   **Application crashes or unexpected behavior:**
    *   Check the terminal/console where you ran the application.  Error messages will often be printed there, providing valuable clues.
    *  If video pause/resume isn't working as expected, try different values for the Video Detection Interval setting.
* **Too many screenshots:** Increase the "Change Sensitivity" value and/or increase the "Capture Interval".  Enable "Adaptive Sensitivity".
* **Missing slide changes:** Decrease the "Change Sensitivity" value.
* **"Video Detected" notification keeps appearing:** This has been addressed in the latest code. If you're using an older version, upgrade.

## Contributing

Contributions are welcome!  If you'd like to improve this project:

1.  Fork the repository on GitHub.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with clear, descriptive commit messages.
4.  Submit a pull request.

Please follow good coding practices and include any necessary tests.

## License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.
