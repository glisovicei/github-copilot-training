---
applyTo: "airline-discount-ml/src/mcp*/**/*.py"
---

# MCP Server Instructions

## Purpose
Model Context Protocol (MCP) servers expose tools and functionality to LLM agents like GitHub Copilot. These servers act as **bridges** between the LLM and your application logic.

## MCP Server Structure

### FastAPI-Based MCP Server Pattern
```python
"""
MCP server for airline discount ML operations.

Exposes model training, prediction, and data management as MCP tools.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from . import __version__

app = FastAPI(title="Airline Discount MCP Server", version=__version__)


# Health check
@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# Version endpoint
@app.get("/version")
def version():
    return {"version": __version__}


# MCP JSON-RPC endpoint (main interface)
@app.post("/mcp")
async def mcp(request: Request):
    """
    Handle MCP JSON-RPC requests.
    
    Supported methods:
    - initialize: Setup handshake
    - tools/list: List available tools
    - tools/call: Execute a tool
    """
    try:
        payload = await request.json()
    except Exception:
        return mcp_err(None, -32700, "Parse error")
    
    method = payload.get("method")
    rpc_id = payload.get("id")
    
    if method == "initialize":
        return mcp_ok(rpc_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "airline-discount-mcp",
                "version": __version__
            }
        })
    
    if method == "tools/list":
        return mcp_ok(rpc_id, {"tools": TOOLS})
    
    if method == "tools/call":
        return handle_tool_call(payload, rpc_id)
    
    return mcp_err(rpc_id, -32601, f"Unknown method: {method}")
```

## Tool Definition Pattern

### JSON Schema for Tool Parameters
```python
# Define tool schemas following JSON Schema Draft 7
TRAIN_MODEL_SCHEMA = {
    "type": "object",
    "properties": {
        "output_path": {
            "type": "string",
            "description": "Path to save trained model",
            "default": "models/discount_model.pkl"
        },
        "test_size": {
            "type": "number",
            "description": "Test set proportion (0.0-1.0)",
            "minimum": 0.1,
            "maximum": 0.5,
            "default": 0.2
        }
    },
    "required": []  # All params optional (have defaults)
}

PREDICT_DISCOUNT_SCHEMA = {
    "type": "object",
    "properties": {
        "distance_km": {
            "type": "number",
            "description": "Route distance in kilometers",
            "minimum": 0
        },
        "history_trips": {
            "type": "integer",
            "description": "Number of past trips",
            "minimum": 0
        },
        "avg_spend": {
            "type": "number",
            "description": "Average spending per trip",
            "minimum": 0
        },
        "route_id": {
            "type": "string",
            "description": "Route identifier"
        },
        "origin": {
            "type": "string",
            "description": "Departure airport code"
        },
        "destination": {
            "type": "string",
            "description": "Arrival airport code"
        }
    },
    "required": ["distance_km", "history_trips", "avg_spend", 
                 "route_id", "origin", "destination"]
}

# Tools list for MCP
TOOLS = [
    {
        "name": "train_model",
        "description": "Train discount prediction model from database",
        "inputSchema": TRAIN_MODEL_SCHEMA
    },
    {
        "name": "predict_discount",
        "description": "Predict discount for passenger/route combination",
        "inputSchema": PREDICT_DISCOUNT_SCHEMA
    }
]
```

## Request/Response Models

### Pydantic Models for Type Safety
```python
from pydantic import BaseModel, Field


class TrainModelRequest(BaseModel):
    """Request to train model."""
    output_path: str = Field(
        default="models/discount_model.pkl",
        description="Path to save trained model"
    )
    test_size: float = Field(
        default=0.2,
        ge=0.1,
        le=0.5,
        description="Test set proportion"
    )


class TrainModelResponse(BaseModel):
    """Response from training."""
    success: bool
    model_path: str
    metrics: Dict[str, float]
    message: str


class PredictDiscountRequest(BaseModel):
    """Request to predict discount."""
    distance_km: float = Field(ge=0, description="Route distance")
    history_trips: int = Field(ge=0, description="Past trips count")
    avg_spend: float = Field(ge=0, description="Average spending")
    route_id: str
    origin: str
    destination: str


class PredictDiscountResponse(BaseModel):
    """Response from prediction."""
    discount_pct: float
    confidence: str
    message: str
```

