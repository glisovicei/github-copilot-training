---
applyTo: "airline-discount-ml/src/data/**/*.py"
---

# Data Layer Instructions

## Purpose
The data layer is responsible for **all database operations**. It must return pandas DataFrames/Series and never contain ML logic.

## Critical Rules

### Layer Separation (Enforced)
- ✅ **Can import:** `pandas`, `sqlite3`, standard library
- ❌ **Cannot import:** `sklearn`, `src.models.*`, `src.agents.*`
- ✅ **Returns:** pandas DataFrames, Series, or Python primitives
- ❌ **Never:** sklearn objects, model instances, business logic

### Database Access Pattern
```python
# Always use context manager or explicit close
def get_training_data():
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

# OR with context manager
def get_training_data():
    with get_connection() as conn:
        return pd.read_sql(query, conn)
```

### Database Location
- **Path:** `data/airline_discount.db` (relative to project root)
- **Connection:** Always use `get_connection()` helper, never hardcoded paths
- **Initialization:** Via `init_database()` function

## Schema Contract

### Tables (SQLite)
```sql
CREATE TABLE passengers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    travel_history INTEGER,  -- Number of past trips
    avg_spend REAL           -- Average spending per trip
);

CREATE TABLE routes (
    id INTEGER PRIMARY KEY,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    distance_km REAL NOT NULL
);

CREATE TABLE discounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    passenger_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    discount_pct REAL NOT NULL,
    FOREIGN KEY (passenger_id) REFERENCES passengers(id),
    FOREIGN KEY (route_id) REFERENCES routes(id)
);
```

### Query Patterns
```python
# JOIN for training data
query = """
SELECT 
    p.travel_history as history_trips,
    p.avg_spend,
    r.distance_km,
    r.id as route_id,
    r.origin,
    r.destination,
    d.discount_pct
FROM passengers p
JOIN discounts d ON p.id = d.passenger_id
JOIN routes r ON d.route_id = r.id
"""

# NEVER include passenger_id as a feature (PII policy)
```

## Function Signatures

### Required Functions
```python
def get_connection(db_path: str = "data/airline_discount.db") -> sqlite3.Connection:
    """Return SQLite connection. Caller must close."""
    pass

def init_database(db_path: str = "data/airline_discount.db") -> None:
    """Create schema and insert sample data if needed."""
    pass

def get_training_data(db_path: str = "data/airline_discount.db") -> tuple[pd.DataFrame, pd.Series]:
    """
    Load training data from database.
    
    Returns:
        X: Features DataFrame with columns ['distance_km', 'history_trips', 
           'avg_spend', 'route_id', 'origin', 'destination']
        y: Target Series with discount percentages
    """
    pass
```

### Data Validation (In Data Layer)
```python
def get_training_data(...):
    # Validate before returning
    if df.empty:
        raise ValueError("No training data found in database")
    
    required_cols = ['distance_km', 'history_trips', 'route_id']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return X, y
```

## No PII Policy

### ❌ Forbidden
```python
# NEVER return passenger_id as a feature
df = pd.read_sql("SELECT passenger_id, ...", conn)  # BAD
X = df[['passenger_id', 'distance_km']]  # BAD
```

### ✅ Allowed
```python
# Use passenger_id only for SQL JOINs, exclude from returned DataFrame
query = """
SELECT 
    r.distance_km,
    p.travel_history,
    -- passenger_id excluded from SELECT
FROM passengers p
JOIN discounts d ON p.id = d.passenger_id
"""
```

## Testing Requirements

### Test Structure
- **File:** `tests/data/test_database.py`
- **Use:** In-memory SQLite (`:memory:`) for isolation
- **Fixture:** `temp_db` with cleanup via yield

### Test Coverage
```python
@pytest.fixture
def temp_db():
    db = Database(db_path=":memory:")
    init_database(db_path=":memory:")
    yield db
    if db.conn:
        db.conn.close()

def test_get_training_data_returns_dataframe(temp_db):
    X, y = get_training_data(db_path=":memory:")
    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)
    assert len(X) == len(y)
```

## Error Handling

### Database Errors
```python
def get_connection(db_path: str) -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")
```

### Data Quality Checks
```python
def get_training_data():
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Check for data quality issues
    if df['discount_pct'].isnull().any():
        raise ValueError("Training data contains null discount values")
    
    if (df['distance_km'] <= 0).any():
        raise ValueError("Invalid distance values found (≤0)")
    
    return X, y
```

## Database Class Pattern

```python
class Database:
    """Manages SQLite connection with connection reuse."""
    
    def __init__(self, db_path: str = "data/airline_discount.db"):
        self.db_path = db_path
        self._conn = None
    
    def get_connection(self) -> sqlite3.Connection:
        """Get or create connection (reuses existing)."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn
    
    def close(self):
        """Close connection if open."""
        if self._conn:
            self._conn.close()
            self._conn = None
```

## Common Pitfalls

### ❌ Importing models layer
```python
from src.models.discount_predictor import DiscountPredictor  # FORBIDDEN
```

### ❌ ML logic in data layer
```python
# BAD - preprocessing belongs in models layer
def get_training_data():
    df = pd.read_sql(query, conn)
    df['distance_scaled'] = StandardScaler().fit_transform(df[['distance_km']])  # NO
    return df
```

### ❌ Leaking connections
```python
# BAD - connection never closed
def get_data():
    conn = get_connection()
    return pd.read_sql(query, conn)  # Leaks connection
```

### ✅ Correct patterns
```python
# Return raw data, let models layer handle preprocessing
def get_training_data():
    conn = get_connection()
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()
```

## Summary Checklist

Every data layer function must:
- ✅ Close database connections (use `try/finally` or context manager)
- ✅ Return pandas objects (DataFrame/Series) or primitives
- ✅ Validate data quality before returning
- ✅ Exclude `passenger_id` from returned features
- ✅ Have corresponding tests in `tests/data/`
- ❌ Never import from `src.models` or `src.agents`
- ❌ Never contain sklearn/ML logic