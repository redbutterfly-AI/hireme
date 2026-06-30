path = r"C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\start_backend.ps1"

script = r"""# HireMe Backend Starter - Daphne (ASGI) for WebSocket support
Set-Location "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend"

# Activate virtual environment
& "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend\venv\Scripts\Activate.ps1"

$env:DJANGO_SETTINGS_MODULE = "HireMeBackend.settings"

Write-Host "Virtual environment activated" -ForegroundColor Green
Write-Host "Starting Daphne ASGI server (supports WebSockets) on 0.0.0.0:8000 ..." -ForegroundColor Green

daphne -b 0.0.0.0 -p 8000 HireMeBackend.asgi:application
"""

with open(path, "w", encoding="utf-8") as f:
    f.write(script)

print("Done! start_backend.ps1 now uses Daphne instead of runserver")
print("This is REQUIRED for WebSocket (real-time chat) to work")
