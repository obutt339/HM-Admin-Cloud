@echo off
title HM Testpoint & Hardware Tool - 1-Click VIP Auto-Updater
color 0A
cls
echo ======================================================================
echo    HM TESTPOINT & HARDWARE TOOL v8.6 - 1-CLICK CLIENT VIP UPDATER
echo    Official Server: obutt339/HM-Admin-Cloud (Live CDN)
echo ======================================================================
echo.
echo [*] Checking Client Installation Directory...

set "TARGET_DIR=%LOCALAPPDATA%\HM_Testpoint_Tool_v8.5\runtime"

if not exist "%TARGET_DIR%" (
    if exist "C:\HM_Toolkits\runtime" (
        set "TARGET_DIR=C:\HM_Toolkits\runtime"
    ) else (
        echo [!] Default directory not found. Creating %TARGET_DIR%...
        mkdir "%TARGET_DIR%" 2>nul
    )
)

echo [*] Target Directory: %TARGET_DIR%
echo.

:: Ensure Assets folder exists
if not exist "%TARGET_DIR%\assets" (
    mkdir "%TARGET_DIR%\assets" 2>nul
)

echo [*] Downloading SUGON 3010PM Photo...
powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/assets/sugon_3010pm.jpg', '%TARGET_DIR%\assets\sugon_3010pm.jpg')"

echo [*] Downloading UNI-T UT33B+ Multimeter Photo...
powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/assets/unit_ut33b.jpg', '%TARGET_DIR%\assets\unit_ut33b.jpg')"

echo [*] Downloading Official Facebook Logos...
powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $wc = New-Object Net.WebClient; $wc.DownloadFile('https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/assets/fb_logo.png', '%TARGET_DIR%\assets\fb_logo.png'); $wc.DownloadFile('https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/assets/fb_icon_18.png', '%TARGET_DIR%\assets\fb_icon_18.png'); $wc.DownloadFile('https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/assets/fb_icon_22.png', '%TARGET_DIR%\assets\fb_icon_22.png')"

echo [*] Downloading latest hm_testpoint.py (Hardware Lab + Photos + UTF-8 Fix)...
powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/runtime/hm_testpoint.py', '%TARGET_DIR%\hm_testpoint.py')"

echo [*] Downloading HM_Hardware_Diagnostic_Lab.exe...
powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/runtime/HM_Hardware_Diagnostic_Lab.exe', '%TARGET_DIR%\HM_Hardware_Diagnostic_Lab.exe')"

:: Sync to C:\HM_Toolkits if present
if exist "C:\HM_Toolkits" (
    if not exist "C:\HM_Toolkits\assets" mkdir "C:\HM_Toolkits\assets" 2>nul
    copy /y "%TARGET_DIR%\assets\*" "C:\HM_Toolkits\assets\" >nul 2>&1
    copy /y "%TARGET_DIR%\HM_Hardware_Diagnostic_Lab.exe" "C:\HM_Toolkits\" >nul 2>&1
)

:: Reset notice state so client sees the VIP notification immediately on startup
del /f /q "%TARGET_DIR%\.last_notice_seen" >nul 2>&1
del /f /q "%LOCALAPPDATA%\HM_Testpoint_Tool_v8.5\.last_notice_seen" >nul 2>&1

echo.
echo ======================================================================
echo    [SUCCESS] VIP UPDATE COMPLETE!
echo    - Real Instrument Photos Added (SUGON 3010PM + UNI-T Multimeter)
echo    - Hardware Diagnostic Lab Installed & Activated
echo    - VIP Update Notification Broadcast Reset & Armed
echo    - Clean UTF-8 Encoding (All Urdu & English Text Perfect)
echo ======================================================================
echo.
echo Starting HM Testpoint Tool...
start "" "%TARGET_DIR%\pythonw.exe" "%TARGET_DIR%\hm_testpoint.py"
if %errorlevel% neq 0 (
    start "" "%TARGET_DIR%\python.exe" "%TARGET_DIR%\hm_testpoint.py"
)

timeout /t 3 >nul
exit
