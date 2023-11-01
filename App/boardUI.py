from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class BoardUi(QMainWindow):
    def __init__(self):
        super(BoardUi, self).__init__()

        self.setWindowTitle("Barge Kanban")
        self.setGeometry(100, 100, 800, 400)

        widget = QWidget()
        self.layout = QHBoxLayout(widget)
        self.setCentralWidget(widget)

        self.setUp_ui()

    def setUp_ui(self):
        self.toDo_List = QListWidget()
        self.toDo_List.setMinimumWidth(300)
        self.toDo_List.setMaximumWidth(400)

        self.inProgress_List = QListWidget()
        self.inProgress_List.setMinimumWidth(300)
        self.inProgress_List.setMaximumWidth(400)

        self.done_List = QListWidget()
        self.done_List.setMinimumWidth(300)
        self.done_List.setMaximumWidth(400)

        self.addTask_button = QPushButton("Add Task")

        self.layout.addWidget(self.column_ui("To Do", self.toDo_List))
        self.layout.addWidget(self.column_ui("In Progress", self.inProgress_List))
        self.layout.addWidget(self.column_ui("Done", self.done_List))
        self.layout.addWidget(self.addTask_button)
        
    def column_ui(self, title, list_widget):
        column_layout = QVBoxLayout()
        column_label = QLabel(title)
        column_label.setStyleSheet("font-weight: bold;")

        column_layout.addWidget(column_label)
        column_layout.addWidget(list_widget)

        group_container = QWidget()
        group_container.setLayout(column_layout)

        return group_container
