@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM 设置控制台代码页为UTF-8，请确保控制台字体支持中文（如Lucida Console）

:run_crawler
set PYTHONIOENCODING=utf-8
python gov_news_crawler.py
if not exist gov_news.json (
    echo 错误：未找到gov_news.json文件，请检查爬虫脚本是否运行成功。
    pause
    exit /b 1
)

:check_json
choice /c 12 /m "gov_news.json是否合格？1.继续 2.重新生成"
if errorlevel 2 goto run_crawler

:generate_broadcast
set PYTHONIOENCODING=utf-8
python news_broadcast_generator.py
if errorlevel 1 (
    echo 新闻稿生成失败
    pause
    exit /b 1
)

:review_broadcast
choice /c 12 /m "新闻稿是否合格？1.合格退出 2.重新生成"
if errorlevel 2 goto generate_broadcast

endlocal