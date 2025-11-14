---
applyTo: "airline-discount-ml/notebooks/**/*.ipynb"
---

# Jupyter Notebook Instructions

## Purpose
Notebooks in this directory are for exploratory data analysis, experimentation, and teaching demonstrations. They should remain self-contained and reproducible.

## Sys.path Workaround Pattern

**Always add this to the first cell** (notebooks can't use editable install):

```python
import sys
from pathlib import Path

# Add project root to Python path for imports
sys.path.insert(0, str(Path().resolve().parent))

# Now imports work
from src.data.database import get_connection
from src.models.discount_predictor import DiscountPredictor
```

**Why needed:** Jupyter kernels don't respect `pip install -e .` editable installs, so we manually add the parent directory to `sys.path`.

## Kernel Selection

**Always use:** `"Python (airline-discount-ml)"` kernel (registered by `setup.sh`)

**If kernel missing:**
```bash
cd airline-discount-ml
source .venv/bin/activate  # or venv/bin/activate
python -m ipykernel install --user --name=airline-discount-ml --display-name="Python (airline-discount-ml)"
```

**Reload:** VS Code → Reload Window → Select kernel from picker

## Deterministic Results

**Seed all random number generators at the start:**

```python
import random
import numpy as np

# For reproducibility across notebook runs
random.seed(42)
np.random.seed(42)
```

**sklearn models:** Always set `random_state=42` on estimators

## Database Access Pattern

**Use context managers for connections:**

```python
from src.data.database import get_connection

with get_connection() as conn:
    df = pd.read_sql("SELECT * FROM passengers LIMIT 10", conn)
    # Connection automatically closed after block
```

**For multiple queries:**
```python
conn = get_connection()
try:
    passengers = pd.read_sql("SELECT * FROM passengers", conn)
    routes = pd.read_sql("SELECT * FROM routes", conn)
finally:
    conn.close()  # Always cleanup
```

## Model Loading Pattern

**Load trained models for inference:**

```python
from src.models.discount_predictor import DiscountPredictor

# Load pre-trained model
model = DiscountPredictor.load("../models/discount_model.pkl")

# Prepare input data
X_new = pd.DataFrame({
    'distance_km': [2500],
    'history_trips': [15],
    'avg_spend': [450.0],
    'route_id': ['route_123'],
    'origin': ['NYC'],
    'destination': ['LAX']
})

# Get predictions
discounts = model.predict(X_new)
```

**For training experiments:**
```python
from src.data.database import get_connection

# Load training data
conn = get_connection()
query = """
SELECT 
    p.id as passenger_id,
    r.distance_km,
    p.travel_history as history_trips,
    p.avg_spend,
    r.id as route_id,
    r.origin,
    r.destination,
    d.discount_pct
FROM passengers p
JOIN discounts d ON p.id = d.passenger_id
JOIN routes r ON d.route_id = r.id
"""
df = pd.read_sql(query, conn)
conn.close()

# Split features and target
X = df[['distance_km', 'history_trips', 'avg_spend', 'route_id', 'origin', 'destination']]
y = df['discount_pct']

# Train model
model = DiscountPredictor()
model.fit(X, y)
```

## Visualization Standards

**Use consistent style:**

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style once at top of notebook
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Standard figure size
fig, ax = plt.subplots(figsize=(10, 6))

# Always label axes and add title
ax.set_xlabel("Feature Name", fontsize=12)
ax.set_ylabel("Value", fontsize=12)
ax.set_title("Descriptive Title", fontsize=14)

plt.tight_layout()
plt.show()
```

## Code Organization

### Cell Order
1. **Setup cell:** Imports + sys.path + seeds
2. **Data loading:** Database queries or file reads
3. **EDA cells:** Exploration and visualization
4. **Model cells:** Training or inference
5. **Results cells:** Metrics, plots, conclusions

### Cell Size Guidelines
- **Keep cells small** (< 20 lines) for easy re-execution
- **One task per cell** (load data, train model, plot results)
- **Add markdown cells** between major sections

### Markdown Documentation

**Use markdown cells to explain:**
- Purpose of the analysis
- Hypotheses being tested
- Key findings from visualizations
- Model performance interpretations

**Example:**
```markdown
## Hypothesis: Distance Correlates with Discount

We expect longer routes to receive higher discounts to incentivize bookings.

**Analysis approach:**
1. Plot distance vs. discount_pct scatter
2. Calculate Pearson correlation
3. Fit linear regression for trend line
```

## Data Validation

**Always validate loaded data:**

```python
# Check for nulls
print(f"Null counts:\n{df.isnull().sum()}")

# Check data types
print(f"\nData types:\n{df.dtypes}")

# Basic statistics
print(f"\nSummary stats:\n{df.describe()}")

# Check for unexpected values
assert df['distance_km'].min() > 0, "Distance should be positive"
assert df['discount_pct'].between(0, 100).all(), "Discount should be 0-100%"
```

## Performance Considerations

### Limit Query Results
```python
# For exploration, limit rows
df = pd.read_sql("SELECT * FROM passengers LIMIT 100", conn)
```

### Cache Expensive Operations
```python
# Use variables to avoid re-running expensive cells
if 'trained_model' not in locals():
    trained_model = DiscountPredictor()
    trained_model.fit(X_train, y_train)
```

### Clear Output for Large Results
```python
from IPython.display import clear_output

for i in range(100):
    print(f"Processing {i}...")
    clear_output(wait=True)  # Prevents notebook bloat
```

## Common Pitfalls

### ❌ Forgetting sys.path
```python
# This fails
from src.data.database import get_connection  # ModuleNotFoundError
```

### ✅ Correct approach
```python
# First cell always
import sys
from pathlib import Path
sys.path.insert(0, str(Path().resolve().parent))

# Now works
from src.data.database import get_connection
```

### ❌ Hardcoded paths
```python
# Brittle - breaks on other machines
df = pd.read_csv("/home/username/data/file.csv")
```

### ✅ Relative paths
```python
# Portable - works everywhere
df = pd.read_csv("../data/synthetic_output/generated_data.json")
```

### ❌ Uncommitted database changes
```python
# Don't modify production database in notebooks
conn.execute("DROP TABLE passengers")  # NEVER DO THIS
```

### ✅ Use in-memory SQLite for experiments
```python
import sqlite3
temp_conn = sqlite3.connect(":memory:")
# Now safe to experiment
```

## Export Guidelines

### For Sharing
- **Clear all outputs** before committing: Cell → All Output → Clear
- **Restart & Run All** to verify reproducibility
- **Add markdown summary** at the end with key findings

### For Production
- **Extract reusable code to `src/`** (don't duplicate logic)
- **Notebook → script:** `jupyter nbconvert --to script notebook.ipynb`
- **Parameterize:** Use `papermill` for automated notebook execution

## Example Notebook Structure

```python
# ====================================
# Cell 1: Setup
# ====================================
import sys
from pathlib import Path
sys.path.insert(0, str(Path().resolve().parent))

import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

random.seed(42)
np.random.seed(42)

from src.data.database import get_connection
from src.models.discount_predictor import DiscountPredictor

# ====================================
# Cell 2: Load Data
# ====================================
conn = get_connection()
df = pd.read_sql("""
    SELECT p.*, r.distance_km, d.discount_pct
    FROM passengers p
    JOIN discounts d ON p.id = d.passenger_id
    JOIN routes r ON d.route_id = r.id
""", conn)
conn.close()

print(f"Loaded {len(df)} records")
df.head()

# ====================================
# Cell 3: EDA
# ====================================
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df['distance_km'], df['discount_pct'], alpha=0.5)
ax.set_xlabel("Distance (km)")
ax.set_ylabel("Discount (%)")
ax.set_title("Distance vs. Discount Relationship")
plt.show()

