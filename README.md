# A training repository for learning GitHub Copilot best practices through hands-on ML and MCP server exercises.

> IMPORTANT: Before the training, you must complete the pre-training setup.
>
> See PRE-TRAINING-SETUP.md and finish all steps at least 48 hours in advance.

## 📚 What's Inside

This repository contains:
- **Training exercises** for GitHub Copilot workflows and Model Context Protocol (MCP) servers
- **Minimal ML pipeline** for airline discount prediction using synthetic data
- **Complete setup automation** with cross-platform support (Mac/Linux/Windows)

## 🎯 Learning Path

### Exercise 01: Setup Copilot Instructions
Learn to configure repo-wide and path-scoped Copilot instructions for consistent, high-quality code generation.

📁 `exercises/01-setup/`

### Exercise 02: MCP Server for GitHub
Explore GitHub's MCP server for repository management, issue tracking, and code search through Copilot.

📁 `exercises/02-mcp-server-for-github/`

### Exercise 03: Build a Custom MCP Server
Create your own MCP server that wraps the Synth CLI for synthetic data generation, then connect it to VS Code.

📁 `exercises/03-custom-mcp-server/`
- **Setup guide**: Install Synth, generate data, load into SQLite
- **Main exercise**: Build FastAPI MCP server, add tools, connect to Copilot
- **Homework**: Deploy with Docker, add security, share with team

### Exercise 04: Unit Tests with pytest
Master test-driven development with GitHub Copilot by writing comprehensive unit tests.

📁 `exercises/04-unit-tests/`

## 🚀 Quick Start

### For the ML Pipeline

```bash
cd airline-discount-ml
./setup.sh  # Mac/Linux
# OR
setup.bat   # Windows

# Verify setup
make test
```

See `airline-discount-ml/README.md` for detailed instructions.

### For Exercises

Each exercise folder contains:
- Detailed step-by-step instructions
- Code samples and templates
- Troubleshooting guides
- Expected outcomes

Start with Exercise 01 to configure your Copilot environment.

## 📁 Repository Structure

```
airlst-github-copilot-training/
├── README.md                    # This file
├── exercises/                   # Training exercises
│   ├── 01-setup/               # Copilot instructions setup
│   ├── 02-mcp-server-for-github/  # GitHub MCP server
│   ├── 03-custom-mcp-server/   # Build custom MCP server
│   └── 04-unit-tests/          # pytest unit testing with copilot
└── airline-discount-ml/        # ML project
    ├── src/                    # Source code
    ├── tests/                  # Test suite
    ├── data/                   # SQLite database and schemas
    ├── notebooks/              # Jupyter notebooks
    ├── setup.sh / setup.bat    # Automated setup
    └── README.md               # Detailed project docs
```

## 🎓 Who Is This For?

- Developers learning GitHub Copilot best practices
- Teams adopting AI-assisted development workflows
- Anyone interested in building custom MCP servers
- Data scientists exploring synthetic data generation

## 📝 Prerequisites

- VS Code with GitHub Copilot extensions
- Python 3.8+
- Git
- (Optional) Docker for custom MCP deployment

## 🔗 Key Technologies

- **GitHub Copilot** - AI pair programming
- **Model Context Protocol (MCP)** - Extend Copilot with custom tools
- **Synth CLI** - Generate realistic synthetic data
- **FastAPI** - Build web APIs for MCP servers
- **SQLite** - Lightweight database for training
- **pytest** - Python testing framework
- **scikit-learn** - Machine learning models

## 🤝 Contributing

This is a training repository. Feel free to fork and adapt for your own training needs.

## 📄 License

Training materials for educational purposes.

---

**Ready to start?** Head to `exercises/01-setup/` and follow the instructions to configure your Copilot environment.
