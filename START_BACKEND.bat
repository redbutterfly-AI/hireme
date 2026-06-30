@echo off
cd "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend"
set DJANGO_SETTINGS_MODULE=HireMeBackend.settings
echo Starting Daphne ASGI server (supports WebSockets) on 0.0.0.0:8000 ...
"C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend\venv\Scripts\daphne.exe" -b 0.0.0.0 -p 8000 HireMeBackend.asgi:application
pause
