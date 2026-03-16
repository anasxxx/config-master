@echo off
cd /d "%~dp0"
set CONFIGMASTER_TOKEN=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmdWxsQGdtYWlsLmNvbSIsImV4cCI6MTk4ODUwMzY0MX0.QxG8Y2S6WaciWGB4ZakwHfdyetaI9uxdM4GZD6Nt4Ok
.venv\Scripts\python.exe -m uvicorn api:app --host localhost --port 8000
