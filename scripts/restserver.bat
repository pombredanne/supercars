@ECHO OFF

REM ##
REM # start python restserver in a batch process (kill the process to kill the restserver)
REM #
REM # USAGE:
REM #   ./scripts/manage_restserver.bat
REM #
REM # VIEW:
REM #   http://localhost:8000

set BASE_DIR=%cd%
set PYTHON=%PYTHON_HOME%\python
REM set PYTHON=%BASE_DIR%\..\tutorial_ci\runtime\python\python


if "%1" == "start" (
    start %PYTHON% %BASE_DIR%\backend\restserver.py %BASE_DIR%\app > NUL
) else (
    if "%1" == "stop" (
        TASKKILL /F /IM python.exe
    ) else (
        echo 'needs start or stop'
    )
)
