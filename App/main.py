import sys, os
import json
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from sync import Syncing
from task import Task
from taskList import TaskList
from boardUI import BoardUi


# Controller
class MainController:
    def __init__(self):
        self.view = BoardUi()
        self.board = TaskList("test Board")
        self.taskDict = {}
        self.addAllTasksFromFile()
        self.view.syncBoard_button.clicked.connect(self.clickSync)
        self.view.addGithubKey_button.clicked.connect(self.addGithubKey)
        self.view.addTask_button.clicked.connect(self.addTaskScript)
        self.view.toDo_List.itemClicked.connect(self.clickTaskScript)
        self.view.inProgress_List.itemClicked.connect(self.clickTaskScript)
        self.view.done_List.itemClicked.connect(self.clickTaskScript)
        self.view.search_bar.textChanged.connect(self.filterTasks)

        self.view.toDo_List.itemDropped.connect(self.handleItemDrop)
        self.view.inProgress_List.itemDropped.connect(self.handleItemDrop)
        self.view.done_List.itemDropped.connect(self.handleItemDrop)

        # TODO: Need to add board name later VVVV
        self.sync = Syncing("test Board")

        self.view.show()

    def clickSync(self) -> None:
        if self.sync.readyToSync():
            # Eventually switch to not and display error message "missing token/username"
            if not self.sync.connected():
                self.sync.connectRepo()
            self.sync.sync()

    def addAllTasksFromFile(self) -> None:
        if os.path.isfile(self.board.filename):
            with open(self.board.filename, "r") as infile:
                file_dict = json.load(infile)
                test = file_dict[self.board.boardName]["Tasks"]
                print(test)
                for task in test:
                    self.addTaskFromInput(
                        task["id"],
                        task["name"],
                        task["description"],
                        task["timeframe"],
                        task["links"],
                        task["people"],
                        task["points"],
                        task["progress"],
                    )

    def addTaskFromInput(
        self, id, name, description, timeframe, links, people, points, status
    ) -> None:
        newTask = Task(
            id,
            name,
            description,
            timeframe,
            links,
            people,
            points,
            status,
        )
        self.taskDict[id] = newTask
        item = QListWidgetItem(newTask.name)
        item.setData(Qt.ItemDataRole.UserRole, id)
        if status == "To Do":
            self.view.toDo_List.addItem(item)
        elif status == "In Progress":
            self.view.inProgress_List.addItem(item)
        elif status == "Done":
            self.view.done_List.addItem(item)

    def handleItemDrop(self, item, sourceList, targetList) -> bool:
        row = sourceList.row(sourceList.currentItem())
        sourceList.takeItem(row)

        newItem = QListWidgetItem(item)
        targetList.addItem(newItem)

        task_id = item.data(Qt.ItemDataRole.UserRole)
        task = self.taskDict.get(task_id)
        if not task:
            return False

        newTask = Task(
            0,
            task.name,
            task.description,
            task.timeframe,
            task.links,
            task.people,
            task.points,
            targetList.type,
        )
        self.board.editTask(task_id, newTask)
        self.taskDict[task_id] = newTask

        QMessageBox.information(
            self.view,
            "Task Moved",
            f"Task moved from {sourceList.type} to {targetList.type}",
        )
        return True

    def writeKeyAndUserToFile(self, userText, keyText) -> None:
        if self.sync.addUsername(userText) and self.sync.addToken(keyText):
            with open("boardname_gitkey.txt", "w") as f:
                f.write(f"Key :f{keyText}\n")
                f.write(f"User : f{userText}\n")
        else:
            exit()

    def addGithubKey(self) -> None:
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Add GitHub Key")
        dialog_layout = QFormLayout(dialog)
        githubUsername_input = QLineEdit(dialog)
        githubKey_input = QLineEdit(dialog)
        dialog_layout.addRow("Github Key:", githubKey_input)
        dialog_layout.addRow("Github Username:", githubUsername_input)

        add_key_button = QPushButton("Add Username and Key", dialog)
        add_key_button.clicked.connect(
            lambda: self.writeKeyAndUserToFile(
                githubUsername_input.text(), githubKey_input.text()
            )
        )
        add_key_button.clicked.connect(dialog.accept)
        dialog_layout.addWidget(add_key_button)

        dialog.exec()

    def addTaskScript(self) -> None:
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Add Task")
        dialog_Layout = QFormLayout(dialog)

        name_input = QLineEdit(dialog)
        description_input = QLineEdit(dialog)
        timeframe_input = QLineEdit(dialog)
        link_input = QLineEdit(dialog)
        people_input = QLineEdit(dialog)
        points_input = QLineEdit(dialog)
        status_input = QComboBox(dialog)
        status_input.addItems(["To Do", "In Progress", "Done"])

        dialog_Layout.addRow("Name:", name_input)
        dialog_Layout.addRow("Description:", description_input)
        dialog_Layout.addRow("Timeframe(mm/dd/yyyy):", timeframe_input)
        dialog_Layout.addRow("Links:", link_input)
        dialog_Layout.addRow("People:", people_input)
        dialog_Layout.addRow("Points:", points_input)
        dialog_Layout.addRow("Status:", status_input)

        buttons_layout = QHBoxLayout()

        # add button
        add_button = QPushButton("Add", dialog)
        add_button.clicked.connect(
            lambda: self.addTaskToBoard(
                name_input.text(),
                description_input.text(),
                timeframe_input.text(),
                link_input.text(),
                people_input.text(),
                points_input.text(),
                status_input.currentText(),
            )
        )
        add_button.clicked.connect(dialog.accept)

        buttons_layout.addWidget(add_button)
        dialog_Layout.addRow(buttons_layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(
                self.view, "Task Added", "The new task has been added successfully!"
            )

    def addTaskToBoard(
        self, name, description, timeframe, links, people, points, status
    ):
        newTask = Task(
            0,
            name,
            description,
            timeframe,
            links,
            people,
            points,
            status,
        )

        tid = self.board.addTask(newTask)
        self.taskDict[tid] = newTask
        item = QListWidgetItem(newTask.name)
        item.setData(Qt.ItemDataRole.UserRole, tid)

        if status == "To Do":
            self.view.toDo_List.addItem(item)
        elif status == "In Progress":
            self.view.inProgress_List.addItem(item)
        elif status == "Done":
            self.view.done_List.addItem(item)

    def clickTaskScript(self, item):
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Task Options")
        dialog_layout = QVBoxLayout(dialog)

        edit_button = QPushButton("Edit Task")
        delete_button = QPushButton("Delete Task")
        archive_button = QPushButton("Archive Task")
        view_button = QPushButton("View Task")

        edit_button.clicked.connect(lambda: self.edit_task(item))
        edit_button.clicked.connect(lambda: dialog.close())
        delete_button.clicked.connect(lambda: self.delete_task(item))
        delete_button.clicked.connect(lambda: dialog.close())
        archive_button.clicked.connect(lambda: self.archive_task(item))
        archive_button.clicked.connect(lambda: dialog.close())
        view_button.clicked.connect(lambda: self.viewTaskScript(item))
        view_button.clicked.connect(lambda: dialog.close())

        dialog_layout.addWidget(edit_button)
        dialog_layout.addWidget(delete_button)
        if self.taskDict.get(item.data(Qt.ItemDataRole.UserRole)).progress == "Done":
            dialog_layout.addWidget(archive_button)
        dialog_layout.addWidget(view_button)

        dialog.setLayout(dialog_layout)
        dialog.exec()

    def edit_task(self, item):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        task = self.taskDict.get(task_id)

        dialog = QDialog(self.view)
        dialog.setWindowTitle("Edit Task")
        dialog_Layout = QFormLayout(dialog)

        name_input = QLineEdit(dialog)
        name_input.setText(task.name)
        description_input = QLineEdit(dialog)
        description_input.setText(task.description)
        timeframe_input = QLineEdit(dialog)
        timeframe_input.setText(task.timeframe)
        link_input = QLineEdit(dialog)
        link_input.setText(task.links)
        people_input = QLineEdit(dialog)
        people_input.setText(task.people)
        points_input = QLineEdit(dialog)
        points_input.setText(task.points)
        status_input = QComboBox(dialog)
        status_input.addItems(["To Do", "In Progress", "Done"])
        if task.progress == "To Do":
            status_input.setCurrentIndex(0)
        elif task.progress == "In Progress":
            status_input.setCurrentIndex(1)
        elif task.progress == "Done":
            status_input.setCurrentIndex(2)

        dialog_Layout.addRow("Name:", name_input)
        dialog_Layout.addRow("Description:", description_input)
        dialog_Layout.addRow("Timeframe(mm/dd/yyyy):", timeframe_input)
        dialog_Layout.addRow("Links:", link_input)
        dialog_Layout.addRow("People:", people_input)
        dialog_Layout.addRow("Points:", points_input)
        dialog_Layout.addRow("Status:", status_input)

        buttons_layout = QHBoxLayout()

        # edit button
        edit_button = QPushButton("Edit", dialog)
        edit_button.clicked.connect(
            lambda: self.editTaskOnBoard(
                task,
                task_id,
                name_input.text(),
                description_input.text(),
                timeframe_input.text(),
                link_input.text(),
                people_input.text(),
                points_input.text(),
                status_input.currentText(),
            )
        )
        edit_button.clicked.connect(dialog.accept)

        # cancel button
        cancel_button = QPushButton("Cancel", dialog)
        cancel_button.clicked.connect(dialog.reject)

        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(cancel_button)
        dialog_Layout.addRow(buttons_layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(
                self.view, "Task Modified", "The task has been changed successfully!"
            )

    def editTaskOnBoard(
        self,
        task,
        taskid,
        nameIn,
        descriptionIn,
        timeframeIn,
        linkIn,
        peopleIn,
        pointsIn,
        statusIn,
    ):
        if taskid in self.taskDict:
            newTask = Task(
                0,
                nameIn,
                descriptionIn,
                timeframeIn,
                linkIn,
                peopleIn,
                pointsIn,
                statusIn,
            )

            self.board.editTask(taskid, newTask)
            self.taskDict[taskid] = newTask
            item = QListWidgetItem(newTask.name)
            item.setData(Qt.ItemDataRole.UserRole, taskid)
            self.refresh()
            return True
        return False

    def delete_task(self, item):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        task = self.taskDict.get(task_id)
        dialog = QMessageBox()
        dialog.setWindowTitle("Confirm Delete.")
        dialog.setText("Are you sure you want to delete this task?")
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if dialog.exec() == QMessageBox.StandardButton.Yes:
            if self.removeTaskFromBoard(task, task_id):
                self.board.deleteTask(task_id)
                QMessageBox.information(
                    self.view, "Task Deleted", "The task has been deleted successfully!"
                )
            else:
                QMessageBox.information(
                    self.view, "Failure", "The task has not been deleted."
                )

    def removeTaskFromBoard(self, task, taskid):
        if taskid in self.taskDict:
            del self.taskDict[taskid]
            self.refresh()
            return self.board.deleteTask(taskid)
        return False

    def archive_task(self, item):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        task = self.taskDict.get(task_id)
        dialog = QMessageBox()
        dialog.setWindowTitle("Confirm Archive.")
        dialog.setText("Are you sure you want to archive this task?")
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if dialog.exec() == QMessageBox.StandardButton.Yes:
            if self.hideTaskFromBoard(task, task_id):
                QMessageBox.information(
                    self.view, "Task Archived", "The task has been hidden successfully!"
                )
            else:
                QMessageBox.information(
                    self.view, "Failure", "The task was not archived."
                )

    def hideTaskFromBoard(self, task, taskid):
        if taskid in self.taskDict:
            del self.taskDict[taskid]
            self.refresh()
            return True
        return False

    def refresh(self):
        # Clear all lists
        self.view.toDo_List.clear()
        self.view.inProgress_List.clear()
        self.view.done_List.clear()
        for task_id, task in self.taskDict.items():
            item = QListWidgetItem(task.name)
            item.setData(Qt.ItemDataRole.UserRole, task_id)
            if task.progress == "To Do":
                self.view.toDo_List.addItem(item)
            elif task.progress == "In Progress":
                self.view.inProgress_List.addItem(item)
            elif task.progress == "Done":
                self.view.done_List.addItem(item)

    def viewTaskScript(self, item):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        task = self.taskDict.get(task_id)

        if task:
            task_info = (
                f"Name: {task.name}\n"
                f"Description: {task.description}\n"
                f"Timeframe: {task.timeframe}\n"
                f"Status: {task.progress}\n"
            )

        QMessageBox.information(self.view, "Task Information", task_info)

    def filterTasks(self, query):
        query = self.view.search_bar.text().lower()

        # Clear all lists
        self.view.toDo_List.clear()
        self.view.inProgress_List.clear()
        self.view.done_List.clear()
        for task_id, task in self.taskDict.items():
            if query in task.name.lower() or query in task.description.lower():
                item = QListWidgetItem(task.name)
                item.setData(Qt.ItemDataRole.UserRole, task_id)

                if task.progress == "To Do":
                    self.view.toDo_List.addItem(item)
                elif task.progress == "In Progress":
                    self.view.inProgress_List.addItem(task)
                elif task.progress == "Done":
                    self.view.done_List.addItem(task)


class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window")
        layout.addWidget(self.label)
        self.setLayout(layout)


basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "Barge.V1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, "bargeLogo.ico")))
    controller = MainController()
    app.exec()
