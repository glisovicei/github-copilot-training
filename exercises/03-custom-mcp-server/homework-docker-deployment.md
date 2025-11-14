# Homework: Deploy Your MCP Server with Docker

## 🎯 What You'll Build

You'll take your local MCP server and make it available to your whole team using Docker. Think of Docker as a "shipping container" for your application - it packages everything needed to run your server so anyone can use it without complex setup.

**Time needed:** 2-3 hours  
**Difficulty:** Intermediate

---

## Why Docker?

**The Problem:** Your MCP server works on your laptop, but:
- Teammates need to install Python, Synth, dependencies
- "Works on my machine" doesn't help the team
- Manual setup is error-prone and time-consuming

**The Solution:** Docker creates a self-contained package that:
- Includes everything (Python, Synth, your code, dependencies)
- Runs the same way on everyone's computer
- Takes 5 minutes to set up (not 1 hour)

---

## Part 1: Package Your Server in Docker

### What is a Docker Image?

A **Docker image** is like a recipe that describes:
- What operating system to use (Ubuntu, Alpine, etc.)
- What software to install (Python, Synth)
- What files to include (your code)
- How to run the application

### Task 1: Create the Recipe (Dockerfile)

Create a new file called `Dockerfile.mcp` in the `airline-discount-ml` folder:

```dockerfile
# Start with a pre-made Python environment
FROM python:3.11-slim

# Install system tools we need (curl for downloading Synth)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Download and install Synth
RUN curl -sSL https://getsynth.com/install | sh

# Set up our app folder inside the container
WORKDIR /app

# Copy our code into the container
COPY src/mcp_synth/ /app/mcp_synth/
COPY synth_models/ /app/synth_models/
COPY requirements.txt setup.py README.md /app/

# Install Python packages our app needs
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Create a folder for generated data
RUN mkdir -p /app/data/synthetic_output

# Tell Docker our app uses port 8010
EXPOSE 8010

# Add a health check (Docker will test if the app is running)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8010/healthz || exit 1

# When the container starts, run our server
CMD ["uvicorn", "mcp_synth.server:app", "--host", "0.0.0.0", "--port", "8010"]
```

**What each line does:**
- `FROM python:3.11-slim` → Use a lightweight Python 3.11 base
- `RUN apt-get...` → Install system packages
- `WORKDIR /app` → All commands run in the /app folder
- `COPY` → Put our code into the container
- `RUN pip install...` → Install Python dependencies
- `EXPOSE 8010` → Document that we use port 8010
- `HEALTHCHECK` → Docker checks if the server is healthy every 30 seconds
- `CMD` → The command to run when container starts

### Task 2: Build the Docker Image

Think of this as "following the recipe to create the package":

```bash
cd airline-discount-ml

# Build the image and give it a name
docker build -f Dockerfile.mcp -t airline-mcp-synth:v1.0 .
```

**What this command does:**
- `docker build` → Follow the recipe (Dockerfile)
- `-f Dockerfile.mcp` → Use this specific file
- `-t airline-mcp-synth:v1.0` → Tag (name) the result
- `.` → Use current directory as context (where to find files)

**Expected output:** You'll see Docker download packages, copy files, and build layers. Takes 1-2 minutes.

### Task 3: Test the Container Locally

Now let's "unpack the shipping container" and run it:

```bash
# Start the container in the background
docker run -d --name airline-mcp-test -p 8010:8010 airline-mcp-synth:v1.0
```

**What this command does:**
- `docker run` → Start a container from an image
- `-d` → Run in background (detached mode)
- `--name airline-mcp-test` → Give the container a friendly name
- `-p 8010:8010` → Map container port 8010 to your computer's port 8010
- `airline-mcp-synth:v1.0` → Use this image

**Check it's running:**

```bash
# List running containers
docker ps

# You should see something like:
# CONTAINER ID   IMAGE                      STATUS         PORTS
# abc123def456   airline-mcp-synth:v1.0     Up 10 seconds  0.0.0.0:8010->8010/tcp
```

**Test the endpoints:**

