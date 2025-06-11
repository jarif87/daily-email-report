@echo off
cd /d E:\dailyreport
call .\venv\Scripts\activate.bat
python app.py >> log.txt 2>&1