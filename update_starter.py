path = r"C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\start_backend.ps1"

script = r"""# HireMe Backend Starter
Set-Location "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend"

# Activate virtual environment
& "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend\venv\Scripts\Activate.ps1"

# Set Django settings
$env:DJANGO_SETTINGS_MODULE = "HireMeBackend.settings"

Write-Host "Virtual environment activated" -ForegroundColor Green
Write-Host "Starting Django server on http://10.0.2.2:8000 ..." -ForegroundColor Green

python manage.py runserver 0.0.0.0:8000
"""

with open(path, "w", encoding="utf-8") as f:
    f.write(script)

# Also create a shortcut batch file that can be double-clicked
bat = r"""@echo off
cd "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend"
call "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend\venv\Scripts\activate.bat"
set DJANGO_SETTINGS_MODULE=HireMeBackend.settings
python manage.py runserver 0.0.0.0:8000
pause
"""

bat_path = r"C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\START_BACKEND.bat"
with open(bat_path, "w", encoding="utf-8") as f:
    f.write(bat)

print("Done!")
print("")
print("Two ways to start the backend:")
print("  1. PowerShell: & \"C:\\Users\\YOHHANNESS MAULIDI\\StudioProjects\\hireme\\start_backend.ps1\"")
print("  2. Double-click: START_BACKEND.bat in your project folder")