```bash
# Health check (should return {"status": "ok"})
curl -s http://localhost:8010/healthz | jq .

# Version check
curl -s http://localhost:8010/version | jq .

# Generate test data
curl -X POST http://localhost:8010/synth_generate \
  -H "Content-Type: application/json" \
  -d '{"size": 50, "seed": 42}' | jq .
```

**Clean up when done:**

```bash
# Stop the container
docker stop airline-mcp-test

# Remove the container
docker rm airline-mcp-test
```

✅ **Success Checkpoint:** If all three curl commands returned valid JSON, your Docker image works!

---

## Part 2: Add Security with API Keys

### Why Add Security?

Right now, anyone who can reach your server can generate unlimited data. That's fine for testing, but not for team use. We'll add an API key that only your team knows.

### Task 4: Update Server Code with Authentication

Open `src/mcp_synth/server.py` and add this code at the top:

```python
import os
from fastapi import HTTPException, Security, Header
from typing import Optional

# Read API key from environment variable (or use default for testing)
API_KEY = os.getenv("MCP_API_KEY", "dev-key-change-in-production")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Check if the provided API key matches our secret key."""
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key. Add X-API-Key header."
        )
    return x_api_key
```

**What this does:**
- Reads the secret key from an environment variable
- Creates a function that checks if the request has the correct key
- Returns an error (403) if the key is wrong or missing

Now update the `synth_generate` endpoint to require the key:

```python
@app.post("/synth_generate", response_model=GenerateResponse)
def synth_generate(
    req: GenerateRequest,
    api_key: str = Security(verify_api_key)  # Add this line
):
    # ... rest of your code stays the same
```

### Task 5: Test with API Key

Rebuild the image with security:

```bash
docker build -f Dockerfile.mcp -t airline-mcp-synth:v1.1 .
```

Run with a custom API key:

```bash
# Set your secret key as an environment variable
docker run -d \
  --name airline-mcp-secure \
  -p 8010:8010 \
  -e MCP_API_KEY="my-secret-team-key-12345" \
  airline-mcp-synth:v1.1
```

**What `-e MCP_API_KEY="..."` does:** Passes an environment variable into the container (like setting a password).

**Test with the correct key:**

```bash
curl -X POST http://localhost:8010/synth_generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-secret-team-key-12345" \
  -d '{"size": 50}' | jq .
```

**Test without the key (should fail):**

```bash
curl -X POST http://localhost:8010/synth_generate \
  -H "Content-Type: application/json" \
  -d '{"size": 50}' | jq .

# Expected: {"detail": "Invalid or missing API key. Add X-API-Key header."}
```

✅ **Success Checkpoint:** Requests with the key work, requests without the key fail.

```bash
# Clean up
docker stop airline-mcp-secure
docker rm airline-mcp-secure
```

---

## Part 3: Share with Your Team

### What is a Container Registry?

Think of it like GitHub, but for Docker images. Instead of sharing code, you share packaged applications. Your teammates can "download" (pull) your image and run it instantly.

**Two popular options:**
1. **Docker Hub** - Public, free for public images
2. **GitHub Packages** - Private, integrated with GitHub

### Task 6: Push to Docker Hub (Public Option)

