# E7AutoShop

Application designed to refresh Epic Seven Secret Shop and buy Mystic bookmarks and Covenent bookmarks

Automatic epic seven refresh secret shop

![image](https://github.com/purpxd/E7AutoShop/assets/136267320/6578788c-d53b-4d20-91aa-3fd1db2c26f8)


# Getting Started

1. Download autoshop zip file (https://github.com/purpxd/E7AutoShop/releases/download/v2.2/E7AutoShop.zip)
2. Right click zip file > properties > unblock
3. Extract zip file
4. Launch autoshop.exe

#### Alternative - Build from source
*detailed instructions in contributions section*

1. Build ui
2. Install python dependencies & activate virtualenv
3. pyinstaller main.spec

**Under Emulator settings**

4. Display -> Display resolution ->  **1920 x 1080**
5. Advanced -> Android Debug Bridge(ADB) -> **ON**
6. Take note of the emulator port number (example: 127.0.0.1:**5555**)

**In app**

7. Settings ⚙️ -> Enter port number -> save -> connect

# Notes

1. You will need to set the resolution in your emulator to **1920 x 1080** or it will not work properly
2. Use the default E7 original background or a neutral color background 
3. Turn off chat notifications 

# Contributing

I'll need help with writing the client mode integration as I won't really have time to do it myself.

```
git clone https://github.com/purpxd/E7AutoShop.git
```

## UI

**Install UI dependencies**

```
pnpm i
```

**Start UI**

```
pnpm run dev
```

**Build UI to test with API**

```
pnpm build
```

The client mode only needs to set up the button toggle to interact with the serverless API. Set the boolean value in local storage, retrieve on load and pass it to the API.

## Serverless API

**Create virtualenv and install dependencies**

```
pip install -r requirements.txt
```

**In `main.py` point to index.html**

```
webview.create_window('E7AutoShop', 'ui/dist/index.html', js_api=api, min_size=(780, 985))
```

**Run app**

```
python main.py
```

### To connect API to frontend calls

**Create a function in** `main.py`

```
def example(self):
	print("hello world")
```

**Add entry to** `pywebview.d.ts`

```
example: () => Promise<Any>;
```

**Call it in the UI**

```
window.pywebview.api.example()
```


The emulator mode script is `shop.py` and is called in our thread worker  `worker.py`. For the client mode create a new script and worker to execute in `main.py`

In the client script we need to capture the client window with a specific resolution and take a screenshot of just the item prices and pass it to tesseract. It will be a lot like `shop.py` but we don't have adb to help us with clicks and screenshots. 

I recommend using `pyautogui` for screenshots and inputs. If the inputs aren't registering in the game client I found success using `PyDirectInput`. To get coordinates to crop the images download `autohotkey` and use windows spy mode to see app coordinates in real time. 

**Proceed with caution**. Not sure what kind of mechanisms SG has to detect inputs in the client version. Use a dummy account to test first.