# ... more cells follow pattern ...
```

## Naming Conventions

**Notebook files:**
- `01_data_exploration.ipynb` - Number prefix for ordering
- `02_model_training.ipynb` - Descriptive verb + noun
- `03_discount_analysis.ipynb` - Use underscores, not spaces

**Variables in notebooks:**
- `df` - Main DataFrame (generic exploration)
- `df_passengers`, `df_routes` - Specific DataFrames
- `X_train`, `y_train` - ML training data
- `model`, `trained_model` - Model instances

## Testing in Notebooks

**Quick validation (not formal tests):**

```python
# Sanity checks after data loading
assert len(df) > 0, "DataFrame is empty"
assert 'distance_km' in df.columns, "Missing expected column"

# Model sanity check
predictions = model.predict(X_test)
assert len(predictions) == len(X_test), "Prediction length mismatch"
assert predictions.min() >= 0, "Negative discounts detected"
```

**For formal tests:** Move logic to `src/` and write pytest tests instead.

## Summary

**Every notebook should:**
- ✅ Start with sys.path workaround
- ✅ Use `"Python (airline-discount-ml)"` kernel
- ✅ Seed random number generators
- ✅ Close database connections
- ✅ Include markdown documentation
- ✅ Be reproducible via Restart & Run All
- ✅ Clear outputs before git commit

**Notebooks are for exploration, not production code.** Extract reusable logic to `src/` modules and write proper tests in `tests/`.
