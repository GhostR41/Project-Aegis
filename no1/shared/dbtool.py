import json
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import text


def seed_reference_data(session) -> None:
    # Seed known agents
    agents = [
        ("Agent 1", "Intelligence Officer"),
        ("Agent 2", "Strategic Planner"),
        ("Agent 3", "Safety Validator")
    ]
    for name, role in agents:
        session.execute(
            text("INSERT IGNORE INTO agent_ref (Agent_name, Agent_role) VALUES (:name, :role)"),
            {"name": name, "role": role}
        )

    # Seed known algorithms
    algorithms = [
        ("CUDA_PARALLEL", "Parallel", 256, 1000),
        ("Grovers Algorithm", "Quantum", 32, 100)
    ]
    for name, type_, blocks, iters in algorithms:
        session.execute(
            text(
                "INSERT IGNORE INTO algorithm_ref (Algorithm_name, Algorithm_type, Typical_CUDABlocks_used, Typical_Iterations) "
                "VALUES (:name, :type, :blocks, :iters)"
            ),
            {"name": name, "type": type_, "blocks": blocks, "iters": iters}
        )
    session.commit()

def _get_agent_ref_id(session, agent_name: str) -> int:
    result = session.execute(
        text("SELECT Agent_ref_id FROM agent_ref WHERE Agent_name LIKE :name"),
        {"name": f"{agent_name}%"}
    ).first()
    if not result:
        raise ValueError(f"Unknown agent: {agent_name}. Ensure seed_reference_data() was run.")
    return result[0]

def _get_algorithm_id(session, algo_name: str) -> int:
    result = session.execute(
        text("SELECT Algorithm_id FROM algorithm_ref WHERE Algorithm_name = :name"),
        {"name": algo_name}
    ).first()
    if not result:
        raise ValueError(f"Unknown algorithm: {algo_name}. Ensure seed_reference_data() was run.")
    return result[0]


def _jsonify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str, ensure_ascii=False)


def _state_text(state: Dict[str, Any]) -> str:
    return _jsonify(state)


def _now_sql() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "pass", "approved"}
    return False


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _resolve_asteroid_id(session, payload: Dict[str, Any], fallback_name: str = "Unknown Asteroid") -> int:
    asteroid_id = _to_int(payload.get("asteroid_id") or payload.get("Asteroid_id") or payload.get("id"), 0)
    if asteroid_id > 0:
        exists = session.execute(
            text("SELECT Asteroid_id FROM asteroid WHERE Asteroid_id = :asteroid_id"),
            {"asteroid_id": asteroid_id},
        ).first()
        if exists:
            return asteroid_id

    diameter_km = _to_float(payload.get("Diameter_km") or payload.get("diameter_km"), 0.0)
    if diameter_km <= 0.0:
        diameter_m = _to_float(payload.get("diameter_m") or payload.get("diameter"), 0.0)
        diameter_km = diameter_m / 1000.0 if diameter_m > 0 else 1.0

    mass_kg = _to_float(payload.get("Mass_kg") or payload.get("mass_kg") or payload.get("mass"), 1.0)
    velocity_km_s = _to_float(payload.get("Velocity_km_s") or payload.get("velocity_km_s") or payload.get("velocity"), 1.0)

    result = session.execute(
        text(
            """
            INSERT INTO asteroid
                (Name, Diameter_km, Mass_kg, Velocity_km_s, Composition, Detection_source, Detection_date)
            VALUES
                (:name, :diameter_km, :mass_kg, :velocity_km_s, :composition, :detection_source, :detection_date)
            """
        ),
        {
            "name": payload.get("Name") or payload.get("name") or payload.get("asteroid_name") or fallback_name,
            "diameter_km": max(diameter_km, 0.0001),
            "mass_kg": max(mass_kg, 1.0),
            "velocity_km_s": max(velocity_km_s, 0.0001),
            "composition": payload.get("Composition") or payload.get("composition") or "unknown",
            "detection_source": payload.get("Detection_source") or payload.get("detection_source") or "agent_1",
            "detection_date": _now_sql(),
        },
    )
    return _to_int(result.lastrowid, 0)


