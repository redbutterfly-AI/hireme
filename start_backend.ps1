# HireMe Backend Starter - Daphne (ASGI) for WebSocket support
Set-Location "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend"

$env:DJANGO_SETTINGS_MODULE = "HireMeBackend.settings"

Write-Host "Starting Daphne ASGI server (supports WebSockets) on 0.0.0.0:8000 ..." -ForegroundColor Green

# Use absolute path to venv daphne to ensure it always works
& "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend\venv\Scripts\daphne.exe" -b 0.0.0.0 -p 8000 HireMeBackend.asgi:application
