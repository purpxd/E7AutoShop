
import re
import os
import sys
import time
import random
import socket
import logging
import subprocess
import pytesseract
from PIL import Image
from io import BytesIO
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import  QThread, pyqtSignal


class ShopThread(QThread):
    progress_updated = pyqtSignal(int)
    status_message = pyqtSignal(str)
    inventory = pyqtSignal(dict)
    finished = pyqtSignal(dict)
    def __init__(self, skystones) -> None:
        super().__init__()
        self.skystones = skystones
        self.progress = 0
        self.paused = False 
        self.stopped = False 
        self.stash = {}

    def start_run(self, autoshop):
        for i in range(1, self.skystones + 1):
            if self.stopped: 
                break
            inventory = autoshop.main()
            self.inventory.emit(inventory)
            self.progress_updated.emit(i)
            self.stash.update(inventory)
            while self.paused:  
                time.sleep(1)  
        self.finished.emit(self.stash)
        autoshop.clear_inventory()

    def run(self):
        autoshop = Shop()
        self.start_run(autoshop)

    def stop(self):
        self.stopped = True

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False


class Shop:
    inventory = {
        'covenants': 0,
        'mystics': 0,
        'session_refreshes': 0,
        'gems_spent': 0,
        'gold_spent': 0
        }
    
    def __init__(self) -> None:
        logging.basicConfig(filename='error.log', level=logging.ERROR)
        adb_path = os.path.join(os.path.dirname(__file__), '..', 'tools/adb', 'adb.exe')
        self.adb = os.path.abspath(adb_path)
        #pytesseract.pytesseract.tesseract_cmd = r"tesseract-ocr\tesseract.exe"
        pytesseract.pytesseract.tesseract_cmd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools/tesseract-ocr', 'tesseract.exe'))
        subprocess.call(['taskkill', '/F', '/IM', 'adb.exe'])
        subprocess.run(f'{self.adb} start-server', shell=True)              #static y values
        self.items = {'item_1': ['1730', f'{random.randint(222, 270)}'],    #250
                      'item_2': ['1730', f'{random.randint(440, 485)}'],    #470
                      'item_3': ['1730', f'{random.randint(660, 705)}'],    #680
                      'item_4': ['1730', f'{random.randint(875, 918)}'],    #890
                      'item_5': ['1730', f'{random.randint(770, 811)}'],    #788
                      'item_6': ['1730', f'{random.randint(985, 1030)}'],   #1000
                      }
        self.ss_crops = { #value capture
                'item_1': (1660, 140, 1860, 190),
                'item_2': (1660, 350, 1860, 410),
                'item_3': (1660, 570, 1860, 630),
                'item_4': (1660, 790, 1860, 850),
                'item_5': (1660, 680, 1860, 735),
                'item_6': (1660, 900, 1860, 955),
                }
        self.purchase_list = ['184000', '280000']

    def purchase(self, item):
        _, y = self.items[item] 
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1600, 1850)} {y}")
        time.sleep(0.25)
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1600, 1850)} {y}")
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1000, 1275)} {random.randint(740, 790)}")
        time.sleep(0.5)
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1000, 1275)} {random.randint(740, 790)}")
        time.sleep(0.5)
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1000, 1275)} {random.randint(740, 790)}")
        time.sleep(0.5)
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1000, 1275)} {random.randint(740, 790)}")
        time.sleep(1)

    def screen(self):
        screen_bytes = subprocess.Popen(f"{self.adb} exec-out screencap -p", stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        img_bytes = screen_bytes.stdout.read()
        screenshot = Image.open(BytesIO(img_bytes))
        return screenshot

    def swipe(self):
        start_x = 1050
        start_y = 500
        end_x = 1250
        end_y = 50
        speed_range = 50
        randomized_start_x = start_x + random.randint(-speed_range, speed_range)
        randomized_start_y = start_y + random.randint(-speed_range, speed_range)
        randomized_end_x = end_x + random.randint(-speed_range, speed_range)
        randomized_end_y = end_y + random.randint(-speed_range, speed_range)
        subprocess.Popen(f"{self.adb} shell input touchscreen swipe {randomized_start_x} {randomized_start_y} {randomized_end_x} {randomized_end_y}", shell=True)

    def click_missions(self):
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1142, 1490)} {random.randint(850, 909)}")
        time.sleep(0.1)
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1142, 1490)} {random.randint(850, 909)}")
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1142, 1490)} {random.randint(850, 909)}")
        time.sleep(0.1)
        subprocess.Popen(f"{self.adb} shell input tap {random.randint(1142, 1490)} {random.randint(850, 909)}")

    def refresh(self):
        time.sleep(0.25)
        subprocess.call(f"{self.adb} shell input tap {random.randint(120, 520)} {random.randint(965, 1030)}")
        time.sleep(0.5)
        subprocess.call(f"{self.adb} shell input tap {random.randint(120, 520)} {random.randint(965, 1030)}")
        time.sleep(0.25)
        subprocess.call(f"{self.adb} shell input tap {random.randint(990, 1240)} {random.randint(639, 704)}")
        time.sleep(0.25)
        subprocess.call(f"{self.adb} shell input tap {random.randint(990, 1240)} {random.randint(639, 704)}")
        time.sleep(0.25)
        subprocess.call(f"{self.adb} shell input tap {random.randint(990, 1240)} {random.randint(639, 704)}")
        self.inventory['gems_spent']+=3
        self.inventory['session_refreshes']+=1

    def clear_inventory(self):
        self.inventory.update({
        'covenants': 0,
        'mystics': 0,
        'session_refreshes': 0,
        'gems_spent': 0,
        'gold_spent': 0
        })

    def identify_item(self, item):
        gear_grade = {
            '240000' : 'Level 55 Equipment Grade: Good',
            '360000' : 'Level 55 Equipment Grade: Rare',
            '480000' : 'Level 55 Equipment Grade: Heroic',
            '600000' : 'Level 55 Equipment Grade: Epic',
            '380000' : 'Level 70 Equipment Grade: Good',
            '560000' : 'Level 70 Equipment Grade: Rare',
            '750000' : 'Level 70 Equipment Grade: Heroic',
            '940000' : 'Level 70 Equipment Grade: Epic',
            '540000' : 'Level 85 Equipment Grade: Good',
            '810000' : 'Level 85 Equipment Grade: Rare',
            '1100000' : 'Level 85 Equipment Grade: Heroic',
            '1400000' : 'Level 85 Equipment Grade: Epic'
        }
        if item == '184000':
            return 'Covenant Bookmarks'
        elif item == '280000':
            return 'Mystic Medals'
        elif item == '18000':
            return 'Friendship Bookmarks'
        elif item == '29000':
            return 'Fodder'
        else:
            try:
                return gear_grade[item]
            except KeyError:
                return 'Error'

    def capture(self, screenshot, item_number):
        ss = screenshot.crop(self.ss_crops[f'item_{item_number}'])
        # ss.show() #pop out screenshot to verify
        convert = pytesseract.image_to_string(ss)
        item = re.sub(r'[\n\s,\.]', '', convert)
        # print(item)
        # print(repr(item)) ##print each item
        self.output.append(self.identify_item(item))
        if item in self.purchase_list:
            if item == '18000':
                self.inventory['friendships']+= 5
                self.inventory['gold_spent']+=18000
                self.output.append(f'Purchased: Friendship Bookmarks')
            elif item == '184000':
                self.inventory['covenants']+=5
                self.inventory['gold_spent']+=184000
                self.output.append(f"Purchased: Covenant Bookmarks at {self.inventory['session_refreshes']} refreshes")
            elif item == '280000':
                self.inventory['mystics']+=50
                self.inventory['gold_spent']+=280000
                self.output.append(f"Purchased: Mystic Medals at {self.inventory['session_refreshes']} refreshes")
            self.purchase(f'item_{item_number}')

    def main(self):
        host = 'localhost'
        port = 42069
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        stdout = sys.stdout
        sys.stdout = self.output = []
        try:
            self.refresh()
            # self.click_missions()
            self.output.append(f"\n\n{self.inventory['session_refreshes']}")
            time.sleep(0.5)
            screenshot = self.screen()
            for n in range(1, 5):
                self.capture(screenshot, n)
            time.sleep(0.5)
            self.swipe()
            time.sleep(1)
            # self.click_missions()
            screenshot = self.screen()
            for n in range(5, 7):
                self.capture(screenshot, n)
            time.sleep(0.5)
            output_text = '\n'.join(self.output)
            self.sock.sendall(output_text.encode())
            return self.inventory
        except Exception as e:
            logging.exception(str(e))
        finally:
            sys.stdout = stdout


if __name__ == "__main__":
    pass