**Step 1: Create a Docker Hub account**
- Go to [hub.docker.com](https://hub.docker.com)
- Sign up (free)

**Step 2: Login from terminal**

```bash
docker login
# Enter your Docker Hub username and password
```

**Step 3: Tag your image with your username**

```bash
# Replace YOUR_USERNAME with your Docker Hub username
docker tag airline-mcp-synth:v1.1 YOUR_USERNAME/airline-mcp-synth:v1.1
docker tag airline-mcp-synth:v1.1 YOUR_USERNAME/airline-mcp-synth:latest
```

**What this does:** Renames the image to include your username (like a namespace).

**Step 4: Push to Docker Hub**

```bash
docker push YOUR_USERNAME/airline-mcp-synth:v1.1
docker push YOUR_USERNAME/airline-mcp-synth:latest
```

This uploads your image to Docker Hub. Takes 1-2 minutes depending on internet speed.

**Step 5: Share with teammates**

Your team can now run:

```bash
docker pull YOUR_USERNAME/airline-mcp-synth:latest
docker run -d -p 8010:8010 -e MCP_API_KEY="team-key" YOUR_USERNAME/airline-mcp-synth:latest
```

✅ **Success Checkpoint:** You can see your image at `hub.docker.com/r/YOUR_USERNAME/airline-mcp-synth`

### Alternative: GitHub Packages (Private Option)

If you want to keep your image private (only visible to your organization):

**Step 1: Create a Personal Access Token**
- Go to [github.com/settings/tokens](https://github.com/settings/tokens)
- Click "Generate new token (classic)"
- Select scopes: `write:packages`, `read:packages`, `delete:packages`
- Copy the token (save it somewhere safe!)

**Step 2: Login to GitHub Container Registry**

```bash
echo YOUR_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

**Step 3: Tag and push**

```bash
# Tag with GitHub Container Registry format
docker tag airline-mcp-synth:v1.1 ghcr.io/YOUR_USERNAME/airline-mcp-synth:v1.1
docker tag airline-mcp-synth:v1.1 ghcr.io/YOUR_USERNAME/airline-mcp-synth:latest

# Push to GitHub Packages
docker push ghcr.io/YOUR_USERNAME/airline-mcp-synth:v1.1
docker push ghcr.io/YOUR_USERNAME/airline-mcp-synth:latest
```

**Step 4: Make it accessible to your team**
- Go to the package page on GitHub
- Settings → Change visibility (if needed)
- Add collaborators

---

## Part 4: Write Team Documentation

Your teammates need instructions! Create a simple guide they can follow.

### Task 7: Create Team Setup Guide

Create `docs/team-mcp-setup.md` in your repository:

````markdown
# MCP Server Setup - 5 Minute Guide

## What You Need
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- VS Code with GitHub Copilot
- API key (ask the team lead)

## Step 1: Start the Server

```bash
# Pull the image
docker pull YOUR_USERNAME/airline-mcp-synth:latest

# Run it (replace the API key)
docker run -d \
  --name airline-mcp \
  -p 8010:8010 \
  -e MCP_API_KEY="ask-team-lead-for-this" \
  YOUR_USERNAME/airline-mcp-synth:latest

# Check it's running
docker ps
```

## Step 2: Configure VS Code

Create `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "synth-team": {
      "type": "http",
      "url": "http://localhost:8010",
      "headers": {
        "X-API-Key": "${env:MCP_API_KEY}"
      },
      "toolAllowList": [
        "synth_generate",
        "preview_table_head"
      ]
    }
  }
}
```

## Step 3: Set the API Key

**Mac/Linux:**
```bash
echo 'export MCP_API_KEY="ask-team-lead-for-this"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (PowerShell):**
```powershell
[Environment]::SetEnvironmentVariable("MCP_API_KEY", "ask-team-lead-for-this", "User")
```

## Step 4: Restart VS Code

- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
- Type "Reload Window"
- Press Enter

## Step 5: Test It!

In Copilot Chat, try:
```
#synth-team Generate 100 passengers with seed 42
```

## Troubleshooting

**"Connection refused"**
→ Container isn't running. Run: `docker start airline-mcp`

**"403 Forbidden"**
→ Wrong API key. Check: `echo $MCP_API_KEY` (should show the key)

**"Port already in use"**
→ Use a different port: `-p 8011:8010` and update VS Code config to `http://localhost:8011`

## Need Help?
Ask in #ml-tools Slack channel!
````

### Task 8: Share the Setup

1. Commit the documentation:
```bash
git add docs/team-mcp-setup.md
git commit -m "Add team setup guide for MCP server"
git push
```

2. Announce in your team chat:
```
🚀 MCP Server is ready!

Docker image: YOUR_USERNAME/airline-mcp-synth:latest
Setup guide: docs/team-mcp-setup.md
Setup time: 5 minutes

DM me for the API key!
```

