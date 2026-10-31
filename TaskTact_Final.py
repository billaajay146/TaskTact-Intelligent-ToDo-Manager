import json
from pathlib import Path
from datetime import datetime

# Store tasks in the same folder as this Python file.
DATA_FILE = Path(__file__).resolve().parent / "tasks.json"


def load_tasks():
    """Load tasks from tasks.json."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            tasks = json.load(file)

        if not isinstance(tasks, list):
            print("Warning: tasks.json has an invalid format. Starting with no tasks.")
            return []

        # Add missing fields if the file was created by an older version.
        for index, task in enumerate(tasks, start=1):
            task.setdefault("id", index)
            task.setdefault("title", "Untitled task")
            task.setdefault("category", "Other")
            task.setdefault("due_date", "Not set")
            task.setdefault("priority", "Medium")
            task.setdefault("status", "Pending")
            task.setdefault("created_at", "")

        return tasks

    except (json.JSONDecodeError, OSError) as error:
        print(f"Warning: Could not load tasks.json: {error}")
        return []


def save_tasks(tasks):
    """Save tasks to JSON and report whether saving succeeded."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4, ensure_ascii=False)
        return True
    except OSError as error:
        print(f"Error saving tasks: {error}")
        return False


def next_task_id(tasks):
    return max((task.get("id", 0) for task in tasks), default=0) + 1


def pause():
    input("\nPress Enter to return to the main menu...")


def show_tasks(tasks):
    """Option 2: display every task, including a message when none exist."""
    print("\n" + "=" * 90)
    print("                         TASKTACT - ALL TASKS")
    print("=" * 90)

    if not tasks:
        print("No tasks found.")
        print("Use option 1 to add your first task.")
        print("=" * 90)
        return

    print(
        f"{'ID':<5}{'TITLE':<25}{'CATEGORY':<15}"
        f"{'DUE DATE':<15}{'PRIORITY':<12}{'STATUS':<12}"
    )
    print("-" * 90)

    for task in tasks:
        print(
            f"{task['id']:<5}"
            f"{task['title'][:23]:<25}"
            f"{task['category'][:13]:<15}"
            f"{task['due_date']:<15}"
            f"{task['priority']:<12}"
            f"{task['status']:<12}"
        )

    print("-" * 90)
    print(f"Total tasks: {len(tasks)}")
    print("=" * 90)


