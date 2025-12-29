from flask import Flask, render_template, request, jsonify
import db
from pathlib import Path

app = Flask(__name__, static_folder="static", template_folder="templates")
DB_PATH = "kanban_board.db"


@app.route("/")
def index():
    return render_template("index.html")


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
    description = data.get("description", "")
    column = data.get("column", "Backlog")
    priority = data.get("priority", "Medium")
    project = data.get("project", "Default")
    date_added = data.get("date_added", None)
    deadline = data.get("deadline", None)
    if not title:
        return jsonify({"error": "title required"}), 400
    tid = db.add_task(
        title,
        description,
        column=column,
        priority=priority,
        project=project,
        date_added=date_added,
        deadline=deadline,
        db_path=DB_PATH,
    )
    return jsonify({"id": tid})


@app.route("/api/task/<int:task_id>/move", methods=["POST"])
def api_move(task_id):
    data = request.json or {}
    # Accept an authoritative target column from the client: {"to": "In Progress"}
    to_col = data.get("to")
    STATUSES = ["Backlog", "In Progress", "Done"]
    if not to_col or to_col not in STATUSES:
        return jsonify({"error": "invalid target column"}), 400

    task = db.get_task(task_id, db_path=DB_PATH)
    if not task:
        return jsonify({"error": "task not found"}), 404

    try:
        db.move_task(task_id, to_col, db_path=DB_PATH)
        return jsonify({"moved": True, "to": to_col})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/task/<int:task_id>/archive", methods=["POST"])
def api_archive(task_id):
    db.archive_task(task_id, db_path=DB_PATH)
    return jsonify({"archived": True})


@app.route("/api/task/<int:task_id>/unarchive", methods=["POST"])
def api_unarchive(task_id):
    db.unarchive_task(task_id, db_path=DB_PATH)
    return jsonify({"unarchived": True})


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
    # Allowed fields: title, description, priority, column, project
    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority")
    column = data.get("column")
    project = data.get("project")
    deadline = data.get("deadline", None)

    try:
        db.update_task(
            task_id,
            title=title,
            description=description,
            priority=priority,
            column=column,
            project=project,
            deadline=deadline,
            db_path=DB_PATH,
        )
        return jsonify({"updated": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # ensure DB exists
    db.init_db(DB_PATH)
    app.run(port=8502, debug=True)
