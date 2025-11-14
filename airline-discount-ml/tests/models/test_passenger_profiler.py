"""
Unit tests for passenger_profiler module.

Validates:
- build_features produces required columns
- Distance conversion from miles to km
- Error handling for empty input
"""
from __future__ import annotations

import pandas as pd
import pytest

from src.models import build_features


def test_build_features_basic():
    """Test build_features produces required columns."""
    df = pd.DataFrame({
        "distance_km": [3459.0, 5478.0],
        "history_trips": [10, 25],
        "avg_spend": [500.0, 1200.0],
        "route_id": ["R1", "R2"],
        "origin": ["NYC", "LAX"],
        "destination": ["LON", "TYO"],
    })
    
    result = build_features(df)
    
    expected_cols = [
        "distance_km", "history_trips", "avg_spend",
        "route_id", "origin", "destination"
    ]
    assert list(result.columns) == expected_cols
    assert len(result) == 2
    assert result.index.equals(df.index)


def test_build_features_converts_miles():
    """Test build_features converts distance in miles to km."""
    df = pd.DataFrame({
        "distance": [2150.0],  # miles
        "history_trips": [5],
        "avg_spend": [800.0],
        "route_id": ["R1"],
        "origin": ["NYC"],
        "destination": ["LON"],
    })
    
    result = build_features(df)
    assert result["distance_km"].iloc[0] == pytest.approx(2150.0 * 1.60934, rel=1e-3)


def test_build_features_empty_raises():
    """Test build_features raises on empty DataFrame."""
    with pytest.raises(ValueError, match="non-empty"):
        build_features(pd.DataFrame())
