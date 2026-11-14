@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===== THANH VIEN 2 - ALPHA BETA =====
where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON=py"
) else (
    set "PYTHON=python"
)
echo Cai dat thu vien...
%PYTHON% -m pip install -r requirements.txt
if errorlevel 1 goto :error
echo.
echo Chay bo test...
%PYTHON% -m unittest discover -s tests -v
if errorlevel 1 goto :error
echo.
echo Chay demo depth=2...
%PYTHON% demo.py --depth 2
if errorlevel 1 goto :error
echo.
echo Chay benchmark (depth 1,2) de kiem tra nhanh...
%PYTHON% benchmark.py --depths 1 2
if errorlevel 1 goto :error
echo.
echo HOAN TAT. Mo thu muc outputs de xem CSV va bieu do.
pause
exit /b 0
:error
echo CO LOI. Xem dong thong bao o tren va gui anh Terminal neu can.
pause
exit /b 1
