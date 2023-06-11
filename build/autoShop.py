from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar, QTabWidget, QWidget, QPushButton, QVBoxLayout, QDialogButtonBox,  QTableWidget, QTableWidgetItem, QSpacerItem, QSizePolicy
import sys
from PyQt5.QtGui import QMovie
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from shop import Emulator
import asyncio, time
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from sqlobject import *
from models import Sessions, Settings
import os
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QCoreApplication
from squish import squeeze

import subprocess
class WorkerThread(QThread):
    progress_updated = pyqtSignal(int)
    status_message = pyqtSignal(str)
    def __init__(self, skystones) -> None:
        super().__init__()
        self.skystones = skystones
        self.progress = 0



    async def process_emulator(self, emulator):
        for i in range(1, self.skystones + 1):
            inventory = await emulator.main()
            print(i)
            self.status_message.emit(f"runs: {inventory['session_refreshes']} covenant: {inventory['covenants']} mystics: {inventory['mystics']} gems_spent: {inventory['gems_spent']} gold_spent: {inventory['gold_spent']} time_spent: {inventory['session_duration']} seconds")
            self.progress_updated.emit(i)
        session = Sessions(covenants=inventory['covenants'], 
                    mystics=inventory['mystics'], 
                    friendships=inventory['friendships'], 
                    session_duration=inventory['session_duration'], 
                    session_refreshes=inventory['session_refreshes'], 
                    gems_spent=inventory['gems_spent'], 
                    gold_spent=inventory['gold_spent'])
        squeeze() # condense the data
        session.sync()
        print(inventory)
        emulator.clear_inventory()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        emulator = Emulator()
        loop.run_until_complete(self.process_emulator(emulator))

    def stop(self):
        loop = asyncio.get_event_loop()
        loop.stop()
