```instructions
---
applyTo: "airline-discount-ml/tests/**/*.py,tests/**/*.py"
---

# Copilot Instructions for tests/

Purpose
- Ensure Copilot generates comprehensive, maintainable pytest tests for all project layers.
- Validate functionality, error handling, edge cases, and layer separation.

Scope (this folder)
- tests/models/: Test ML models (fit, predict, save/load, validation, baseline comparison)
- tests/data/: Test database operations and data layer (queries, connections, no business logic)
- tests/agents/: Test business logic orchestration (integration between layers)
- test_hello.py: Sanity check (keep minimal)

Project context Copilot must assume
- Framework: pytest (NOT unittest) with fixtures, parametrize, and pytest.raises
- Structure: tests/ mirrors src/ directory layout (test_foo.py tests src/foo.py)
- Data: Use synthetic/in-memory data; avoid real database unless testing database.py itself
- Isolation: Each test is independent; use fixtures for shared setup
- Determinism: Tests must pass consistently (set random seeds to 42)
- Python ≥3.8, type hints in test signatures encouraged but not required

Hard constraints
- No unittest.TestCase classes; use plain test functions or pytest classes
- No external API calls, real file I/O (use tempfile for save/load tests)
- No time-dependent tests without mocking (use freezegun if needed)
- Tests must complete in <5 seconds per test (use small datasets)
- Never test implementation details; test public API behavior only

Testing standards
- Naming: test_<function>_<scenario> (e.g., test_predict_before_fit_raises)
- Fixtures: Use @pytest.fixture for reusable setup; prefer function scope
- Assertions: Use descriptive messages with custom messages when helpful
- Coverage: Aim for 80%+ line coverage; prioritize happy path + error cases
- Parametrize: Use @pytest.mark.parametrize for multiple input scenarios
- Markers: Use pytest.mark.discount or custom markers for selective test runs

Test categories to implement
1. Happy path: Normal inputs produce expected outputs
2. Error handling: Invalid inputs raise clear exceptions (ValueError, RuntimeError)
3. Edge cases: Empty data, missing columns, boundary values
4. Round-trip: Save/load, serialize/deserialize produces identical results
5. Index preservation: pandas operations maintain input index
6. Baseline comparison: ML models outperform simple baselines (DummyRegressor)
7. Integration: Components work together across layers (agents calling models)

Layer-specific patterns
- models/: Test fit/predict/save/load; validate required features; compare to baseline; check determinism
- data/: Test database connections, query execution, DataFrame returns; use in-memory SQLite for isolation
- agents/: Test orchestration logic; mock dependencies (models, database) when appropriate

Required test structure for models
```python
@pytest.fixture
def synthetic_data():
    """Create minimal synthetic dataset (100 rows, all required features)."""
    np.random.seed(42)
    # ... return X (DataFrame), y (Series)

def test_<model>_fit_predict(synthetic_data):
    """Test model can fit and predict."""
    # Instantiate, fit, predict, assert types and shapes

def test_predict_before_fit_raises(synthetic_data):
    """Test predict raises RuntimeError if called before fit."""
    with pytest.raises(RuntimeError, match="not fitted"):
        model.predict(X)

def test_fit_validates_empty_X():
    """Test fit raises ValueError on empty DataFrame."""
    with pytest.raises(ValueError, match="empty"):
        model.fit(pd.DataFrame(), pd.Series([1]))

def test_fit_validates_missing_columns(synthetic_data):
    """Test fit raises ValueError on missing required columns."""
    with pytest.raises(ValueError, match="column"):
        model.fit(X_bad, y)

def test_save_load_roundtrip(synthetic_data):
    """Test save/load produces identical predictions."""
    # fit, predict, save, load, predict again, assert equal

def test_model_outperforms_baseline(synthetic_data):
    """Test model beats DummyRegressor on MAE and R²."""
    # train/test split, fit baseline and model, compare metrics

def test_predict_preserves_index():
    """Test predict preserves custom index."""
    # Use custom index on X, assert preds.index equals X.index
```

Required test structure for data layer
```python
@pytest.fixture
def in_memory_db():
    """Create in-memory SQLite database for testing."""
    # Create tables, insert sample data, yield connection, cleanup

