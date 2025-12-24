# Project Plan: Local Kanban Board (Streamlit + SQLite)

This document outlines the phased development of a local-first personal productivity tool built with **Python**, **Streamlit**, and **SQLite**.

---

## Phase 1: Data Structure & Storage
**Goal:** Establish a reliable way to store and retrieve tasks locally.

* **Database Choice:** SQLite (using the built-in `sqlite3` library).
* **Schema Design:**
    * `id`: INTEGER (Primary Key, Autoincrement)
    * `title`: TEXT (The task heading)
    * `description`: TEXT (Detailed notes)
    * `column`: TEXT (The current status: e.g., 'Backlog', 'In Progress', 'Done')
    * `priority`: TEXT (e.g., 'Low', 'Medium', 'High')
    * `date_added`: DATETIME (Default to current timestamp)
* **Implementation:** Create a utility script to initialize the `.db` file and handle SQL queries for adding, moving, and deleting tasks.

---

## Phase 2: Streamlit Layout Design
**Goal:** Create a visual "Board" feel using Streamlit's layout primitives.

* **Columnar Layout:** Use `st.columns()` to define the vertical Kanban lanes based on the user's defined statuses.
* **Card UI:** * Since Streamlit lacks a native "Card" component, use `st.container` with a border.
    * Inject custom CSS via `st.markdown(unsafe_allow_html=True)` to style card backgrounds, borders, and shadows.
* **Visual Hierarchy:** Use `st.caption` for metadata (like dates) and bold text for titles.

---

## Phase 3: Task Interaction Logic
**Goal:** Implement task management via buttons and forms.

* **Task Creation:** * Use `st.sidebar` or `st.popover` to host a "New Task" form.
* **State Management (Moving Tasks):**
    * Instead of drag-and-drop, place small directional buttons on each card (e.g., `[ ⮕ ]` to move right, `[ ⬅ ]` to move left).
    * Clicking a button triggers a database update and a UI rerun.
* **Data Entry:** Use `st.text_input` for titles and `st.text_area` for descriptions.

---

## Phase 4: State Persistence
**Goal:** Ensure the UI is reactive and data persists across app restarts.

* **Session State:** Use `st.session_state` to store the current list of tasks to ensure the UI updates instantly after an interaction.
* **Synchronization:** * **Read:** Fetch all rows from SQLite upon the initial script execution.
    * **Write:** Every time a task is moved or edited, execute the SQL update and call `st.rerun()` to refresh the view.
* **Local Focus:** Ensure the database file resides in the same directory as the app.

---

## Phase 5: Refinement & UI Polish
**Goal:** Enhance usability and aesthetic appeal.

* **Priority Highlighting:** Implement color-coded tabs or text (e.g., Red for "High", Gray for "Low").
* **Search & Filter:** * Add a search bar in the sidebar to filter cards by keyword using a simple `df[df['title'].str.contains(query)]` logic.
* **Archive Function:** Add an "Archive" button to move tasks from the "Done" column into a hidden state, keeping the board clean without deleting history.
* **Empty States:** Add helpful illustrations or text when a column is empty.

---

### Technical Constraints
* **Storage:** Local SQLite file (`kanban_board.db`).
* **Dependencies:** `streamlit`, `sqlite3`.
* **UI Style:** Minimalist, clean, and optimized for personal desktop use.