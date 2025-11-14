---
applyTo: "airline-discount-ml/src/agents/**/*.py"
---

# Agents Layer Instructions

## Purpose
Business logic orchestration. Agents **coordinate** between data and models layers but contain no ML or database logic themselves.

## Critical Rules

### Layer Responsibilities
- ✅ **Can import:** `src.data.*`, `src.models.*`, `pandas`, standard library
- ✅ **Orchestrates:** Data loading → Model prediction → Result formatting
- ❌ **Never contains:** sklearn code, SQL queries, preprocessing logic
- ✅ **Returns:** Business-friendly data structures (dicts, lists, DataFrames)

### Single Responsibility
Each agent focuses on **one business workflow**. Don't mix concerns.

## Agent Pattern

### Standard Structure
```python
from src.data.database import get_training_data, get_connection
from src.models.discount_predictor import DiscountPredictor
import pandas as pd

class DiscountAgent:
    """Orchestrates discount prediction workflow."""
    
    def __init__(self, model_path: str = "models/discount_model.pkl"):
        """
        Initialize agent with trained model.
        
        Args:
            model_path: Path to serialized model file
        """
        self.model = DiscountPredictor.load(model_path)
    
    def predict_discount(self, passenger_data: dict) -> dict:
        """
        Predict discount for a passenger on a specific route.
        
        Args:
            passenger_data: Dict with keys 'distance_km', 'history_trips',
                          'avg_spend', 'route_id', 'origin', 'destination'
        
        Returns:
            Dict with 'discount_pct' and 'confidence' keys
        
        Example:
            >>> agent = DiscountAgent()
            >>> result = agent.predict_discount({
            ...     'distance_km': 3459.0,
            ...     'history_trips': 25,
            ...     'avg_spend': 450.0,
            ...     'route_id': 'route_123',
            ...     'origin': 'NYC',
            ...     'destination': 'LAX'
            ... })
            >>> result['discount_pct']
            12.5
        """
        # Convert dict to DataFrame (model expects DataFrame)
        X = pd.DataFrame([passenger_data])
        
        # Delegate prediction to model layer
        prediction = self.model.predict(X)
        
        # Format result for business use
        return {
            'discount_pct': round(float(prediction.iloc[0]), 2),
            'confidence': 'high'  # Placeholder for future logic
        }
```

## Workflow Patterns

### Pattern 1: Single Prediction
```python
def predict_for_passenger(self, passenger_id: int, route_id: int) -> dict:
    """Predict discount for specific passenger/route combination."""
    # Step 1: Fetch data (delegates to data layer)
    conn = get_connection()
    query = f"""
    SELECT 
        r.distance_km,
        p.travel_history as history_trips,
        p.avg_spend,
        r.id as route_id,
        r.origin,
        r.destination
    FROM passengers p
    CROSS JOIN routes r
    WHERE p.id = {passenger_id} AND r.id = {route_id}
    """
    X = pd.read_sql(query, conn)
    conn.close()
    
    # Step 2: Predict (delegates to models layer)
    discount = self.model.predict(X)
    
    # Step 3: Format result
    return {
        'passenger_id': passenger_id,
        'route_id': route_id,
        'discount_pct': float(discount.iloc[0])
    }
```

### Pattern 2: Batch Prediction
```python
def predict_batch(self, passenger_ids: list[int]) -> pd.DataFrame:
    """Predict discounts for multiple passengers across all routes."""
    # Fetch all combinations
    conn = get_connection()
    ids_str = ','.join(map(str, passenger_ids))
    query = f"""
    SELECT 
        p.id as passenger_id,
        r.id as route_id,
        r.distance_km,
        p.travel_history as history_trips,
        p.avg_spend,
        r.origin,
        r.destination
    FROM passengers p
    CROSS JOIN routes r
    WHERE p.id IN ({ids_str})
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Predict for all rows
    X = df[['distance_km', 'history_trips', 'avg_spend', 
            'route_id', 'origin', 'destination']]
    predictions = self.model.predict(X)
    
    # Add predictions to result
    df['discount_pct'] = predictions.values
    return df[['passenger_id', 'route_id', 'discount_pct']]
```

### Pattern 3: Training Workflow
```python
def train_new_model(self, output_path: str = "models/discount_model.pkl") -> dict:
    """
    Train new model from current database state.
    
    Returns:
        Dict with training metrics
    """
    # Step 1: Load training data (data layer)
    X, y = get_training_data()
    
    # Step 2: Train model (models layer)
    model = DiscountPredictor()
    model.fit(X, y)
    
    # Step 3: Evaluate (models layer provides predictions)
    predictions = model.predict(X)
    from sklearn.metrics import mean_absolute_error, r2_score
    mae = mean_absolute_error(y, predictions)
    r2 = r2_score(y, predictions)
    
    # Step 4: Save model
    model.save(output_path)
    
    # Step 5: Return metrics
    return {
        'model_path': output_path,
        'training_samples': len(X),
        'mae': round(mae, 2),
        'r2_score': round(r2, 4)
    }
```

## Input Validation (Business Rules)

### Validate Business Constraints
```python
def predict_discount(self, passenger_data: dict) -> dict:
    # Validate business rules (not ML validation)
    if passenger_data.get('history_trips', 0) < 0:
        raise ValueError("history_trips cannot be negative")
    
    if passenger_data.get('distance_km', 0) <= 0:
        raise ValueError("distance_km must be positive")
    
    # Delegate to model (model validates ML requirements)
    X = pd.DataFrame([passenger_data])
    prediction = self.model.predict(X)
    
    return {'discount_pct': float(prediction.iloc[0])}
```

