@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting RAG Knowledge Base Demo...
echo.
streamlit run app.py
pause
