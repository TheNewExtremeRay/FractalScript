@echo off
start "FractalScript" cmd /k "title FractalScript && python "%~dp0runner.py" "%~1" && pause"
