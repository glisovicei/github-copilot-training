# Airline Discount ML - Training Repository

> **Purpose:** This repository is designed as a training exercise for learning GitHub Copilot agents, MCP tools, and ML workflows. It demonstrates airline discount prediction without real customer data.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎯 Learning Objectives

This project helps teams learn:
- ✅ GitHub Copilot best practices for ML projects
- ✅ Building custom MCP (Model Context Protocol) servers
- ✅ Working with database schemas without real data
- ✅ ML model training and evaluation workflows
- ✅ Agent-based discount prediction systems

## 📁 Project Structure

```
airline-discount-ml/
├── src/
│   ├── agents/          # Discount agents and route analyzers
│   ├── models/          # ML models for prediction and profiling
│   ├── data/            # Database handlers and preprocessors
│   ├── mcp/             # Custom MCP server implementation
│   ├── training/        # Training and evaluation scripts
│   └── utils/           # Configuration and utilities
├── data/
│   ├── schema.sql       # Database schema (no real data)
│   └── sample_data.sql  # Synthetic training data
├── notebooks/           # Jupyter notebooks for exploration
├── tests/               # Unit tests
├── setup.py             # Package configuration
├── setup.sh             # Automated setup script (Mac/Linux)
├── setup.bat            # Automated setup script (Windows)
├── Makefile             # Convenient command shortcuts
└── requirements.txt     # Backup dependency list
```

## 🚀 Quick Setup (Recommended for Training)

### Option 1: Automated Setup (Easiest) ⭐

**macOS/Linux:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

This will:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Register Jupyter kernel
- ✅ Initialize the database
- ✅ Verify the installation

### Option 2: Using Make (macOS/Linux)

```bash
make setup      # Complete setup
make help       # See all available commands
```

### Option 3: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install package with dev dependencies
pip install -e ".[dev]"

# 4. Register Jupyter kernel
python -m ipykernel install --user --name=airline-discount-ml \
    --display-name="Python (airline-discount-ml)"

# 5. Initialize database
python -c "from src.data.database import init_database; init_database()"
```

## 🎓 Training Workflow

### Day 1: Environment Setup & GitHub Copilot Basics
1. Run the setup script
2. Open the project in VS Code
3. Practice using GitHub Copilot for code completion
4. Explore the project structure with Copilot Chat

### Day 2: Working with Data & Agents
1. Open `notebooks/exploratory_analysis.ipynb`
2. Use Copilot to understand the data schema
3. Learn agent patterns in `src/agents/`
4. Practice writing tests with Copilot

### Day 3: Building MCP Tools
1. Explore `src/mcp/` directory
2. Learn to create custom MCP tools
3. Test MCP server integration
4. Add context to Copilot with MCP

### Day 4: Model Training & Evaluation
1. Review `src/training/` scripts
2. Train models with Copilot assistance
3. Run evaluation metrics
4. Document findings

## 💻 Common Commands

```bash
# Activate environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Start Jupyter Lab
jupyter lab
# or
make run-notebook

# Run tests
pytest tests/
# or
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint

# Train model
python src/training/train.py
# or
make train

# Evaluate model
python src/training/evaluate.py
# or
make evaluate
```

## 🐛 Troubleshooting

### Jupyter kernel not showing packages
```bash
# Re-register the kernel
python -m ipykernel install --user --name=airline-discount-ml \
    --display-name="Python (airline-discount-ml)"

# In VS Code: Select kernel "Python (airline-discount-ml)"
```

### Import errors in notebook
```bash
# Install packages in the notebook kernel
# In notebook cell:
!pip install matplotlib seaborn
```

### Database connection issues
```bash
# Reinitialize database
make db-init
# or
python -c "from src.data.database import init_database; init_database()"
```

## 📚 Resources for Training

- **GitHub Copilot Docs:** https://docs.github.com/copilot
- **MCP Protocol:** https://modelcontextprotocol.io
- **Scikit-learn:** https://scikit-learn.org/stable/
- **SQLAlchemy:** https://docs.sqlalchemy.org/

## 🎯 Training Exercises

1. **Exercise 1:** Use Copilot to add a new route analysis feature
2. **Exercise 2:** Build a custom MCP tool for discount calculations
3. **Exercise 3:** Improve model accuracy using feature engineering
4. **Exercise 4:** Add comprehensive tests with Copilot assistance
5. **Exercise 5:** Create visualization dashboards for predictions

## 📝 Best Practices Learned

- ✅ Use setup scripts for consistent environments
- ✅ Install packages with `setup.py` instead of just `requirements.txt`
- ✅ Register Jupyter kernels for notebook work
- ✅ Use Makefiles for common commands
- ✅ Keep synthetic data separate from real data
- ✅ Document setup thoroughly for team onboarding

## 🤝 Contributing

This is a training repository. Feel free to:
- Add new exercises
- Improve documentation
- Suggest better patterns
- Create additional examples

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note:** This repository contains only synthetic data for training purposes. No real passenger or airline data is included.