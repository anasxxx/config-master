@echo off
cd /d "C:\Users\amahmoudi\Downloads\config-master-main\nv-ai-agent-hps"
set CONFIGMASTER_TOKEN=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmdWxsQGdtYWlsLmNvbSIsImV4cCI6MTk4ODUwMzY0MX0.QxG8Y2S6WaciWGB4ZakwHfdyetaI9uxdM4GZD6Nt4Ok
.venv\Scripts\python.exe -m uvicorn api:app --host 0.0.0.0 --port 8000
