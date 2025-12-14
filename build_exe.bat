@echo off
echo ========================================
echo Generando ejecutable de WebM to MP4
echo ========================================
echo.

REM Instalar PyInstaller si no está instalado
echo Instalando PyInstaller...
pip install PyInstaller
echo.

REM Limpiar builds anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist webm_to_mp4.spec del webm_to_mp4.spec

echo Creando ejecutable...
python -m PyInstaller --onefile --windowed --name="WebmToMP4Converter" --icon=NONE webm_to_mp4.py

echo.
echo ========================================
echo Proceso completado
echo El ejecutable está en: dist\WebmToMP4Converter.exe
echo ========================================
pause
