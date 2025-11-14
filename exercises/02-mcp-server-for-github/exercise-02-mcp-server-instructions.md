# Exercise 02 — Set up MCP Server for GitHub


---

## 0) Prereqs (once)

- VS Code updated to a version with GA MCP support.
- GitHub Copilot installed & signed in.
- If you’re in an org, your admin must allow MCP servers in Copilot policies.

---

## 1) Enable MCP & discover servers

### Open Settings

- macOS: `⌘ ,`
- Windows: `Ctrl ,`
- Or: Command Palette → “Preferences: Open Settings (UI)”

### Configure MCP

1. In Settings search, type `mcp`.
2. Set `chat.mcp.access` → `all` (or `registry` if your org restricts to approved servers).
3. (Optional) Turn on `chat.mcp.gallery.enabled` to browse `@mcp` servers in the Extensions view.
4. Reload Window (Command Palette → “Developer: Reload Window”).

### Add an official server (GitHub MCP)

1. Command Palette → “MCP: Add Server” → choose HTTP.
2. URL:

	```text
	https://api.githubcopilot.com/mcp/
	```
3. When prompted, choose Workspace to save into `.vscode/mcp.json` (repo-scoped).
4. Complete sign-in/authorization if asked.

### Verify discovery

1. Open Copilot Chat and switch to Agent mode.
2. Click on the "Select tools" button; you should see "MCP Server: GitHub" (or your chosen server) along with available actions.
3. In MCP.json click start the server if not started
4. Run a safe read test:

	```text
	#github-mcp List open issues in this repository (top 5).
	```

5. Enable Issue Management Tools

	To enable issue management tools in your workspace, run:

	```text
	@workspace /enableTools issue_management
	```

6. Create an issue

	```text
	Create a new issue titled "MCP discovery smoke test" with body "Created via GitHub MCP".
	```
	Run again:
	```text
	#github-mcp List open issues in this repository (top 5).
	```

7. List available tools

	```text
		#github-mcp list available tools
	```

8. Now write a command to list commits 


### Troubleshooting

- Tools not visible → ensure `.vscode/mcp.json` exists at repo root (and you opened the repo root), then Reload Window.
- Auth loops → re‑sign in; if your org requires PAT, configure with the required scopes.
- Org policy blocks → verify MCP servers are allowed by your admin.

### Explore the MCP gallery (bonus)

- Open Extensions:
  - macOS: `⌘⇧X`
  - Windows: `Ctrl⇧X`
- In the search box, type `@mcp` to filter for MCP servers.
- Browse what’s available (e.g., issue trackers, CI, databases, Jira).
- Pick one read-only server and add it via “MCP: Add Server” → save to Workspace so your team inherits it on clone.

