# Exercise 03: Build a Custom MCP Server with Synth

## 🎯 What You'll Learn

In this exercise, you'll:
1. Confirm setup prerequisites (Synth, generated data, and SQLite loaded)
2. Build a **custom MCP server** that wraps Synth commands
3. Add MCP tools for generation and inspection
4. Run and test the server locally
5. Connect the server to VS Code and use it with GitHub Copilot

**Why this matters:** Custom MCP servers let you add ANY tool to Copilot - not just pre-built ones. This is how you extend Copilot with your organization's internal tools.

---
## ✅ Prerequisites

Complete the setup steps first:

- Setup guide: `exercises/03-custom-mcp-server/setup-instructions.md`

You should have:
- Synth installed (or Docker-based Synth on Windows)
- Generated data at `airline-discount-ml/data/synthetic_output/generated_data.json`
- Data loaded into SQLite at `airline-discount-ml/data/airline_discount.db`

If not, finish Parts 1–5 in the setup guide and return here.

---

## Part 6: Build a Custom MCP Server

### What is an MCP Server?

An MCP (Model Context Protocol) server is a bridge between GitHub Copilot and external tools. Think of it as a plugin for Copilot that adds new capabilities. In this exercise, we’ll build an MCP server that wraps Synth CLI commands so Copilot can generate data on demand.

### Step 11: Understand the MCP Architecture

```
GitHub Copilot ←→ MCP Server ←→ Synth CLI ←→ JSON files
```

The MCP server sits in the middle and:
1. Receives requests from Copilot (e.g., "generate 500 passengers")
2. Translates them into Synth commands
3. Runs the commands
4. Returns results to Copilot

### Step 12: Review the Starter MCP Server

Your repository includes a minimal MCP server at `src/mcp_synth/server.py`. Take a look:

```bash
cd airline-discount-ml
cat src/mcp_synth/server.py
```

This server currently has 2 basic endpoints:
- `GET /healthz` — Health check (returns `{ "status": "ok" }`)
- `GET /version` — Returns server version

Next you'll add endpoints that wrap Synth commands.


### Step 13: Install MCP Server Dependencies

The MCP server uses **FastAPI** (a Python web framework) and **Uvicorn** (a web server). These are already in your `setup.py`, so just install:

```bash
cd airline-discount-ml
venv/bin/pip install -e ".[dev]"
```

This installs FastAPI and Uvicorn along with your package.

### Step 14: Run the MCP Server

Start the server:

```bash
venv/bin/uvicorn src.mcp_synth.server:app --host 127.0.0.1 --port 8010 --reload

```

**What this does:**
- `uvicorn` - The web server
- `mcp_synth.server:app` - Your FastAPI app
- `--host 127.0.0.1 --port 8010` - Run on localhost:8010
- `--reload` - Auto-restart when you edit code

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8010 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Leave this running in your terminal!

### Step 15: Test the MCP Server

Open a **new terminal** and test the endpoints:

```bash
# Health check
curl -s http://127.0.0.1:8010/healthz | jq .

# Version check
curl -s http://127.0.0.1:8010/version | jq .
```

You should see:
```json
{"status": "ok"}
{"version": "0.1.0"}
```

**Success!** Your MCP server is running. 🎉

---

## Part 7: Add Synth Tools to MCP Server

### Step 16: Understanding MCP Tools

An **MCP tool** is a function that Copilot can call. Each tool has:
- A **name** (e.g., `synth_generate`)
- **Input parameters** (e.g., size, seed)
- **Output** (e.g., success/failure, file paths)

We'll add 9 tools to our MCP server:

| Tool | What It Does |
|------|-------------|
| `synth_import_schema` | Import DB schema into Synth |
| `synth_inspect_model` | View Synth schema details |
| `synth_generate` | Generate synthetic data |
| `preview_table_head` | Show first N rows |
| `validate_fk` | Check foreign key integrity |
| `synth_stats` | Get data statistics |
| `synth_dry_run` | Preview generation without creating files |
| `policy_check` | Enforce organizational limits |
| `export_archive` | Zip output files |

