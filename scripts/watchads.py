import os
import time
import random
import logging
import subprocess
import pytesseract
from PIL import Image
from io import BytesIO
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import  QThread, pyqtSignal

class WatcherThread(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.stopped = False
        adb_path = os.path.join(os.path.dirname(__file__), '..', 'tools/adb', 'adb.exe')
        self.adb = os.path.abspath(adb_path)
        #pytesseract.pytesseract.tesseract_cmd = r"tesseract-ocr\tesseract.exe"
        pytesseract.pytesseract.tesseract_cmd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools/tesseract-ocr', 'tesseract.exe'))
        subprocess.call(['taskkill', '/F', '/IM', 'adb.exe'])
        subprocess.run(f'{self.adb} start-server', shell=True)

    def screen(self) -> Image:
        screen_bytes = subprocess.Popen(f"{self.adb} exec-out screencap -p", stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        img_bytes = screen_bytes.stdout.read()
        screenshot = Image.open(BytesIO(img_bytes))
        screenshot.crop((1575, 116, 1675, 162))
        crop_box = (1575, 116, 1675, 162)
        cropped = screenshot.crop(crop_box)
        return cropped
    
    def stop(self):
        self.stopped = True

    def run(self):
        count = 0
        try:
            subprocess.Popen(f"{self.adb} shell input tap {random.randint(1224, 1400)} {random.randint(705, 900)}")
            time.sleep(0.5)
            subprocess.Popen(f"{self.adb} shell input tap {random.randint(1224, 1400)} {random.randint(705, 900)}")
            while True:
                if self.stopped:
                    break
                if count == 0:
                    time.sleep(10)
                else:
                    time.sleep(5)
                if count == 5:
                    break
                cropped = self.screen()
                text = pytesseract.image_to_string(cropped)
                if text.strip() == "Event":
                    subprocess.Popen(f"{self.adb} shell input tap {random.randint(1504, 1718)} {random.randint(111, 160)}")
                    subprocess.Popen(f"{self.adb} shell input tap {random.randint(1504, 1718)} {random.randint(111, 160)}")
                    time.sleep(2)
                    subprocess.Popen(f"{self.adb} shell input tap {random.randint(1224, 1400)} {random.randint(705, 900)}")
                    time.sleep(0.5)
                    subprocess.Popen(f"{self.adb} shell input tap {random.randint(1224, 1400)} {random.randint(705, 900)}")
                    count+=1
                    self.progress.emit(count)
                    time.sleep(2)
                else:
                    subprocess.Popen(f"{self.adb} shell input keyevent 4")
            self.finished.emit()
        except Exception as e:
            logging.exception(str(e))
