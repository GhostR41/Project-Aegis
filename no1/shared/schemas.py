from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AsteroidData(BaseModel):
    id: str = Field(..., description="Asteroid Identifier")
    name: str = Field(..., description="Full Name")
    diameter: float = Field(..., description="Diameter in meters")
    mass: float = Field(..., description="Mass in kg")
    velocity: float = Field(..., description="Velocity in km/s")
    composition: str = Field(..., description="E.g., stony, iron, carbonaceous")
    impact_probability: float = Field(..., description="Probability of impact 0.0-1.0")
    days_until_approach: int = Field(..., description="Days until closest approach or impact")

class ThreatAssessment(BaseModel):
    asteroid_name: str
    threat_level: str
    urgency: str
    risk_score: float
    impact_analysis: Dict[str, Any]
    damage_radii: Dict[str, float]
    recommended_action: str

class StrategyPlan(BaseModel):
    asteroid_data: AsteroidData
    threat_assessment: ThreatAssessment
    strategy_type: str = Field(..., description="e.g., kinetic, gravity")
    simulation_candidates_path: str = Field(..., description="Path to generated candidates")
    selected_candidate: Optional[Dict[str, Any]] = None

class SafetyValidation(BaseModel):
    safety_score: float
    recommendation: str # APPROVE or REJECT
    checks_passed: List[str]
    checks_failed: List[str]
    reasoning: str
    is_approved: bool
