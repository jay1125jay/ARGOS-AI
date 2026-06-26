@echo off
cd /d C:\ARGOS_AI
start cmd /k python app_server.py
start http://localhost:8000