## Error Handling

### Wrap Layer Errors with Business Context
```python
def predict_for_passenger(self, passenger_id: int, route_id: int) -> dict:
    try:
        # Data layer call
        conn = get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty:
            raise ValueError(
                f"No data found for passenger {passenger_id} "
                f"and route {route_id}"
            )
        
        # Model layer call
        prediction = self.model.predict(df)
        
    except FileNotFoundError as e:
        raise RuntimeError(f"Model file not found. Train model first: {e}")
    except ValueError as e:
        raise ValueError(f"Prediction failed for business reason: {e}")
    
    return {'discount_pct': float(prediction.iloc[0])}
```

## Testing Requirements

### Test Structure
- **File:** `tests/agents/test_discount_agent.py`
- **Use mocks:** Mock data/model layers to isolate agent logic
- **Test workflows:** Focus on orchestration, not ML accuracy

### Example Tests
```python
@pytest.fixture
def mock_model(monkeypatch):
    """Mock model to isolate agent testing."""
    class MockPredictor:
        def predict(self, X):
            # Return deterministic predictions for testing
            return pd.Series([10.0] * len(X), index=X.index)
    
    def mock_load(path):
        return MockPredictor()
    
    monkeypatch.setattr(
        'src.models.discount_predictor.DiscountPredictor.load',
        mock_load
    )

def test_predict_discount_returns_dict(mock_model):
    """Test agent returns properly formatted dict."""
    agent = DiscountAgent()
    result = agent.predict_discount({
        'distance_km': 3000.0,
        'history_trips': 10,
        'avg_spend': 400.0,
        'route_id': 'route_1',
        'origin': 'NYC',
        'destination': 'LAX'
    })
    
    assert isinstance(result, dict)
    assert 'discount_pct' in result
    assert result['discount_pct'] == 10.0
```

## API Design (For External Use)

### REST-Friendly Methods
```python
def get_discount_recommendation(
    self,
    passenger_id: int,
    route_id: int
) -> dict:
    """
    REST endpoint-friendly method.
    
    Returns:
        {
            'passenger_id': int,
            'route_id': int,
            'discount_pct': float,
            'recommended': bool,
            'message': str
        }
    """
    prediction = self.predict_for_passenger(passenger_id, route_id)
    discount = prediction['discount_pct']
    
    return {
        **prediction,
        'recommended': discount >= 10.0,
        'message': f"Offer {discount}% discount" if discount >= 10.0 
                   else "No discount recommended"
    }
```

## Common Pitfalls

### ❌ Mixing ML logic in agent
```python
# BAD - preprocessing belongs in models layer
def predict_discount(self, data: dict):
    X = pd.DataFrame([data])
    X['distance_scaled'] = (X['distance_km'] - X['distance_km'].mean()) / X['distance_km'].std()
    return self.model.predict(X)
```

### ❌ Direct SQL in agent
```python
# BAD - SQL belongs in data layer
def predict(self, pid: int):
    conn = sqlite3.connect("data/airline_discount.db")
    df = pd.read_sql(f"SELECT * FROM passengers WHERE id={pid}", conn)
    # ...
```

### ❌ Not closing connections
```python
# BAD - connection leak
def predict(self):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    return self.model.predict(df)  # conn never closed
```

### ✅ Correct: Delegate to layers
```python
def predict_discount(self, passenger_data: dict) -> dict:
    # 1. Convert to model-expected format
    X = pd.DataFrame([passenger_data])
    
    # 2. Delegate to model layer
    prediction = self.model.predict(X)
    
    # 3. Format for business use
    return {'discount_pct': float(prediction.iloc[0])}
```

## Documentation Requirements

### Docstrings (Required)
```python
def predict_discount(self, passenger_data: dict) -> dict:
    """
    Predict discount percentage for a passenger/route combination.
    
    This method orchestrates the discount prediction workflow:
    1. Validates business rules
    2. Formats input for model layer
    3. Delegates prediction to trained model
    4. Returns business-friendly result
    
    Args:
        passenger_data: Dict containing:
            - distance_km (float): Route distance
            - history_trips (int): Number of past trips
            - avg_spend (float): Average spending per trip
            - route_id (str): Route identifier
            - origin (str): Departure airport code
            - destination (str): Arrival airport code
    
    Returns:
        Dict with keys:
            - discount_pct (float): Predicted discount (0-100)
            - confidence (str): Prediction confidence level
    
    Raises:
        ValueError: If passenger_data invalid or missing required keys
        RuntimeError: If model not loaded
    
    Example:
        >>> agent = DiscountAgent("models/discount_model.pkl")
        >>> result = agent.predict_discount({
        ...     'distance_km': 3459.0,
        ...     'history_trips': 25,
        ...     'avg_spend': 450.0,
        ...     'route_id': 'route_123',
        ...     'origin': 'NYC',
        ...     'destination': 'LAX'
        ... })
        >>> print(result)
        {'discount_pct': 12.5, 'confidence': 'high'}
    """
    pass
```

## Summary Checklist

Every agent must:
- ✅ Orchestrate between data and models layers
- ✅ Return business-friendly data structures
- ✅ Validate business rules (not ML validation)
- ✅ Close database connections properly
- ✅ Have comprehensive docstrings with examples
- ✅ Have tests with mocked dependencies
- ❌ Never contain sklearn preprocessing code
- ❌ Never write SQL queries (use data layer)
- ❌ Never implement ML algorithms