# Exercise 01 — Set up Copilot Instructions (repo-wide + path-scoped)

Goal: make Copilot follow our rules **without guessing**.
You will:
1) Move the prepared instruction files into the **.github** folder at the repo root.
2) Add a **models-specific** instruction file (`models.instructions.md`) with an `applyTo` glob.
3) Verify Copilot sees and uses both instruction layers.
4) Try the **Generate Instructions** button and compare.

---

## Prereqs
- You're working from the **repo root** (not a subfolder).
- VS Code with GitHub Copilot & Copilot Chat extensions installed.
- Git CLI available.

---

## 1) Copy the exercise files into `.github` (repo root)

> We want Copilot to auto-load instructions from `.github`. Files under `exercises/` are not auto-loaded.

```bash
# From the repo root
mkdir -p .github/instructions

# Copy the repo-wide instructions file
cp -v exercises/01-setup/copilot-instructions.md .github/copilot-instructions.md

# Copy the path-scoped models instructions file
cp -v exercises/01-setup/models.instructions.md .github/instructions/models.instructions.md

# Sanity check
ls -la .github
ls -la .github/instructions
```

## 2) Ensure the path-scoped file has a correct applyTo front matter

Open `.github/instructions/models.instructions.md` and make sure the top looks like this:

```yaml
---
applyTo: "airline-discount-ml/src/models/**/*.py,src/models/**/*.py"
---
```

Two globs are included so it works whether you open the repo root or the `airline-discount-ml/` subfolder as your workspace.

Keep the rest of your models instructions below that front matter.

Save the file.

## 3) Commit your changes (optional but recommended)

```bash
git add .github/copilot-instructions.md .github/instructions/models.instructions.md
git commit -m "chore: add repo-wide and models path-scoped Copilot instructions"
git push
```

## 4) Verify in VS Code that Copilot sees the files

Reload the window: `Cmd+Shift+P` (Mac/Linux) or `Ctrl+Shift+P` (Windows) → `Developer: Reload Window`.

Open Copilot Chat → click the gear icon (Configure Chat) → Instructions:

You should see Workspace instructions listing:

- `.github/instructions/models.instructions.md`

In Copilot Chat, click `Add context` → `Instructions`: should be selectable.

If you don't see them, see Troubleshooting at the end.

## 5) Ask Copilot to confirm the active instructions (fast tests)

In Copilot Chat (with a file under `src/models/` open/active), run:

### A. Which rules apply?

```
Which repository and path-scoped instructions are applied to this file? Summarize the key constraints.
```

Check the References panel — it should list both instruction files.

### B. "Don't guess" behavioral check

Add this temporary line to `.github/copilot-instructions.md` (then reload VS Code):

To reload VS Code on macOS, use the keyboard shortcut Cmd+Shift+P to open the Command Palette, then type and select "Developer: Reload Window" (or just "Reload Window").

```
  If provided columns are not in the database, ask for clarification instead of guessing.
```

Now ask Copilot:

```
Train a predictor using columns flight_duration_hours and passenger_age_years.
```

You didn't provide those columns. Copilot should ask a clarifying question, not invent columns.

Remove the temporary line after confirming behavior.

## 6) Try the Generate Instructions button (compare & learn)

In VS Code: Copilot Chat → Configure Chat → Generate Instructions.

Let it draft instructions based on your workspace.

Do not commit as-is. Compare with your repo file:

Keep your guardrails: Use ATTACHED context only; ask—don't guess; minimal diffs; plan before multi-file edits.

Merge any helpful build/lint/test detection it found.

If you want to experiment, paste parts of the generated text into a separate temp file and test them, but keep `.github/copilot-instructions.md` as the source of truth.

## 7) Create custom instructions for the data module

Now that you understand how path-scoped instructions work, let's create instructions for the `src/data/` module.

### Task: Create data.instructions.md

Create a new instruction file specifically for the data layer:

```bash
# Create the data instructions file
touch .github/instructions/data.instructions.md
```

Open `.github/instructions/data.instructions.md` and add:

```yaml
---
applyTo: "airline-discount-ml/src/data/**/*.py,src/data/**/*.py"
---
add your instructions to the file

### Verify the new instructions

1. **Commit the new file:**
```bash
git add .github/instructions/data.instructions.md
git commit -m "Add data layer instructions for SQLite operations"
```

2. **Reload VS Code** and verify Copilot sees the new instructions

3. **Test with a data module file:**
Open `src/data/database.py` and ask:
```
What specific constraints apply to this data layer file according to data.instructions.md?
```

## 8) Quick prompts to use after setup

### Repo rules check

```
Summarize the repository instructions you will follow for any edits. What will you do if context is missing?
```

### Models rules check (path-scoped)

Press # and choose discount_predictor.py or passenger_profiler.py, then ask:

```
In this models file, what additional constraints apply per models.instructions.md?
```

### Data layer rules check (new!)

Press # and choose database.py or load_synthetic_data.py, then ask:

```
In this data file, what specific database and schema constraints apply per data.instructions.md?
```

### Minimal diff edit (with selection attached)

run:

```
pytest -q
```
You should get one failing test (test_fit_validates_missing_columns).

Go to chat, press #, start typing "validate", select a function _validate_X, then ask:
```
Using the ATTACHED selection only, propose a minimal diff to add input validation.
If required columns are missing, ask before guessing. Output only a unified diff.
```
You should see the minimum diff output


## Troubleshooting

### Not seeing the repo-wide file

- Ensure the workspace root in VS Code is the repo root (contains the `.github` folder).
- File must be named exactly `.github/copilot-instructions.md` (spelling matters).
- Reload the window after changes.

### Path-scoped file not applying

Confirm the `applyTo:` glob matches your actual path. Try a broader pattern:

```yaml
---
applyTo: "**/src/models/**/*.py"
---
```

Make sure the file lives under `.github/instructions/` and includes the front matter.

### Still not working

- Update the GitHub Copilot and Copilot Chat extensions.
- Start a new chat session (old ones can cache context).
- Use `Add context` → `Instructions` to explicitly attach the file(s) and see if behavior changes.