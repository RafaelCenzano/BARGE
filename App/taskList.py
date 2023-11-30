from curses.ascii import isdigit
import json
import os

from task import Task


class TaskList:
    def __init__(self, boardName) -> None:
        self.numTasks = 0
        self.boardName = boardName
        data_path = os.path.join(
            os.path.abspath(os.path.join(__file__, "../")),
            self.boardName.replace(" ", "_"),
        )
        self.filename = os.path.join(data_path, "data.json")
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as infile:
                file_data = json.load(infile)
                self.numTasks = file_data[self.boardName]["numTasks"]

    def addTask(self, newTask):
        if not os.path.isfile(self.filename):
            self.numTasks = 0
            file_data = {self.boardName: {"numTasks": self.numTasks, "Tasks": []}}
        else:
            with open(self.filename, "r") as file:
                file_data = json.load(file)

        existing_ids = {task["id"] for task in file_data[self.boardName]["Tasks"]}
        if newTask.id in existing_ids:
            newTask.id = self.numTasks

        taskDict = newTask.serialize()
        file_data[self.boardName]["Tasks"].append(taskDict)
        self.numTasks += 1
        file_data[self.boardName]["numTasks"] = self.numTasks

        if not os.path.isdir(os.path.dirname(self.filename)):
            os.mkdir(os.path.dirname(self.filename))
        with open(self.filename, "w") as file:
            json.dump(file_data, file, indent=2)

        return newTask.id

    def deleteTask(self, task_id):
        filename = self.filename

        if not os.path.isfile(filename):
            return False  # No file or tasks to delete

        with open(filename, "r") as file:
            file_data = json.load(file)

        tasks = file_data.get(self.boardName, {}).get("Tasks", [])

        # Find the task with the given ID
        found_task = None
        for task in tasks:
            if task.get("id") == task_id:
                found_task = task
                break

        if found_task:
            tasks.remove(found_task)
            self.numTasks -= 1
            file_data[self.boardName]["Tasks"] = tasks
            file_data[self.boardName]["numTasks"] = self.numTasks

            with open(filename, "w") as file:
                json.dump(file_data, file, indent=2)
            return True  # Task deleted successfully
        else:
            return False  # Task with given ID not found

    def editTask(self, task_id, newTask):
        if self.deleteTask(task_id):
            filename = self.filename

            if not os.path.isfile(filename):
                self.numTasks = 0
                file_data = {self.boardName: {"numTasks": self.numTasks, "Tasks": []}}
            else:
                with open(filename, "r") as file:
                    file_data = json.load(file)

            newTask.id = task_id

            taskDict = newTask.serialize()
            file_data[self.boardName]["Tasks"].append(taskDict)
            self.numTasks += 1
            file_data[self.boardName]["numTasks"] = self.numTasks

            with open(filename, "w") as file:
                json.dump(file_data, file, indent=2)

            return newTask.id
            return task_id
        return False


# t = TaskList("testBoard")

# newT = Task(
#     0,
#     "test",
#     "this is a test",
#     "01/01/9999",
#     ["www.google.com", "www.duckduckgo.com"],
#     ["me", "you"],
#     5,
#     "To Do",
# )
# newT2 = Task(
#     0,
#     "test",
#     "this is a test",
#     "01/01/9999",
#     ["www.google.com", "www.duckduckgo.com"],
#     ["me", "you"],
#     5,
#     "To Do",
# )

# test for local machine
if __name__ == "__main__":
    t = TaskList("testBoard")

    newT = Task(
        0,
        "test",
        "this is a test",
        "01/01/9999",
        ["www.google.com", "www.duckduckgo.com"],
        ["me", "you"],
        5,
        "To Do",
    )
    newT2 = Task(
        0,
        "test",
        "this is a test",
        "01/01/9999",
        ["www.google.com", "www.duckduckgo.com"],
        ["me", "you"],
        5,
        "To Do",
    )

    t.addTask(newT)
    t.addTask(newT2)
