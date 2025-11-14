#!/bin/bash
# Automated setup script for airline-discount-ml training project
# This script ensures consistent environment setup for all team members

set -e  # Exit on error

echo "🚀 Setting up airline-discount-ml training environment..."
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "2️⃣  Creating virtual environment..."
    python3 -m venv venv
else
    echo ""
    echo "2️⃣  Virtual environment already exists ✓"
fi

# Activate virtual environment
echo ""
echo "3️⃣  Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "4️⃣  Upgrading pip..."
pip install --upgrade pip

# Install the package in editable mode with dev dependencies
echo ""
echo "5️⃣  Installing package and dependencies..."
pip install -e ".[dev]"

# Register Jupyter kernel
echo ""
echo "6️⃣  Registering Jupyter kernel..."
python -m ipykernel install --user --name=airline-discount-ml --display-name="Python (airline-discount-ml)"

# Initialize database
echo ""
echo "7️⃣  Setting up local database..."
if [ -f "data/schema.sql" ]; then
    python -c "
from src.data.database import init_database
init_database()
print('Database initialized successfully ✓')
"
else
    echo "⚠️  schema.sql not found, skipping database setup"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start Jupyter Lab, run:"
echo "  jupyter lab"
echo ""
echo "To run tests, run:"
echo "  pytest tests/"
echo ""
