from typing import Dict, Any

FRAGMENTATION_THRESHOLDS = {
    "metallic": 10_000_000, # Iron/Nickel cores
    "iron": 10_000_000,
    "stony-iron": 5_000_000,
    "stony": 1_500_000,    # L/LL Chondrites
    "rocky": 1_000_000,
    "carbonaceous": 500_000, # C-type asteroids
    "rubble pile": 100_000,  # Bennu / Ryugu / Dimorphos (Low density/porous)
    "rubble": 100_000,
    "icy": 50_000,
    "unknown": 1_000_000
}

MOMENTUM_BETA = 1.5

def calculate_fragmentation_risk(
    velocity_km_s: float,
    impactor_mass_kg: float,
    asteroid_mass_kg: float,
    asteroid_diameter_m: float,
    composition: str
) -> Dict[str, Any]:
    velocity_m_s = velocity_km_s * 1000
    impact_energy_joules = 0.5 * impactor_mass_kg * (velocity_m_s ** 2)
    specific_energy = impact_energy_joules / asteroid_mass_kg
    composition_key = composition.lower().strip()
    threshold = FRAGMENTATION_THRESHOLDS.get(composition_key, FRAGMENTATION_THRESHOLDS["unknown"])
    
    fragmentation_risk_pct = (specific_energy / threshold) * 100
    
    if fragmentation_risk_pct < 50:
        assessment, explanation = "LOW", "Energy well below limits."
    elif fragmentation_risk_pct < 80:
        assessment, explanation = "ACCEPTABLE", "Minor damage expected, no fragmentation."
    elif fragmentation_risk_pct < 100:
        assessment, explanation = "MARGINAL", "Approaching limits."
    else:
        assessment, explanation = "CRITICAL", "Asteroid will fragment!"
        
    return {
        "fragmentation_risk_pct": round(fragmentation_risk_pct, 2),
        "assessment": assessment,
        "explanation": explanation,
        "is_safe": fragmentation_risk_pct < 100
    }

def calculate_deflection_distance(
    velocity_km_s: float,
    impactor_mass_kg: float,
    asteroid_mass_kg: float,
    time_to_impact_days: int
) -> Dict[str, Any]:
    velocity_m_s = velocity_km_s * 1000
    momentum = impactor_mass_kg * velocity_m_s
    enhanced_momentum = momentum * MOMENTUM_BETA
    delta_v_m_s = enhanced_momentum / asteroid_mass_kg
    time_seconds = time_to_impact_days * 24 * 60 * 60
    ORBITAL_AMPLIFICATION = 1000
    deflection_m = delta_v_m_s * time_seconds * ORBITAL_AMPLIFICATION
    deflection_km = deflection_m / 1000
    
    if deflection_km > 20000:
        assessment = "EXCELLENT"
    elif deflection_km > 10000:
        assessment = "SUFFICIENT"
    elif deflection_km > 5000:
        assessment = "MARGINAL"
    else:
        assessment = "INSUFFICIENT"
        
    return {
        "deflection_distance_km": round(deflection_km, 2),
        "assessment": assessment,
        "is_sufficient": deflection_km >= 10000
    }

def evaluate_safety_score(
    fragmentation_risk_pct: float,
    deflection_distance_km: float,
    quantum_confidence: float
) -> Dict[str, Any]:
    checks_passed = []
    checks_failed = []
    
    if fragmentation_risk_pct < 100:
        checks_passed.append("FRAGMENTATION_SAFE")
    else:
        checks_failed.append("FRAGMENTATION_CRITICAL")
        
    if deflection_distance_km >= 10000:
        checks_passed.append("DEFLECTION_SUFFICIENT")
    else:
        checks_failed.append("DEFLECTION_INSUFFICIENT")
        
    if quantum_confidence >= 0.70:
        checks_passed.append("CONFIDENCE_HIGH")
    else:
        checks_failed.append("CONFIDENCE_LOW")
        
    safety_score = len(checks_passed) / (len(checks_passed) + len(checks_failed))
    
    recommendation = "APPROVE" if not checks_failed else "REJECT"
    rejection_reason = "" if not checks_failed else ", ".join(checks_failed)

    return {
        "safety_score": round(safety_score, 2),
        "recommendation": recommendation,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "is_approved": recommendation == "APPROVE"
        ,"rejection_reason": rejection_reason
    }