def _create_strategy(session, asteroid_id: int, method: str, status: str = "Proposed") -> int:
    agent_ref_id = _get_agent_ref_id(session, "Agent 2")
    result = session.execute(
        text(
            """
            INSERT INTO deflection_strategy
                (Asteroid_id, Method, Created_by_agent, Statusof, Created_at, Agent_ref_id)
            VALUES
                (:asteroid_id, :method, :created_by_agent, :statusof, :created_at, :agent_ref_id)
            """
        ),
        {
            "asteroid_id": asteroid_id,
            "method": method or "kinetic",
            "created_by_agent": "Agent_2",
            "statusof": status,
            "created_at": _now_sql(),
            "agent_ref_id": agent_ref_id,
        },
    )
    return _to_int(result.lastrowid, 0)


def ensure_asteroid(session, payload: Dict[str, Any], fallback_name: str = "Unknown Asteroid") -> int:
    return _resolve_asteroid_id(session, payload, fallback_name=fallback_name)


def ensure_strategy(session, asteroid_id: int, method: str = "kinetic", status: str = "Proposed") -> int:
    return _create_strategy(session, asteroid_id, method=method, status=status)


def _create_simulation(session, strategy_id: int, sim_data: Dict[str, Any]) -> int:
    generation_number = _to_int(sim_data.get("generation_id") or sim_data.get("generation_number"), 1)
    delta_v = _to_float(sim_data.get("Delta_v") or sim_data.get("delta_v") or sim_data.get("delta_v_ms") or sim_data.get("delta_v_m_s"), 0.0)
    miss_distance = _to_float(sim_data.get("Miss_distance_km") or sim_data.get("miss_distance_km") or sim_data.get("deflection_distance_km"), 0.0)
    fuel_cost = _to_float(sim_data.get("Fuel_cost") or sim_data.get("fuel_cost"), 0.0)
    if fuel_cost <= 0.0:
        fuel_cost = _to_float(sim_data.get("energy_deposited_j"), 0.0) / 1_000_000_000.0

    success = _to_bool(sim_data.get("Success") or sim_data.get("is_selected"))
    if not success and str(sim_data.get("status") or "").upper() == "PASS":
        success = True

    result = session.execute(
        text(
            """
            INSERT INTO simulation_run
                (Strategy_id, Impact_angle_deg, Delta_v, Execution_time, Miss_distance_km, Fuel_cost, Success, Simulated_at)
            VALUES
                (:strategy_id, :impact_angle_deg, :delta_v, :execution_time, :miss_distance_km, :fuel_cost, :success, :simulated_at)
            """
        ),
        {
            "strategy_id": strategy_id,
            "impact_angle_deg": _to_float(sim_data.get("impact_angle_deg"), 0.0),
            "delta_v": delta_v,
            "execution_time": _to_float(sim_data.get("execution_time") or sim_data.get("execution_time_days"), float(generation_number)),
            "miss_distance_km": miss_distance,
            "fuel_cost": max(fuel_cost, 0.0),
            "success": success,
            "simulated_at": _now_sql(),
        },
    )
    return _to_int(result.lastrowid, 0)


def log_generation(session, sim_data: Dict[str, Any]) -> None:
    strategy_id = _to_int(sim_data.get("strategy_id") or sim_data.get("Strategy_id"), 0)
    if strategy_id <= 0:
        asteroid_id = _resolve_asteroid_id(session, _as_dict(sim_data), fallback_name="Simulation Asteroid")
        strategy_id = _create_strategy(
            session,
            asteroid_id,
            method=str(sim_data.get("strategy_type") or sim_data.get("strategy") or "kinetic"),
        )

    simulation_id = _create_simulation(session, strategy_id, sim_data)

    generation_number = _to_int(sim_data.get("generation_id") or sim_data.get("generation_number"), 1)
    selected_flag = _to_bool(sim_data.get("is_selected"))
    optimal_probability = _to_float(sim_data.get("optimal_probability"), 1.0 if selected_flag else 0.5)

    algorithm_name = sim_data.get("algorithm_name") or sim_data.get("algorithm_used") or "CUDA_PARALLEL"
    algorithm_id = _get_algorithm_id(session, algorithm_name)

    session.execute(
        text(
            """
            INSERT INTO cuda_optimization_result
                (Simulation_id, Algorithms, Qubits_used, Iterations, Optimal_probability, CUDA_advantage, Optimized_at, Algorithm_id)
            VALUES
                (:simulation_id, :algorithms, :qubits_used, :iterations, :optimal_probability, :cuda_advantage, :optimized_at, :algorithm_id)
            """
        ),
        {
            "simulation_id": simulation_id,
            "algorithms": algorithm_name,
            "qubits_used": _to_int(sim_data.get("qubits_used"), 32),
            "iterations": max(generation_number, 1),
            "optimal_probability": _clamp(optimal_probability, 0.0, 1.0),
            "cuda_advantage": _to_float(sim_data.get("speedup_factor") or sim_data.get("cuda_advantage"), 1.0),
            "optimized_at": _now_sql(),
            "algorithm_id": algorithm_id,
        },
    )

    session.commit()


