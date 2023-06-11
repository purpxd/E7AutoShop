
import subprocess, re , time
from PIL import Image
from io import BytesIO
import asyncio, os
import pytesseract
import atexit, signal
from sqlobject import *
from models import Sessions, Settings
class Emulator:
    inventory = {
        'covenants': 0,
        'mystics': 0,
        'friendships': 0,
        'session_duration': 0,
        'session_refreshes': 0,
        'gems_spent': 0,
        'gold_spent': 0
        }
    def __init__(self) -> None:
        self.adb = r"adb\adb.exe"
        pytesseract.pytesseract.tesseract_cmd = r"tesseract-ocr\tesseract.exe"
        self.delay = 0
        self.load_settings()
        try:
            if len(str(self.port_number)) <5:
                self.connect = subprocess.Popen(f"{self.adb} devices")
            else:
                self.connect = subprocess.Popen(f"{self.adb} connect 127.0.0.1:{self.port_number}")
        except AttributeError:
            self.connect = subprocess.Popen(f"{self.adb} connect devices")
        self.items = {'item_1': ['1730', '250'],
                      'item_2': ['1730', '470'],
                      'item_3': ['1730', '680'],
                      'item_4': ['1730', '890'],
                      'item_5': ['1730', '788'],
                      'item_6': ['1730', '1000'],
                      }
        # self.ss_crops = { #old coords when capturing characters instead of values
        #               'item_1': (1000, 185, 1500, 230),
        #               'item_2': (1000, 395, 1500, 460),
        #               'item_3': (1000, 610, 1500, 670),
        #               'item_4': (1000, 830, 1500, 890),
        #               'item_5': (1000, 720, 1500, 780),
        #               'item_6': (1000, 935, 1500, 1000),
        #               }
        self.ss_crops = { #value capture
                'item_1': (1660, 140, 1860, 190),
                'item_2': (1660, 350, 1860, 410),
                'item_3': (1660, 570, 1860, 630),
                'item_4': (1660, 790, 1860, 850),
                'item_5': (1660, 680, 1860, 735),
                'item_6': (1660, 900, 1860, 955),
                }
        # self.purchase_list = ['Covenant Bookmarks', 
        #                  'Mystic Medals'
        #                  ]
        self.purchase_list = ['184000', '280000']
        
    def load_settings(self):
        database_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")
        connection_string = f'sqlite:///{database_file}'
        connection = connectionForURI(connection_string)
        sqlhub.processConnection = connection

        try:
            settings = Settings.selectBy(id=1) 
            if settings:
                for setting in settings:
                    self.port_number = setting.port_number
                    self.delay = setting.delay
                    if setting.enable_friendship == 1:
                        self.friendship = True
                    else:
                        self.friendship = False
                else:
                    pass
            else:
                settings = Settings(id=1, enable_friendship=0, port_number=0)
                settings.sync()
        except (SQLObjectNotFound, AttributeError):
            settings = Settings(id=1, enable_friendship=0, port_number=0)
            settings.sync()

    async def purchase(self, item):
        x, y = self.items[item]
        subprocess.Popen(f"{self.adb} shell input tap {x} {y}")
        time.sleep(2.5)
        subprocess.Popen(f"{self.adb} shell input tap 1055 744") # buy
        subprocess.Popen(f"{self.adb} shell input tap 1055 744")
        time.sleep(1)

    def screen(self):
        screen_bytes = subprocess.Popen(f"{self.adb} exec-out screencap -p", stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        img_bytes = screen_bytes.stdout.read()
        screenshot = Image.open(BytesIO(img_bytes))
        return screenshot

    def swipe(self):
        subprocess.Popen(f"{self.adb} shell input touchscreen swipe 1000 300 1100 50")

    def refresh(self):
        subprocess.Popen(f"{self.adb} shell input tap 328 1000")
        time.sleep(1)
        subprocess.Popen(f"{self.adb} shell input tap 1109 666")
        subprocess.Popen(f"{self.adb} shell input tap 1109 666")
        self.inventory['gems_spent']+=3
        self.inventory['session_refreshes']+=1

    def clear_inventory(self):
        self.inventory['covenants'] = 0
        self.inventory['mystics'] = 0
        self.inventory['friendships'] = 0
        self.inventory['session_duration'] = 0
        self.inventory['session_refreshes'] = 0
        self.inventory['gems_spent'] = 0
        self.inventory['gold_spent'] = 0
        print('clearing inventory')

    async def capture(self, screenshot, item_number):
        ss = screenshot.crop(self.ss_crops[f'item_{item_number}'])
        #ss.show() #pop out screenshot to verify
        item = re.sub(r'[\n\s,\.]', '', pytesseract.image_to_string(ss))
        #print(repr(item)) #print each item
        if item in self.purchase_list:
            if item == '18000':
                self.inventory['friendships']+= 5
                self.inventory['gold_spent']+=18000
                print(f'Purchased: Friendship Bookmarks')
            elif item == '184000':
                self.inventory['covenants']+=5
                self.inventory['gold_spent']+=184000
                print(f'Purchased: Covenant Bookmarks')
            elif item == '280000':
                self.inventory['mystics']+=50
                self.inventory['gold_spent']+=280000
                print(f'Purchased: Mystic Medals')
            await self.purchase(f'item_{item_number}')
            
    async def main(self):
        try:
            if self.friendship:
                self.purchase_list.append('18000')
        except AttributeError:
            pass
        start_time = int(time.time())
        time.sleep(1.5 + self.delay/3)
        screenshot = self.screen()
        
        for n in range(1, 5):
            await self.capture(screenshot, n)
        

        self.swipe()
        time.sleep(1.25 + self.delay/3)
        screenshot = self.screen()
        
        for n in range(5, 7):
            await self.capture(screenshot, n)
        
        time.sleep(0.5 + self.delay/3)
        self.refresh()
        
        end_time = int(time.time()) 
        self.inventory['session_duration'] += end_time - start_time
        return self.inventory
    
if __name__ == "__main__":
    pass

