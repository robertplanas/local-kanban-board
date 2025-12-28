from pathlib import Path

import db
import app


def test_single_click_move(tmp_path: Path):
    db_path = tmp_path / "test_handlers.db"
    db.init_db(str(db_path))

    # add task into Backlog
    tid = app.add_task_handler(
        "T1", "desc", column="Backlog", priority="Medium", db_path=str(db_path)
    )
    task = db.get_task(tid, db_path=str(db_path))
    assert task["column"] == "Backlog"

    # single 'right' move should move to In Progress
    moved = app.move_task_handler(tid, "right", db_path=str(db_path))
    assert moved is True
    task = db.get_task(tid, db_path=str(db_path))
    assert task["column"] == "In Progress"

    # single 'right' move again should move to Done
    moved = app.move_task_handler(tid, "right", db_path=str(db_path))
    assert moved is True
    task = db.get_task(tid, db_path=str(db_path))
    assert task["column"] == "Done"

    # moving right at last column should return False and not change
    moved = app.move_task_handler(tid, "right", db_path=str(db_path))
    assert moved is False
    task = db.get_task(tid, db_path=str(db_path))
    assert task["column"] == "Done"

    # move left should work once
    moved = app.move_task_handler(tid, "left", db_path=str(db_path))
    assert moved is True
    task = db.get_task(tid, db_path=str(db_path))
    assert task["column"] == "In Progress"


def test_debounce_wrapper(tmp_path: Path):
    db_path = tmp_path / "test_handlers_debounce.db"
    db.init_db(str(db_path))
    tid = app.add_task_handler(
        "Tdb", "desc", column="Backlog", priority="Medium", db_path=str(db_path)
    )
    key = f"right-{tid}"

    # first action should execute
    executed = app.process_action_once(
        key,
        lambda: app.move_task_handler(tid, "right", db_path=str(db_path)),
        debounce_seconds=0.5,
    )
    assert executed is True
    task = db.get_task(tid, db_path=str(db_path))
    assert task["column"] == "In Progress"

    # immediate second call should be debounced
    executed2 = app.process_action_once(
        key,
        lambda: app.move_task_handler(tid, "right", db_path=str(db_path)),
        debounce_seconds=0.5,
    )
    assert executed2 is False


def test_archive_visibility_and_delete(tmp_path: Path):
    db_path = tmp_path / "test_handlers2.db"
    db.init_db(str(db_path))

    tid = app.add_task_handler(
        "T-arch", "arch", column="Done", priority="Low", db_path=str(db_path)
    )
    # archive it
    app.archive_task_handler(tid, db_path=str(db_path))
    all_tasks = db.get_tasks(str(db_path), include_archived=True)
    assert any(t["id"] == tid and t["column"] == "Archived" for t in all_tasks)

    # delete it
    app.delete_task_handler(tid, db_path=str(db_path))
    all_tasks = db.get_tasks(str(db_path), include_archived=True)
    assert not any(t["id"] == tid for t in all_tasks)