def log_safety_evaluation(session, safety_data: Dict[str, Any]) -> None:
    simulation_id = _to_int(safety_data.get("simulation_id") or safety_data.get("Simulation_id"), 0)
    if simulation_id <= 0:
        asteroid_id = _resolve_asteroid_id(session, _as_dict(safety_data), fallback_name="Safety Evaluation Asteroid")
        strategy_id = _create_strategy(session, asteroid_id, method="safety_validation")
        simulation_id = _create_simulation(session, strategy_id, safety_data)

    confidence = _to_float(safety_data.get("confidence_score") or safety_data.get("safety_score"), 0.0)
    debris_risk = _to_float(safety_data.get("debris_risk"), 1.0 - _clamp(confidence, 0.0, 1.0))
    fragmentation_risk = _to_float(safety_data.get("fragmentation_risk_pct") or safety_data.get("fragmentation_risk"), 0.0)
    if fragmentation_risk > 1.0:
        fragmentation_risk = fragmentation_risk / 100.0

    agent_ref_id = _get_agent_ref_id(session, "Agent 3")
    session.execute(
        text(
            """
            INSERT INTO safety_evaluation
                (Simulation_id, Fragmentation_risk, Debris_risk, Approved, Evaluated_by_agent, Evaluated_at, Agent_ref_id)
            VALUES
                (:simulation_id, :fragmentation_risk, :debris_risk, :approved, :evaluated_by_agent, :evaluated_at, :agent_ref_id)
            """
        ),
        {
            "simulation_id": simulation_id,
            "fragmentation_risk": _clamp(fragmentation_risk, 0.0, 1.0),
            "debris_risk": _clamp(debris_risk, 0.0, 1.0),
            "approved": _to_bool(safety_data.get("is_approved") or safety_data.get("approved") or safety_data.get("verdict") == "APPROVE"),
            "evaluated_by_agent": safety_data.get("evaluated_by_agent") or "Agent_3",
            "evaluated_at": _now_sql(),
            "agent_ref_id": agent_ref_id,
        },
    )
    session.commit()


