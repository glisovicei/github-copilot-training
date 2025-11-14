```markdown
## Best practices (what works)

- Target the code precisely
	- Highlight the function/class and ask for tests for the selection. This reduces boilerplate and hallucinations.  

- Be explicit about scope & edges
	- In your prompt, name success/edge/error cases, exceptions, and boundary values you need covered. Copilot responds best to concrete cases.  

- State the test harness
	- Specify fixtures/mocks/stubs and that no external network/filesystem is allowed (DI or mocking required). Copilot can scaffold mocks if you say so.  

- Prefer black-box assertions
	- Assert on public API and observable effects, not internals. Ask Copilot to avoid brittle implementation checks and to preserve input index/order when relevant (e.g., pandas). (General testing guidance; refine via prompts.)

- Use codebase context to find gaps
	- Ask: “which branches/paths in X lack tests?” or “generate tests to cover the error paths”. Copilot can help explore the file and nearby call sites.  

- Keep tests fast & deterministic
	- Seed RNGs, avoid time & I/O, and parametrize inputs instead of random generation.

- Review & run
	- Generated tests are a starting point—review and add missing cases. Then run `pytest -q` (or the project's test command) to validate.  

---

# Exercise 04 — Add Unit Tests (pytest)

## Learning Objectives
- Practice "target code precisely" by highlighting specific functions for test generation
- Write deterministic, fast unit tests using pytest
- Use Copilot to generate tests for edge cases and validation logic


## Using descriptions above create 
.github/instructions/tests.instructions.md

## Test Structure

Tests are organized by module to mirror the code structure:
```
tests/
├── models/
│   ├── test_discount_predictor.py
│   └── test_passenger_profiler.py
├── data/
│   └── test_database.py
└── agents/
    └── test_discount_agent.py
```

---

## Task 1: Organize Test Structure

**Goal:** Set up the test directory structure to mirror the source code organization.

### Instructions

**Step 1:** Use Copilot Chat with this prompt to create the test structure (don't forget to add context with #):
```
Create test files that mirror src/ code structure. For each module in #file:models
create a matching folder and file in #tests Same for #file:data and #file:agents
Include init.py in each test subdirectory. If already created, do not do anything
```

**Step 2:** Configure pytest for VS Code integration using the `/setupTests` slash command:

```
@workspace /setupTests for pytest
Tests live in airline-discount-ml/tests/ directory with subdirectories: airline-discount-ml/tests/models/, airline-discount-ml/tests/data/, airline-discount-ml/tests/agents/.
Use imports from src.* (CWD=airline-discount-ml).
Create pytest.ini at airline-discount-ml/pytest.ini with testpaths=tests.
Update .vscode/settings.json to set python.testing.cwd=airline-discount-ml and extraPaths.
Show the diff before applying
```


#### What does `/setupTests` do?

The `/setupTests` command is a **Copilot workspace agent** that automates test framework configuration. It:

1. **Creates `pytest.ini`** at the repository root with proper test discovery paths
   - Sets `testpaths` to locate your tests
   - Configures `pythonpath` so imports work correctly

2. **Updates `.vscode/settings.json`** with VS Code Python testing settings:
   - Enables pytest and disables other test frameworks
   - Sets `python.testing.cwd` to the correct working directory
   - Configures `python.analysis.extraPaths` for IntelliSense on `src.*` imports

3. **Shows a diff before applying** so you can review changes

4. **Enables VS Code Test Explorer UI** - you'll see test icons in the sidebar and can run/debug tests with one click

This eliminates manual configuration and ensures your test environment works consistently across the team.

### Acceptance Criteria

- [ ] Test subdirectories exist: `tests/models/`, `tests/data/`, `tests/agents/`
- [ ] Each subdirectory has `__init__.py`
- [ ] Test files mirror source modules (e.g., `test_discount_predictor.py` for `discount_predictor.py`)

---

## Task 2: Target Code Precisely — Test `_validate_y`

**Goal:** Demonstrate the "target code precisely" best practice by generating tests for a single, focused function.

### Instructions

1. **Open the file:** `airline-discount-ml/src/models/discount_predictor.py`

2. **Locate and select the `_validate_y` method:**
   ```python
   @staticmethod
   def _validate_y(y: pd.Series) -> None:
       if not isinstance(y, pd.Series):
           raise ValueError("y must be a pandas Series.")
       if y.empty:
           raise ValueError("y is empty.")
   ```

3. **Target the selection with Copilot Chat:**
   - Highlight only the `_validate_y` method (lines 69-73)
   - Open Copilot Chat
   - Use this prompt:
     ```
     /tests Write pytest tests for the selected _validate_y method. Cover these cases:
     - Valid non-empty Series (should pass without exception)
     - Invalid input: not a Series (list, dict, DataFrame, None)
     - Invalid input: empty Series
     Use pytest.raises for exception cases.
     ```
   
   **Alternative:** Use built-in context addition functions
   ```
