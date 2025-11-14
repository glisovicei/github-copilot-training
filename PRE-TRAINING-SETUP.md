# Pre-Training Setup Guide - GitHub Copilot & MCP Training

**Estimated setup time:** 60-90 minutes  
**Please complete this setup at least 48 hours before the training session.**

This guide ensures your development environment is ready for a smooth training experience. We'll cover everything from hardware recommendations to software installation and verification steps.

---

## 📋 Table of Contents

1. [Hardware Requirements](#-hardware-requirements)
2. [GitHub Copilot License & Setup](#-github-copilot-license--setup)
3. [Software Prerequisites by Operating System](#-software-prerequisites-by-operating-system)
4. [Verification Checklist](#-verification-checklist)
5. [Troubleshooting](#-troubleshooting)
6. [Day-Of Training Checklist](#-day-of-training-checklist)

---

## 💻 Hardware Requirements

### Minimum Requirements
- **RAM:** 8 GB (16 GB strongly recommended)
- **Storage:** 10 GB free disk space
- **Processor:** Dual-core CPU (2 GHz or higher)
- **Internet:** Stable broadband connection (required throughout training)

### Display Recommendations

**Strongly Recommended:**
- **Dual monitors** (or one large monitor 27"+ / 4K)
- **Resolution:** 1920x1080 minimum per screen

**Why?** You'll need to:
- Keep training instructions visible on one screen
- Work in VS Code on another screen
- View documentation, terminal outputs, and browser simultaneously

**Not Recommended:**
- Single small laptop screens (13" or smaller)
- Working solely on a tablet (this is impossible!!!)
- Limited screen real estate makes it difficult to follow along efficiently

**Alternative if you only have one screen:**
- Use virtual desktops/workspaces to quickly switch between windows but not recommended! 
- Consider connecting an external monitor to your laptop

---

## 🔑 GitHub Copilot License & Setup

### Step 1: Verify Your GitHub Copilot Subscription

You need an **active GitHub Copilot Pro or Pro+ subscription** for this training.

**⚠️ Important:** The free trial will NOT work for this training because you need:
- **Agent mode** (multi-step autonomous tasks)
- **Advanced models** (GPT-5, Claude 4 Sonnet, Claude 4.5 Sonnet)
- **MCP (Model Context Protocol)** support

**Required subscription levels:**
- ✅ **GitHub Copilot Pro+** (best - includes all features)
- ✅ **GitHub Copilot Pro** (minimum - sufficient for training)
- ❌ **Free Trial** (insufficient - lacks agent mode and advanced models)
- ✅ **Business/Enterprise** (contact your admin to verify you have agent access)

**Check your access:**
1. Go to https://github.com/settings/copilot
2. Verify you see "GitHub Copilot is enabled"
3. Confirm your subscription shows **"Pro"** or **"Pro+"** (not "Free Trial")

e.g  GitHub Copilot Pro+ is active for your account

**Don't have access?**
- **Individual:** Upgrade to Pro at https://github.com/settings/copilot
- **Business/Enterprise:** Contact your organization's GitHub admin and request agent mode access
- **Students/Teachers:** Check if GitHub Education includes Pro https://education.github.com/

### Step 2: Verify Copilot Models

Ensure you have access to the following models:

| Model | Purpose | Access Level |
|-------|---------|--------------|
| **Claude 3.5 Sonnet** | Alternative for comparisons | Pro/Pro+ |
| **Claude Sonnet 4** | Advanced model | Pro+ |
| **Claude Sonnet 4.5** | Latest advanced model | Pro+ |
| **GPT-5** | Advanced reasoning | Pro+ |
| **GPT-5-Codex** | Specialized for code generation | Pro+ |

**To check available models:**
1. Open GitHub Copilot Chat in VS Code
  - macOS shortcut: press Cmd+Shift+P, type "Copilot: Open Chat" and press Enter or Cmd+Shift+I
  - Windows shortcut: press Ctrl+Shift+P, type "Copilot: Open Chat" and press Enter
2. Click the model selector dropdown (top-right of chat panel)
3. Verify you can see the advanced models (Claude Sonnet 4/4.5, GPT-5, GPT-5-Codex)

**If advanced models are missing:**
- You likely have **Pro** instead of **Pro+** - this will work but with limited access to newest models, this is not a problem for the training! 
- Business/Enterprise users: Your organization may have restricted models - contact your admin to request Pro+ access
- Individual users with Pro+: All models should be available by default

**Enable models on GitHub:** If you don't see the advanced models in VS Code, go to your GitHub Copilot settings and explicitly enable model access:

1. Visit: https://github.com/settings/copilot/features
2. Enable the advanced models or agent features (toggle on GPT-5 / Sonnet models)
3. Restart VS Code and re-open Copilot Chat

If you still don't see models after enabling, sign out and sign back into Copilot in VS Code, or contact your GitHub admin.

---

## 🛠️ Software Prerequisites by Operating System

### All Operating Systems

#### 1. **Git** (Version 2.30+)

**Check if installed:**
```bash
git --version
```

**Install:**
- **macOS:** Included with Xcode Command Line Tools (see below)
- **Linux:** `sudo apt-get install git` (Ubuntu/Debian) or `sudo yum install git` (CentOS/RHEL)
- **Windows:** https://git-scm.com/download/win

**Configure Git (required):**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### 2. **VS Code** (Latest Stable Version)

**Download:** https://code.visualstudio.com/download

**Required VS Code Extensions:**

Install these extensions by clicking the links or searching in VS Code Extensions panel (`Cmd+Shift+X` / `Ctrl+Shift+X`):

1. **GitHub Copilot** (`GitHub.copilot`)
   - https://marketplace.visualstudio.com/items?itemName=GitHub.copilot

  You do not need to switch to pre-release version though if some features will not be available during the training that might be a solution. However, for now install the latest version.  
   
2. **GitHub Copilot Chat** (`GitHub.copilot-chat`)
   - https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat

3. **Python** (`ms-python.python`)
   - https://marketplace.visualstudio.com/items?itemName=ms-python.python

**Recommended Extensions:**
4. **Jupyter** (`ms-toolsai.jupyter`) - for notebook exercises
5. **Docker** (`ms-azuretools.vscode-docker`) - if doing Docker homework, it will not be needed for the training itself, so it is not a must! 

**Verify extensions are installed:**
1. Open VS Code
2. Open the Extensions view:
  - macOS: press `Cmd+Shift+X`
  - Windows/Linux: press `Ctrl+Shift+X`
3. In the search box, verify each of the following shows "Installed":
  - "GitHub Copilot"
  - "GitHub Copilot Chat"
  - "Python" (by Microsoft)
4. If any are missing, click "Install" and then "Reload" if prompted
5. If prompted, "Sign in to GitHub" to activate Copilot 
6. Before the training make sure that you are signed in and you can clone the repositories, otherwise it will take too much time during training! 

---

### macOS Setup

#### 1. **Xcode Command Line Tools**

Required for compiling Python packages and Git.

**Install:**
```bash
xcode-select --install
```

Click "Install" when prompted. This takes 5-10 minutes.

**Verify:**
```bash
xcode-select -p
# Should output: /Library/Developer/CommandLineTools
```

#### 2. **Homebrew** (Package Manager)

**Install Homebrew:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the post-install instructions to add Homebrew to your PATH.

**Verify:**
```bash
brew --version
```
If brew is not found, make sure you are in zsh and not bash terminal in VS Code



#### 3. **Python 3.11** (Python 3.9-3.11 recommended)

**Install via Homebrew:**
```bash
brew install python@3.11
```

**Verify:**
```bash
python3 --version
# Should show Python 3.8 or higher
```

**Add to PATH (if needed):**
```bash
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### 4. **Synth CLI** (Data Generation Tool)

**IMPORTANT:** This tool is required for the exercises. Make sure it runs successfully on your machine before training.

**Install:**
```bash
# Create directory for synth
mkdir -p ~/.synth/bin

# Download Synth v0.6.9 from shuttle-hq repository
curl -L https://github.com/shuttle-hq/synth/releases/download/v0.6.9/synth-macos-latest-x86_64.tar.gz -o /tmp/synth.tar.gz

# Extract to synth directory
tar -xzf /tmp/synth.tar.gz -C ~/.synth/bin/

# Make executable
chmod +x ~/.synth/bin/synth

# Add to PATH
echo 'export PATH="$HOME/.synth/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Verify (must succeed):**
```bash
synth version
```

Expected output: `synth 0.6.9`


---

### Windows Setup

#### 1. **Windows Terminal** (Recommended)

**Install from Microsoft Store:**
https://aka.ms/terminal

Provides a better terminal experience than Command Prompt.

#### 2. **Python 3.8+**

**Download:** https://www.python.org/downloads/

**During installation:**
- ✅ **Check "Add Python to PATH"** (critical!)
- ✅ Choose "Customize installation"
- ✅ Enable "pip"
- ✅ Install for all users (if you have admin rights)

**Verify (in Command Prompt or PowerShell):**
```cmd
python --version
pip --version
```

**Troubleshooting:** If "python" is not recognized:
1. Search for "Environment Variables" in Windows
2. Edit PATH variable
3. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\` (adjust version)
4. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\Scripts\`
5. Restart terminal

#### 3. **Git for Windows**

** WSL 2 (Windows Subsystem for Linux)**

1. **Enable WSL 2:**
```powershell
wsl --install
```

2. **Install Ubuntu from Microsoft Store**

3. **Inside WSL Ubuntu:**

**Then follow the MacOS instructions above for remaining setup.**

#### 4. **Synth CLI** (Optional - Native Windows)

**Note:** Not tested on Windows, but there is a native Windows binary available. 

**Download:**
```
https://github.com/shuttle-hq/synth/releases/download/v0.6.9/synth-windows-latest-x86_64.exe
```

1. Download the `.exe` file
2. Rename it to `synth.exe`
3. Place it in a directory (e.g., `C:\Program Files\Synth\`)
4. Add that directory to your system PATH
5. Verify: Open a new terminal and run `synth version`

---

### Additional Tools (All Platforms)

#### **jq** (JSON Processor - for testing)

**macOS:**
```bash
brew install jq
```

**Linux:**
```bash
sudo apt-get install -y jq
```

**Windows:**
```powershell
# Via chocolatey (if installed)
choco install jq

# Or download from: https://stedolan.github.io/jq/download/
```

**Verify:**
```bash
echo '{"test": "value"}' | jq .
```

---

## ✅ Verification Checklist

Complete this checklist **before the training day** and save the output.

### 1. Git Configuration
```bash
git --version
git config --global user.name
git config --global user.email
```

Expected: Version 2.30+, your name and email displayed

### 2. Python Environment
```bash
python3 --version  # or python --version on Windows
pip --version      # or pip3 --version
```

Expected: Python 3.8+ and pip installed

### 3. VS Code Extensions
```bash
code --list-extensions | grep "copilot"
```

Expected output:
```
github.copilot
github.copilot-chat
```

### 4. GitHub Copilot Authentication

1. Open VS Code
2. Open Copilot Chat (`Cmd/Ctrl + I`)
3. Type: "Hello, what models are available?"
4. Verify you get a response and see model selector with GPT-4o

### 5. Synth CLI (macOS/Linux)
```bash
synth version
```

Expected: Version 0.6.0 or higher


### 6. Create Your Training Repository From Template

This repository is a **GitHub template**. You should create your own copy from it:

1. **Create from template:**
   - Go to: https://github.com/ktoetotam/airlst-github-copilot-training
   - Click the green **"Use this template"** button (top right)
   - Select **"Create a new repository"**
   - Name your repository (e.g., `my-copilot-training`, `copilot-ml-workshop`, or any name you prefer)
   - Choose **Public** or **Private** (your preference)
   - Click **"Create repository"**

2. **Clone your new repository:**
   ```bash
   cd ~/Projects  # or your preferred location
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME/airline-discount-ml
   ```

   Example:
   ```bash
   git clone https://github.com/yourusername/my-copilot-training.git
   cd my-copilot-training/airline-discount-ml
   ```

### 7. Run Setup Script

**macOS/Linux:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

**Expected output:**
```
✅ Setup complete!
```

### 8. Verify Installation
```bash
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

python -c "import pandas, sklearn, fastapi; print('All packages installed ✓')"
pytest airline-discount-ml/tests -v
```

Expected: Tests pass (some may be skipped)


---

## 🐛 Troubleshooting

### Python Issues

**Problem:** "python: command not found"
- **macOS/Linux:** Try `python3` instead of `python`
- **Windows:** Reinstall Python with "Add to PATH" checked

**Problem:** "Permission denied" when installing packages
- **macOS/Linux:** Never use `sudo pip` - always use virtual environments
- **Windows:** Run terminal as Administrator

**Problem:** Virtual environment activation fails
- **Windows:** Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell

### Git Issues

**Problem:** "Permission denied (publickey)" when cloning
- Generate SSH key: `ssh-keygen -t ed25519`
- Add to GitHub: https://github.com/settings/keys

**Problem:** Git credentials not working
- Use Personal Access Token instead of password: https://github.com/settings/tokens

### VS Code / Copilot Issues

**Problem:** Copilot not responding
- Sign out and sign in: Click profile icon → Sign out → Sign in
- Check internet connection
- Verify subscription at https://github.com/settings/copilot

**Problem:** Copilot suggestions not appearing
- Check Copilot status icon (bottom-right)
- Verify file type is supported (Python, Markdown, etc.)
- Restart VS Code

### Synth Issues

**Problem:** Synth not found after installation
- Add to PATH (see OS-specific instructions above)
- Restart terminal
- Verify installation directory: `ls ~/.synth/bin` (macOS/Linux)

**Problem:** Windows can't run Synth natively
- Use Docker method (recommended)
- Or install WSL 2 and follow Linux instructions


---

## 📅 Day-Of Training Checklist

**Morning of the training (before session starts):**

- [ ] **Charge your laptop** (or ensure power cable is available)
- [ ] **Test internet connection** (stable WiFi or Ethernet)
- [ ] **Update VS Code** and extensions to latest versions
- [ ] **Pull latest training repository:**
  ```bash
  cd ~/Documents/airlst-github-copilot-training
  git pull origin main
  ```
- [ ] **Activate virtual environment:**
  ```bash
  cd airline-discount-ml
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate     # Windows
  ```
- [ ] **Test Copilot is working:** Open VS Code, create new Python file, type `def hello` and verify suggestions appear
- [ ] **Close unnecessary applications** to free up RAM
- [ ] **Set up dual monitors** (if available)
- [ ] **Have GitHub Copilot Chat open** and ready
- [ ] **Mute notifications** to avoid distractions

**Keep these open and accessible:**
- VS Code with the training repository
- Web browser with:
  - Training materials (will be provided)
  - GitHub documentation
  - Synth documentation (https://www.getsynth.com/docs)
- Terminal window
- Notes app (for questions/observations)

---

## 🆘 Getting Help

**Before the training:**
- Review this document completely
- Complete all verification steps
- Test your setup thoroughly
- Contact the training coordinator if issues persist

**During the training:**
- Use the designated Slack/Teams channel
- Ask questions as they arise
- Trainers will provide additional support

---

## 📚 Additional Resources

- **GitHub Copilot Documentation:** https://docs.github.com/en/copilot
- **VS Code Documentation:** https://code.visualstudio.com/docs
- **Python Virtual Environments:** https://docs.python.org/3/tutorial/venv.html
- **Synth CLI Documentation:** https://www.getsynth.com/docs
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Docker Documentation:** https://docs.docker.com/

---

**Questions or issues with setup?** Contact the training coordinator at least 24 hours before the session.

**Ready to go?** See you at the training! 🚀
