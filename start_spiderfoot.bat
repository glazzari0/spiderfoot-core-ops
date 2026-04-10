@echo off
TITLE SpiderFoot Server - OSINT Lab
SET BASE_DIR=%~dp0
SET BASE_DIR=%BASE_DIR:~0,-1%
SET VENV_DIR=%BASE_DIR%\venv

cd /d "%BASE_DIR%"

:: Verifica se a pasta venv existe, caso contrário, avisa o usuário
IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual nao encontrado em %VENV_DIR%
    echo Por favor, crie o venv antes de rodar este script.
    pause
    exit /b
)

echo [INFO] Ativando ambiente virtual...
call "%VENV_DIR%\Scripts\activate.bat"

echo [INFO] Iniciando SpiderFoot em http://127.0.0.1:5001
echo Pressione Ctrl+C para encerrar o servico.

:: Inicia o SpiderFoot
python ./sf.py -l 127.0.0.1:5001

pause
