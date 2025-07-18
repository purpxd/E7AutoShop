# E7AutoShop
Application designed to refresh Epic Seven Secret Shop and buy Mystic bookmarks and Covenent bookmarks

Automatic epic seven refresh secret shop

![image](https://github.com/purpxd/E7AutoShop/assets/136267320/6578788c-d53b-4d20-91aa-3fd1db2c26f8)



# Getting Started
1. Download the installer (https://github.com/purpxd/E7AutoShop/releases/download/v2.1.1/autoshop_installer_v2.1.1.exe)
2. Launch installer
3. Inside your emulator set the resolution to **1920 x 1080**. In advanced settings, enable ADB
4. Start autoshop.exe

# Video Demo



https://github.com/purpxd/E7AutoShop/assets/136267320/f8659821-1c0a-4378-823a-aaac91f5e58c


# Notes
1. You will need to set the resolution in your emulator to 1920 x 1080 or it will not work properly

# Developers

1. Setup python version to use 3.10.5
2. Setup venv
3. Modify ui with designer

```
qt5-tools designer
```

4. Generate resource & ui files

```
pyuic5 -x main.ui -o ui.py
```

```
pyrcc5 resource.qrc -o resource_rc.py
```

5. Download Android Debug Bridge(ADB) and Tesseract executables
- ADB: https://developer.android.com/tools/releases/platform-tools
- Tesseract: https://tesseract-ocr.github.io/tessdoc/Downloads.html

copy the binaries over to their respective folders in tools/

6. Build app

```
pyinstaller autoshop.spec
```