---

## Part 5: Deploy to Cloud (Optional Advanced)

If you want the server always running (not just on your laptop), deploy it to the cloud.

### Option 1: Heroku (Easiest - $7/month)

**What is Heroku?** A platform that runs your app for you. No server management needed.

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku  # Mac
# OR download from https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create an app
heroku create airline-mcp-synth

# Set the API key
heroku config:set MCP_API_KEY="production-key-123" -a airline-mcp-synth

# Deploy your container
heroku container:push web -a airline-mcp-synth
heroku container:release web -a airline-mcp-synth

# Get the URL
heroku info -a airline-mcp-synth
```

Your server is now at: `https://airline-mcp-synth.herokuapp.com`

Update your team's `.vscode/mcp.json`:
```json
{
  "servers": {
    "synth-cloud": {
      "type": "http",
      "url": "https://airline-mcp-synth.herokuapp.com",
      "headers": {
        "X-API-Key": "${env:MCP_API_KEY}"
      }
    }
  }
}
```

### Option 2: Google Cloud Run (Free tier available)

**What is Cloud Run?** Google's serverless container platform. Only pay when requests come in.

```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy
gcloud run deploy airline-mcp-synth \
  --image YOUR_USERNAME/airline-mcp-synth:latest \
  --platform managed \
  --region us-central1 \
  --port 8010 \
  --set-env-vars MCP_API_KEY="production-key-123" \
  --allow-unauthenticated

# Get the URL
gcloud run services describe airline-mcp-synth --region us-central1 --format 'value(status.url)'
```

**Cost:** Free for first 2 million requests/month, then ~$0.40 per million.

---

## 📋 Homework Checklist

Complete these tasks and submit:

### Required Tasks
- [ ] Created Dockerfile.mcp
- [ ] Built Docker image successfully
- [ ] Tested container locally (all endpoints work)
- [ ] Added API key authentication
- [ ] Pushed image to Docker Hub or GitHub Packages
- [ ] Created team setup documentation
- [ ] Had at least one teammate pull and run your image

### Submission

Create a document with:

1. **Screenshots:**
   - Terminal showing `docker ps` with your running container
   - Successful curl request with timestamp
   - Your image on Docker Hub/GitHub Packages

2. **Links:**
   - Your Docker image URL (e.g., hub.docker.com/r/yourname/airline-mcp-synth)
   - Your team setup guide (link to GitHub file)

3. **Reflection (150-200 words):**
   - What was the hardest part?
   - What surprised you?
   - How would you improve the deployment?

### Optional Bonus
- [ ] Deployed to a cloud platform (Heroku, Cloud Run, etc.)
- [ ] Added monitoring/health checks
- [ ] Created a CI/CD pipeline (auto-builds on git push)

---

## 🎓 Learning Resources

**Docker Basics:**
- [Docker 101 Tutorial](https://www.docker.com/101-tutorial/)
- [Play with Docker](https://labs.play-with-docker.com/) - Free online practice

**Security:**
- [FastAPI Security Docs](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

**Cloud Deployment:**
- [Heroku Container Registry](https://devcenter.heroku.com/articles/container-registry-and-runtime)
- [Google Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts)

---

## 💡 Common Questions

**Q: Why not just share my Python code?**  
A: Docker includes everything (Python version, OS, dependencies). No "it works on my machine" problems.

**Q: How big are Docker images?**  
A: Ours is ~400MB. Uses Python slim image + Synth. Could optimize to ~150MB with multi-stage builds.

**Q: Can I run multiple versions simultaneously?**  
A: Yes! Use different ports: `-p 8010:8010` for v1, `-p 8011:8010` for v2.

**Q: What if I update my code?**  
A: Rebuild the image with a new version tag (v1.2, v1.3, etc.) and push to the registry.

**Q: Is my API key secure?**  
A: For development, yes. For production, use a secrets manager (AWS Secrets Manager, HashiCorp Vault).

---

**Remember:** The goal isn't perfection - it's learning by doing. Start simple, then improve! 🚀
