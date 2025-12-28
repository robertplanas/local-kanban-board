import logging
import time
import streamlit as st
import db

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    filename="ui.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("local-kanban")

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
DB_PATH = "kanban_board.db"
STATUSES = ["Backlog", "In Progress", "Done"]


# -----------------------------------------------------------------------------
# Streamlit-safe debounce
# -----------------------------------------------------------------------------
def process_action_once(key: str, fn, debounce_seconds: float = 0.4) -> bool:
    """
    Execute fn() only if the last execution for key was older than debounce_seconds.
    Uses st.session_state so it survives Streamlit reruns.
    """
    if "last_action_ts" not in st.session_state:
        st.session_state.last_action_ts = {}

    now = time.time()
    last = st.session_state.last_action_ts.get(key, 0)

    if now - last < debounce_seconds:
        logger.info("debounced action %s (%.3fs since last)", key, now - last)
        return False

    fn()
    st.session_state.last_action_ts[key] = now
    return True


# -----------------------------------------------------------------------------
# UI helpers
# -----------------------------------------------------------------------------
def inject_css():
    st.markdown(
        """
        <style>
        .card { padding: 10px; border:1px solid #e6e6e6; border-radius:8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom:12px;
                background:#ffffff }
        .meta { color: #6b7280; font-size:12px }
        .badge { display:inline-block; padding:3px 8px; border-radius:999px;
                 font-size:12px; color:#fff; margin-right:6px }
        .badge-low { background:#6b7280 }
        .badge-medium { background:#f59e0b }
        .badge-high { background:#ef4444 }
        .col-container { max-height:70vh; overflow:auto; padding-right:6px }
        .empty-state { color:#9ca3af; padding:18px; border:1px dashed #e5e7eb;
                       border-radius:8px; text-align:center }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _format_card_html(title: str, priority: str, date_added: str) -> str:
    badge_class = (
        "badge-low"
        if priority.lower() == "low"
        else "badge-high"
        if priority.lower() == "high"
        else "badge-medium"
    )
    return f"""
    <div style='display:flex;justify-content:space-between;align-items:center'>
      <div style='font-weight:700'>{title}</div>
      <div style='display:flex;gap:8px;align-items:center'>
        <div class='badge {badge_class}'>{priority}</div>
        <div class='meta'>{date_added}</div>
      </div>
    </div>
    """


# -----------------------------------------------------------------------------
# Main app
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Local Kanban Board", layout="wide")
    inject_css()
    db.init_db(DB_PATH)

    # -------------------------------------------------------------------------
    # Sidebar: Add task
    # -------------------------------------------------------------------------
    st.sidebar.header("Add Task")
    with st.sidebar.form("new_task"):
        title = st.text_input("Title")
        desc = st.text_area("Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
        column = st.selectbox("Column", STATUSES, index=0)
        submitted = st.form_submit_button("Add")

        if submitted and title:
            add_task_handler(title, desc, column, priority, DB_PATH)

    st.sidebar.markdown("---")
    show_archived = st.sidebar.checkbox("Show archived tasks", value=False)
    query = st.sidebar.text_input("Search")

    # -------------------------------------------------------------------------
    # Fetch + filter tasks
    # -------------------------------------------------------------------------
    tasks = db.get_tasks(DB_PATH, include_archived=show_archived)
    if query:
        q = query.lower()
        tasks = [
            t
            for t in tasks
            if q in (t.get("title") or "").lower()
            or q in (t.get("description") or "").lower()
        ]

    tasks_by_status = {s: [] for s in STATUSES}
    for t in tasks:
        col = t.get("column") or "Backlog"
        if col in tasks_by_status:
            tasks_by_status[col].append(t)

    # -------------------------------------------------------------------------
    # Board
    # -------------------------------------------------------------------------
    cols = st.columns(len(STATUSES))
    for idx, status in enumerate(STATUSES):
        with cols[idx]:
            st.subheader(status)
            st.markdown("<div class='col-container'>", unsafe_allow_html=True)

            items = tasks_by_status.get(status, [])
            if not items:
                st.markdown(
                    f"<div class='empty-state'>No tasks in {status}.</div>",
                    unsafe_allow_html=True,
                )

            for task in items:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(
                    _format_card_html(
                        task["title"],
                        task.get("priority", "Medium"),
                        task.get("date_added", ""),
                    ),
                    unsafe_allow_html=True,
                )

                if task.get("description"):
                    with st.expander("Details"):
                        st.write(task["description"])

                arch, delete = st.columns(2)
                tid = task["id"]

                if arch.button("Archive", key=f"arch-{tid}"):
                    process_action_once(
                        f"arch-{tid}",
                        lambda tid=tid: archive_task_handler(tid, DB_PATH),
                    )

                if delete.button("Delete", key=f"del-{tid}"):
                    process_action_once(
                        f"del-{tid}",
                        lambda tid=tid: delete_task_handler(tid, DB_PATH),
                    )

                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Archived section
    # -------------------------------------------------------------------------
    if show_archived:
        archived = [t for t in tasks if t.get("column") == "Archived"]
        st.markdown("---")
        st.subheader("Archived")

        if not archived:
            st.info("No archived tasks")

        for task in archived:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(
                _format_card_html(
                    task["title"],
                    task.get("priority", "Medium"),
                    task.get("date_added", ""),
                ),
                unsafe_allow_html=True,
            )
            if task.get("description"):
                with st.expander("Details"):
                    st.write(task["description"])

            if st.button("Delete", key=f"del-arch-{task['id']}"):
                delete_task_handler(task["id"], DB_PATH)

            st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Handlers (UI + tests)
# -----------------------------------------------------------------------------
def add_task_handler(
    title, description, column="Backlog", priority="Medium", db_path=DB_PATH
):
    tid = db.add_task(
        title, description, column=column, priority=priority, db_path=db_path
    )
    logger.info("add_task: id=%s title=%s", tid, title)
    return tid


def move_task_handler(task_id, direction, db_path=DB_PATH) -> bool:
    task = db.get_task(task_id, db_path=db_path)
    if not task:
        return False

    cur = task.get("column", "Backlog")
    if cur not in STATUSES:
        return False

    idx = STATUSES.index(cur)
    if direction == "left" and idx > 0:
        db.move_task(task_id, STATUSES[idx - 1], db_path=db_path)
        return True
    if direction == "right" and idx < len(STATUSES) - 1:
        db.move_task(task_id, STATUSES[idx + 1], db_path=db_path)
        return True
    return False


def archive_task_handler(task_id, db_path=DB_PATH):
    db.archive_task(task_id, db_path=db_path)
    logger.info("archive_task: id=%s", task_id)


def delete_task_handler(task_id, db_path=DB_PATH):
    db.delete_task(task_id, db_path=db_path)
    logger.info("delete_task: id=%s", task_id)


if __name__ == "__main__":
    main()
