@echo off
cd /d C:\Users\jerez\logbook
call .venv\Scripts\activate.bat
waitress-serve --listen=0.0.0.0:8000 logbook.wsgi:application