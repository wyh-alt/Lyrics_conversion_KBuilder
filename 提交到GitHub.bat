@echo off
chcp 65001 >nul
echo ========================================
echo 提交代码到GitHub
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] 检查Git状态...
git status >nul 2>&1
if errorlevel 1 (
    echo 初始化Git仓库...
    git init
)

echo.
echo [2/5] 添加所有文件...
git add .

echo.
echo [3/5] 提交更改...
git commit -m "初始提交：小灰熊歌词格式转换器

功能特点：
- PyQt6图形界面
- 支持拖拽文件/文件夹
- 批量转换歌词文件
- 自动识别多种格式
- 支持中英日韩多语言
- 智能编码处理（GBK/UTF-8）
- 可打包为EXE独立运行"

echo.
echo [4/5] 添加远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/wyh-alt/Lyrics_conversion_KBuilder.git

echo.
echo [5/5] 推送到GitHub...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ⚠️ 推送失败！
    echo.
    echo 可能的原因：
    echo 1. 未配置Git用户信息
    echo 2. 未配置GitHub认证
    echo 3. 网络连接问题
    echo.
    echo 请手动执行以下命令：
    echo   git config --global user.name "Your Name"
    echo   git config --global user.email "your.email@example.com"
    echo   git push -u origin main
    echo.
) else (
    echo.
    echo ✅ 推送成功！
    echo.
    echo 仓库地址：
    echo https://github.com/wyh-alt/Lyrics_conversion_KBuilder.git
    echo.
)

pause