def test_database_connect():
    """Test Database connects successfully."""
    # Instantiate, connect, assert connection is not None

def test_fetch_data_returns_rows(in_memory_db):
    """Test fetch_data returns list of rows."""
    # Execute SELECT, assert result is list, check length

def test_fetch_data_with_params(in_memory_db):
    """Test fetch_data handles parameterized queries."""
    # Execute SELECT with params, assert correct filtering

def test_execute_insert(in_memory_db):
    """Test execute performs INSERT successfully."""
    # Execute INSERT, assert True, verify data with SELECT

def test_init_database_creates_tables():
    """Test init_database creates expected tables."""
    # Use tempfile for db_path, run init, check tables exist
```

Required test structure for agents
```python
@pytest.fixture
def mock_model(monkeypatch):
    """Mock DiscountPredictor for isolated agent tests."""
    # Use unittest.mock.Mock or monkeypatch to replace model behavior

def test_discount_agent_calculates_discount():
    """Test DiscountAgent calculates discount correctly."""
    # Call calculate_discount, assert return type and value range

def test_discount_agent_handles_missing_data(mock_model):
    """Test DiscountAgent handles missing passenger history gracefully."""
    # Call with incomplete data, assert no exceptions, reasonable defaults

def test_route_analyzer_analyzes_route():
    """Test RouteAnalyzer returns insights dictionary."""
    # Call analyze_route, assert return is dict with expected keys
```

Validation checklist Copilot should satisfy
- All tests use pytest (no unittest imports)
- Fixtures use @pytest.fixture, not setUp/tearDown
- Error tests use `with pytest.raises(ExceptionType, match="pattern"):`
- Numeric assertions use pytest.approx() for floating point comparisons
- DataFrame/Series assertions use pd.testing.assert_frame_equal or assert_series_equal
- Random operations set np.random.seed(42) or random.seed(42) in fixture
- Test names are descriptive and follow test_<what>_<scenario> pattern
- No hardcoded paths; use Path(__file__).parent or tempfile
- Tests don't depend on execution order (can run in any order)
- Each test validates one specific behavior (SINGLE RESPONSIBILITY)

Common patterns to use
```python
# Parametrized tests for multiple scenarios
@pytest.mark.parametrize("input,expected", [
    ({"flights": 5}, 0.0),
    ({"flights": 10}, 10.0),
    ({"flights": 20}, 15.0),
])
def test_calculate_discount(input, expected):
    agent = DiscountAgent()
    assert agent.calculate_discount("R1", input) == expected

# Testing pandas operations
def test_returns_dataframe():
    result = build_features(df)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["expected", "columns"]
    assert len(result) == len(df)
    assert result.index.equals(df.index)

# Testing file operations
def test_save_model():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "model.joblib"
        model.save(path)
        assert path.exists()
        loaded = DiscountPredictor.load(path)
        # Assert loaded model behaves identically

# Testing exceptions with messages
def test_invalid_input_raises():
    with pytest.raises(ValueError, match="must be non-empty"):
        model.fit(pd.DataFrame(), pd.Series())
