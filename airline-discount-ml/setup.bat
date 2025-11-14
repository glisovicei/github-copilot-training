@echo off
REM Automated setup script for airline-discount-ml training project (Windows)
REM This script ensures consistent environment setup for all team members

echo 🚀 Setting up airline-discount-ml training environment...
echo.

REM Check Python version
echo 1️⃣  Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo 2️⃣  Creating virtual environment...
    python -m venv venv
) else (
    echo.
    echo 2️⃣  Virtual environment already exists ✓
)

REM Activate virtual environment
echo.
echo 3️⃣  Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo 4️⃣  Upgrading pip...
pip install --upgrade pip

REM Install the package in editable mode with dev dependencies
echo.
echo 5️⃣  Installing package and dependencies...
pip install -e ".[dev]"

REM Register Jupyter kernel
echo.
echo 6️⃣  Registering Jupyter kernel...
python -m ipykernel install --user --name=airline-discount-ml --display-name="Python (airline-discount-ml)"

REM Initialize database
echo.
echo 7️⃣  Setting up local database...
if exist "data\schema.sql" (
    python -c "from src.data.database import init_database; init_database(); print('Database initialized successfully ✓')"
) else (
    echo ⚠️  schema.sql not found, skipping database setup
)

echo.
echo ✅ Setup complete!
echo.
echo To activate the environment, run:
echo   venv\Scripts\activate
echo.
echo To start Jupyter Lab, run:
echo   jupyter lab
echo.
echo To run tests, run:
echo   pytest tests/
echo.
pause