3. **Target the selection with Copilot Chat:**
   - Highlight only the `_validate_y` method (lines 69-73)
   - Open Copilot Chat
   - Use this prompt:
     ```
     /tests Write pytest tests for the selected _validate_y method. Cover these cases:
     - Valid non-empty Series (should pass without exception)
     - Invalid input: not a Series (list, dict, DataFrame, None)
     - Invalid input: empty Series
     Use pytest.raises for exception cases.
     ```
   
   **Alternative:** Use built-in context addition functions:
   ```
   /tests #file:discount_predictor.py #sym:_validate_y Write pytest tests for the selected _validate_y method. Cover these cases:
     - Valid non-empty Series (should pass without exception)
     - Invalid input: not a Series (list, dict, DataFrame, None)
     - Invalid input: empty Series
     Use pytest.raises for exception cases. save test in #file:test_discount_predictor.py 
   ```

   > **💡 Tip:** Prepending `/tests` switches Copilot into "generate unit tests" mode, applying test-specific heuristics for imports, fixtures, and idioms. It respects the current file/selection and produces cleaner, framework-correct tests with less boilerplate to fix.


4. **Review and add the generated tests:**
   - Copilot should generate tests 
   - The tests should be minimal and focused only on `_validate_y`
   - **Expected test structure:**
     ```python
     def test_validate_y_valid_series():
         # Should not raise
         
     def test_validate_y_not_series():
         # Should raise ValueError with message about Series
         
     def test_validate_y_empty_series():
         # Should raise ValueError with message about empty
     ```

5. **Run the tests:**
   ```bash
   cd airline-discount-ml
   source .venv/bin/activate  # or: source venv/bin/activate
   pytest tests/test_models.py::test_validate_y -v
   ```

### Why This Works

- **Precise targeting** → Copilot generates only what you need (no extra boilerplate for the entire class)
- **Clear cases in prompt** → Copilot knows exactly which edge cases to cover
- **Small, testable function** → Easy to verify the tests are correct and complete

### Acceptance Criteria

- [ ] Tests cover all three cases: valid, not-a-Series, empty Series
- [ ] Tests use `pytest.raises` for exception validation
- [ ] Tests run successfully with `pytest`
- [ ] No unnecessary setup/teardown or mocking (this function is pure validation)

---

## Task 3: Use Codebase Context to Find Gaps

**Goal:** Practice using Copilot to identify untested code paths and generate tests for missing coverage.

### Instructions

1. **Analyze the `_validate_X` method for test gaps:**
   - Open `airline-discount-ml/src/models/discount_predictor.py`
   - Locate the `_validate_X` method (similar to `_validate_y` but for DataFrame validation)

2. **Ask Copilot to identify missing tests:**
   - Open Copilot Chat
   - Use this prompt with codebase context:
     ```
     #file:discount_predictor.py #file:test_discount_predictor.py 
     
     Which branches/paths in the _validate_X method lack tests? 
     Looking at the existing test file, what error paths are missing?
     ```

3. **Review Copilot's analysis:**
   - Read through Copilot's response about what's tested vs. untested
   - Compare with the `_validate_y` tests you wrote in Task 2
   - Ask yourself: Does `_validate_X` need similar coverage?

4. **Generate tests for the gaps Copilot identified:**
   - Use this follow-up prompt (adjust based on what Copilot found):
     ```
     /tests Generate tests to cover the missing error paths you identified in _validate_X.
     Use pytest.raises for exception cases. Add to #file:test_discount_predictor.py
     ```

5. **Review the generated tests:**
   - Copilot should identify that `_validate_X` needs the same test coverage as `_validate_y`
   - Tests should follow the same pattern but for DataFrame validation
   - **Expected new tests:**
     ```python
     def test_validate_X_valid_dataframe():
         # Should not raise
         
     def test_validate_X_not_dataframe():
         # Should raise ValueError
         
     def test_validate_X_empty_dataframe():
         # Should raise ValueError
     ```

6. **Run the new tests:**
   ```bash
   cd airline-discount-ml
   pytest tests/models/test_discount_predictor.py::test_validate_X -v
   ```

### Why This Works

- **Codebase context** → Copilot can compare the implementation file with the test file to spot gaps
- **Explicit gap-finding prompt** → Asking "which branches lack tests?" helps Copilot analyze code paths
- **Iterative approach** → First identify gaps, then generate tests (more accurate than doing both at once)
- **Pattern recognition** → Copilot can see similar methods (`_validate_y`) and suggest parallel test coverage

### Acceptance Criteria

- [ ] Copilot successfully identifies untested code paths in `_validate_X`
- [ ] Tests cover all validation cases (valid input, wrong type, empty input)
- [ ] Tests follow the same pattern as `_validate_y` tests
- [ ] All tests pass when run with pytest

---

```
# Exercise 04 — Add Unit Tests (pytest)

