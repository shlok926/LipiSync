@echo off
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          BRAILLE CONVERTER - BUILD SCRIPT                 ║
echo ║         Creating Windows .exe Installer                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10+
    exit /b 1
)

echo ✅ Python found
echo.

REM Install PyInstaller if needed
echo 📦 Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo   Installing PyInstaller...
    pip install PyInstaller --quiet
    echo   ✅ PyInstaller installed
) else (
    echo   ✅ PyInstaller already installed
)

echo.
echo 🔧 Choose Build Mode:
echo ═════════════════════════════
echo [1] Directory Mode (RECOMMENDED - Opens Instantly ^< 2 sec)
echo     Creates a 'dist/BrailleConverter' folder containing the app.
echo     Faster startup, no antivirus delay, best for daily use.
echo.
echo [2] Single File Mode (Slower Startup, but portable)
echo     Creates a single 'dist/BrailleConverter.exe' file.
echo     Takes 20-30 seconds to open on first start because it extracts 470MB of libraries.
echo     (UPX compression is disabled to make it as fast as possible).
echo.
set /p choice="Enter choice (1 or 2, default is 1): "

if "%choice%"=="2" (
    set BUILD_MODE=onefile
    echo.
    echo 🎨 Building in Single File Mode (onefile)...
) else (
    set BUILD_MODE=onedir
    echo.
    echo 🎨 Building in Directory Mode (onedir)...
)
echo.

REM Build using spec file
pyinstaller braille_converter.spec --clean

if errorlevel 1 (
    echo.
    echo ❌ Build failed! Check the errors above.
    exit /b 1
)

echo.
echo ✨ Build completed successfully!
echo.
echo 📍 Output location:
if "%BUILD_MODE%"=="onefile" (
    echo    dist\BrailleConverter.exe
) else (
    echo    dist\BrailleConverter\ (Run BrailleConverter.exe inside this folder)
)
echo.
pause

