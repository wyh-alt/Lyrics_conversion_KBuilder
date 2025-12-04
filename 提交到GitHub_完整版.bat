@echo off
chcp 65001 >nul
title 提交代码到GitHub
color 0B

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║     小灰熊歌词转换器 - 提交到GitHub                   ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [步骤 1/6] 检查Git安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Git！
    echo 请先安装Git: https://git-scm.com/
    pause
    exit /b 1
)
git --version
echo ✅ Git已安装
echo.

echo [步骤 2/6] 检查Git用户配置...
git config user.name >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未配置Git用户信息
    echo.
    set /p git_name="请输入您的姓名: "
    set /p git_email="请输入您的邮箱: "
    git config --global user.name "%git_name%"
    git config --global user.email "%git_email%"
    echo ✅ 用户信息已配置
) else (
    echo ✅ 用户信息已配置
    echo    姓名: %git config user.name%
    echo    邮箱: %git config user.email%
)
echo.

echo [步骤 3/6] 初始化/检查Git仓库...
if not exist .git (
    echo 初始化Git仓库...
    git init
    echo ✅ 仓库已初始化
) else (
    echo ✅ 仓库已存在
)
echo.

echo [步骤 4/6] 添加文件到暂存区...
git add .
echo ✅ 文件已添加
echo.

echo [步骤 5/6] 提交更改...
git commit -m "初始提交：小灰熊歌词格式转换器

功能特点：
- PyQt6图形界面，简洁易用
- 支持拖拽文件/文件夹批量转换
- 自动识别多种歌词格式（时间戳位置灵活）
- 支持中英日韩多语言
- 智能编码处理（GBK/UTF-8自动降级）
- 可打包为EXE独立运行
- 完整的文档和说明"

if errorlevel 1 (
    echo ⚠️  提交失败或没有更改需要提交
) else (
    echo ✅ 提交成功
)
echo.

echo [步骤 6/6] 配置远程仓库并推送...
git remote remove origin 2>nul
git remote add origin https://github.com/wyh-alt/Lyrics_conversion_KBuilder.git
echo ✅ 远程仓库已配置

git branch -M main
echo.
echo 正在推送到GitHub...
echo 如果提示输入用户名和密码：
echo   - 用户名：您的GitHub用户名
echo   - 密码：使用Personal Access Token（不是账户密码）
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo ⚠️  推送失败！
    echo.
    echo 可能的原因和解决方案：
    echo.
    echo 1. 认证失败
    echo    解决方案：使用Personal Access Token
    echo    - 访问: https://github.com/settings/tokens
    echo    - 生成新token（勾选repo权限）
    echo    - 推送时密码输入token
    echo.
    echo 2. 权限不足
    echo    解决方案：确认仓库权限
    echo    - 确认您是仓库所有者或有推送权限
    echo    - 确认仓库地址正确
    echo.
    echo 3. 网络问题
    echo    解决方案：检查网络连接
    echo    - 确认能访问GitHub
    echo    - 尝试使用代理
    echo.
    echo 手动推送命令：
    echo   git push -u origin main
    echo.
) else (
    echo.
    echo ╔═══════════════════════════════════════════════════════╗
    echo ║                  ✅ 推送成功！                        ║
    echo ╚═══════════════════════════════════════════════════════╝
    echo.
    echo 📦 仓库地址：
    echo    https://github.com/wyh-alt/Lyrics_conversion_KBuilder
    echo.
    echo 💡 您可以在浏览器中查看您的代码了！
    echo.
)

pause

