@echo off
setlocal
cd /d "%~dp0"

rem Start the local AAP/n8n demo and open the product in the default browser.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-demo.ps1" -Restart
if errorlevel 1 (
    echo.
    echo The demo could not be started. Review the message above.
    pause
    exit /b 1
)

endlocal
