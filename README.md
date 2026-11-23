# Intelligent Task Priority Manager

A beginner-friendly, medium-level Data Structures and Algorithms project built with Python, Streamlit, and SQLite.

## Features

- Add tasks with a title, description, priority, and deadline.
- Automatically recommend which pending task should be completed first.
- Mark tasks as completed or move them back to pending.
- Delete tasks.
- Search by task title or description.
- Filter tasks by status.
- Display total, pending, completed, and overdue task counts.
- Save tasks in a local SQLite database.

## DSA concepts demonstrated

| DSA concept | Where it is used |
|---|---|
| Hash Map (dictionary) | Find a task directly using its unique ID |
| Priority Queue (heap) | Recommend the most urgent pending task |
| Sorting | Arrange search results |
| Searching | Find tasks by title or description |

## How the recommendation works

Each task gets a score:

- High priority starts at 100.
- Medium priority starts at 200.
- Low priority starts at 300.
- Close or overdue deadlines reduce the score.

The task with the lowest score is recommended first. The heap (`heapq`) keeps this priority order efficiently.

This is a rule-based recommendation system, not machine learning. Its logic is simple enough to explain and demonstrate in a viva.

## Requirements

- Python 3.9 or newer
- Internet connection for the first installation only

## Run on Windows

1. Download and extract this project.
2. Open the extracted folder in VS Code.
3. Open the VS Code terminal.
4. Install the requirements:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Run the app:

   ```bash
   python -m streamlit run app.py
   ```

6. Streamlit will show a local URL. Open it in your browser.

## Deploy using GitHub and Streamlit Community Cloud

1. Create a new GitHub repository.
2. Upload `app.py`, `requirements.txt`, and `README.md`.
3. Open Streamlit Community Cloud and connect your GitHub account.
4. Select the repository and set the main file path to `app.py`.
5. Deploy.

## Project files

```text
intelligent_task_priority_manager/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

The `tasks.db` SQLite database is created automatically when the app runs for the first time. Do not upload your personal database to a public repository.

## Viva explanation

**What is the main purpose?**  
It helps users organize tasks and recommends which pending task to do first based on priority and deadline.

**Why use a priority queue?**  
Because the system needs to repeatedly identify the most urgent task. A min-heap makes the lowest score available at the top.

**Why use a hash map?**  
A dictionary stores each task using its ID, making it easy to retrieve a task directly.

**Where is searching used?**  
The search tab checks task titles and descriptions.

**Where is sorting used?**  
Search results are arranged by completion status, priority, and deadline.

**Is this machine learning?**  
No. It uses fixed rules and DSA structures. It is an algorithm-based task manager.

**What happens when a task is completed?**  
Its status changes to Completed, so it is no longer included in the pending-task priority queue.

## Note about online deployment

The included SQLite database is suitable for a simple single-user demonstration. Some hosted platforms may reset local files when an app restarts or redeploys. For a persistent multi-user production app, use a hosted database.
