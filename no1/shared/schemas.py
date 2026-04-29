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


class AsteroidRecord(BaseModel):
    asteroid_id: Optional[int] = None
    name: str
    diameter_m: float
    mass_kg: float
    velocity_km_s: float
    composition: str
    impact_probability: float
    days_until_approach: int


class RiskAssessmentRecord(BaseModel):
    session_id: str
    asteroid_payload: Dict[str, Any]
    threat_level: str
    urgency: str
    risk_score: float
    impact_analysis: Dict[str, Any]
    damage_radii: Dict[str, float]
    recommended_action: str


class DeflectionStrategyRecord(BaseModel):
    session_id: str
    strategy_type: str
    simulation_candidates_path: str
    selected_candidate: Optional[Dict[str, Any]] = None
    strategy_details: Dict[str, Any]


class SimulationRunRecord(BaseModel):
    generation_number: int
    strategy_type: str
    delta_v_ms: float
    miss_distance_km: float
    fragmentation_risk_pct: float
    energy_deposited_j: float
    status: str


class CUDAOptimizationResultRecord(BaseModel):
    generation_number: int
    qubits_used: int
    algorithm_used: str
    speedup_factor: float
    selected_flag: bool


class SafetyEvaluationRecord(BaseModel):
    session_id: Optional[str] = None
    fragmentation_risk_pct: float
    miss_distance_km: float
    confidence_score: float
    verdict: str
    rejection_reason: Optional[str] = None


class FinalDecisionRecord(BaseModel):
    session_id: str
    status: str
    approved: bool
    decision_reason: str


class AgentLogRecord(BaseModel):
    session_id: str
    agent_name: str
    agent_role: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    reasoning: str
    trace_json: str
