from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError

from . import __version__

app = FastAPI(title="MCP Synth Server", version=__version__)

# -------------------------
# Health & version (unchanged)
# -------------------------

class HealthResponse(BaseModel):
    status: str

@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")

class VersionResponse(BaseModel):
    version: str

@app.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(version=__version__)

# -------------------------
# Tool: synth_generate (existing logic)
# -------------------------

class GenerateRequest(BaseModel):
    """Request to generate synthetic data via Synth CLI."""
    model_dir: str = Field(default="synth_models/airline_data", description="Path to Synth schemas")
    out_dir: str = Field(default="data/synthetic_output", description="Output directory")
    size: int = Field(default=5, ge=1, le=10000, description="Records per collection")
    seed: int = Field(default=42, description="Random seed for reproducibility")
    log_file: str = Field(default="", description="Optional path to save formatted log output")

class GenerateResponse(BaseModel):
    """Response from data generation."""
    success: bool
    message: str
    files_created: List[str]
    data: Dict[str, Any] = Field(default_factory=dict, description="Generated data preview")
    command: str = Field(description="Synth CLI command that was executed")

@app.post("/synth_generate", response_model=GenerateResponse)
def synth_generate(req: GenerateRequest) -> GenerateResponse:
    """Generate synthetic data using Synth CLI."""
    try:
        cmd = [
            "synth", "generate",
            req.model_dir,
            "--size", str(req.size),
            "--seed", str(req.seed),
        ]
        cmd_str = " ".join(cmd)
        # Run Synth
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Persist output as a single JSON file
        os.makedirs(req.out_dir, exist_ok=True)
        out_file = os.path.join(req.out_dir, "generated_data.json")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result.stdout)

        # Parse the generated data to include in response
        generated_data = json.loads(result.stdout)

        return GenerateResponse(
            success=True,
            message=f"Generated {req.size} records per collection",
            files_created=[out_file],
            data=generated_data,
            command=cmd_str,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Synth command failed: {e.stderr}") from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e


class InspectModelRequest(BaseModel):
    model_dir: str = Field(default="synth_models/airline_data", description="Path to Synth schemas")
    log_file: str = Field(default="", description="Optional path to save inspection output")

class InspectModelResponse(BaseModel):
    model_dir: str
    files: List[str]

def synth_inspect_model(req: InspectModelRequest) -> InspectModelResponse:
    p = Path(req.model_dir)
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=400, detail=f"Model dir not found: {p}")
    files = sorted([str(x) for x in p.glob("**/*") if x.is_file()])
    return InspectModelResponse(model_dir=str(p), files=files)

class PreviewHeadRequest(BaseModel):
    path: str = Field(
        default="data/synthetic_output/generated_data.json",
        description="Path to JSON/NDJSON/CSV file"
    )
    n: int = Field(default=10, ge=1, le=200, description="Number of rows to preview")
    log_file: str = Field(default="", description="Optional path to save preview output")

class PreviewHeadResponse(BaseModel):
    path: str
    rows: List[dict]

def preview_table_head(req: PreviewHeadRequest) -> PreviewHeadResponse:
    p = Path(req.path)
    
    # Security: prevent directory traversal and restrict to safe paths
    try:
        resolved = p.resolve()
        # Allow only data/ and synth_models/ directories (relative to project root)
        allowed_prefixes = [
            Path("data").resolve(),
            Path("synth_models").resolve(),
        ]
        if not any(str(resolved).startswith(str(prefix)) for prefix in allowed_prefixes):
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied: path must be under data/ or synth_models/"
            )
    except (OSError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {e}") from e
    
    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {resolved}")
    rows: List[dict] = []

    # Simple preview for JSON arrays or NDJSON; CSV fallback.
    try:
        text = resolved.read_text(encoding="utf-8")
        text_stripped = text.strip()
        if text_stripped.startswith("["):
            data = json.loads(text_stripped)
            if isinstance(data, list):
                rows = data[: req.n]
            else:
                rows = [data]
        elif "\n" in text_stripped and text_stripped.startswith("{"):
            # NDJSON
            lines = [ln for ln in text.splitlines() if ln.strip()]
            for ln in lines[: req.n]:
                rows.append(json.loads(ln))
        elif resolved.suffix.lower() == ".csv":
            import csv
            with resolved.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for i, rec in enumerate(reader):
                    if i >= req.n:
                        break
                    rows.append(rec)
        else:
            # Fallback: return first N lines as opaque text
            rows = [{"line": ln} for ln in text.splitlines()[: req.n]]
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Could not preview file: {e}") from e

    return PreviewHeadResponse(path=str(resolved), rows=rows)

# -------------------------
# MCP JSON-RPC endpoint
# -------------------------

# JSON Schemas for tool parameters (derived from Pydantic)
# Following JSON Schema Draft 7 specification for MCP compatibility
SYNTH_GENERATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "model_dir": {
            "type": "string", 
            "description": "Path to Synth schemas",
            "default": "synth_models/airline_data"
        },
        "out_dir": {
            "type": "string", 
            "description": "Output directory",
            "default": "data/synthetic_output"
        },
        "size": {
            "type": "integer",
            "description": "Records per collection",
            "minimum": 1, 
            "maximum": 10000,
            "default": 1000
        },
        "seed": {
            "type": "integer",
            "description": "Random seed for reproducibility",
            "default": 42
        },
        "log_file": {
            "type": "string", 
            "description": "Optional path to save formatted log output",
            "default": ""
        }
    },
    "required": []
}

