#!/bin/bash
# Quick test script for Synth CLI with airline schema

set -e

echo "🧪 Testing Synth CLI with Airline Schema"
echo "========================================"
echo ""

# Check if synth is installed
if ! command -v synth &> /dev/null; then
    echo "❌ Synth is not installed. Install with:"
    echo "   curl -sSL https://getsynth.com/install | sh"
    exit 1
fi

echo "✅ Synth version: $(synth version)"
echo ""

# Create Synth models directory
MODELS_DIR="synth_models/airline_data"
if [ -d "synth_models" ]; then
    echo "🗑️  Cleaning existing models directory..."
    rm -rf synth_models
fi

mkdir -p "$MODELS_DIR"

echo "📝 Creating Synth schema for passengers..."
cat > "$MODELS_DIR/passengers.json" << 'EOF'
{
  "type": "array",
  "length": {
    "type": "number",
    "constant": 10
  },
  "content": {
    "type": "object",
    "id": {
      "type": "number",
      "subtype": "u64",
      "range": {
        "low": 1,
        "high": 100000,
        "step": 1
      }
    },
    "name": {
      "type": "string",
      "faker": {
        "generator": "name"
      }
    },
    "travel_history": {
      "type": "object",
      "trips": {
        "type": "number",
        "range": {
          "low": 0,
          "high": 50,
          "step": 1
        }
      },
      "total_spend": {
        "type": "number",
        "subtype": "f64",
        "range": {
          "low": 0.0,
          "high": 50000.0,
          "step": 0.01
        }
      }
    }
  }
}
EOF

echo "📝 Creating Synth schema for routes..."
cat > "$MODELS_DIR/routes.json" << 'EOF'
{
  "type": "array",
  "length": {
    "type": "number",
    "constant": 5
  },
  "content": {
    "type": "object",
    "id": {
      "type": "number",
      "subtype": "u64",
      "range": {
        "low": 1,
        "high": 10000,
        "step": 1
      }
    },
    "origin": {
      "type": "string",
      "pattern": "[A-Z]{3}"
    },
    "destination": {
      "type": "string",
      "pattern": "[A-Z]{3}"
    },
    "distance": {
      "type": "number",
      "subtype": "f64",
      "range": {
        "low": 100.0,
        "high": 5000.0,
        "step": 1.0
      }
    }
  }
}
EOF

echo "✅ Schemas created!"
echo ""

echo "🎲 Generating synthetic passengers data..."
synth generate synth_models/airline_data --collection passengers --size 10

echo ""
echo "✅ Generation successful!"
echo ""

echo "🎲 Generating synthetic routes data..."
synth generate synth_models/airline_data --collection routes --size 5

echo ""
echo "✅ All tests passed!"
echo ""
echo "📝 Next steps:"
echo "   1. Generate to files: synth generate synth_models/airline_data --to json://./output/ --size 100"
echo "   2. View output: cat output/passengers.json | jq '.'"
echo "   3. Edit schemas in: synth_models/airline_data/"
