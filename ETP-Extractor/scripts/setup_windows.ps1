$ErrorActionPreference = "Stop"

Write-Host "Creando entorno virtual..."
py -3.11 -m venv .venv

Write-Host "Activando entorno..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Instalando dependencias..."
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Instalación completada."
Write-Host "Ejecutá: python -m etp_extractor.cli status"
