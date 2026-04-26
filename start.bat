@echo off
chcp 65001 >nul
echo ========================================
echo   RAG 知识库问答系统 - 一键启动
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查依赖
echo [1/3] 检查依赖...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt
)

REM 检查 .env
if not exist .env (
    echo [警告] 未找到 .env 文件！
    echo 请复制 .env.example 为 .env 并填入 API Key
    copy .env.example .env
    echo 已创建 .env，请编辑后重新运行
    pause
    exit /b 1
)

echo [2/3] 启动 Streamlit...
echo [3/3] 浏览器将自动打开 http://localhost:8501
echo.
streamlit run app.py --server.port 8501
pause
