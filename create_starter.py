import os

script_content = r"""# HireMe Backend Starter - auto installs deps and starts server
Set-Location "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend"

# Activate venv
& "C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\HireMeBackend\venv\Scripts\Activate.ps1"

# Install/verify all requirements
Write-Host "Checking dependencies..." -ForegroundColor Cyan
pip install -q djangorestframework djangorestframework-simplejwt channels channels-redis daphne Pillow django-cors-headers psycopg2-binary

$env:DJANGO_SETTINGS_MODULE = "HireMeBackend.settings"

Write-Host "Starting Django server on 0.0.0.0:8000..." -ForegroundColor Green
python manage.py runserver 0.0.0.0:8000
"""

path = r"C:\Users\YOHHANNESS MAULIDI\StudioProjects\hireme\start_backend.ps1"
with open(path, "w", encoding="utf-8") as f:
    f.write(script_content)

print("Done! start_backend.ps1 updated.")
