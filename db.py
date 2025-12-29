import sqlite3
from typing import List, Dict, Optional


def _dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def init_db(db_path: str = "kanban_board.db") -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            column TEXT NOT NULL,
            priority TEXT,
            project TEXT DEFAULT 'Default',
            date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
            deadline DATETIME DEFAULT (DATETIME('now', '+1 day'))
        )
        """
    )
    conn.commit()
    conn.close()


def _connect(db_path: str = "kanban_board.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = _dict_factory
    return conn


def get_tasks(
    db_path: str = "kanban_board.db",
    include_archived: bool = False,
    project: str | None = None,
) -> List[Dict]:
    conn = _connect(db_path)
    cur = conn.cursor()
    params = []
    where = []
    if not include_archived:
        where.append("column != 'Archived'")
    if project:
        where.append("project = ?")
        params.append(project)

    q = "SELECT * FROM tasks"
    if where:
        q += " WHERE " + " AND ".join(where)
    q += " ORDER BY date_added DESC"
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_task(task_id: int, db_path: str = "kanban_board.db") -> Optional[Dict]:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    return row


def add_task(
    title: str,
    description: str,
    column: str = "Backlog",
    priority: str = "Medium",
    project: str = "Default",
    date_added: Optional[str] = None,
    deadline: Optional[str] = None,
    db_path: str = "kanban_board.db",
) -> int:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, column, priority, project, date_added, deadline) VALUES (?, ?, ?, ?, ?,?,?)",
        (title, description, column, priority, project, date_added, deadline),
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    return task_id


def move_task(task_id: int, new_column: str, db_path: str = "kanban_board.db") -> None:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET column = ? WHERE id = ?", (new_column, task_id))
    conn.commit()
    conn.close()


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    column: Optional[str] = None,
    project: Optional[str] = None,
    date_added: Optional[str] = None,
    deadline: Optional[str] = None,
    db_path: str = "kanban_board.db",
) -> None:
    conn = _connect(db_path)
    cur = conn.cursor()
    fields = []
    params = []
    if title is not None:
        fields.append("title = ?")
        params.append(title)
    if description is not None:
        fields.append("description = ?")
        params.append(description)
    if priority is not None:
        fields.append("priority = ?")
        params.append(priority)
    if column is not None:
        fields.append("column = ?")
        params.append(column)
    if project is not None:
        fields.append("project = ?")
        params.append(project)
    if date_added is not None:
        fields.append("date_added = ?")
        params.append(date_added)
    if deadline is not None:
        fields.append("deadline = ?")
        params.append(deadline)
    params.append(task_id)
    if fields:
        cur.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
    conn.close()


def delete_task(task_id: int, db_path: str = "kanban_board.db") -> None:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def archive_task(task_id: int, db_path: str = "kanban_board.db") -> None:
    move_task(task_id, "Archived", db_path=db_path)


def unarchive_task(task_id: int, db_path: str = "kanban_board.db") -> None:
    """Move a task out of Archived back to Backlog."""
    move_task(task_id, "Backlog", db_path=db_path)


def get_projects(db_path: str = "kanban_board.db") -> List[str]:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT project FROM tasks ORDER BY project COLLATE NOCASE")
    rows = cur.fetchall()
    conn.close()
    return [r["project"] for r in rows if r.get("project")]