class MainWidget(QWidget):
    status_message = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        layout = QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        # Create and configure the label
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(25, 0, 200, 200))
        self.label.setMinimumSize(QtCore.QSize(200, 200))
        self.label.setMaximumSize(QtCore.QSize(600, 400))
        self.label.setObjectName("label")

        # Set QMovie as the label
        self.movie = QMovie("img/lobby.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")

        self.text = QtWidgets.QLabel("Skystones you want to use") 
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.text.setFont(font)

        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBoxValue = 100
        font = QtGui.QFont()
        font.setPointSize(11)
        self.spinBox.setFont(font)
        self.spinBox.setMaximum(100000)
        self.spinBox.setProperty("value", self.spinBoxValue)
        self.spinBox.setObjectName("spinBox")


        self.start_button = QPushButton("Start")
        self.exit_button = QPushButton("Quit")
        self.button_box = QDialogButtonBox()
        
        self.button_box.addButton(self.start_button, QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.exit_button, QDialogButtonBox.RejectRole)



        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.text)
        layout.addWidget(self.spinBox)
        layout.addWidget(self.button_box)

        #connections
        
        self.spinBox.valueChanged.connect(self.spin_box_value_changed)
        self.start_button.clicked.connect(self.start_button_clicked)
        self.exit_button.clicked.connect(self.exit_button_clicked)
        
    def handle_status_message(self, message): #from main
        self.status_message.emit(message)



    def spin_box_value_changed(self, value):
        self.spinBoxValue = value
        print("Updated value:", self.spinBoxValue)

    def start_button_clicked(self):
        print("Start")
        self.progressBar.setProperty("value", 0) #reset progress
        print(f'starting {self.spinBoxValue // 3} runs')
        self.start_task(self.spinBoxValue // 3)

    def exit_button_clicked(self):
        sys.exit()

    def start_task(self, skystones):
        self.start_button.setEnabled(False)  # Disable the button while the task is running

        self.worker_thread = WorkerThread(skystones)
        self.worker_thread.finished.connect(self.task_finished)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.status_message.connect(self.handle_status_message)
        self.worker_thread.start()

    def update_progress(self, progress):
        total_runs = self.spinBoxValue // 3
        adjusted_percentage = (progress / total_runs) * 100
        self.progressBar.setProperty("value", adjusted_percentage)


    def task_finished(self):
        print("Task finished")
        self.start_button.setEnabled(True) 

class DataWorker(QThread):
    data_loaded = pyqtSignal()

    def run(self):
        # Connect to the SQLite database
        database_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")
        connection_string = f'sqlite:///{database_file}'
        connection = connectionForURI(connection_string)
        sqlhub.processConnection = connection

        # Fetch data from the Sessions table
        sessions = Sessions.select()

        # Emit the signal to indicate that data loading is complete
        self.data_loaded.emit()

class LogWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

        # Create the data worker thread
        self.data_worker = DataWorker()
        self.data_worker.data_loaded.connect(self.on_data_loaded)

        # Load initial data
        self.load_data()

        # Refresh the data every 2 minutes
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(60000) 

    def load_data(self):
        # Start the data worker thread
        self.data_worker.start()

    def on_data_loaded(self):
        # Retrieve data from the database and update the table
        sessions = Sessions.select(orderBy=Sessions.q.id)

        self.table_widget.setRowCount(sessions.count())
        self.table_widget.setColumnCount(8)

        headers = ["date", "cov", "mystic", "friend", "elapsed(s)", "refreshes", "gems spent", "gold spent"]
        self.table_widget.setHorizontalHeaderLabels(headers)
        rows = list(sessions)
        for row, session in enumerate(rows):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(session.date)))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(session.covenants)))
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(session.mystics)))
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(session.friendships)))
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(session.session_duration)))
            self.table_widget.setItem(row, 5, QTableWidgetItem(str(session.session_refreshes)))
            self.table_widget.setItem(row, 6, QTableWidgetItem(str(session.gems_spent)))
            self.table_widget.setItem(row, 7, QTableWidgetItem(str(session.gold_spent)))
        print('Fetching db')
        self.table_widget.resizeColumnsToContents()

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        label = QtWidgets.QLabel("Enter Port Number:")
        layout.addWidget(label)

        self.port_num = QtWidgets.QLineEdit()
        self.port_num.setPlaceholderText("Port Number")
        self.port_num.setFixedWidth(150)
        layout.addWidget(self.port_num)

        dlabel = QtWidgets.QLabel("Enter Delay:")
        layout.addWidget(dlabel)
        self.delay = QtWidgets.QLineEdit()
        self.delay.setPlaceholderText("delay")
        self.delay.setFixedWidth(150)
        layout.addWidget(self.delay)

        self.checkBox = QtWidgets.QCheckBox(self)
        self.checkBox.setCheckable(True)
        self.checkBoxStatus = False
        self.checkBox.setChecked(self.checkBoxStatus)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.setText("Friendship BM")
        layout.addWidget(self.checkBox)
        
        spacer_item = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer_item)
        self.save_button = QPushButton("Save")
        self.button_box = QDialogButtonBox()
        self.button_box.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        layout.addWidget(self.button_box)

        self.checkBox.clicked.connect(self.toggle_checkbox)
        self.save_button.clicked.connect(self.save)
        self.load_settings()

    def load_settings(self):
        # Connect to the SQLite database
        database_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")
        connection_string = f'sqlite:///{database_file}'
        connection = connectionForURI(connection_string)
        sqlhub.processConnection = connection

        try:
            settings = Settings.selectBy(id=1) 
            if settings:
                for setting in settings:
                    print(f"{setting.port_number}")
                    self.port_num.setText(f"{setting.port_number}")
                    self.delay.setText(f"{setting.delay}")

                    if setting.enable_friendship == 1:
                        self.checkBoxStatus = True
                        self.checkBox.setChecked(self.checkBoxStatus)
                    else:
                        self.checkBoxStatus = False
                        self.checkBox.setChecked(self.checkBoxStatus)
                else:
                    pass
            else:
                settings = Settings(id=1, enable_friendship=0, port_number=0, delay=0)
                settings.sync()
        except SQLObjectNotFound:
            settings = Settings(id=1, enable_friendship=0, port_number=0, delay=0)
            settings.sync()

    def save(self):
        if self.checkBoxStatus:
            checkbox = 1
        else:
            checkbox = 0
        try:
            settings = Settings.selectBy(id=1).getOne()
        except SQLObjectNotFound:
            settings = Settings(id=1, enable_friendship=0, port_number=0, delay=0)
            settings.sync()
        try:
            if settings:
                # Update existing row
                settings.enable_friendship = checkbox
                settings.port_number = int(self.port_num.text())
                settings.delay = int(self.delay.text())
                settings.sync()
            else:
                # Create new row
                settings = Settings(id=1, enable_friendship=checkbox, port_number=1, delay=0)
                settings.sync()
        except ValueError:
            pass
        print(settings)
        
    def toggle_checkbox(self, checked):
        self.checkBoxStatus = checked
        print(self.checkBoxStatus)
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoShop")
        self.resize(684, 765)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.West)
        tabs.setMovable(True)

        main_tab = MainWidget()
        log_tab = LogWidget()
        settings_tab = SettingsWidget()

        tabs.addTab(main_tab, "Main")
        tabs.addTab(log_tab, "Log")
        tabs.addTab(settings_tab, "Settings")

        self.setCentralWidget(tabs)


        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")  

        main_tab.status_message.connect(self.update_status_bar)

    def update_status_bar(self, message): #from mainwindow
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(message)  
app = QApplication(sys.argv)
window = MainWindow()
icon = QIcon("img/arky.png")  
window.setWindowIcon(icon)

window.show()

sys.exit(app.exec_())