SYNTH_INSPECT_MODEL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "model_dir": {
            "type": "string", 
            "description": "Path to Synth schemas"
        },
        "log_file": {
            "type": "string", 
            "description": "Optional path to save inspection output"
        }
    }
}

PREVIEW_TABLE_HEAD_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string", 
            "description": "Path to JSON/NDJSON/CSV file (default: data/synthetic_output/generated_data.json)"
        },
        "n": {
            "type": "integer",
            "description": "Number of rows to preview",
            "minimum": 1, 
            "maximum": 200
        },
        "log_file": {
            "type": "string", 
            "description": "Optional path to save preview output"
        }
    },
    "required": []
}

def mcp_ok(id_: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id_, "result": result}

def mcp_err(id_: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}

@app.post("/mcp")
async def mcp(request: Request):
    """
    Minimal MCP JSON-RPC endpoint supporting:
      - tools/list
      - tools/call
    """
    try:
        payload = await request.json()
    except Exception:
        return mcp_err(None, -32700, "Parse error")

    method = payload.get("method")
    rpc_id = payload.get("id")

    # Basic lifecycle methods used by some MCP clients
    if method == "initialize":
        # Return a minimal successful init response so clients don't error
        return mcp_ok(rpc_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "logging": {}
            },
            "serverInfo": {
                "name": "mcp-synth",
                "version": __version__
            }
        })

    if method == "shutdown":
        # Client requests server shutdown; acknowledge. We don't stop the process here.
        return mcp_ok(rpc_id, {"shutdown": True})

    if method == "tools/list":
        return mcp_ok(rpc_id, {
            "tools": [
                {
                    "name": "synth_generate",
                    "description": "Generate synthetic data via Synth CLI",
                    "inputSchema": SYNTH_GENERATE_SCHEMA,
                },
                {
                    "name": "synth_inspect_model",
                    "description": "List files under the Synth model directory",
                    "inputSchema": SYNTH_INSPECT_MODEL_SCHEMA,
                },
                {
                    "name": "preview_table_head",
                    "description": "Preview the first N rows of a generated file (JSON/NDJSON/CSV)",
                    "inputSchema": PREVIEW_TABLE_HEAD_SCHEMA,
                },
            ]
        })

    if method == "tools/call":
        params = payload.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}

        try:
            if name == "synth_generate":
                req = GenerateRequest(**args)
                resp = synth_generate(req)
                data = resp.model_dump()
                # Format output with generated data preview
                command_text = data.get("command", "(unknown)")
                text_output = (
                    f"🛠 Command: {command_text}\n\n"
                    f"✅ {data['message']}\n\n"
                    f"📁 Files created: {', '.join(data['files_created'])}\n\n"
                    f"📊 Generated Data:\n{json.dumps(data.get('data', {}), indent=2)}"
                )
                
                # Save formatted output to a log file
                if req.log_file:
                    log_file = Path(req.log_file)
                else:
                    log_dir = Path(req.out_dir)
                    log_file = log_dir / "generation_log.txt"
                
                log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(text_output)
                
                text_output += f"\n\n💾 Output also saved to: {log_file}"
                return mcp_ok(rpc_id, {"content": [
                    {"type": "text", "text": text_output},
                    {"type": "json", "data": data}
                ]})
            elif name == "synth_inspect_model":
                req = InspectModelRequest(**args)
                resp = synth_inspect_model(req)
                data = resp.model_dump()
                text_output = f"📂 Model directory: {data['model_dir']}\n\n📄 Files ({len(data['files'])}):\n" + "\n".join(f"  - {f}" for f in data['files'])
                
                # Save inspection output
                if req.log_file:
                    log_file = Path(req.log_file)
                else:
                    log_file = Path("data/synthetic_output/model_inspection.txt")
                
                log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(text_output)
                
                text_output += f"\n\n💾 Output also saved to: {log_file}"
                return mcp_ok(rpc_id, {"content": [
                    {"type": "text", "text": text_output},
                    {"type": "json", "data": data}
                ]})
            elif name == "preview_table_head":
                req = PreviewHeadRequest(**args)
                resp = preview_table_head(req)
                data = resp.model_dump()
                text_output = f"📄 Preview of {data['path']} (first {len(data['rows'])} rows):\n\n{json.dumps(data['rows'], indent=2)}"
                
                # Save preview output
                if req.log_file:
                    log_file = Path(req.log_file)
                else:
                    preview_path = Path(req.path)
                    log_file = preview_path.parent / f"{preview_path.stem}_preview.txt"
                
                log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(text_output)
                
                text_output += f"\n\n💾 Output also saved to: {log_file}"
                return mcp_ok(rpc_id, {"content": [
                    {"type": "text", "text": text_output},
                    {"type": "json", "data": data}
                ]})
            else:
                return mcp_err(rpc_id, -32601, f"Unknown tool: {name}")

            # MCP result payload: array of content items
            return mcp_ok(rpc_id, {"content": [{"type": "json", "data": data}]})

        except ValidationError as ve:
            return mcp_err(rpc_id, -32602, f"Invalid params: {ve}")
        except HTTPException as he:
            return mcp_err(rpc_id, he.status_code, he.detail)
        except Exception as e:  # noqa: BLE001
            return mcp_err(rpc_id, -32000, f"Server error: {e}")

    # Unknown method
    return mcp_err(rpc_id, -32601, f"Unknown method: {method}")