def add_task(tasks):
    """Option 1: add a new task."""
    print("\n--- ADD NEW TASK ---")

    title = input("Enter task title: ").strip()
    if not title:
        print("Task title cannot be empty.")
        return

    category = input("Category (Study/Work/Personal/Other): ").strip()
    if not category:
        category = "Other"

    due_date = input("Due date (YYYY-MM-DD) or press Enter to skip: ").strip()
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD.")
            return
    else:
        due_date = "Not set"

    priority = input("Priority (Low/Medium/High): ").strip().capitalize()
    if not priority:
        priority = "Medium"

    if priority not in ("Low", "Medium", "High"):
        print("Invalid priority. Choose Low, Medium, or High.")
        return

    task = {
        "id": next_task_id(tasks),
        "title": title,
        "category": category,
        "due_date": due_date,
        "priority": priority,
        "status": "Pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    tasks.append(task)

    if save_tasks(tasks):
        print(f"Task added successfully. Task ID: {task['id']}")


def get_task_by_id(tasks):
    """Ask for an ID and return the matching task."""
    if not tasks:
        print("There are no tasks to select.")
        return None

    try:
        task_id = int(input("Enter task ID: ").strip())
    except ValueError:
        print("Please enter a valid numeric task ID.")
        return None

    for task in tasks:
        if task["id"] == task_id:
            return task

    print("Task ID not found.")
    return None


def update_task(tasks):
    """Option 3: update an existing task."""
    print("\n--- UPDATE TASK ---")
    show_tasks(tasks)

    task = get_task_by_id(tasks)
    if task is None:
        return

    print("Press Enter to keep the current value.")

    new_title = input(f"Title [{task['title']}]: ").strip()
    new_category = input(f"Category [{task['category']}]: ").strip()
    new_priority = input(
        f"Priority [{task['priority']}] (Low/Medium/High): "
    ).strip().capitalize()
    new_due_date = input(
        f"Due date [{task['due_date']}] (YYYY-MM-DD): "
    ).strip()

    if new_priority and new_priority not in ("Low", "Medium", "High"):
        print("Invalid priority. No changes were saved.")
        return

    if new_due_date:
        try:
            datetime.strptime(new_due_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date. No changes were saved.")
            return

    if new_title:
        task["title"] = new_title
    if new_category:
        task["category"] = new_category
    if new_priority:
        task["priority"] = new_priority
    if new_due_date:
        task["due_date"] = new_due_date

    if save_tasks(tasks):
        print("Task updated successfully.")


def delete_task(tasks):
    """Option 4: delete a task after confirmation."""
    print("\n--- DELETE TASK ---")
    show_tasks(tasks)

    task = get_task_by_id(tasks)
    if task is None:
        return

    confirmation = input(
        f"Delete task '{task['title']}'? (y/n): "
    ).strip().lower()

    if confirmation == "y":
        tasks.remove(task)
        if save_tasks(tasks):
            print("Task deleted successfully.")
    else:
        print("Deletion cancelled.")


def filter_tasks(tasks):
    """Option 5: filter tasks by category, status, or priority."""
    print("\n--- CATEGORIZE / FILTER TASKS ---")

    if not tasks:
        print("No tasks available to filter.")
        return

    print("1. Filter by category")
    print("2. Filter by status")
    print("3. Filter by priority")

    choice = input("Choose filter (1-3): ").strip()

    if choice == "1":
        value = input("Enter category: ").strip().casefold()
        filtered = [
            task for task in tasks
            if task["category"].casefold() == value
        ]

    elif choice == "2":
        value = input("Enter status (Pending/Completed): ").strip().capitalize()
        if value not in ("Pending", "Completed"):
            print("Invalid status.")
            return
        filtered = [task for task in tasks if task["status"] == value]

    elif choice == "3":
        value = input("Enter priority (Low/Medium/High): ").strip().capitalize()
        if value not in ("Low", "Medium", "High"):
            print("Invalid priority.")
            return
        filtered = [task for task in tasks if task["priority"] == value]

    else:
        print("Invalid filter choice.")
        return

    print("\n--- FILTER RESULTS ---")
    show_tasks(filtered)


def mark_completed(tasks):
    """Option 6: mark a selected task as completed."""
    print("\n--- MARK TASK AS COMPLETED ---")
    show_tasks(tasks)

    task = get_task_by_id(tasks)
    if task is None:
        return

    if task["status"] == "Completed":
        print("This task is already completed.")
        return

    task["status"] = "Completed"

    if save_tasks(tasks):
        print("Task marked as completed.")


def show_summary(tasks):
    """Option 7: display task statistics."""
    total = len(tasks)
    completed = sum(1 for task in tasks if task["status"] == "Completed")
    pending = total - completed

    print("\n========== TASK SUMMARY ==========")
    print(f"Total tasks     : {total}")
    print(f"Completed tasks : {completed}")
    print(f"Pending tasks   : {pending}")

    if total:
        completion_rate = (completed / total) * 100
        print(f"Completion rate : {completion_rate:.1f}%")

    print("==================================")


def main():
    tasks = load_tasks()

    print("\nWelcome to TaskTact - Intelligent To-Do Manager!")
    print(f"Task data file: {DATA_FILE}")

    while True:
        print("\n" + "=" * 48)
        print("          TASKTACT - INTELLIGENT TO-DO")
        print("=" * 48)
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Categorize / Filter Tasks")
        print("6. Mark Task as Completed")
        print("7. View Task Summary")
        print("8. Exit")
        print("-" * 48)

        choice = input("Enter your choice (1-8): ").strip()
        print(f"\nYou selected: {choice}")

        if choice == "1":
            add_task(tasks)
            pause()

        elif choice == "2":
            show_tasks(tasks)
            pause()

        elif choice == "3":
            update_task(tasks)
            pause()

        elif choice == "4":
            delete_task(tasks)
            pause()

        elif choice == "5":
            filter_tasks(tasks)
            pause()

        elif choice == "6":
            mark_completed(tasks)
            pause()

        elif choice == "7":
            show_summary(tasks)
            pause()

        elif choice == "8":
            print("Thank you for using TaskTact. Your tasks are saved.")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 8.")
            pause()


if __name__ == "__main__":
    main()
