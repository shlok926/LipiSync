@echo off
REM Build script for Braille Converter .exe
REM This script creates a standalone Windows executable

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
echo 🎨 Building Braille Converter .exe...
echo   (This may take 1-2 minutes)
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
echo    dist\BrailleConverter.exe
echo.
echo 🎯 Next steps:
echo    1. Test: Run dist\BrailleConverter.exe
echo    2. Create installer: (Optional - use InnoSetup or WiX)
echo    3. Deploy: Share the .exe with users
echo.
echo 📊 Build statistics:
dir dist\BrailleConverter.exe | find "BrailleConverter.exe"
echo.
pause