### Step 17: Add the `synth_generate` Tool

Let's add the most important tool - data generation. Open `src/mcp_synth/server.py` and add:

```python
from pydantic import BaseModel, Field
from fastapi import HTTPException
import subprocess
import json

class GenerateRequest(BaseModel):
    """Request to generate synthetic data."""
    model_dir: str = Field(default="synth_models/airline_data", description="Path to Synth schemas")
    out_dir: str = Field(default="data/synthetic_output", description="Output directory")
    size: int = Field(default=1000, ge=1, le=10000, description="Records per collection")
    seed: int = Field(default=42, description="Random seed for reproducibility")

class GenerateResponse(BaseModel):
    """Response from data generation."""
    success: bool
    message: str
    files_created: list[str]

@app.post("/synth_generate", response_model=GenerateResponse)
def synth_generate(req: GenerateRequest):
    """Generate synthetic data using Synth CLI."""
    try:
        # Build Synth command
        cmd = [
            "synth", "generate",
            req.model_dir,
            "--size", str(req.size),
            "--seed", str(req.seed)
        ]
        
        # Run command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Save output to file
        import os
        os.makedirs(req.out_dir, exist_ok=True)
        out_file = os.path.join(req.out_dir, "generated_data.json")
        with open(out_file, 'w') as f:
            f.write(result.stdout)
        
        return GenerateResponse(
            success=True,
            message=f"Generated {req.size} records per collection",
            files_created=[out_file]
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Synth command failed: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**What this does:**
1. Defines input/output models with Pydantic
2. Creates a POST endpoint at `/synth_generate`
3. Runs the `synth generate` command as a subprocess
4. Returns success/failure with created files

### Step 18: Test the New Tool

The server auto-reloads when you save the file. Test it:

```bash
curl -X POST http://127.0.0.1:8010/synth_generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_dir": "synth_models/airline_data",
    "out_dir": "data/synthetic_output",
    "size": 100,
    "seed": 42
  }' | jq .
```

You should see:
```json
{
  "success": true,
  "message": "Generated 100 records per collection",
  "files_created": ["passengers.json", "routes.json", "discounts.json"]
}
```

Check the files were created:
```bash
ls -lh data/synthetic_output/
```

**Excellent!** Your MCP server can now generate data. 🚀

---

## Part 8: Connect MCP Server to VS Code

### Step 19: Configure VS Code MCP Settings

Create or update `.vscode/mcp.json` at your **repository root**:

```json
{
  "servers": {
    "synth-local": {
      "type": "http",
      "url": "http://127.0.0.1:8010"
    }
  }
}
```

**What this does:**
- Registers your local MCP server with VS Code
- Whitelists specific tools Copilot can use
- Points to `http://127.0.0.1:8010` (your running server)

### Step 20: Reload VS Code

Reload the window to pick up the new MCP server:
- **macOS:** `Cmd+Shift+P` → "Developer: Reload Window"
- **Windows:** `Ctrl+Shift+P` → "Developer: Reload Window"

### Step 21: Verify Copilot Sees Your Tools

Open Copilot Chat, click "Select tools", and you should see:
- **MCP Server: synth-local**
  - synth_generate
  - (other tools you added)

### Step 22: Use Your MCP Server with Copilot!

Try this prompt in Copilot Chat:

```
#synth-local Generate 500 passengers with seed 99
```

Copilot should:
1. Call your `synth_generate` tool
2. Pass the parameters
3. Show you the results

**You just built a custom MCP server!** 🎊

---

## 🐛 Troubleshooting

### Problem: "synth: command not found"
**Solution:** Synth isn't installed or not in your PATH. Re-run the install command and restart your terminal.

