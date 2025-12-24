import logging
import streamlit as st
from typing import List
import db

# simple UI logger
logging.basicConfig(
    filename="ui.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("local-kanban")


DB_PATH = "kanban_board.db"
STATUSES = ["Backlog", "In Progress", "Done"]


def inject_css():
    st.markdown(
        """
        <style>
        .card { padding: 10px; border:1px solid #e6e6e6; border-radius:8px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom:12px; background:#ffffff}
        .card-title { font-weight:700; font-size:14px; margin-bottom:4px }
        .meta { color: #6b7280; font-size:12px }
        .badge { display:inline-block; padding:3px 8px; border-radius:999px; font-size:12px; color:#fff; margin-right:6px }
        .badge-low { background:#6b7280 }
        .badge-medium { background:#f59e0b }
        .badge-high { background:#ef4444 }
        .col-container { max-height:70vh; overflow:auto; padding-right:6px }
        .empty-state { color:#9ca3af; padding:18px; border:1px dashed #e5e7eb; border-radius:8px; text-align:center }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _format_card_html(title: str, priority: str, date_added: str) -> str:
    return f"""
    <div style='display:flex;justify-content:space-between;align-items:center'>
      <div style='font-weight:700'>{title}</div>
      <div style='display:flex;gap:8px;align-items:center'>
        <div class='badge {"badge-low" if priority.lower() == "low" else ("badge-high" if priority.lower() == "high" else "badge-medium")}'>{priority}</div>
        <div class='meta'>{date_added}</div>
      </div>
    </div>
    """


def main():
    st.set_page_config(page_title="Local Kanban Board", layout="wide")
    inject_css()

    db.init_db(DB_PATH)

    statuses = STATUSES
    st.sidebar.header("Add Task")
    with st.sidebar.form("new_task"):
        t = st.text_input("Title")
        d = st.text_area("Description")
        p = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
        col = st.selectbox("Column", statuses, index=0)
        submitted = st.form_submit_button("Add")
        if submitted and t:
            db.add_task(t, d, column=col, priority=p, db_path=DB_PATH)

    st.sidebar.markdown("---")
    show_archived = st.sidebar.checkbox("Show archived tasks", value=False)
    query = st.sidebar.text_input("Search")

    tasks = db.get_tasks(DB_PATH, include_archived=show_archived)
    if query:
        tasks = [
            t
            for t in tasks
            if query.lower() in (t.get("title") or "").lower()
            or query.lower() in (t.get("description") or "").lower()
        ]

    cols = st.columns(len(statuses))
    # Group tasks by status for efficient rendering
    tasks_by_status = {s: [] for s in statuses}
    for tsk in tasks:
        colname = tsk.get("column") or "Backlog"
        if colname in tasks_by_status:
            tasks_by_status[colname].append(tsk)

    for idx, status in enumerate(statuses):
        with cols[idx]:
            st.subheader(status)
            with st.container():
                st.markdown("<div class='col-container'>", unsafe_allow_html=True)
                items = tasks_by_status.get(status, [])
                if not items:
                    st.markdown(
                        f"<div class='empty-state'>No tasks in {status}. Add one from the sidebar.</div>",
                        unsafe_allow_html=True,
                    )
                for task in items:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    # Header with title, priority badge and date
                    st.markdown(
                        _format_card_html(task.get("title"), task.get("priority") or "Medium", task.get("date_added") or ""),
                        unsafe_allow_html=True,
                    )
                    # Keep description in expander to save space
                    if task.get("description"):
                        with st.expander("Details"):
                            st.write(task.get("description"))
                    # Action buttons: only show arrows when move is valid
                    left_col, right_col, arch_col, del_col = st.columns([1, 1, 1, 1])
                    cur_idx = statuses.index(status)
                    if cur_idx > 0:
                        if left_col.button("⬅", key=f"left-{task['id']}"):
                            db.move_task(task["id"], statuses[cur_idx - 1], db_path=DB_PATH)
                    else:
                        left_col.write("")
                    if cur_idx < len(statuses) - 1:
                        if right_col.button("➡", key=f"right-{task['id']}"):
                            db.move_task(task["id"], statuses[cur_idx + 1], db_path=DB_PATH)
                    else:
                        right_col.write("")
                    if arch_col.button("Archive", key=f"arch-{task['id']}"):
                        db.archive_task(task["id"], db_path=DB_PATH)
                    if del_col.button("Delete", key=f"del-{task['id']}"):
                        db.delete_task(task["id"], db_path=DB_PATH)
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # Archived tasks view (optional)
    if show_archived:
        archived = [t for t in tasks if (t.get("column") or "") == "Archived"]
        st.markdown("---")
        st.subheader("Archived")
        if not archived:
            st.info("No archived tasks")
        for task in archived:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(
                _format_card_html(task.get("title"), task.get("priority") or "Medium", task.get("date_added") or ""),
                unsafe_allow_html=True,
            )
            if task.get("description"):
                with st.expander("Details"):
                    st.write(task.get("description"))
            # Allow delete from archive
            if st.button("Delete", key=f"del-arch-{task['id']}"):
                db.delete_task(task["id"], db_path=DB_PATH)
            st.markdown("</div>", unsafe_allow_html=True)


# ---- Handlers used by UI (and tests) ----
def add_task_handler(title: str, description: str, column: str = "Backlog", priority: str = "Medium", db_path: str = DB_PATH) -> int:
    tid = db.add_task(title, description, column=column, priority=priority, db_path=db_path)
    logger.info("add_task: id=%s title=%s column=%s priority=%s", tid, title, column, priority)
    return tid


def move_task_handler(task_id: int, direction: str, db_path: str = DB_PATH) -> bool:
    """Move task left or right relative to STATUSES. Returns True if moved."""
    task = db.get_task(task_id, db_path=db_path)
    if not task:
        return False
    cur = task.get("column") or "Backlog"
    try:
        idx = STATUSES.index(cur)
    except ValueError:
        return False
    if direction == "left" and idx > 0:
        db.move_task(task_id, STATUSES[idx - 1], db_path=db_path)
        logger.info("move_task: id=%s from=%s to=%s", task_id, STATUSES[idx], STATUSES[idx - 1])
        return True
    if direction == "right" and idx < len(STATUSES) - 1:
        db.move_task(task_id, STATUSES[idx + 1], db_path=db_path)
        logger.info("move_task: id=%s from=%s to=%s", task_id, STATUSES[idx], STATUSES[idx + 1])
        return True
    return False


def archive_task_handler(task_id: int, db_path: str = DB_PATH) -> None:
    db.archive_task(task_id, db_path=db_path)
    logger.info("archive_task: id=%s", task_id)


def delete_task_handler(task_id: int, db_path: str = DB_PATH) -> None:
    db.delete_task(task_id, db_path=db_path)
    logger.info("delete_task: id=%s", task_id)
    


if __name__ == "__main__":
    main()
