import threading
import random
from shop import Shop
from datetime import datetime
def dummy():
    """simulate returning loot"""
    loot_table = {
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
        '1400000' : 'Level 85 Equipment Grade: Epic',
        '184000'  : 'Covenant Bookmarks',
        '280000' : 'Mystic Medals',
        '18000' : 'Friendship Bookmarks',
        '29000' : 'Fodder'
    }
    loot = [loot_table[[k for k in loot_table][random.randint(0, len(loot_table) - 1)]] for _ in range(6)]
    return loot


class Worker:
    def __init__(self):
        self._running = False
        self._paused = False
        self._pause_cond = threading.Condition(threading.Lock())
        self._thread = None
        self.inventory = {"b": 0, "m": 0, "s": 0, "g": 0}
        self.logs = []
        self.cycles = 0

    def start(self, runs, adb, port):
        self.total_runs = runs
        self.shop = Shop(adb, port)
        if self._thread is None or not self._thread.is_alive():
            print(f"Running {runs} times")
            self._running = True
            self._paused = False
            self._thread = threading.Thread(target=self._run_loop)
            self._thread.start()

    def _run_loop(self):
        self.cycles = 0
        while self._running:
            with self._pause_cond:
                while self._paused:
                    self._pause_cond.wait()
                print(f"Run: {self.cycles}")
                self.cycles+=1
                self.inventory['s'] += 3
                loot = self.shop.Run()
                for l in loot:
                    match l:
                        case 'Covenant Bookmarks':
                            self.inventory['b'] += 5
                            self.inventory['g'] += 184000
                        case 'Mystic Medals':
                            self.inventory['m'] += 50
                            self.inventory['g'] += 280000
                logs = [{"id": i + len(self.logs) * 6, "name": item, "run": self.cycles, "time": f"{datetime.now()}"} for i, item in enumerate(loot)]
                for l in logs:
                    self.logs.append(l)
                if self.cycles == self.total_runs:
                    print("runs completed")
                    self.stop()

    def toggle_pause(self):
        if not self._running:
            return

        self._paused = not self._paused

        if not self._paused:
            with self._pause_cond:
                self._pause_cond.notify()

    def stop(self):
        self._running = False
        self._paused = False
        self.bookmarks = 0
        with self._pause_cond:
            self._pause_cond.notify()
        if self._thread is not None:
            self._thread.join()

if __name__ == "__main__":
    dummy()