```

Ready-to-copy prompts for Copilot
- "Generate pytest tests for DiscountPredictor covering fit, predict, save/load, validation, baseline comparison, and index preservation. Use fixtures for synthetic data with 100 rows."
- "Write tests for Database class verifying connect, fetch_data, execute, and init_database. Use in-memory SQLite for isolation."
- "Add parametrized tests for DiscountAgent.calculate_discount covering zero trips, low trips, and high trips scenarios."
- "Create integration test for agents layer: agent fetches data from database, calls model predict, returns discount recommendation."
- "Generate edge case tests: empty DataFrame, missing columns, mismatched X/y lengths, non-DataFrame inputs."
- "Add test to verify model determinism: fit twice with same data produces identical predictions."
- "Write test to check build_features handles distance unit conversion from miles to km."

Do
- Mirror src/ structure in tests/ (test_discount_predictor.py for discount_predictor.py)
- Use fixtures for repeated setup (synthetic data, database connections, mock objects)
- Test both success cases and failure modes (ValueError, RuntimeError)
- Use pytest.approx() for floating point comparisons (e.g., `assert x == pytest.approx(3.14, rel=1e-3)`)
- Use pd.testing for pandas assertions (assert_frame_equal, assert_series_equal)
- Set random seeds in fixtures for reproducibility
- Use tempfile.TemporaryDirectory() for file I/O tests
- Keep tests fast (<5s each) with small synthetic datasets (n=100)
- Use descriptive test names that explain the scenario
- Group related tests in classes (optional, but can help organization)

Don't
- Use unittest.TestCase or unittest imports (use pytest exclusively)
- Test private methods (anything starting with _)
- Hardcode file paths or assume specific directory structure
- Use real databases or external services (mock or use in-memory alternatives)
- Write overly complex tests (if test is hard to understand, simplify)
- Duplicate logic from source code in tests (test behavior, not implementation)
- Skip error cases (they're as important as happy path)
- Forget to clean up resources (use fixtures with yield for teardown)

Model testing must verify
- fit/predict work with valid inputs
- predict before fit raises RuntimeError with message "not fitted"
- fit with empty DataFrame raises ValueError
- fit with missing required columns raises ValueError
- save/load roundtrip produces identical predictions
- predict preserves input DataFrame index
- Model outperforms DummyRegressor(strategy='mean') on MAE and R²
- Required features: ['distance_km', 'history_trips', 'avg_spend', 'route_id', 'origin', 'destination']
- Determinism: same inputs produce same outputs (random_state=42)

Data layer testing must verify
- Database connects successfully to SQLite
- fetch_data returns list of Row objects
- execute performs INSERT/UPDATE/DELETE successfully
- init_database creates expected tables (passengers, routes, discounts)
- get_connection returns connected Database instance
- Queries handle parameters safely (no SQL injection)

Agents layer testing must verify
- Business logic orchestrates data + models correctly
- Missing data handled gracefully with defaults
- Return types match expected (float for discounts, dict for insights)
- Integration: agents can call real models with mocked data

Coverage goals
- Line coverage: 80%+ (use `pytest --cov=src --cov-report=html`)
- Branch coverage: 70%+ (test both if/else branches)
- Priority: Public APIs > error handling > edge cases > internal helpers

Running tests
- All tests: `pytest tests/ -v` or `make test`
- Specific file: `pytest tests/models/test_discount_predictor.py -v`
- Specific test: `pytest tests/models/test_discount_predictor.py::test_name -v`
- With coverage: `pytest tests/ --cov=src --cov-report=html -v` or `make test-cov`
- Fast fail: `pytest tests/ -x` (stop on first failure)
- Show print output: `pytest tests/ -v -s`

Markers usage
- `@pytest.mark.discount`: Mark discount-related tests
- Run marked tests: `pytest -m discount`
- Skip slow tests: `@pytest.mark.slow` then `pytest -m "not slow"`

Continuous improvement
- If test fails intermittently, add random seed or mock time
- If test is slow, reduce dataset size or mock expensive operations
- If test is unclear, add docstring explaining what's being validated
- If many tests share setup, extract to fixture
- If parametrize gets too complex, split into multiple tests

Notes for Copilot
- Prefer fixtures over repeated setup code in each test
- Use `match="pattern"` in pytest.raises to validate error messages
- For pandas, use .equals() for index comparison, assert_series_equal for values
- For ML models, always compare to baseline (DummyRegressor) to prove value
- Test index preservation: models should return Series with same index as input X
- Keep synthetic datasets minimal (n=100) but diverse (multiple categories, wide numeric ranges)
- When testing agents, mock dependencies to isolate business logic
- Document expected behavior in test docstrings (helps future maintainers)

Example test file structure
```python
"""
Unit tests for <module_name>.

Validates:
- <Key behavior 1>
- <Key behavior 2>
- <Key behavior 3>
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.module import ClassToTest


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    # Setup code
    return data


def test_basic_functionality(sample_data):
    """Test basic use case works correctly."""
    # Arrange
    obj = ClassToTest()
    
    # Act
    result = obj.method(sample_data)
    
    # Assert
    assert isinstance(result, ExpectedType)
    assert len(result) == expected_length


def test_error_on_invalid_input():
    """Test method raises ValueError on invalid input."""
    obj = ClassToTest()
    
    with pytest.raises(ValueError, match="expected error message"):
        obj.method(invalid_input)


# ... more tests following same pattern
```
```
