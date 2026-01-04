import sys
import os
import threading
import webview
from flask import Flask, render_template, request, jsonify
import db
import json

# --- CONFIGURATION ---
if getattr(sys, "frozen", False):
    base_dir = getattr(
        sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable))
    )
    template_folder = os.path.join(base_dir, "templates")
    static_folder = os.path.join(base_dir, "static")
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__, static_folder="static", template_folder="templates")

# Save DB in User Home (Critical for Mac Apps)
user_home = os.path.expanduser("~")
DB_PATH = os.path.join(user_home, "kanban_board.db")


@app.route("/")
def index():
    return render_template("index.html")


# --- API ROUTES (Same as before) ---
@app.route("/api/tasks")
def api_tasks():
    include_archived = request.args.get("archived", "0") == "1"
    project = request.args.get("project")
    tasks = db.get_tasks(DB_PATH, include_archived=include_archived, project=project)
    return jsonify(tasks)


@app.route("/api/task", methods=["POST"])
def api_add_task():
    data = request.json or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title required"}), 400

    tid = db.add_task(
        title,
        data.get("description", ""),
        column=data.get("column", "Backlog"),
        priority=data.get("priority", "Medium"),
        project=data.get("project", "Default"),
        date_added=data.get("date_added"),
        deadline=data.get("deadline"),
        subtasks=json.dumps(data.get("subtasks", [])),
        db_path=DB_PATH,
    )
    return jsonify({"id": tid})


@app.route("/api/projects")
def api_projects():
    projects = db.get_projects(DB_PATH)
    return jsonify(projects)


@app.route("/api/task/<int:task_id>", methods=["DELETE"])
def api_delete(task_id):
    db.delete_task(task_id, db_path=DB_PATH)
    return jsonify({"deleted": True})


@app.route("/api/task/<int:task_id>", methods=["PUT", "PATCH"])
def api_update_task(task_id):
    data = request.json or {}
    subtasks = data.get("subtasks")
    db.update_task(
        task_id,
        title=data.get("title"),
        description=data.get("description"),
        priority=data.get("priority"),
        column=data.get("column"),
        project=data.get("project"),
        deadline=data.get("deadline"),
        subtasks=json.dumps(subtasks) if subtasks is not None else None,
        db_path=DB_PATH,
    )
    return jsonify({"updated": True})


def start_server():
    """Runs Flask in a separate thread"""
    app.run(host="127.0.0.1", port=8502, threaded=True, use_reloader=False)


if __name__ == "__main__":
    db.init_db(DB_PATH)

    # 1. Start Flask in the background
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # 2. Start the Native Window
    # This blocks execution until the window is closed
    webview.create_window(
        "Personal Kanban",
        "http://127.0.0.1:8502",
        width=1400,
        height=800,
        resizable=True,
    )
    webview.start()
