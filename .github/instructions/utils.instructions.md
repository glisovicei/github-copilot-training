---
applyTo: "airline-discount-ml/src/utils/**/*.py"
---

# Utils Module Instructions

## Purpose
Shared utility functions and configuration helpers that **don't fit** in data/models/agents layers. Keep this module minimal—most logic belongs in a specific layer.

## What Belongs Here

### ✅ Appropriate for utils/
- Configuration loading/parsing
- Path resolution helpers
- Environment variable handling
- Logging setup
- Constants and enums
- Generic string/date formatting

### ❌ Does NOT belong in utils/
- Database operations → `src/data/`
- ML preprocessing → `src/models/`
- Business logic → `src/agents/`
- Feature engineering → `src/models/`

## Configuration Pattern

### config.py Structure
```python
"""
Configuration management for airline-discount-ml project.

Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from typing import Optional


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Config:
    """Application configuration with environment variable support."""
    
    # Database
    DB_PATH: str = os.getenv(
        'AIRLINE_DB_PATH',
        str(PROJECT_ROOT / 'data' / 'airline_discount.db')
    )
    
    # Model paths
    MODEL_DIR: Path = Path(os.getenv(
        'MODEL_DIR',
        str(PROJECT_ROOT / 'models')
    ))
    DEFAULT_MODEL_PATH: Path = MODEL_DIR / 'discount_model.pkl'
    
    # Training parameters
    RANDOM_STATE: int = int(os.getenv('RANDOM_STATE', '42'))
    TEST_SIZE: float = float(os.getenv('TEST_SIZE', '0.2'))
    
    # Feature schema
    REQUIRED_FEATURES = [
        'distance_km',
        'history_trips',
        'avg_spend',
        'route_id',
        'origin',
        'destination'
    ]
    
    NUMERIC_FEATURES = ['distance_km', 'history_trips', 'avg_spend']
    CATEGORICAL_FEATURES = ['route_id', 'origin', 'destination']
    
    @classmethod
    def get_model_path(cls, filename: Optional[str] = None) -> Path:
        """
        Get path to model file.
        
        Args:
            filename: Model filename (default: discount_model.pkl)
        
        Returns:
            Absolute path to model file
        """
        if filename is None:
            return cls.DEFAULT_MODEL_PATH
        return cls.MODEL_DIR / filename
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings."""
        # Check database exists
        if not Path(cls.DB_PATH).exists():
            raise FileNotFoundError(
                f"Database not found: {cls.DB_PATH}. "
                "Run 'make db-init' to initialize."
            )
        
        # Check model directory exists
        cls.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Config validated")
        print(f"  DB: {cls.DB_PATH}")
        print(f"  Models: {cls.MODEL_DIR}")


# Singleton instance
config = Config()
```

### Usage in Other Modules
```python
# In src/data/database.py
from src.utils.config import config

def get_connection():
    return sqlite3.connect(config.DB_PATH)

# In src/models/discount_predictor.py
from src.utils.config import config

class DiscountPredictor:
    def __init__(self):
        self.required_features = config.REQUIRED_FEATURES
```

## Path Utilities

### Path Resolution Helpers
```python
"""Path utilities for consistent file access."""
from pathlib import Path


def get_project_root() -> Path:
    """
    Get absolute path to project root directory.
    
    Returns:
        Path object pointing to airline-discount-ml/
    """
    # This file is in src/utils/, so go up 2 levels
    return Path(__file__).resolve().parent.parent.parent


def get_data_dir() -> Path:
    """Get absolute path to data directory."""
    return get_project_root() / 'data'


def get_model_dir() -> Path:
    """Get absolute path to models directory."""
    return get_project_root() / 'models'


def ensure_dir_exists(path: Path) -> Path:
    """
    Ensure directory exists, create if needed.
    
    Args:
        path: Directory path
    
    Returns:
        Same path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


# Usage example
from src.utils.paths import get_model_dir, ensure_dir_exists

model_path = ensure_dir_exists(get_model_dir()) / 'discount_model.pkl'
```

## Logging Setup

### Consistent Logging Configuration
```python
"""Logging configuration for the project."""
import logging
import sys
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    log_file: str = None
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('airline_discount_ml')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Usage in training script
from src.utils.logging import setup_logging

logger = setup_logging(level='INFO', log_file='logs/training.log')
logger.info("Starting training pipeline...")
```

## Constants and Enums

### Project Constants
```python
"""Project-wide constants."""
from enum import Enum


# Feature schema (read-only)
REQUIRED_FEATURES = [
    'distance_km',
    'history_trips', 
    'avg_spend',
    'route_id',
    'origin',
    'destination'
]

# Determinism
RANDOM_STATE = 42

# Database schema
class TableName(Enum):
    """Database table names."""
    PASSENGERS = 'passengers'
    ROUTES = 'routes'
    DISCOUNTS = 'discounts'


class ColumnName(Enum):
    """Common column names."""
    PASSENGER_ID = 'passenger_id'
    ROUTE_ID = 'route_id'
    DISCOUNT_PCT = 'discount_pct'
    DISTANCE_KM = 'distance_km'


# Usage
from src.utils.constants import TableName, REQUIRED_FEATURES

query = f"SELECT * FROM {TableName.PASSENGERS.value}"
```

## Validation Helpers

