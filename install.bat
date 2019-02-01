@ECHO off
:: Check for Python Installation
pip --version 2>NUL
IF %ERRORLEVEL% NEQ 0 goto errorNoPython
pip install .
IF %ERRORLEVEL% NEQ 0 goto errorNoSetup

goto END

:errorNoPython
echo.
echo Error^: pip not found. Please, install Python and/or pip or add them to your system PATH and try again.
goto END

:errorNoSetup
echo.
echo Error^: Installation not successful, try to run "pip install ."

:END
pause