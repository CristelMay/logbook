@echo off
cd /d "c:\Users\jerez\new-logbook\logbook"
call .venv\Scripts\activate
start "Logbook Server" cmd /k ".venv\Scripts\python -m waitress --port=8000 logbook.wsgi:application"