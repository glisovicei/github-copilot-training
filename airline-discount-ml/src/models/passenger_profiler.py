"""
Passenger profiler: pure feature construction for discount modeling.
"""
from __future__ import annotations

import pandas as pd


REQUIRED_OUTPUT_COLUMNS = [
    "distance_km",
    "history_trips",
    "avg_spend",
    "route_id",
    "origin",
    "destination",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pure feature construction for discount modeling.

    Expects a tabular DataFrame with columns that can derive:
      - distance or distance_km
      - history_trips or trips_count
      - avg_spend or spend/total_spend + trips_count
      - route_id (optional if origin/destination present)
      - origin, destination

    Returns a DataFrame with REQUIRED_OUTPUT_COLUMNS only.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("Input must be a non-empty pandas DataFrame.")

    out = pd.DataFrame(index=df.index)

    # distance_km: prefer distance_km, else convert miles if 'distance' present
    if "distance_km" in df.columns:
        out["distance_km"] = df["distance_km"]
    elif "distance" in df.columns:
        out["distance_km"] = df["distance"] * 1.60934
    else:
        out["distance_km"] = pd.NA

    # history_trips: prefer provided, else derive from trips_count
    if "history_trips" in df.columns:
        out["history_trips"] = df["history_trips"]
    elif "trips_count" in df.columns:
        out["history_trips"] = df["trips_count"]
    else:
        out["history_trips"] = pd.NA

    # avg_spend: prefer provided, else derive from total_spend / history_trips
    if "avg_spend" in df.columns:
        out["avg_spend"] = df["avg_spend"]
    elif "total_spend" in df.columns and ("history_trips" in out.columns):
        with pd.option_context("mode.use_inf_as_na", True):
            out["avg_spend"] = df["total_spend"] / out["history_trips"]
    else:
        out["avg_spend"] = pd.NA

    # route_id, origin, destination
    out["route_id"] = df["route_id"] if "route_id" in df.columns else pd.NA
    out["origin"] = df["origin"] if "origin" in df.columns else pd.NA
    out["destination"] = df["destination"] if "destination" in df.columns else pd.NA

    # Keep only required columns in defined order
    out = out[REQUIRED_OUTPUT_COLUMNS]
    return out