# Copilot Instructions for this repo

Principles
- Use ATTACHED context only. If context is missing or ambiguous, **ask before guessing**.
- Prefer **minimal diffs**; avoid multi-file edits unless I attach those files.
- Follow repository standards: formatter/linter/test commands below.

Build & Test
- Setup: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Lint: `ruff check .`
- Tests: `pytest -q`

Policies
- Don’t invent APIs or change public interfaces without approval.
- If an edit touches >2 files or >50 lines, **propose the plan first** and wait for confirmation.
- If a command/tool is required, show the exact command and ask to run it.

Context to prefer
- When I say “Add context,” prioritize: **selections > symbols > files**. Use `#codebase` only when I request it.

Tools (MCP)
- Safe to call: `query_db`, `train_model`, `predict`, `evaluate`, `read_file_span`.
- **Ask first** before any tool call that writes or could be long-running.
