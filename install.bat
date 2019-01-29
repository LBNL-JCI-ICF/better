@ECHO off
:: Check for Python Installation
python --version 2>NUL
IF %ERRORLEVEL% NEQ 0 goto errorNoPython
python setup.py install
IF %ERRORLEVEL% NEQ 0 goto errorNoSetup

goto END

:errorNoPython
echo.
echo Error^: Python not found. Please, install Python or add it to your system PATH and try again.
goto END

:errorNoSetup
echo.
echo Error^: Installation not successful, try to run "python setup.py install"

:END
pause