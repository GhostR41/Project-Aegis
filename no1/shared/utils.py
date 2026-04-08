import json
from typing import Dict, Any, Optional

def save_json(filepath: str, data: Any):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filepath: str) -> Any:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def standardize_asteroid_data(raw_data: dict) -> dict:
    """Normalizes scraped or retrieved data into standard Aegis format."""
    return {
        "id": raw_data.get("id", "UNKNOWN"),
        "name": raw_data.get("name", "Unknown Asteroid"),
        "diameter": float(raw_data.get("diameter", 0.0)),
        "mass": float(raw_data.get("mass", 0.0)),
        "velocity": float(raw_data.get("velocity", 0.0)),
        "composition": str(raw_data.get("composition", "unknown")),
        "impact_probability": float(raw_data.get("impact_probability", 0.0)),
        "days_until_approach": int(raw_data.get("days_until_approach", 0))
    }
