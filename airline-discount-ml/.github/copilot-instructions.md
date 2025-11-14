# GitHub Copilot Instructions - Airline Discount ML Training Repository

## Project Context
This is a **training repository** for teaching GitHub Copilot, MCP tools, and ML workflows. Uses SQLite with synthetic data only—no real passenger information.

**Core Pattern:** `src.models` contains pure ML code (no I/O), `src.data.database` handles all database operations, `src.agents` implements discount calculation logic.

## Architecture & Data Flow

### 1. Database Layer (`src/data/`)
- **SQLite only** (no PostgreSQL) - `data/airline_discount.db`
- Schema: `passengers` (name, travel_history JSON), `routes` (origin, destination, distance), `discounts` (links passengers/routes with discount_value)
- Initialize with: `python -c "from src.data.database import init_database; init_database()"`
- All DB access goes through `Database` class or `get_connection()` helper

### 2. Models Layer (`src/models/`)
**Critical:** Models NEVER import from `src.data.database`. They are pure functions/classes taking DataFrames.

- `discount_predictor.py`: sklearn Pipeline with ColumnTransformer → LinearRegression
  - API: `fit(X, y)`, `predict(X)`, `save(path)`, `load(path)` (classmethod)
  - Required features: `['distance_km', 'history_trips', 'avg_spend', 'route_id', 'origin', 'destination']`
  - Numeric features: SimpleImputer(median) → StandardScaler
  - Categorical features: SimpleImputer(most_frequent) → OneHotEncoder
  - Always set `random_state=42` and module-level seeds: `random.seed(42); np.random.seed(42)`

- `passenger_profiler.py`: Pure function `build_features(df) -> DataFrame`
  - Converts miles to km: `distance * 1.60934`
  - Derives `avg_spend` from `total_spend / history_trips` if needed
  - Returns only required columns in correct order
  - No PII (no `passenger_id` in output)

### 3. Agents Layer (`src/agents/`)
Stub implementations for training exercises. Pattern: classes with business logic methods that could call models/database.

## Development Workflows

### Setup (one-time)
```bash
./setup.sh  # Mac/Linux, creates venv, installs deps, registers Jupyter kernel, init DB
# OR: setup.bat on Windows
# OR: pip install -e ".[dev]" (manual)
```

### Tests
```bash
pytest tests/ -v              # Run all tests
pytest tests/test_models.py   # Specific file
make test-cov                 # With coverage
```

**Test Structure:**
- `tests/test_models.py`: Comprehensive pytest suite with fixtures
- Tests validate: fit/predict, baseline comparison (DummyRegressor), save/load roundtrip, index preservation
- 10 tests must pass before committing model changes

### Notebooks
- Start: `jupyter lab` or `make run-notebook`
- Kernel name: `"Python (airline-discount-ml)"` (registered by setup script)
- Sample notebook: `notebooks/exploratory_analysis.ipynb` shows DB connection pattern:
  ```python
  import sys; from pathlib import Path
  sys.path.insert(0, str(Path().resolve().parent))
  from src.data.database import get_connection
  db = get_connection()
  ```

### Database Operations
```bash
make db-init        # Reinitialize schema and sample data
make db-sample      # Load sample data only
# Check data: jupyter lab → notebooks/exploratory_analysis.ipynb → run cells
```

## Project-Specific Conventions

### 1. **Editable Install Pattern**
- Package installed with `pip install -e ".[dev]"` (not just requirements.txt)
- Enables `from src.models import DiscountPredictor` without sys.path hacks (except in notebooks)
- Dev dependencies in `setup.py` extras_require: pytest, jupyter, black, flake8

### 2. **Deterministic ML**
- ALWAYS set `random_state=42` in sklearn estimators
- Set module-level seeds: `random.seed(42); np.random.seed(42)` at top of model files
- Required for reproducible training exercises

### 3. **No PII in Models**
- Never use `passenger_id` as a feature (only for joins)
- Only schema-driven features: distance, history metrics, route info
- Travel history stored as JSON text, not referenced directly by models

### 4. **Validation-First Approach**
- All model methods validate inputs before processing
- Raise `ValueError` with clear messages for empty DataFrames, missing columns
- Raise `RuntimeError` if predict called before fit

### 5. **Index Preservation**
- `predict()` must return Series with same index as input X
- Critical for joining predictions back to source data
- Tested explicitly in `test_predict_preserves_index`

## Common Pitfalls & Solutions

### ❌ Import Error in Notebooks
**Problem:** `ModuleNotFoundError: No module named 'src'`
**Solution:** Add to first cell:
```python
import sys; from pathlib import Path
sys.path.insert(0, str(Path().resolve().parent))
```

### ❌ Database Not Found
**Problem:** `sqlite3.OperationalError: no such table`
**Solution:** Run `make db-init` or `python -c "from src.data.database import init_database; init_database()"`

### ❌ Model Predicting Before Fit
**Problem:** RuntimeError during predict
**Solution:** Check `self._fitted` flag, call `fit()` first

### ❌ Wrong Jupyter Kernel
**Problem:** Imports work in terminal but not notebook
**Solution:** Restart kernel, select "Python (airline-discount-ml)" kernel

## When to Use Which Tool

### MCP Tools (custom server in `src/mcp/`)
- `query_db`: Fetch data from SQLite for training
- `train_model`: Execute model training pipelines
- `predict`: Run predictions on new data
- `evaluate`: Calculate MAE, R² metrics

### Standard Commands
- **Format:** `black src tests` or `make format`
- **Lint:** `flake8 src tests` or `make lint`
- **Train:** `python src/training/train.py` or `make train`
- **Evaluate:** `python src/training/evaluate.py` or `make evaluate`

## File-Specific Guidance

When working in **`src/models/`**, follow `.github/instructions/models.instructions.md` for detailed API contracts, feature requirements, and testing checklist.

## Editing Guidelines

- **<2 files, <50 lines:** Proceed with changes
- **≥2 files OR ≥50 lines:** Propose plan first, wait for approval
- **API changes:** Always ask before modifying public interfaces (fit/predict signatures, function names)
- **Context priority:** selections > symbols > files > #codebase (use #codebase only if requested)

## Training Repository Philosophy

This repo demonstrates **professional ML project setup** for teaching purposes:
- Automated setup scripts (cross-platform)
- Makefile for command shortcuts
- Comprehensive tests with pytest
- Type hints and docstrings throughout
- Clear separation: data layer, model layer, agent layer
- No production secrets (synthetic data only)

**Goal:** Trainees learn GitHub Copilot best practices through well-structured, documented code.