## Tool Implementation Pattern

### Delegate to Application Layers
```python
def handle_tool_call(payload: dict, rpc_id: Any):
    """Route tool calls to implementation functions."""
    params = payload.get("params", {})
    tool_name = params.get("name")
    args = params.get("arguments", {})
    
    try:
        if tool_name == "train_model":
            req = TrainModelRequest(**args)
            resp = train_model(req)
            return mcp_ok(rpc_id, {
                "content": [
                    {"type": "text", "text": format_training_result(resp)},
                    {"type": "json", "data": resp.model_dump()}
                ]
            })
        
        elif tool_name == "predict_discount":
            req = PredictDiscountRequest(**args)
            resp = predict_discount(req)
            return mcp_ok(rpc_id, {
                "content": [
                    {"type": "text", "text": format_prediction_result(resp)},
                    {"type": "json", "data": resp.model_dump()}
                ]
            })
        
        else:
            return mcp_err(rpc_id, -32601, f"Unknown tool: {tool_name}")
    
    except Exception as e:
        return mcp_err(rpc_id, -32000, f"Tool execution failed: {e}")


def train_model(req: TrainModelRequest) -> TrainModelResponse:
    """
    Train model using agents layer.
    
    Delegates to agents layer, which orchestrates data + models.
    """
    from src.agents.discount_agent import DiscountAgent
    
    agent = DiscountAgent()
    metrics = agent.train_new_model(output_path=req.output_path)
    
    return TrainModelResponse(
        success=True,
        model_path=metrics['model_path'],
        metrics={
            'mae': metrics['mae'],
            'r2_score': metrics['r2_score']
        },
        message=f"Model trained successfully with MAE={metrics['mae']:.2f}"
    )


def predict_discount(req: PredictDiscountRequest) -> PredictDiscountResponse:
    """Predict discount using agents layer."""
    from src.agents.discount_agent import DiscountAgent
    
    agent = DiscountAgent()
    result = agent.predict_discount(req.model_dump())
    
    return PredictDiscountResponse(
        discount_pct=result['discount_pct'],
        confidence='high',
        message=f"Predicted discount: {result['discount_pct']:.2f}%"
    )
```

## Response Formatting

### User-Friendly Text + Machine-Readable JSON
```python
def format_training_result(resp: TrainModelResponse) -> str:
    """Format training result for LLM display."""
    return f"""✅ Model Training Complete

📁 Model saved to: {resp.model_path}

📊 Performance Metrics:
  • MAE:  {resp.metrics['mae']:.2f}%
  • R²:   {resp.metrics['r2_score']:.4f}

{resp.message}
"""


def format_prediction_result(resp: PredictDiscountResponse) -> str:
    """Format prediction result for LLM display."""
    return f"""🎯 Discount Prediction

Predicted discount: {resp.discount_pct:.2f}%
Confidence: {resp.confidence}

{resp.message}
"""
```

## Error Handling

### MCP Error Response Pattern
```python
def mcp_ok(id_: Any, result: Any) -> Dict[str, Any]:
    """Success response."""
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def mcp_err(id_: Any, code: int, message: str) -> Dict[str, Any]:
    """Error response."""
    return {
        "jsonrpc": "2.0",
        "id": id_,
        "error": {"code": code, "message": message}
    }


# Error codes (JSON-RPC standard)
# -32700: Parse error (invalid JSON)
# -32600: Invalid request
# -32601: Method not found
# -32602: Invalid params
# -32603: Internal error
# -32000 to -32099: Server error

# Usage
try:
    result = some_operation()
    return mcp_ok(rpc_id, result)
except ValueError as e:
    return mcp_err(rpc_id, -32602, f"Invalid parameters: {e}")
except FileNotFoundError as e:
    return mcp_err(rpc_id, -32000, f"Resource not found: {e}")
except Exception as e:
    return mcp_err(rpc_id, -32603, f"Internal error: {e}")
```

