---
applyTo: "airline-discount-ml/src/training/**/*.py"
---

# Training Scripts Instructions

## Purpose
Executable scripts for training ML models. These **orchestrate** the full training workflow from data loading to model serialization.

## Script Structure

### Standard Training Script Pattern
```python
#!/usr/bin/env python3
"""
Train discount prediction model from database.

Usage:
    python src/training/train.py [--output models/discount_model.pkl]
"""
import argparse
import sys
from pathlib import Path

# Add project root to path (for standalone execution)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.database import get_training_data
from src.models.discount_predictor import DiscountPredictor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


def main(output_path: str = "models/discount_model.pkl"):
    """
    Full training workflow.
    
    Steps:
        1. Load data from database (data layer)
        2. Split into train/test sets
        3. Train model (models layer)
        4. Evaluate on test set
        5. Save trained model
        6. Print metrics
    """
    print("=" * 60)
    print("Discount Predictor Training Pipeline")
    print("=" * 60)
    
    # Step 1: Load data
    print("\n[1/5] Loading training data from database...")
    X, y = get_training_data()
    print(f"  ✓ Loaded {len(X)} samples with {X.shape[1]} features")
    
    # Step 2: Split data
    print("\n[2/5] Splitting into train/test sets (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"  ✓ Train: {len(X_train)} samples")
    print(f"  ✓ Test:  {len(X_test)} samples")
    
    # Step 3: Train model
    print("\n[3/5] Training RandomForest model...")
    model = DiscountPredictor()
    model.fit(X_train, y_train)
    print("  ✓ Model trained successfully")
    
    # Step 4: Evaluate
    print("\n[4/5] Evaluating on test set...")
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"  ✓ MAE:  {mae:.2f}%")
    print(f"  ✓ R²:   {r2:.4f}")
    
    # Step 5: Save model
    print(f"\n[5/5] Saving model to {output_path}...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    model.save(output_path)
    print(f"  ✓ Model saved successfully")
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)
    
    return {
        'model_path': output_path,
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'mae': mae,
        'r2_score': r2
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train discount predictor")
    parser.add_argument(
        '--output',
        type=str,
        default='models/discount_model.pkl',
        help='Path to save trained model'
    )
    args = parser.parse_args()
    
    try:
        metrics = main(output_path=args.output)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Training failed: {e}", file=sys.stderr)
        sys.exit(1)
```

## Determinism (Critical)

### Always Set Seeds
```python
import random
import numpy as np

# At module level (before any ML operations)
random.seed(42)
np.random.seed(42)

# In train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Models already have random_state=42 from models layer
```

## CLI Arguments

### Standard Arguments Pattern
```python
parser = argparse.ArgumentParser(description="Train discount predictor")
parser.add_argument(
    '--output',
    type=str,
    default='models/discount_model.pkl',
    help='Path to save trained model (default: models/discount_model.pkl)'
)
parser.add_argument(
    '--test-size',
    type=float,
    default=0.2,
    help='Test set proportion (default: 0.2)'
)
parser.add_argument(
    '--db-path',
    type=str,
    default='data/airline_discount.db',
    help='Database path (default: data/airline_discount.db)'
)
args = parser.parse_args()
```

## Progress Reporting

### User-Friendly Output
```python
# Use clear section markers
print("=" * 60)
print("Step Description")
print("=" * 60)

# Show progress with checkmarks
print("  ✓ Subtask completed")
print("  ✗ Subtask failed")

# Display metrics clearly
print(f"  MAE:  {mae:>8.2f}%")
print(f"  R²:   {r2:>8.4f}")
```

## Error Handling

### Graceful Failures
```python
def main(output_path: str):
    try:
        X, y = get_training_data()
    except FileNotFoundError:
        print("❌ Database not found. Run 'make db-init' first.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Invalid data: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        model = DiscountPredictor()
        model.fit(X, y)
    except Exception as e:
        print(f"❌ Model training failed: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Save model...
    return metrics
```

## Validation Checks

### Pre-Training Validation
```python
def validate_data(X: pd.DataFrame, y: pd.Series) -> None:
    """Validate data before training."""
    # Check sufficient samples
    if len(X) < 10:
        raise ValueError(f"Insufficient data: {len(X)} samples (need ≥10)")
    
    # Check for nulls in target
    if y.isnull().any():
        raise ValueError("Target variable contains null values")
    
    # Check feature variance
    numeric_cols = ['distance_km', 'history_trips', 'avg_spend']
    for col in numeric_cols:
        if X[col].std() == 0:
            raise ValueError(f"Feature '{col}' has zero variance")
    
    print("  ✓ Data validation passed")

# In main()
print("\n[1/5] Loading and validating data...")
X, y = get_training_data()
validate_data(X, y)
```

## Baseline Comparison

### Always Compare to Baseline
```python
from sklearn.dummy import DummyRegressor

def evaluate_with_baseline(X_train, X_test, y_train, y_test, model):
    """Evaluate model against baseline."""
    # Baseline: always predict mean
    baseline = DummyRegressor(strategy='mean')
    baseline.fit(X_train, y_train)
    baseline_pred = baseline.predict(X_test)
    baseline_mae = mean_absolute_error(y_test, baseline_pred)
    
    # Actual model
    y_pred = model.predict(X_test)
    model_mae = mean_absolute_error(y_test, y_pred)
    
    improvement = ((baseline_mae - model_mae) / baseline_mae) * 100
    
    print(f"  Baseline MAE: {baseline_mae:.2f}%")
    print(f"  Model MAE:    {model_mae:.2f}%")
    print(f"  Improvement:  {improvement:.1f}%")
    
    if improvement < 10:
        print("  ⚠️  Warning: Model barely beats baseline")

# In main()
print("\n[4/5] Evaluating against baseline...")
evaluate_with_baseline(X_train, X_test, y_train, y_test, model)
```

## Model Metadata

### Save Training Info
```python
import json
from datetime import datetime

def save_metadata(output_path: str, metrics: dict):
    """Save training metadata alongside model."""
    metadata = {
        'trained_at': datetime.now().isoformat(),
        'model_type': 'RandomForestRegressor',
        'n_estimators': 100,
        'random_state': 42,
        **metrics
    }
    
    metadata_path = output_path.replace('.pkl', '_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"  ✓ Metadata saved to {metadata_path}")

# In main()
metrics = {
    'train_samples': len(X_train),
    'test_samples': len(X_test),
    'mae': float(mae),
    'r2_score': float(r2)
}
save_metadata(output_path, metrics)
```

## Common Pitfalls

### ❌ Forgetting seeds
```python
# BAD - non-deterministic splits
X_train, X_test = train_test_split(X, y, test_size=0.2)
```

### ❌ Silent failures
```python
# BAD - swallows errors
try:
    model.fit(X, y)
except:
    pass  # User never knows what failed
```

### ✅ Correct patterns
```python
# Deterministic
X_train, X_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Explicit error handling
except ValueError as e:
    print(f"❌ Data validation failed: {e}", file=sys.stderr)
    sys.exit(1)

# Clear progress
print("[1/5] Loading data...")
print("  ✓ Loaded 1000 samples")
```

## Summary Checklist

Every training script must:
- ✅ Set `random_state=42` everywhere (splits, models)
- ✅ Show clear progress with section markers
- ✅ Validate data before training
- ✅ Compare to baseline model
- ✅ Save model and metadata
- ✅ Handle errors gracefully with exit codes
- ✅ Work from command line with `python src/training/train.py`
- ❌ Never use hardcoded paths (use argparse defaults)
- ❌ Never silently fail (always print errors to stderr)
