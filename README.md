# Personal Kanban

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Personal Kanban** is a lightweight, privacy-focused desktop application for managing tasks. Built with **Flask** and **pywebview**, it combines the power of a web interface with the convenience of a native desktop app. All data is stored locally on your machine, ensuring your plans remain private.

![Demo GIF](./auxiliar/kanban_app.gif)*

## 🚀 Key Features

* **Native Desktop Experience:** Runs as a standalone window (macOS/Windows) without a browser address bar.
* **Kanban Workflow:** Drag-and-drop tasks between *Backlog*, *Requested*, *In Progress*, and *Done*.
* **Project Management:** Filter tasks by project with a dynamic tag system.
* **Subtasks & Progress:** Add checklists to cards and visualize progress with automatic progress bars.
* **Archive System:** Archive completed tasks to keep your board clean without losing history.
* **Data Persistence:** Auto-saves to a local SQLite database located in your user home directory.
* **Visual Priority:** Distinct visual cues for High, Medium, and Low priority tasks.

## 📂 Project Structure

```text
.
├── web.py                 # Application entry point (Flask + PyWebView logic)
├── db.py                  # Database schema and CRUD operations (SQLite)
├── deploy.sh              # Script to build the standalone executable
├── launch.sh              # Helper script to run dev mode
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Single-page application frontend (Bootstrap + JS)
├── auxiliar/
│   └── app.icns           # Application icon
└── tests/                 # Pytest suite
    ├── test_api.py
    └── test_db.py
```
## 🛠  Installation & Development

1. Clone the repository

    ```
    git clone [https://github.com/yourusername/personal-kanban.git](https://github.com/yourusername/personal-kanban.git)
    cd personal-kanban
    ```
2. Set up a Virtual Environment

    ```
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3. Install Dependencies

    ```
    pip install -r requirements.txt
    ```
4. Run in Development Mode

    You can run the app directly using the helper script:

    ```
    ./launch.sh
    ```
    Or manually:

    ```
    python web.py
    ```

## 📦 Building the Executable
To package the application as a standalone .app (macOS) or .exe (Windows), use the provided deploy script. This uses PyInstaller.

    ./deploy.sh

The executable will be generated in the dist/ folder.

- macOS: dist/Personal Kanban.app
- Windows: dist/Personal Kanban.exe

## 💽 Data Storage
The application stores your data in a simple SQLite database file located in your home directory to prevent data loss during updates or rebuilds.

- **Location**: ~/kanban_board.db (User Home Directory)

##  ✅ Testing
The project includes a test suite using pytest to ensure API and Database stability.

    # Run all tests
    pytest tests/

## 🤝 Contributing
Fork the repository.

Create a feature branch (git checkout -b feature/AmazingFeature).

Commit your changes (git commit -m 'Add some AmazingFeature').

Push to the branch (git push origin feature/AmazingFeature).

Open a Pull Request.

📄 License
Distributed under the MIT License. See LICENSE for more information.