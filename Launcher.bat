@echo off
start "FractalScript" cmd /k "title FractalScript && python "%~dp0selector.py" "%~1" && pause"
