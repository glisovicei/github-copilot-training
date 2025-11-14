"""
Unit tests for DiscountPredictor model.

Validates:
- fit/predict/save/load functionality
- Baseline comparison
- Error handling and validation
- Index preservation
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from src.models import DiscountPredictor


@pytest.fixture
def synthetic_data():
    """Create minimal synthetic dataset for testing."""
    np.random.seed(42)
    n = 100
    
    df = pd.DataFrame({
        "distance_km": np.random.uniform(1000, 6000, n),
        "history_trips": np.random.randint(1, 50, n),
        "avg_spend": np.random.uniform(100, 2000, n),
        "route_id": np.random.choice(["R1", "R2", "R3"], n),
        "origin": np.random.choice(["NYC", "LAX", "SFO"], n),
        "destination": np.random.choice(["LON", "TYO", "PAR"], n),
    })
    
    # Simple linear target: discount increases with distance and history
    y = (
        0.002 * df["distance_km"] 
        + 0.3 * df["history_trips"] 
        + 0.005 * df["avg_spend"]
        + np.random.normal(0, 2, n)
    )
    y = pd.Series(y, name="discount_value")
    
    return df, y


def test_discount_predictor_fit_predict(synthetic_data):
    """Test DiscountPredictor can fit and predict."""
    X, y = synthetic_data
    
    model = DiscountPredictor()
    model.fit(X, y)
    
    preds = model.predict(X)
    
    assert isinstance(preds, pd.Series)
    assert len(preds) == len(X)
    assert preds.index.equals(X.index)
    assert preds.name == "discount_value"


def test_predict_before_fit_raises(synthetic_data):
    """Test predict raises error if called before fit."""
    X, _ = synthetic_data
    
    model = DiscountPredictor()
    
    with pytest.raises(RuntimeError, match="not fitted"):
        model.predict(X)


def test_fit_validates_empty_X():
    """Test fit raises on empty DataFrame."""
    model = DiscountPredictor()
    
    with pytest.raises(ValueError, match="empty"):
        model.fit(pd.DataFrame(), pd.Series([1]))


def test_fit_validates_missing_columns(synthetic_data):
    """Test fit raises on missing required columns."""
    _, y = synthetic_data
    X_bad = pd.DataFrame({"distance_km": [3000]})
    
    model = DiscountPredictor()
    
    with pytest.raises(ValueError, match="column is not a column of the dataframe"):
        model.fit(X_bad, y.iloc[:1])


def test_save_load_roundtrip(synthetic_data):
    """Test save/load produces identical predictions."""
    X, y = synthetic_data
    
    model = DiscountPredictor()
    model.fit(X, y)
    
    preds_before = model.predict(X)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "model.joblib"
        model.save(path)
        
        loaded = DiscountPredictor.load(path)
        preds_after = loaded.predict(X)
    
    pd.testing.assert_series_equal(preds_before, preds_after)


def test_model_outperforms_baseline(synthetic_data):
    """Test model beats DummyRegressor baseline on MAE and R²."""
    X, y = synthetic_data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )
    
    # Baseline
    baseline = DummyRegressor(strategy="mean")
    baseline.fit(X_train, y_train)
    baseline_preds = baseline.predict(X_test)
    baseline_mae = mean_absolute_error(y_test, baseline_preds)
    baseline_r2 = r2_score(y_test, baseline_preds)
    
    # Model
    model = DiscountPredictor()
    model.fit(X_train, y_train)
    model_preds = model.predict(X_test)
    model_mae = mean_absolute_error(y_test, model_preds)
    model_r2 = r2_score(y_test, model_preds)
    
    # Model should be better
    assert model_mae < baseline_mae, f"Model MAE {model_mae} should be < baseline {baseline_mae}"
    assert model_r2 > baseline_r2, f"Model R² {model_r2} should be > baseline {baseline_r2}"
    
    print(f"\nBaseline: MAE={baseline_mae:.3f}, R²={baseline_r2:.3f}")
    print(f"Model:    MAE={model_mae:.3f}, R²={model_r2:.3f}")


def test_predict_preserves_index():
    """Test predict preserves custom index."""
    X = pd.DataFrame({
        "distance_km": [3000, 4000],
        "history_trips": [5, 10],
        "avg_spend": [500, 800],
        "route_id": ["R1", "R2"],
        "origin": ["NYC", "LAX"],
        "destination": ["LON", "TYO"],
    }, index=["row_a", "row_b"])
    
    y = pd.Series([10.0, 15.0], index=["row_a", "row_b"])
    
    model = DiscountPredictor()
    model.fit(X, y)
    preds = model.predict(X)
    
    assert list(preds.index) == ["row_a", "row_b"]
