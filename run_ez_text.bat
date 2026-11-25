@echo off
start "FractalScript" cmd /k "title FractalScript && python "%~dp0translator.py" "%~1" && pause"
