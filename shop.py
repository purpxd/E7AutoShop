
import re
import time
import random
import subprocess
import pytesseract
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from io import BytesIO
import concurrent.futures
from typing import Tuple, List
from multiprocessing import Pool

class Shop:
    def __init__(self, adb: str, port: str) -> None:
        self.adb = adb
        self.emulator_port = port

    def _random_tap(self, args: Tuple[Tuple[int, int], Tuple[int, int], int]):
        (x_range, y_range, delay) = args
        time.sleep(float(f"0.{delay}"))
        x = random.randint(*x_range)
        y = random.randint(*y_range)
        cmd = f"{self.adb} -s 127.0.0.1:{self.emulator_port} shell input tap {x} {y}"
        subprocess.run(cmd, shell=True, check=False)

    def parallel_taps(
        self, 
        x_range: Tuple[int, int], 
        y_range: Tuple[int, int], 
        num_taps: int = 4,
        delay: int = 0
    ) -> None:
        with Pool(processes=num_taps) as pool:
            pool.map(self._random_tap, [(x_range, y_range, delay)] * num_taps)

    def refresh(self):
        self.parallel_taps(x_range=(120, 520), y_range=(965, 1030), num_taps=3, delay=1)
        self.parallel_taps(x_range=(120, 520), y_range=(965, 1030), num_taps=1, delay=3)
        self.parallel_taps(x_range=(1000, 1240), y_range=(639, 704), num_taps=3, delay=1)
        self.parallel_taps(x_range=(1000, 1240), y_range=(639, 704), num_taps=1, delay=3)

    def screen(self):
        screen_bytes = subprocess.Popen(f"{self.adb} -s 127.0.0.1:{self.emulator_port} exec-out screencap -p", stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        img_bytes = screen_bytes.stdout.read()
        screenshot = Image.open(BytesIO(img_bytes))
        img = screenshot.convert("L")
        return img

    def purchase(self, item: str):
        items = {
            'item_1': (1730, random.randint(222, 270)),    #250
            'item_2': (1730, random.randint(440, 485)),    #470
            'item_3': (1730, random.randint(660, 705)),    #680
            'item_4': (1730, random.randint(875, 918)),    #890
            'item_5': (1730, random.randint(770, 811)),    #788
            'item_6': (1730, random.randint(985, 1030)),   #1000
            }
        _, y = items[item]
        for _ in range(2):
            subprocess.Popen(f"{self.adb} -s 127.0.0.1:{self.emulator_port} shell input tap {random.randint(1600, 1850)} {y}", shell=True)
            time.sleep(0.25)

        # self.parallel_taps(x_range=(1600, 1850), y_range=items[item], num_taps=1, delay=0)
        # self.parallel_taps(x_range=(1600, 1850), y_range=items[item], num_taps=1, delay=3)
        time.sleep(0.25)
        # self.parallel_taps(x_range=(1000, 1275), y_range=(740, 790), num_taps=1, delay=0)
        # self.parallel_taps(x_range=(1000, 1275), y_range=(740, 790), num_taps=3, delay=3)

        for _ in range(4):
            subprocess.Popen(f"{self.adb} -s 127.0.0.1:{self.emulator_port} shell input tap {random.randint(1000, 1275)} {random.randint(740, 790)}", shell=True)
            time.sleep(0.5)

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
        subprocess.Popen(f"{self.adb} -s 127.0.0.1:{self.emulator_port} shell input touchscreen swipe {randomized_start_x} {randomized_start_y} {randomized_end_x} {randomized_end_y}", shell=True)

    def identify_item(self, item: str) -> str:
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
        match item:
            case '184000':
                return 'Covenant Bookmarks'
            case '280000':
                return 'Mystic Medals'
            case '18000':
                return 'Friendship Bookmarks'
            case '29000':
                return 'Fodder'
            case _:
                try:
                    return gear_grade[item]
                except KeyError:
                    return 'Error'

    def capture(self, screenshot,  item_number: int):
        bag = {"loot": [], "cart": []}
        ss_crops = {
                'item_1': (1660, 140, 1850, 190),
                'item_2': (1660, 350, 1850, 410),
                'item_3': (1660, 570, 1850, 630),
                'item_4': (1660, 790, 1850, 850),
                'item_5': (1660, 680, 1850, 735),
                'item_6': (1660, 900, 1850, 955),
                }
        purchase_list = ['184000', '280000', '']
        ss = screenshot.crop(ss_crops[f'item_{item_number}'])
        convert = pytesseract.image_to_string(ss)
        item = re.sub(r'[\n\s,\.]', '', convert)
        if item in purchase_list:
            bag['cart'].append(f"item_{item_number}")
        item_name = self.identify_item(item)
        # if item_name == "Error":
        #     ss.show()
        bag['loot'].append(item_name)
        return bag

    def Run(self) -> List[str]:
            loot = []
            self.refresh()
            time.sleep(0.5)
            screenshot = self.screen()
            screenshot.load()

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                process = [executor.submit(self.capture, screenshot, n) for n in range(1,5)]
                results = []
                for future in concurrent.futures.as_completed(process):
                    result = future.result()
                    if result:
                        results.append(result)

            for items in results:
                for bookmarks in items['cart']:
                    self.purchase(bookmarks)
                for item in items['loot']:
                    loot.append(item)

            self.swipe()
            time.sleep(1)
            screenshot = self.screen()
            screenshot.load()

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                process = [executor.submit(self.capture, screenshot, n) for n in range(5,7)]
                results = []
                for future in concurrent.futures.as_completed(process):
                    result = future.result()
                    if result:
                        results.append(result)

            for items in results:
                for bookmarks in items['cart']:
                    self.purchase(bookmarks)

                for item in items['loot']:
                    loot.append(item)
            return loot

if __name__ == "__main__":
    pass
