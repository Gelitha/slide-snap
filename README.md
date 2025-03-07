# Slide Change Screenshot App

This PyQt5 application captures screenshots of your full screen whenever it detects a significant change, such as a slide change during a presentation. It's designed to be simple and easy to use.

## Features

*   **Automatic Screenshot Capture:** Takes screenshots when a visual change is detected.
*   **Adjustable Sensitivity:** You can change the sensitivity threshold to control how much change is needed to trigger a screenshot.
*   **Adjustable Interval:** Set the time interval between checks for changes.
*   **Video Detection (Heuristic):** Attempts to pause capturing when a video is playing to avoid taking many unnecessary screenshots.
*   **Custom Output Folder:** Choose where your screenshots are saved.
*   **Screenshot Preview:** See the last captured screenshot within the application.
*   **Easy Opening of Last Screenshot:** Open the last image with your default image viewer.
*   **Cross-platform:** It should work on Windows, macOS, and Linux.

## Installation

**Prerequisites:**

*   Python 3.7 or higher. (Older versions *might* work, but haven't been tested.)

**Steps:**

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/Gelitha/Zoom-presentation-screenshot-App.git
    cd Zoom-presentation-screenshot-App
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    This command uses the `requirements.txt` file to install all the necessary Python packages.

    **_Highly Recommended:_ Use a Virtual Environment**

    It's strongly recommended to use a virtual environment to manage your project's dependencies.  This keeps them separate from your system-wide Python installation.

    To create and activate a virtual environment:

    ```bash
    # Create the environment (only needed once)
    python3 -m venv venv  # Or python -m venv venv, depending on your system

    # Activate the environment (every time you work on the project)
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

    Then, run `pip install -r requirements.txt` *inside* the activated environment.  When you're finished working, deactivate the environment with `deactivate`.

## Usage

1.  **Run the Application:**

    ```bash
    python screenshot_app.py
    ```

2.  **Configure Settings:**
    *   **Output Folder:** Click "Browse..." to select the folder where screenshots will be saved. A subfolder with today's date will be created automatically.
    *   **Interval:** Use the spin box to set the time (in seconds) between checks for screen changes.
    *   **Sensitivity:** Adjust the spin box to control how much change is needed to trigger a screenshot. Higher values mean more change is required.

3.  **Start and Stop Capture:**
    *   Click "Start" to begin capturing.
    *   Click "Stop" to stop capturing.

4.  **View Last Screenshot:**
    *   The last captured screenshot is displayed in the application window.
    *   Click "Open Last Screenshot" to open it in your default image viewer.

## Video Detection

The application attempts to detect when a video is playing and pause capturing. This is a *heuristic* (an educated guess), and it might not be perfect. If you find it's capturing too many screenshots during videos, you can increase the sensitivity. If it's missing slide changes, you can decrease the sensitivity.

## Troubleshooting

*   **`ModuleNotFoundError: No module named '...'`:** This means you haven't installed the required packages. Make sure you run `pip install -r requirements.txt`. If you're using a virtual environment, make sure it's activated.
*   **Screenshots are not being saved:**
    *   Make sure the output folder you selected exists and that you have write permissions to it.
    *   Check the sensitivity setting. If it's too high, changes might not be detected.
*   **Application crashes:** Check the terminal for error messages. These messages can help you (or someone helping you) diagnose the problem.

## Contributing

If you'd like to contribute to this project, please feel free to submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
