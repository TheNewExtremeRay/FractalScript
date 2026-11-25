@echo off
REM ez command — opens FractalScript terminal or runs a command
REM When double-clicked or run with no args, opens a persistent terminal window
REM When run from an existing terminal with args, runs the command directly

if "%~1"=="" (
    REM No args: open a new terminal window with the FractalScript REPL
    start "FractalScript Terminal" cmd /k "title FractalScript Terminal && cd /d "%~dp0" && python ez_cli.py"
) else (
    REM Has args: run the command in the current terminal
    cd /d "%~dp0"
    python ez_cli.py %*
)
