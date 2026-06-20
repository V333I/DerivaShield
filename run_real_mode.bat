@echo off
cd /d "%~dp0"
echo ========================================================
echo Iniciando DerivaShield en Modo de Captura REAL
echo ========================================================
echo.
echo ATENCION: Para que esto funcione, DEBES:
echo 1. Ejecutar este archivo como Administrador (Clic derecho -^> Ejecutar como administrador).
echo 2. Tener instalado Npcap o Wireshark en este computador.
echo.

:: Verificar permisos de Administrador intentando leer una carpeta de sistema
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Permisos de Administrador detectados correctamente.
) else (
    echo [ERROR] No tienes permisos de Administrador. La captura real probablemente fallara.
    echo Cierra esta ventana, haz clic derecho en "run_real_mode.bat" y selecciona "Ejecutar como administrador".
    pause
    exit /b
)

if not exist ".venv" (
    echo [INFO] Creando entorno virtual de Python...
    python -m venv .venv
)

echo [INFO] Verificando dependencias...
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo [INFO] Ejecutando DerivaShield...
.\.venv\Scripts\python.exe app.py --mode real

pause
