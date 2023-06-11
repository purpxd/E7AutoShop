@echo off
set current_dir=%CD%
cd ..
call "virtual_env\Scripts\activate.bat"

python build/autoShop.py