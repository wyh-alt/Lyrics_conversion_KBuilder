@echo off
chcp 65001 >nul
echo ========================================
echo 小灰熊歌词转换器 - 打包脚本
echo ========================================
echo.

echo [1/3] 检查依赖...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖安装失败！
    pause
    exit /b 1
)
echo.

echo [2/3] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo.

echo [3/3] 开始打包...
pyinstaller --name="小灰熊歌词转换器" ^
    --windowed ^
    --onefile ^
    --icon=NONE ^
    --add-data="README.md;." ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --clean ^
    lyric_converter.py

if errorlevel 1 (
    echo.
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\小灰熊歌词转换器.exe
echo.
echo 您可以将此exe文件复制到任意Windows电脑使用
echo 无需安装Python或任何依赖！
echo.
pause

