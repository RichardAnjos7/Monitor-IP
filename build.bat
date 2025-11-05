@echo off
echo ========================================
echo Criando Executavel do Monitor de IPs
echo ========================================
echo.

REM Verifica se PyInstaller esta instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Instalando PyInstaller...
    python -m pip install pyinstaller
    echo.
)

REM Gera o icone se nao existir
if not exist icon.ico (
    echo Gerando icone...
    python -c "import PIL" 2>nul
    if errorlevel 1 (
        echo Instalando Pillow para gerar icone...
        python -m pip install pillow
    )
    python create_icon.py
    echo.
)

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist MonitorIP.spec del /q MonitorIP.spec
echo.

echo Criando executavel...
echo.

REM Cria o executavel com PyInstaller usando python -m para garantir que funcione
if exist icon.ico (
    set ICON_OPTION=--icon=icon.ico
) else (
    set ICON_OPTION=--icon=NONE
)

python -m PyInstaller --onefile ^
    --windowed ^
    --name "MonitorIP" ^
    %ICON_OPTION% ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=ping_monitor ^
    --hidden-import=ip_catalog ^
    main.py

echo.
echo ========================================
if exist dist\MonitorIP.exe (
    echo Executavel criado com sucesso!
    echo.
    echo Arquivo: dist\MonitorIP.exe
    echo Tamanho: 
    dir dist\MonitorIP.exe | find "MonitorIP.exe"
) else (
    echo Erro ao criar executavel!
    echo Verifique as mensagens acima.
)
echo ========================================
echo.
pause

