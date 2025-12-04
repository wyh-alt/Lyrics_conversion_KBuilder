@echo off
chcp 65001 >nul
echo ========================================
echo 小灰熊歌词转换器 - 高级打包脚本
echo ========================================
echo.
echo 此脚本会创建更优化的打包配置
echo.

echo [1/4] 检查依赖...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖安装失败！
    pause
    exit /b 1
)
echo.

echo [2/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo.

echo [3/4] 创建spec文件...
python -c "import PyInstaller.utils.hooks; print('PyInstaller hooks available')"
echo.

echo [4/4] 开始打包（优化配置）...
pyinstaller --name="小灰熊歌词转换器" ^
    --windowed ^
    --onefile ^
    --icon=NONE ^
    --add-data="README.md;." ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.Qt6 ^
    --collect-all=PyQt6 ^
    --noupx ^
    --clean ^
    --noconfirm ^
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
echo 文件大小可能较大（包含所有依赖）
echo.
echo 优化建议：
echo - 首次运行可能稍慢（解压临时文件）
echo - 可以添加到杀毒软件白名单
echo.
pause