### Generic Validation Functions
```python
"""Common validation utilities."""
import pandas as pd
from typing import List


def validate_dataframe_columns(
    df: pd.DataFrame,
    required_columns: List[str],
    context: str = "DataFrame"
) -> None:
    """
    Validate DataFrame has required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        context: Description for error messages
    
    Raises:
        ValueError: If columns missing
    """
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"{context} missing required columns: {missing}. "
            f"Expected: {required_columns}"
        )


def validate_positive_numeric(
    value: float,
    name: str,
    min_value: float = 0.0
) -> None:
    """
    Validate numeric value is positive.
    
    Args:
        value: Value to validate
        name: Variable name for error messages
        min_value: Minimum allowed value (default: 0.0)
    
    Raises:
        ValueError: If value invalid
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric, got {type(value)}")
    
    if value <= min_value:
        raise ValueError(f"{name} must be > {min_value}, got {value}")


# Usage in models layer
from src.utils.validation import validate_dataframe_columns
from src.utils.config import config

def fit(self, X, y):
    validate_dataframe_columns(X, config.REQUIRED_FEATURES, "Training data")
    # ... rest of fit logic
```

## Testing Utils

### Test Fixtures and Helpers
```python
"""Testing utilities (not for production code)."""
import pandas as pd
import numpy as np
from typing import Tuple


def generate_sample_data(n_samples: int = 100) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Generate synthetic training data for tests.
    
    Args:
        n_samples: Number of samples to generate
    
    Returns:
        X, y tuple (features, target)
    """
    np.random.seed(42)
    
    X = pd.DataFrame({
        'distance_km': np.random.uniform(1000, 6000, n_samples),
        'history_trips': np.random.randint(1, 50, n_samples),
        'avg_spend': np.random.uniform(100, 2000, n_samples),
        'route_id': np.random.choice(['R1', 'R2', 'R3'], n_samples),
        'origin': np.random.choice(['NYC', 'LAX', 'SFO'], n_samples),
        'destination': np.random.choice(['LON', 'TYO', 'PAR'], n_samples),
    })
    
    # Linear target with noise
    y = (
        0.002 * X['distance_km'] 
        + 0.3 * X['history_trips']
        + 0.005 * X['avg_spend']
        + np.random.normal(0, 2, n_samples)
    )
    y = pd.Series(y, name='discount_pct')
    
    return X, y


# Usage in tests
from src.utils.testing import generate_sample_data

def test_model_fit():
    X, y = generate_sample_data(n_samples=50)
    model = DiscountPredictor()
    model.fit(X, y)
    # ... assertions
```

## Formatting Utilities

### String/Number Formatting
```python
"""Formatting utilities for output."""


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage.
    
    Args:
        value: Numeric value (0-100 scale)
        decimals: Decimal places
    
    Returns:
        Formatted string like "12.34%"
    """
    return f"{value:.{decimals}f}%"


def format_metric(name: str, value: float, width: int = 20) -> str:
    """
    Format metric for console output.
    
    Args:
        name: Metric name
        value: Metric value
        width: Total width for alignment
    
    Returns:
        Formatted string like "MAE:           12.34"
    """
    return f"{name}:{value:>{width - len(name) - 1}.2f}"


# Usage in training script
from src.utils.formatting import format_percentage, format_metric

print(format_metric("MAE", mae))
print(format_metric("R² Score", r2))
```

## When to Add New Utils

### Decision Flowchart
```
Is it business logic?
  YES → src/agents/
  NO  ↓

Is it ML-related?
  YES → src/models/
  NO  ↓

Is it database-related?
  YES → src/data/
  NO  ↓

Is it used by multiple layers?
  YES → src/utils/ ✓
  NO  → Keep in originating module
```

### Examples
- ✅ Config loading → utils/config.py
- ✅ Path resolution → utils/paths.py
- ✅ Logging setup → utils/logging.py
- ❌ Feature scaling → models/ (ML preprocessing)
- ❌ SQL query building → data/ (database logic)
- ❌ Discount calculation → agents/ (business logic)

## Common Pitfalls

### ❌ Utils becoming a dumping ground
```python
# BAD - ML logic in utils
def scale_features(X):
    return StandardScaler().fit_transform(X)  # Belongs in models/
```

### ❌ Utils with layer dependencies
```python
# BAD - utils importing from layers creates circular dependencies
from src.models.discount_predictor import DiscountPredictor
```

### ✅ Correct: Keep utils minimal and generic
```python
# GOOD - generic helper
def ensure_dir_exists(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
```

## Testing Requirements

### Test Coverage
```python
# tests/utils/test_config.py
def test_config_loads_defaults():
    """Test Config uses defaults when env vars not set."""
    assert config.RANDOM_STATE == 42
    assert config.TEST_SIZE == 0.2

def test_config_respects_env_vars(monkeypatch):
    """Test Config reads from environment."""
    monkeypatch.setenv('RANDOM_STATE', '99')
    # Reload config...
    assert config.RANDOM_STATE == 99
```

## Summary Checklist

Utils modules must:
- ✅ Be truly generic (usable by multiple layers)
- ✅ Have no dependencies on data/models/agents layers
- ✅ Provide configuration and constants
- ✅ Include comprehensive docstrings
- ✅ Have tests in `tests/utils/`
- ❌ Never contain business logic
- ❌ Never contain ML algorithms
- ❌ Never contain SQL queries
- ❌ Never become a catch-all for random functions