def log_mission_run(session, state: Dict[str, Any]) -> Dict[str, Any]:
    a1_data = _as_dict(state.get("a1_data"))
    a2_plan = _as_dict(state.get("a2_plan"))
    a3_verdict = _as_dict(state.get("a3_verdict"))

    approval_flag = bool(a3_verdict and "APPROVE" in _state_text(a3_verdict).upper())
    decision_status = "APPROVED" if approval_flag else "ESCALATED"

    asteroid_id = _to_int(state.get("asteroid_id"), 0)
    if asteroid_id > 0:
        exists = session.execute(
            text("SELECT Asteroid_id FROM asteroid WHERE Asteroid_id = :asteroid_id"),
            {"asteroid_id": asteroid_id},
        ).first()
        if not exists:
            asteroid_id = 0
    if asteroid_id <= 0:
        asteroid_id = _resolve_asteroid_id(session, a1_data, fallback_name="Agent 1 Asteroid")

    impact_probability = _to_float(a1_data.get("impact_probability"), _to_float(a1_data.get("risk_score"), 0.0) / 10.0)
    risk_score = _to_float(a1_data.get("risk_score"), 0.0)
    time_to_impact_days = _to_int(a1_data.get("days_until_approach") or a1_data.get("time_to_impact_days"), 0)
    estimated_damage = str(a1_data.get("estimated_damage") or a1_data.get("threat_level") or "UNKNOWN")

    session.execute(
        text(
            """
            INSERT INTO risk_assessment
                (Asteroid_id, Impact_probability, Estimated_damage, Time_to_impact_days, Risk_score, Alert_triggered, Assessed_at)
            VALUES
                (:asteroid_id, :impact_probability, :estimated_damage, :time_to_impact_days, :risk_score, :alert_triggered, :assessed_at)
            """
        ),
        {
            "asteroid_id": asteroid_id,
            "impact_probability": _clamp(impact_probability, 0.0, 1.0),
            "estimated_damage": estimated_damage,
            "time_to_impact_days": max(time_to_impact_days, 0),
            "risk_score": _clamp(risk_score, 0.0, 10.0),
            "alert_triggered": _to_bool(a1_data.get("urgency") in {"HIGH", "CRITICAL"} or risk_score >= 7.0),
            "assessed_at": _now_sql(),
        },
    )

    strategy_id = _to_int(state.get("strategy_id"), 0)
    if strategy_id > 0:
        strategy_exists = session.execute(
            text("SELECT Strategy_id FROM deflection_strategy WHERE Strategy_id = :strategy_id"),
            {"strategy_id": strategy_id},
        ).first()
        if strategy_exists:
            session.execute(
                text(
                    """
                    UPDATE deflection_strategy
                    SET Statusof = :statusof
                    WHERE Strategy_id = :strategy_id
                    """
                ),
                {
                    "strategy_id": strategy_id,
                    "statusof": "Approved" if approval_flag else "Proposed",
                },
            )
        else:
            strategy_id = 0

    if strategy_id <= 0:
        strategy_id = _create_strategy(
            session,
            asteroid_id,
            method=str(a2_plan.get("strategy_type") or a2_plan.get("method") or "kinetic"),
            status="Approved" if approval_flag else "Proposed",
        )

    retry_count = 0
    while retry_count < 3:
        try:
            session.execute(text("SAVEPOINT after_strategy"))

            selected_candidate = _as_dict(a2_plan.get("selected_candidate"))
            simulation_id = _create_simulation(session, strategy_id, selected_candidate)

            confidence_score = _to_float(a3_verdict.get("safety_score") or a3_verdict.get("confidence_score"), 0.0)
            frag_risk = _to_float(a3_verdict.get("fragmentation_risk_pct"), 0.0)
            if frag_risk > 1.0:
                frag_risk = frag_risk / 100.0
            session.execute(
                text(
                    """
                    INSERT INTO safety_evaluation
                        (Simulation_id, Fragmentation_risk, Debris_risk, Approved, Evaluated_by_agent, Evaluated_at)
                    VALUES
                        (:simulation_id, :fragmentation_risk, :debris_risk, :approved, :evaluated_by_agent, :evaluated_at)
                    """
                ),
                {
                    "simulation_id": simulation_id,
                    "fragmentation_risk": _clamp(frag_risk, 0.0, 1.0),
                    "debris_risk": _clamp(1.0 - _clamp(confidence_score, 0.0, 1.0), 0.0, 1.0),
                    "approved": approval_flag,
                    "evaluated_by_agent": "Agent_3",
                    "evaluated_at": _now_sql(),
                },
            )

            session.execute(
                text(
                    """
                    INSERT INTO final_decision
                        (Asteroid_id, Chosen_strategy_id, Confidence_score, Explanation, Approved_by_human, Decided_at)
                    VALUES
                        (:asteroid_id, :chosen_strategy_id, :confidence_score, :explanation, :approved_by_human, :decided_at)
                    """
                ),
                {
                    "asteroid_id": asteroid_id,
                    "chosen_strategy_id": strategy_id,
                    "confidence_score": _clamp(confidence_score, 0.0, 1.0),
                    "explanation": _state_text(a3_verdict),
                    "approved_by_human": approval_flag,
                    "decided_at": _now_sql(),
                },
            )

            session.execute(
                text(
                    """
                    INSERT INTO agent_log
                        (Agent_name, Actions, Related_id, Related_table, Logged_at)
                    VALUES
                        (:agent_name, :actions, :related_id, :related_table, :logged_at)
                    """
                ),
                {
                    "agent_name": "Strategic Planner",
                    "actions": _state_text(
                        {
                            "session_id": state.get("session_id"),
                            "decision_status": decision_status,
                            "a1_data": a1_data,
                            "a2_plan": a2_plan,
                            "a3_verdict": a3_verdict,
                        }
                    ),
                    "related_id": strategy_id,
                    "related_table": "deflection_strategy",
                    "logged_at": _now_sql(),
                },
            )

            session.execute(text("RELEASE SAVEPOINT after_strategy"))
            session.commit()
            return {
                "transaction_status": "COMMITTED",
                "decision_status": decision_status,
                "asteroid_id": asteroid_id,
                "strategy_id": strategy_id,
            }
        except Exception:
            session.execute(text("ROLLBACK TO SAVEPOINT after_strategy"))
            retry_count += 1
            if retry_count >= 3:
                session.rollback()
                raise

    session.rollback()
    raise RuntimeError("Mission logging failed after retries")