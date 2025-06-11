from logging import debug
import logging
import os
from worker import Worker
import webview
import time
import sys
import subprocess
import psutil
import random
from PIL import Image
from io import BytesIO
import pytesseract
import re
import multiprocessing
class Api:
    def __init__(self, adb_dir):
        self.adb = f"{adb_dir}/adb.exe"
        self.emulator_port = "5554"

    def start_adb(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == 'adb.exe':
                return
        subprocess.run(f'{self.adb} start-server', shell=True)              
    
    def get_emulators(self):
        subprocess.run(f'{self.adb} devices', shell=True)              
    
    def connect_emulator(self, port: str):
        output = subprocess.run(f'{self.adb} connect 127.0.0.1:{self.emulator_port}', shell=True, capture_output=True)              
        text = output.stdout.decode('utf-8')
        result = next((True for a in text.split() if a == 'connected'), None)
        print(result)

    def set_emulator_port(self, port: str):
        self.emulator_port = port
        subprocess.run(f'{self.adb} connect 127.0.0.1:{self.emulator_port}', shell=True)              

    def clean_up(self):
        output = subprocess.run(f'{self.adb} devices', shell=True, capture_output=True)              
        text = output.stdout.decode('utf-8')
        devices = re.sub(r'\r\n?|\r', '\n', text).replace("List of devices attached", "")
        emulators = [e for e in devices.split()]
        count = sum(1 for d in emulators if d == "device")
        if count <= 1:
            self.kill_adb()
        sys.exit()

    def restart_adb(self):
        subprocess.run(f'{self.adb} kill-server', shell=True)              
        subprocess.run(f'{self.adb} start-server', shell=True)              

    def kill_adb(self):
        subprocess.run(f'{self.adb} kill-server', shell=True)              

    def start(self, runs: int):
        self.worker = Worker()
        self.worker.start(runs, self.adb, self.emulator_port)
    
    def status(self):
        return self.worker._running 
    
    def pause(self):
        self.worker.toggle_pause()

    def stop(self):
        self.worker.stop()

    def get_logs(self):
        return self.worker.logs

    def get_inventory(self):
        return self.worker.inventory

    def get_cycles(self):
        return self.worker.cycles

    def toggleCeciliaBot(self):
        try:
            cb = webview.windows[1]
        except IndexError:
            cb = webview.create_window('CeciliaBot', 'https://ceciliabot.github.io/#/', hidden=True, min_size=(1600, 720), frameless=True, easy_drag=True)
        if cb.hidden:
            cb.show()
            cb.hidden = False
        else:
            cb.hide()
            cb.hidden = True


def on_closing():
    try:
        webview.windows[1].destroy()
    except IndexError:
        pass

if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.INFO)
    multiprocessing.freeze_support()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(base_dir, 'web')
    index_path = os.path.join(web_dir, 'index.html')
    adb_dir = os.path.join(base_dir, 'tools/adb')
    tess_dir = os.path.join(base_dir, 'tools/tesseract')
    pytesseract.pytesseract.tesseract_cmd = f"{tess_dir}/tesseract"
    try: 
        print(f"Index file exists: {os.path.exists(index_path)}")
        api = Api(adb_dir)
        api.start_adb()
        #dev
        # window = webview.create_window('E7AutoShop', 'ui/dist/index.html', js_api=api, min_size=(780, 985))
        # cb = webview.create_window('CeciliaBot', 'https://ceciliabot.github.io/#/', hidden=True, min_size=(1600, 720), frameless=True, easy_drag=True)
        # window.events.closing += on_closing
        # webview.start(ssl=True, private_mode=False, http_server=True, http_port=42069, debug=False)

        #prod
        html_path = f'{os.getcwd()}/_internal/web/index.html'
        window = webview.create_window('E7AutoShop', html_path, js_api=api, min_size=(780, 985))
        cb = webview.create_window('CeciliaBot', 'https://ceciliabot.github.io/#/', hidden=True, min_size=(1400, 720), frameless=True, easy_drag=True)
        window.events.closing += on_closing
        webview.start(ssl=True, private_mode=False, http_server=True, http_port=42069, debug=False)

        api.clean_up()
    except Exception as e:
        logging.info(e)
