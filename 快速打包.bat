@echo off
chcp 65001 >nul
title 小灰熊歌词转换器 - 快速打包
color 0A

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║     小灰熊歌词转换器 - 一键打包工具                  ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

echo [步骤 1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python！
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)
python --version
echo ✅ Python环境正常
echo.

echo [步骤 2/3] 安装/更新依赖...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ 依赖安装失败！
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
echo.

echo [步骤 3/3] 开始打包...
echo 这可能需要几分钟，请耐心等待...
echo.

pyinstaller --name="小灰熊歌词转换器" --windowed --onefile --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --clean --noconfirm lyric_converter.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败！
    echo.
    echo 可能的原因：
    echo 1. PyInstaller未正确安装
    echo 2. 缺少必要的依赖
    echo 3. 文件路径包含特殊字符
    echo.
    pause
    exit /b 1
)

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║                  ✅ 打包成功！                       ║
echo ╚═══════════════════════════════════════════════════════╝
echo.
echo 📁 可执行文件位置：
echo    dist\小灰熊歌词转换器.exe
echo.
echo 💡 使用说明：
echo    • 可以将exe文件复制到任意Windows电脑使用
echo    • 无需安装Python或任何依赖
echo    • 双击即可运行
echo.
echo 是否打开输出文件夹？(Y/N)
set /p choice=
if /i "%choice%"=="Y" (
    start explorer dist
)
echo.
pause

