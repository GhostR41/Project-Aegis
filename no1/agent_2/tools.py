import json
import math
import random
import os
from typing import Dict, Any

from shared import cuda_tool, dbtool, database

CANDIDATES_FILE = "candidates_generated.json"
DEFAULT_SAMPLE_SIZE = 16
LAST_CUDA_RESULTS = []
RUN_DB_CONTEXT = {"asteroid_id": 0, "strategy_id": 0, "asteroid_mass_kg": 0.0}


def set_db_context(asteroid_id: int = 0, strategy_id: int = 0, asteroid_mass_kg: float = 0.0) -> None:
    RUN_DB_CONTEXT["asteroid_id"] = int(asteroid_id or 0)
    RUN_DB_CONTEXT["strategy_id"] = int(strategy_id or 0)
    if asteroid_mass_kg > 0:
        RUN_DB_CONTEXT["asteroid_mass_kg"] = float(asteroid_mass_kg)

def calculate_deflection_parameters(
    asteroid_mass_kg: float,
    days_until_impact: int,
    safety_margin_km: float = 12742.0 # 2x Earth radius as default safety margin
) -> Dict[str, Any]:
    """
    Calculates the required change in velocity (delta-v) to safely deflect an asteroid.
    
    Args:
        asteroid_mass_kg: Mass of the asteroid in kg.
        days_until_impact: Time remaining until predicted impact.
        safety_margin_km: Required deflection distance (Default: 12742km).
        
    Returns:
        Dictionary with required delta-v and suggested deflection angle.
    """
    time_seconds = days_until_impact * 24 * 60 * 60
    
    # Simplified orbital deflection formula: delta_d = 3 * delta_v * t_lead
    # This is a common linear approximation for small displacements over time.
    required_delta_v = (safety_margin_km * 1000) / (3 * time_seconds)
    
    set_db_context(asteroid_mass_kg=asteroid_mass_kg)
    
    # suggesting an optimal thrust angle (usually perpendicular to the velocity vector for max orbit shift)
    suggested_angle = 90.0 
    
    return {
        "required_delta_v_ms": round(required_delta_v, 6),
        "suggested_angle_degrees": suggested_angle,
        "calculation_method": "Linear Orbital Period Approximation",
        "safety_margin_km": safety_margin_km
    }

def generate_simulation_space(

    strategy_type: str,
    min_velocity: float,
    max_velocity: float,
    min_angle: float,
    max_angle: float,
    sample_size: int = DEFAULT_SAMPLE_SIZE
) -> str:
    """
    Generates a list of potential deflection mission trajectories based on physical constraints.
    
    Args:
        strategy_type: "kinetic" or "gravity"
        min_velocity: Minimum impact speed (km/s)
        max_velocity: Maximum impact speed (km/s)
        min_angle: Minimum approach angle (degrees)
        max_angle: Maximum approach angle (degrees)
        sample_size: Number of candidates to generate (Default: 16)
        
    Returns:
        Path to the generated JSON file (candidates_generated.json)
    """
    candidates = []
    candidates_list = []

    for i in range(sample_size):
        velocity = random.uniform(min_velocity, max_velocity)
        angle = random.uniform(min_angle, max_angle)
        angle_radians = math.radians(angle)

        candidate = {
            "id": i,
            "strategy": strategy_type,
            "velocity_km_s": round(velocity, 2),
            "angle_degrees": round(angle, 2),
            "estimated_impact_energy_kt": round(0.5 * 1000 * (velocity * 1000) ** 2 / 4.184e12, 2)
        }
        candidates.append(candidate)
        impact_vel_ms = velocity * 1000.0
        impactor_mass = 500.0 + (i * 25.0)
        ast_mass = RUN_DB_CONTEXT.get("asteroid_mass_kg", 5.0e10)
        # Momentum conservation: m_ast * dv_ast = m_imp * v_imp
        asteroid_delta_v_ms = (impactor_mass * impact_vel_ms) / max(ast_mass, 1.0)

        candidates_list.append({
            "generation_id": i + 1,
            "strategy_type": strategy_type,
            "impact_velocity_ms": round(impact_vel_ms, 2),
            "delta_v_ms": round(asteroid_delta_v_ms, 6),
            "impact_direction": [round(math.cos(angle_radians), 6), round(math.sin(angle_radians), 6), 0.0],
            "impactor_mass_kg": round(impactor_mass, 2),
            "lead_time_years": round(1.0 + (i * 0.05), 2),
            "composition": "stony",
            "asteroid_id": RUN_DB_CONTEXT.get("asteroid_id", 0),
            "strategy_id": RUN_DB_CONTEXT.get("strategy_id", 0),
            "asteroid_mass_kg": ast_mass
        })

    global LAST_CUDA_RESULTS
    LAST_CUDA_RESULTS = cuda_tool.run_parallel_simulation(candidates_list)

    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", CANDIDATES_FILE)

    with open(output_path, "w") as f:
        json.dump(candidates, f, indent=2)

    return json.dumps(LAST_CUDA_RESULTS)
