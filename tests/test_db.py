from pathlib import Path

import db


def test_db_crud(tmp_path: Path):
    db_path = tmp_path / "test.db"
    db.init_db(str(db_path))

    # Create
    tid = db.add_task(
        "Task1", "Desc", column="Backlog", priority="High", db_path=str(db_path)
    )
    tasks = db.get_tasks(str(db_path))
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task1"

    # Move
    db.update_task(tid, column="In Progress", db_path=str(db_path))
    tasks = db.get_tasks(str(db_path))
    assert tasks[0]["column"] == "In Progress"

    # Update
    db.update_task(
        tid, title="Task1-upd", description="New", priority="Low", db_path=str(db_path)
    )
    tasks = db.get_tasks(str(db_path))
    assert tasks[0]["title"] == "Task1-upd"
    assert tasks[0]["priority"] == "Low"

    # Archive
    db.update_task(tid, column="Archived", db_path=str(db_path))
    tasks = db.get_tasks(str(db_path))
    assert len(tasks) == 0
    tasks_all = db.get_tasks(str(db_path), include_archived=True)
    assert tasks_all[0]["column"] == "Archived"

    # Delete
    db.delete_task(tid, db_path=str(db_path))
    tasks_all = db.get_tasks(str(db_path), include_archived=True)
    assert len(tasks_all) == 0
