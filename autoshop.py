import os
import sys
import uuid
import ctypes
import socket
import logging
import requests
import win32gui
import win32con
import webbrowser
import qdarktheme
import subprocess
import win32console
import base64 as b
import segment.analytics as sa
from models import Sessions
from ui import Ui_MainWindow
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from scripts.shop import ShopThread
from scripts.watchads import WatcherThread
from PyQt5.QtGui import (
                            QMovie,
                            QFont,
                            QIcon
)
from PyQt5.QtWidgets import (
                            QMainWindow,
                            QApplication,
                            QHeaderView,
                            QLabel,
                            QTableWidgetItem
)
from PyQt5.QtCore import (
                            pyqtSlot,
                            pyqtSignal,
                            QSettings,
                            QThread,
                            QTimer
)


class SocketThread(QThread):
    data_recv = pyqtSignal(str)

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = 'localhost'
        port = 42069
        self.sock.bind((host, port))
        self.sock.listen(1)
        while True:
            conn, _ = self.sock.accept()
            data = conn.recv(4096).decode()
            self.emit_data(data)
            conn.close()

    def emit_data(self, data):
        self.data_recv.emit(data)


class Stopwatch(QTimer):
    def __init__(self, label: QLabel) -> None:
        super().__init__()
        self.label = label
        self.time_elapsed = 0
        self.is_running = False
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label.setFont(font)
        self.timeout.connect(self.update_time)

    def update_time(self):
        self.time_elapsed += 1
        hours = self.time_elapsed // 3600
        minutes = (self.time_elapsed % 3600) // 60
        seconds = self.time_elapsed % 60
        self.time = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        self.label.setText(self.time)

    def toggle_start_stop(self):
        if self.is_running:
            self.stop()
            self.is_running = False
        else:
            self.start(1000)
            self.is_running = True


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        logging.basicConfig(filename='error.log', level=logging.ERROR)
        load_dotenv()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.shop_stopwatch = Stopwatch(self.ui.lobby_timer)
        self.version = "2.0"
        self.info = self.check()
        self.settings = QSettings('E7autoshop', 'Settings')
        sa.write_key = self.info['key']
        self.addr = self.fetch_addr()
        self.user()
        self.autoshop_status = False
        self.watching = False
        self.lobbymov = QMovie(os.path.abspath(os.path.join(os.path.dirname(__file__), 'img', 'lobby')))
        self.ui.lobby_mov.setMovie(self.lobbymov)
        self.lobbymov.start()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.donation_logo.setOpenExternalLinks(True)
        self.ui.donation_logo.mousePressEvent = self.open_url
        self.ui.autoshop_start_btn.setEnabled(False)
        self.ui.autoshop_pause_btn.setEnabled(False)
        self.ui.autoshop_stop_btn.setEnabled(False)
        self.theme = None
        self.ui_theme()
        self.import_e7leaks()
        self.ui.patch_edit.verticalScrollBar().setValue(self.ui.patch_edit.verticalScrollBar().maximum())
        self.ui.lobby_console.setStyleSheet("background-color: black; color: #1cfc03;")
        self.ui.skystones_input.textChanged.connect(self.validate_input)
        self.populate_table()
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.ui.tableWidget.resizeColumnsToContents()
        Sessions.createTable(ifNotExists=True)
        self.socket_thread = SocketThread()
        self.socket_thread.data_recv.connect(self.update_console)
        self.socket_thread.start()
        self.announcement()

    def update_console(self, data):
        self.ui.lobby_console.append(data)

    def announcement(self):
        self.ui.announcement.setText(self.info['announcement'])

    def validate_input(self):
        if not self.ui.skystones_input.text().isdigit() or len(str(self.ui.skystones_input.text())) == 0:
            self.ui.autoshop_start_btn.setEnabled(False)
            self.ui.skystones_input.clear()
        else:
            self.ui.autoshop_start_btn.setEnabled(True)

    def fetch_addr(self):
        try:
            r = requests.get(self.info['addr1'])
        except Exception:
            r = requests.get(self.info['addr2'])
        return r

    def import_e7leaks(self):
        url = self.info['leaks']
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        div_elements = soup.find_all("div", class_="mb-4")
        for div in div_elements:
            card_header = div.find("h5", class_="card-header")
            header = card_header.text.replace(")", ") ")
            header_with_css = f"<span style='font-weight:bold;'>{header}</span>"
            self.ui.patch_edit.append(header_with_css)
            card_body = div.find("div", class_="card-body")
            ul = card_body.find("ul")
            for li in ul:
                self.ui.patch_edit.append(str(li))
                self.ui.patch_edit.append("\n")

    def on_autoshop_btn_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.history_btn.setChecked(False)

    def on_history_btn_clicked(self):
        self.ui.autoshop_btn.setChecked(False)
        self.ui.history_btn.setChecked(True)
        self.ui.stackedWidget.setCurrentIndex(1)

    @pyqtSlot()
    def on_watchads_btn_clicked(self):
        if not self.watching:
            self.watching = True
            self.watcher = WatcherThread()
            self.ui.lobby_console.append("Watching ads...")
            self.ui.skystones_input.setEnabled(False)
            self.watcher.progress.connect(self.ads_progress)
            self.watcher.finished.connect(self.finished_ads)
            self.watcher.start()
            self.ui.history_btn.setChecked(False)
            self.ui.autoshop_btn.setChecked(False)
            self.ui.watchads_btn.setChecked(True)
        else:
            self.watching = False
            self.ui.lobby_console.append("Stopping Ads")
            self.watcher.stop()
            self.ui.watchads_btn.setChecked(False)

    @pyqtSlot()
    def on_update_btn_clicked(self):
        webbrowser.open(self.info['github'])
        if self.info['github_t']:
            sa.track(self.id, 'UPDATE', self.info['github_sa'])

    def open_url(self, event):
        webbrowser.open(self.info['donation'])
        if self.info['qr_t']:
            sa.track(self.id, 'QR Code', self.info['qr_sa'])

    @pyqtSlot()
    def on_autoshop_start_btn_clicked(self):
        self.ui.autoshop_start_btn.setEnabled(False)
        self.ui.autoshop_pause_btn.setEnabled(True)
        self.ui.autoshop_stop_btn.setEnabled(True)
        self.ui.skystones_input.setEnabled(False)
        self.autoshop_status = True
        self.ui.lobby_timer.setText('00:00:00')
        self.shop_stopwatch.toggle_start_stop()
        self.skystones = int(self.ui.skystones_input.text())
        refreshes = self.skystones // 3
        self.shop_thread = ShopThread(refreshes)
        self.shop_thread.progress_updated.connect(self.update_shop_progress)
        self.shop_thread.inventory.connect(self.update_inventory)
        self.shop_thread.finished.connect(self.finished_run)
        self.shop_thread.start()
        self.ui.lobby_console.append(f"Starting {refreshes} runs")
        self.currency(0, 0, 0, 0)   # reset currency and colors
        self.color_currency()

    @pyqtSlot()
    def on_autoshop_pause_btn_clicked(self):
        self.ui.autoshop_pause_btn.setEnabled(True)
        self.ui.autoshop_stop_btn.setEnabled(True)
        if self.autoshop_status:
            self.ui.autoshop_pause_btn.setText('Resume')
            self.autoshop_status = False
            self.shop_stopwatch.toggle_start_stop()
            self.shop_thread.pause()
            self.ui.lobby_console.append("Pausing")
        else:
            self.ui.autoshop_pause_btn.setText('Pause')
            self.autoshop_status = True
            self.shop_stopwatch.toggle_start_stop()
            self.shop_thread.resume()
            self.ui.lobby_console.append("Resuming")

    def on_autoshop_stop_btn_clicked(self):
        self.ui.autoshop_start_btn.setEnabled(True)
        self.ui.autoshop_pause_btn.setEnabled(False)
        self.ui.autoshop_stop_btn.setEnabled(False)
        self.ui.skystones_input.clear()
        self.ui.skystones_input.setEnabled(True)
        self.shop_stopwatch.stop()
        self.shop_thread.stop()
        self.ui.lobby_console.append("Stopping")

    def ui_theme(self):
        if self.settings.contains('theme'):
            self.theme = self.settings.value('theme')
            qdarktheme.setup_theme(self.theme)
            if self.theme == "dark":
                self.ui.dark_btn.setVisible(False)
                self.ui.light_btn.setVisible(True)
            else:
                self.ui.dark_btn.setVisible(True)
                self.ui.light_btn.setVisible(False)
        else:
            qdarktheme.setup_theme()
            self.theme = "dark"
            self.ui.dark_btn.setVisible(False)
            self.ui.light_btn.setVisible(True)

    def on_dark_btn_clicked(self):
        self.theme = "dark"
        qdarktheme.setup_theme(self.theme)
        self.ui.light_btn.setVisible(True)
        self.ui.dark_btn.setVisible(False)
        self.color_currency()
        self.settings.setValue('theme', self.theme)

    def on_light_btn_clicked(self):
        self.theme = "light"
        qdarktheme.setup_theme(self.theme)
        self.ui.light_btn.setVisible(False)
        self.ui.dark_btn.setVisible(True)
        self.color_currency()
        self.settings.setValue('theme', self.theme)

    def check(self) -> dict:
        headers = {'X-API-KEY': b.b64decode(os.getenv("K")).decode("utf-8")}
        r = requests.get(b.b64decode(os.getenv("U")).decode("utf-8"), headers=headers)
        info = r.json()
        if self.version != info['app_version']:
            self.ui.update_btn.setVisible(True)
        else:
            self.ui.update_btn.setVisible(False)
        return info

    def user(self):
        id = str(uuid.uuid4())
        if self.settings.contains('user_id'):
            self.id = self.settings.value('user_id')
            if self.info['identify']:
                sa.identify(user_id=self.id, traits={'app_version': self.version}, context={'ip': self.addr.text})
        else:
            self.settings.setValue('user_id', id)
            traits = {
                'app_version': self.version,
                'createdAt': datetime.now()
            }
            self.id = id
            if self.info['identify']:
                sa.identify(user_id=self.id, traits=traits, context={'ip': self.addr.text})
        if self.info['session_start']:
            sa.track(self.id, '$session_start', self.info['started'], context={'ip': self.addr.text})

    def finished_ads(self):
        self.ui.watchads_btn.setChecked(False)
        self.ui.lobby_console.append("Ads Finished")
        self.ui.skystones_input.setEnabled(True)
        if self.info['ads_t']:
            sa.track(self.id, 'ads', self.info['ads_sa'])

    def ads_progress(self, progress):
        self.ui.lobby_console.append(f"Finished watching ad {progress}")

    def finished_run(self, stash):
        self.ui.autoshop_start_btn.setEnabled(True)
        self.ui.autoshop_pause_btn.setEnabled(False)
        self.ui.autoshop_stop_btn.setEnabled(False)
        self.ui.skystones_input.clear()
        self.ui.skystones_input.setEnabled(True)
        self.shop_stopwatch.stop()
        Sessions.create_update(date=datetime.today().strftime("%Y-%m-%d"), covenants=stash['covenants'], mystics=stash["mystics"], gems=stash["gems_spent"], gold=stash["gold_spent"])
        if self.info['run_completed_t']:
            sa.track(self.id, 'run_completed', {'application': 'E7AutoShop', 'status': 'finished', 'description': 'Finished autoshop cycle', 'covenents': stash['covenants'], 'mystics': stash["mystics"], 'gems_used': stash["gems_spent"], 'gold_used': stash["gold_spent"], 'duration': self.ui.lobby_timer.text()})
        self.update_inventory(stash)
        self.populate_table()

    def update_shop_progress(self, progress):
        total_runs = self.skystones // 3
        adjusted_percentage = (progress / total_runs) * 100
        if adjusted_percentage == 100:
            self.ui.autoshop_start_btn.setEnabled(True)
            self.ui.autoshop_pause_btn.setEnabled(False)
            self.ui.autoshop_stop_btn.setEnabled(False)
            self.ui.skystones_input.clear()
            self.ui.skystones_input.setEnabled(True)
            self.shop_stopwatch.stop()
        self.ui.lobby_progress_bar.setProperty("value", adjusted_percentage)

    def currency(self, cov: int, myst: int, sky: int, gold: int):
        """Populates the currency box"""
        self.ui.cov_label.setText(str(cov))
        self.ui.mystic_label.setText(str(myst))
        self.ui.skystone_label.setText(str(sky))
        self.ui.gold_label.setText(str(gold))

    def color_currency(self):
        """changes currency text"""
        if self.theme == "light":
            color = "black"
        else:
            color = "white"
        self.ui.cov_label.setStyleSheet(f"color: {color};")
        self.ui.mystic_label.setStyleSheet(f"color: {color};")
        self.ui.skystone_label.setStyleSheet(f"color: {color};")
        self.ui.gold_label.setStyleSheet(f"color: {color};")

    def update_inventory(self, inventory: dict):
        """Inventory status"""
        inventory_styles = {
            'covenants': (self.ui.cov_label, 'green'),
            'mystics': (self.ui.mystic_label, 'green'),
            'gems_spent': (self.ui.skystone_label, 'red'),
            'gold_spent': (self.ui.gold_label, 'red')
        }
        if not sum(inventory.values()) == 0:
            self.currency(inventory['covenants'], inventory['mystics'], inventory['gems_spent'], inventory['gold_spent'])
            for key, (label, color) in inventory_styles.items():
                if inventory[key] > 0:
                    label.setStyleSheet(f"color: {color};")
                else:
                    if self.theme == "light":
                        label.setStyleSheet("color: black;")
                    else:
                        label.setStyleSheet("color: white;")
        else:
            pass

    def populate_table(self):
        """Populates history table"""
        data = Sessions.get_data()
        self.ui.tableWidget.setRowCount(data.count())
        for index, row in enumerate(data):
            self.ui.tableWidget.setItem(index, 0, QTableWidgetItem(str(row.date)))
            self.ui.tableWidget.setItem(index, 1, QTableWidgetItem(str(row.covenants)))
            self.ui.tableWidget.setItem(index, 2, QTableWidgetItem(str(row.mystics)))
            self.ui.tableWidget.setItem(index, 3, QTableWidgetItem(str(row.gems_spent)))
            self.ui.tableWidget.setItem(index, 4, QTableWidgetItem(str(row.gold_spent)))

    def hide_console_window(self):
        try:
            console_window = win32console.GetConsoleWindow()
            if console_window != 0:
                win32gui.ShowWindow(console_window, win32con.SW_HIDE)
        except ImportError as e:
            print(e)

    def exit(self):
        if self.info['session_end']:
            sa.track(self.id, '$session_end', self.info['finished'], context={'ip': self.addr.text})
        subprocess.call(['taskkill', '/F', '/IM', 'adb.exe'])

if __name__ == "__main__":
    basedir = os.path.dirname(__file__)
    try:
        if sys.platform == 'win32':
            myappid = 'mycompany.myproduct.subproduct.version'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        app = QApplication(sys.argv)
        window = MainWindow()
        window.setWindowTitle(f"AutoShop v{window.version}")
        # icon = QIcon("img/arky.png")
        icon = QIcon(os.path.join(basedir, 'img/arky.png'))
        window.setWindowIcon(icon)
        window.show()
        window.hide_console_window()
        app.aboutToQuit.connect(window.exit)
        sys.exit(app.exec())
    except Exception as e:
        logging.exception(str(e))
