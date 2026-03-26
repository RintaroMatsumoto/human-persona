@echo off
REM Run mypy strict type checking on core/ modules (Windows)

setlocal enabledelayedexpansion

echo Running mypy strict type checking on core/ modules...
echo =====================================================

python -m mypy core/ ^
    --strict ^
    --show-error-codes ^
    --show-error-context ^
    --no-implicit-reexport

if errorlevel 1 (
    echo.
    echo Type checking failed!
    exit /b 1
)

echo.
echo Type checking complete!
exit /b 0
