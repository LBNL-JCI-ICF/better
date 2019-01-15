@echo off
rem  python.exe is in the path?
python.exe --version >NUL 2>&1
if errorlevel 1 goto error
python setup.py install
if errorlevel 1 goto error
goto end

:ERROR
echo.
echo Please, install Python or add it to your system PATH and try again.
echo If the installation is not successful, try to run "python setup.py install"

:END
pause