### Problem: "FileNotFoundError: data/synthetic_output/passengers.json"
**Solution:** You haven't generated data yet. Follow the data generation steps in the Setup guide (Parts 1–2), then retry.

### Problem: "✗ Data directory not found"
**Solution:** Make sure you're in the `airline-discount-ml` directory when running commands.

### Problem: "FOREIGN KEY constraint failed" when loading data
**Solution:** The discount records reference non-existent passenger or route IDs. This shouldn't happen with the provided schemas, but if it does:
```bash
# Regenerate with a different seed
synth generate synth_models/airline_data --size 1000 --seed 42 > data/synthetic_output/generated_data.json
```

### Problem: Database shows 0 records after loading
**Solution:** Check for errors in the loader output. Run with verbose error handling:
```bash
python -c "
try:
    from src.data.load_synthetic_data import load_all
    load_all()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
"
```

### Problem: MCP server won't start - "ModuleNotFoundError: No module named 'mcp_synth'"
**Solution:** Install the package in editable mode:
```bash
cd airline-discount-ml
.venv/bin/pip install -e ".[dev]"
```

### Problem: MCP server starts but Copilot can't see it
**Solution:** 
1. Check `.vscode/mcp.json` is at the repository root (not inside airline-discount-ml)
2. Verify the server is running on port 8010: `curl http://127.0.0.1:8010/healthz`
3. Reload VS Code window

### Problem: "Address already in use" when starting server
**Solution:** Port 8010 is taken. Either:
- Find and kill the existing process: `lsof -ti:8010 | xargs kill`
- Use a different port: `uvicorn mcp_synth.server:app --port 8011`

---

## 📝 Windows Installation (Docker Method)

### For Windows Users

Synth doesn't have a native Windows installer. Use Docker:

#### Step 1: Install Docker Desktop
Download from: https://www.docker.com/products/docker-desktop

#### Step 2: Pull Synth Docker Image
```powershell
docker pull getsynth/synth
```

#### Step 3: Run Synth via Docker
```powershell
cd airline-discount-ml

# Generate data (Windows PowerShell)
docker run --rm `
  -v ${PWD}/synth_models:/synth_models `
  -v ${PWD}/data:/data `
  getsynth/synth generate /synth_models/airline_data `
  --to json:///data/synthetic_output/ `
  --size 1000 `
  --seed 42
```

#### Step 4: Load Data (Same as Mac/Linux)
```powershell
python -c "from src.data.load_synthetic_data import load_all; load_all()"
```

### Alternative: WSL (Windows Subsystem for Linux)

If you have WSL installed:

```bash
# Inside Ubuntu (WSL terminal)
curl -sSL https://getsynth.com/install | sh
synth --version
```

Then follow the Mac/Linux instructions above.

---

## ✅ Exercise Complete!

You've learned to:
- ✅ Install and use Synth CLI
- ✅ Generate synthetic data from schemas
- ✅ Load JSON data into SQLite
- ✅ Build a custom MCP server with FastAPI
- ✅ Add tools to your MCP server
- ✅ Connect your MCP server to VS Code
- ✅ Use your custom tools with GitHub Copilot

**Next steps:**
- Add more MCP tools (inspect_model, preview_table_head, etc.)
- Add validation and safety checks
- Create custom Synth schemas for your domain
- Share your MCP server with your team

---

## 📦 Homework: Deploy Your MCP Server with Docker

Ready to share your MCP server with the whole team? Check out the comprehensive deployment guide:

**[homework-docker-deployment.md](./homework-docker-deployment.md)**

Learn how to:
- 🐳 Dockerize your MCP server
- 🔐 Add API key security
- 📤 Push to Docker Hub or GitHub Packages
- 📝 Document for team use
- ☁️ Deploy to cloud platforms (Google Cloud Run, AWS Fargate, Heroku)

This homework builds on what you've learned and takes it to production-ready team deployment!

**Congratulations on building your first custom MCP server!** 🎉
