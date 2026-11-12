@echo off
rem PyTest Pro - Windows'ta çift tıklayarak başlatma
chcp 65001 >nul
title PyTest Pro
cd /d "%~dp0"

rem İlk açılışta proje klasöründe ayrı bir Python ortamı (.venv) kurulur.
if exist ".venv\Scripts\python.exe" goto paketler

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY python --version >nul 2>nul && set "PY=python"
if not defined PY goto python_yok

echo İlk açılış: Python ortamı hazırlanıyor...
%PY% -m venv .venv
if errorlevel 1 goto ortam_hatasi

:paketler
echo Gerekli paketler denetleniyor...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto paket_hatasi

set "PORT=%PYTEST_PORT%"
if not defined PORT set "PORT=5000"
rem Sunucu açılınca öğretmen paneli tarayıcıda açılır.
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://localhost:%PORT%/ogretmen'"

".venv\Scripts\python.exe" server.py
echo.
echo Sunucu durdu.
pause
exit /b 0

:python_yok
echo Python bulunamadı.
echo https://www.python.org/downloads/ adresinden indirip kurun.
echo Kurulumda "Add python.exe to PATH" kutusunu işaretleyin, sonra bu dosyayı yeniden açın.
pause
exit /b 1

:ortam_hatasi
echo Python ortamı oluşturulamadı. Klasöre yazma izni olduğundan emin olun.
pause
exit /b 1

:paket_hatasi
echo Paketler kurulamadı. İlk açılışta internet bağlantısı gerekir; bağlantıyı denetleyip yeniden deneyin.
pause
exit /b 1
