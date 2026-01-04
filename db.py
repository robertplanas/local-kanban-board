import sqlite3

from typing import List, Dict, Optional
from contextlib import contextmanager


def _connect(db_path: str = "kanban_board.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = _dict_factory
    return conn


@contextmanager
def get_db_connection(db_path: str = "kanban_board.db"):
    conn = _connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def _dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def init_db(db_path: str = "kanban_board.db") -> None:
    with get_db_connection(db_path) as conn:
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
                deadline DATETIME DEFAULT (DATETIME('now', '+1 day')), 
                subtasks TEXT DEFAULT '[]'
            )
            """
        )
        conn.commit()


def get_tasks(
    db_path: str = "kanban_board.db",
    include_archived: bool = False,
    project: str | None = None,
) -> List[Dict]:
    with get_db_connection(db_path) as conn:
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
        return rows


def get_task(task_id: int, db_path: str = "kanban_board.db") -> Optional[Dict]:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return cur.fetchone()


def add_task(
    title: str,
    description: str,
    column: str = "Backlog",
    priority: str = "Medium",
    project: str = "Default",
    date_added: Optional[str] = None,
    deadline: Optional[str] = None,
    subtasks: str = "[]",
    db_path: str = "kanban_board.db",
) -> int:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, description, column, priority, project, date_added, deadline, subtasks) VALUES (?, ?, ?, ?, ?,?,?, ?)",
            (
                title,
                description,
                column,
                priority,
                project,
                date_added,
                deadline,
                subtasks,
            ),
        )
        conn.commit()
        task_id = cur.lastrowid
        return task_id


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    column: Optional[str] = None,
    project: Optional[str] = None,
    date_added: Optional[str] = None,
    deadline: Optional[str] = None,
    subtasks: Optional[str] = None,
    db_path: str = "kanban_board.db",
) -> None:
    with get_db_connection(db_path) as conn:
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
        if subtasks is not None:
            fields.append("subtasks = ?")
            params.append(subtasks)
        params.append(task_id)
        if fields:
            cur.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", params)
            conn.commit()


def delete_task(task_id: int, db_path: str = "kanban_board.db") -> None:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()


def get_projects(db_path: str = "kanban_board.db") -> List[str]:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT project FROM tasks ORDER BY project COLLATE NOCASE"
        )
        rows = cur.fetchall()
        return [r["project"] for r in rows if r.get("project")]
