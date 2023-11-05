import json
import os

from task import Task


class TaskList:
    def __init__(self, boardName):
        self.numTasks = 0
        self.boardName = boardName
        filename = boardName + "_taskList.json"
        if os.path.isfile(filename):
            with open(filename, "r") as infile:
                file_data = json.load(infile)
                self.numTasks = file_data[self.boardName]["numTasks"]


    def addTask(self, newTask):
        filename = self.boardName + "_taskList.json"

        if not os.path.isfile(filename):
            self.numTasks = 0
            file_data = {self.boardName: {"numTasks": self.numTasks, "Tasks": []}}
        else:
            with open(filename, "r") as file:
                file_data = json.load(file)

        existing_ids = {task["id"] for task in file_data[self.boardName]["Tasks"]}
        if newTask.id in existing_ids:
            newTask.id = self.numTasks

        taskDict = newTask.serialize()
        file_data[self.boardName]["Tasks"].append(taskDict)
        self.numTasks += 1
        file_data[self.boardName]["numTasks"] = self.numTasks

        with open(filename, "w") as file:
            json.dump(file_data, file, indent=2)

        return True

t = TaskList("testBoard")

newT = Task(0, "test", "this is a test", "01/01/9999", ["www.google.com", "www.duckduckgo.com"], ["me", "you"], 5, "To Do")
newT2 = Task(0, "test", "this is a test", "01/01/9999", ["www.google.com", "www.duckduckgo.com"], ["me", "you"], 5, "To Do")

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
