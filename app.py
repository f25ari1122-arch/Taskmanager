import sqlite3
import heapq
from datetime import date, datetime
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------
# INTELLIGENT TASK PRIORITY MANAGER
# DSA used:
# 1. Hash Map (dictionary): fast task lookup by ID
# 2. Priority Queue (heap): get the next task to complete
# 3. Sorting: arrange tasks by deadline or priority
# 4. Searching: find tasks by title or description
# ---------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "tasks.db"

st.set_page_config(
    page_title="Task Priority Manager",
    page_icon="📋",
    layout="wide"
)

PRIORITY_VALUES = {"High": 1, "Medium": 2, "Low": 3}
PRIORITY_LABELS = {1: "High", 2: "Medium", 3: "Low"}


def connect_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with connect_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL
            )
        """)
        connection.commit()


def add_task(title, description, priority, deadline):
    with connect_db() as connection:
        connection.execute(
            """INSERT INTO tasks
               (title, description, priority, deadline, status, created_at)
               VALUES (?, ?, ?, ?, 'Pending', ?)""",
            (
                title.strip(),
                description.strip(),
                priority,
                deadline.isoformat(),
                datetime.now().isoformat(timespec="seconds")
            )
        )
        connection.commit()


def get_all_tasks():
    with connect_db() as connection:
        rows = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def update_status(task_id, new_status):
    with connect_db() as connection:
        connection.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (new_status, task_id)
        )
        connection.commit()


def delete_task(task_id):
    with connect_db() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()


def build_task_hash_map(tasks):
    """Dictionary provides direct task lookup using the task ID."""
    return {task["id"]: task for task in tasks}


def calculate_priority_score(task):
    """
    Smaller score means a task should be handled sooner.
    High priority receives the strongest weight.
    Overdue and close deadlines receive extra urgency.
    """
    priority_score = PRIORITY_VALUES[task["priority"]] * 100
    days_left = (date.fromisoformat(task["deadline"]) - date.today()).days

    if days_left < 0:
        deadline_score = -100
    elif days_left == 0:
        deadline_score = -80
    elif days_left <= 2:
        deadline_score = -40
    elif days_left <= 7:
        deadline_score = -15
    else:
        deadline_score = 0

    return priority_score + deadline_score


def build_priority_queue(tasks):
    """Heap-based priority queue: lowest score is removed first."""
    task_heap = []

    for task in tasks:
        if task["status"] == "Pending":
            score = calculate_priority_score(task)
            heapq.heappush(
                task_heap,
                (score, task["deadline"], task["id"])
            )

    return task_heap


def get_recommended_tasks(tasks):
    task_map = build_task_hash_map(tasks)
    task_heap = build_priority_queue(tasks)

    recommended = []
    while task_heap:
        score, deadline, task_id = heapq.heappop(task_heap)
        task = task_map.get(task_id)
        if task:
            recommended.append((task, score))

    return recommended


def search_tasks(tasks, search_text):
    """Simple linear search through title and description."""
    search_text = search_text.strip().lower()
    if not search_text:
        return tasks

    return [
        task for task in tasks
        if search_text in task["title"].lower()
        or search_text in task["description"].lower()
    ]


def format_deadline(deadline_text):
    deadline = date.fromisoformat(deadline_text)
    days_left = (deadline - date.today()).days

    if days_left < 0:
        return f"{deadline.strftime('%d %b %Y')} (Overdue)"
    if days_left == 0:
        return f"{deadline.strftime('%d %b %Y')} (Today)"
    if days_left == 1:
        return f"{deadline.strftime('%d %b %Y')} (Tomorrow)"
    return deadline.strftime("%d %b %Y")


def show_task_card(task, score=None):
    deadline_text = format_deadline(task["deadline"])
    priority_icon = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}
    with st.container(border=True):
        first, second = st.columns([4, 1])
        with first:
            st.markdown(f"**{task['title']}**")
            if task["description"]:
                st.caption(task["description"])
            st.write(
                f"{priority_icon[task['priority']]} {task['priority']} priority"
                f"  ·  📅 {deadline_text}  ·  {task['status']}"
            )
            if score is not None:
                st.caption(f"Priority score: {score} (lower means more urgent)")
        with second:
            st.caption(f"Task #{task['id']}")


initialize_database()
st.title("📋 Intelligent Task Priority Manager")
st.caption("Organize tasks, track deadlines, and let a priority queue recommend what to do next.")

tasks = get_all_tasks()
pending_tasks = [task for task in tasks if task["status"] == "Pending"]
completed_tasks = [task for task in tasks if task["status"] == "Completed"]
overdue_tasks = [
    task for task in pending_tasks
    if date.fromisoformat(task["deadline"]) < date.today()
]

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Total tasks", len(tasks))
metric2.metric("Pending", len(pending_tasks))
metric3.metric("Completed", len(completed_tasks))
metric4.metric("Overdue", len(overdue_tasks))

st.divider()

tab_dashboard, tab_add, tab_manage, tab_search, tab_dsa = st.tabs(
    ["🏠 Dashboard", "➕ Add Task", "🛠 Manage Tasks", "🔎 Search", "🧠 DSA Explanation"]
)

with tab_dashboard:
    st.subheader("What should you work on next?")
    recommended = get_recommended_tasks(tasks)

    if recommended:
        st.success("Tasks are ranked using priority level and deadline urgency.")
        for position, (task, score) in enumerate(recommended, start=1):
            st.markdown(f"**Recommendation #{position}**")
            show_task_card(task, score)
    else:
        st.info("No pending tasks. Add a task to see recommendations.")

    st.subheader("Recently completed")
    if completed_tasks:
        for task in completed_tasks[:5]:
            show_task_card(task)
    else:
        st.caption("No completed tasks yet.")

with tab_add:
    st.subheader("Create a new task")
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task title", placeholder="Example: Prepare DSA presentation")
        description = st.text_area("Description", placeholder="Add a short note (optional)")
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        with col2:
            deadline = st.date_input("Deadline", min_value=date(2000, 1, 1))
        submitted = st.form_submit_button("Add Task", type="primary")

        if submitted:
            if not title.strip():
                st.error("Please enter a task title.")
            else:
                add_task(title, description, priority, deadline)
                st.success("Task added successfully.")
                st.rerun()

with tab_manage:
    st.subheader("Update or delete tasks")
    if not tasks:
        st.info("There are no tasks to manage yet.")
    else:
        task_options = {
            f"#{task['id']} — {task['title']} ({task['status']})": task["id"]
            for task in tasks
        }
        selected_label = st.selectbox("Choose a task", list(task_options.keys()))
        selected_id = task_options[selected_label]
        selected_task = build_task_hash_map(tasks).get(selected_id)

        if selected_task:
            st.write(f"**Description:** {selected_task['description'] or 'No description'}")
            st.write(f"**Priority:** {selected_task['priority']}")
            st.write(f"**Deadline:** {format_deadline(selected_task['deadline'])}")

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if selected_task["status"] == "Pending":
                    if st.button("Mark as Completed", type="primary", use_container_width=True):
                        update_status(selected_id, "Completed")
                        st.success("Task marked as completed.")
                        st.rerun()
                else:
                    if st.button("Move back to Pending", use_container_width=True):
                        update_status(selected_id, "Pending")
                        st.rerun()
            with action_col2:
                if st.button("Delete Task", type="secondary", use_container_width=True):
                    delete_task(selected_id)
                    st.success("Task deleted.")
                    st.rerun()

with tab_search:
    st.subheader("Find a task")
    search_text = st.text_input("Search by title or description")
    status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
    results = search_tasks(tasks, search_text)

    if status_filter != "All":
        results = [task for task in results if task["status"] == status_filter]

    st.caption(f"{len(results)} task(s) found")
    if results:
        # Sorting is another DSA operation demonstrated in this project.
        results = sorted(
            results,
            key=lambda task: (
                task["status"] == "Completed",
                PRIORITY_VALUES[task["priority"]],
                task["deadline"]
            )
        )
        for task in results:
            show_task_card(task)
    else:
        st.info("No matching tasks found.")

with tab_dsa:
    st.subheader("Data structures and algorithms used")
    st.markdown("""
    **1. Hash Map (Python dictionary)**  
    Stores tasks using their unique ID as the key. This allows direct lookup of a task.

    **2. Priority Queue (Heap)**  
    The `heapq` module keeps the most urgent pending task at the front. The task with the smallest score is recommended first.

    **3. Sorting**  
    Search results are sorted by status, priority, and deadline.

    **4. Searching**  
    The search feature checks task titles and descriptions for the entered text.
    """)
    st.subheader("How the priority score works")
    st.write("The system starts with a score based on the priority level:")
    st.markdown("- High = 100")
    st.markdown("- Medium = 200")
    st.markdown("- Low = 300")
    st.write("It then subtracts an urgency adjustment when the deadline is close or overdue. A lower final score means the task is recommended earlier.")
    st.info("This is a rule-based DSA project, not a machine-learning model. The recommendation logic is visible and easy to explain in a viva.")

st.divider()
st.caption("Intelligent Task Priority Manager · Python + Streamlit + SQLite")
