@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 企业级电商知识库问答助手（本地 Streamlit）
echo 浏览器默认 http://localhost:8501  首次使用请在侧栏「重新构建索引」
echo.
streamlit run app.py
pause
