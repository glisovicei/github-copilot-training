# Copilot Instructions for src/models

Purpose
- Ensure Copilot produces accurate, minimal, and testable modeling code for discount prediction.

Scope (this folder)
- discount_predictor.py: model training, save/load, predict.
- passenger_profiler.py: feature construction from preprocessed inputs.
- No database or I/O here (pure, testable functions only).

Project context Copilot must assume
- Data source: synthetic SQLite via src/data/database.py (handled outside models).
- Features are tabular (pandas DataFrame/Series); models use scikit-learn.
- Target: numeric discount_value (%) → treat as regression.
- Reproducibility: set random_state=42 for any stochastic step.
- Python >=3.8, use type hints and docstrings; avoid side effects.

Hard constraints
- Do not read/write files or talk to the DB from models.
- Inputs/outputs must be explicit parameters/returns (no globals).
- Keep models small and fast; no deep learning or GPUs.
- No PII; only schema-driven, synthetic features.

Coding standards
- Type hints on all public funcs.
- Docstrings with Args/Returns/Raises.
- Validate inputs (non-empty, required columns present).
- Deterministic behavior (fixed seeds).
- Raise ValueError with clear messages on bad inputs.

Minimal APIs to implement or maintain
- discount_predictor.py
  - fit(X: pd.DataFrame, y: pd.Series) -> "DiscountPredictor"
  - predict(X: pd.DataFrame) -> pd.Series
  - save(path: str | Path) -> None
  - load(path: str | Path) -> "DiscountPredictor"  (classmethod or function)
- passenger_profiler.py
  - build_features(df: pd.DataFrame) -> pd.DataFrame  (pure; no I/O)

Evaluation (for training)
- Use train_test_split, MAE and R^2 for metrics.
- Provide a simple baseline (mean or LinearRegression) before any complex model.

Acceptance criteria for Copilot-generated code
- Passes unit tests in tests/test_models.py (to be added/extended).
- No imports from src.data.database in models.
- Uses sklearn (e.g., LinearRegression or RandomForestRegressor with random_state=42).
- Handles edge cases: empty DataFrames, missing columns → raises ValueError.
- Predict returns same index as X.
- Required features: ['distance_km', 'history_trips', 'avg_spend', 'route_id', 'origin', 'destination']
- No PII features like passenger_id in the model inputs.

Ready-to-copy prompts for Copilot (use after selecting the target file/function)
- "Implement a minimal DiscountPredictor with fit/predict/save/load using scikit-learn LinearRegression. Enforce input validation for required columns: ['distance_km', 'history_trips', 'avg_spend', 'route_id', 'origin', 'destination']. Use Pipeline with ColumnTransformer for preprocessing."
- "Refactor the selected build_features to be a pure function that constructs required features from input DataFrame. Handle distance_km (or convert from distance in miles), history_trips (or trips_count), avg_spend (or derive from total_spend/trips). Add type hints, docstring, and input validation."
- "Add unit tests for DiscountPredictor: trains on a tiny synthetic DataFrame, asserts MAE is reasonable, checks index preservation, and verifies save/load round-trip."
- "Improve predict error handling: if model is not fitted, raise a clear RuntimeError with guidance to call fit first."
- "Update build_features to handle missing columns gracefully by filling with pd.NA, and ensure it returns only the required output columns: ['distance_km', 'history_trips', 'avg_spend', 'route_id', 'origin', 'destination']."

Do
- Keep feature logic in passenger_profiler.py; keep modeling in discount_predictor.py.
- Use ColumnTransformer/Pipeline to ensure consistent preprocessing at predict time.
- Pin random_state=42 and document it (also set random.seed(42) and np.random.seed(42) at module level).
- Separate numeric features (distance_km, history_trips, avg_spend) and categorical (route_id, origin, destination) in preprocessing.
- Use SimpleImputer for missing values, StandardScaler for numeric, OneHotEncoder for categorical.

Don’t
- Query the database or read files inside models.
- Add plotting or notebook-specific code here.
- Introduce heavy dependencies beyond numpy/pandas/scikit-learn/joblib.

Testing checklist Copilot should satisfy
- fit/predict on small synthetic data.
- predict before fit raises error.
- save then load restores identical predictions.
- build_features produces expected columns: ['distance_km', 'history_trips', 'avg_spend', 'route_id', 'origin', 'destination'].
- build_features handles unit conversion (miles to km) when distance_km not present.
- Model outperforms baseline (DummyRegressor with strategy='mean').

Commands (for trainees)
- Run tests: `pytest -q` (or `make test` if provided)
- Format/lint: `black .` and `flake8` (if configured)

Notes for Copilot
- Prefer Pipeline([('prep', ColumnTransformer(...)), ('model', LinearRegression())]).
- Validate required feature columns early, with explicit messages.
- Keep public API stable; add new helpers as internal (_prefixed) functions.