## Security Considerations

### Input Validation
```python
def validate_file_path(path: str) -> None:
    """
    Validate file path to prevent directory traversal.
    
    Raises:
        ValueError: If path is unsafe
    """
    from pathlib import Path
    
    # Resolve to absolute path
    resolved = Path(path).resolve()
    
    # Check within allowed directories
    allowed_dirs = [
        Path("models").resolve(),
        Path("data").resolve(),
        Path("logs").resolve()
    ]
    
    if not any(str(resolved).startswith(str(d)) for d in allowed_dirs):
        raise ValueError(f"Access denied: {path} outside allowed directories")


# In tool implementation
def train_model(req: TrainModelRequest):
    validate_file_path(req.output_path)
    # ... rest of implementation
```

## Configuration

### VS Code MCP Integration
Create `.vscode/mcp.json` at repository root:

```json
{
  "mcpServers": {
    "airline-discount-ml": {
      "command": "uvicorn",
      "args": [
        "src.mcp.server:app",
        "--host", "127.0.0.1",
        "--port", "8010",
        "--reload"
      ],
      "cwd": "${workspaceFolder}/airline-discount-ml"
    }
  }
}
```

## Running the Server

### Development
```bash
cd airline-discount-ml
source venv/bin/activate
uvicorn src.mcp.server:app --host 127.0.0.1 --port 8010 --reload
```

### Testing
```bash
# Health check
curl http://127.0.0.1:8010/healthz

# List tools
curl -X POST http://127.0.0.1:8010/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Call tool
curl -X POST http://127.0.0.1:8010/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "predict_discount",
      "arguments": {
        "distance_km": 3000,
        "history_trips": 10,
        "avg_spend": 400,
        "route_id": "route_1",
        "origin": "NYC",
        "destination": "LAX"
      }
    }
  }'
```

## Common Pitfalls

### ❌ Implementing business logic in MCP layer
```python
# BAD - ML logic in MCP server
def predict_discount(req):
    X = pd.DataFrame([req.dict()])
    X_scaled = StandardScaler().fit_transform(X)  # Should be in models layer
    return model.predict(X_scaled)
```

### ❌ Not validating inputs
```python
# BAD - assumes valid input
def train_model(req):
    agent.train(req.output_path)  # No validation
```

### ✅ Correct: Delegate to layers, validate inputs
```python
def predict_discount(req: PredictDiscountRequest):
    # Validation done by Pydantic model
    # Delegate to agents layer
    agent = DiscountAgent()
    return agent.predict_discount(req.model_dump())
```

## Testing MCP Servers

### Unit Tests with TestClient
```python
from fastapi.testclient import TestClient
from src.mcp.server import app

client = TestClient(app)


def test_healthz():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tools_list():
    """Test tools listing."""
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tools" in data["result"]
    assert len(data["result"]["tools"]) > 0


def test_predict_discount_tool(monkeypatch):
    """Test discount prediction tool."""
    # Mock the agent
    class MockAgent:
        def predict_discount(self, data):
            return {"discount_pct": 12.5}
    
    monkeypatch.setattr(
        "src.mcp.server.DiscountAgent",
        MockAgent
    )
    
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "predict_discount",
            "arguments": {
                "distance_km": 3000,
                "history_trips": 10,
                "avg_spend": 400,
                "route_id": "route_1",
                "origin": "NYC",
                "destination": "LAX"
            }
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
```

## Summary Checklist

MCP servers must:
- ✅ Define tools with JSON Schema
- ✅ Use Pydantic for request/response validation
- ✅ Delegate to application layers (agents/models/data)
- ✅ Return both text and JSON in responses
- ✅ Handle errors gracefully with JSON-RPC error codes
- ✅ Validate file paths for security
- ✅ Have tests using FastAPI TestClient
- ❌ Never implement business logic directly
- ❌ Never contain ML algorithms
- ❌ Never access database directly (use data layer)
