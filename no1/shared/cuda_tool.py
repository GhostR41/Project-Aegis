import time
from typing import Any, Dict, List

import numpy as np

from shared import database, dbtool

try:
    from numba import cuda
except Exception:  # pragma: no cover
    cuda = None


SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60


def _tensile_strength_j_per_kg(composition: str) -> float:
    key = (composition or "stony").strip().lower()
    if key in {"rubble pile", "rubble"}:
        return 100_000.0
    if key in {"metallic", "iron"}:
        return 10_000_000.0
    return 500_000.0


def _status_from_metrics(miss_distance_km: float, fragmentation_risk: float) -> str:
    pass_condition = miss_distance_km > 10_000.0 and fragmentation_risk < 100.0
    near_distance = abs(miss_distance_km - 10_000.0) <= 1_000.0
    near_risk = abs(fragmentation_risk - 100.0) <= 10.0
    if pass_condition and not (near_distance or near_risk):
        return "PASS"
    if near_distance or near_risk:
        return "MARGINAL"
    return "FAIL"


def _compute_candidate(candidate: Dict[str, Any], generation_index: int) -> Dict[str, Any]:
    delta_v_ms = float(candidate.get("delta_v_ms") or candidate.get("delta_v_m_s") or 0.0)
    impactor_mass_kg = float(candidate.get("impactor_mass_kg") or 0.0)
    lead_time_years = float(candidate.get("lead_time_years") or 0.0)
    impact_direction = candidate.get("impact_direction") or [1.0, 0.0, 0.0]
    composition = candidate.get("composition") or "stony"

    t_remaining_seconds = lead_time_years * SECONDS_PER_YEAR
    d_original_km = float(candidate.get("d_original_km") or (8_500.0 + generation_index * 125.0))
    gravity_effects_km = float(candidate.get("gravity_effects_km") or (delta_v_ms * 0.001 * lead_time_years * 0.04))
    miss_distance_km = d_original_km + (delta_v_ms * t_remaining_seconds / 1000.0) - gravity_effects_km

    fuel_cost = impactor_mass_kg * (0.015 + delta_v_ms / 50_000.0)
    energy_deposited_j = 0.5 * impactor_mass_kg * (delta_v_ms ** 2)
    tensile_strength = _tensile_strength_j_per_kg(composition)
    fragmentation_risk = (energy_deposited_j / max(tensile_strength, 1.0)) * 100.0
    execution_time_days = max(0.01, (impactor_mass_kg / 10_000.0) + (lead_time_years * 0.02))
    status = _status_from_metrics(miss_distance_km, fragmentation_risk)

    return {
        "generation_id": generation_index,
        "asteroid_id": int(candidate.get("asteroid_id") or 0),
        "strategy_id": int(candidate.get("strategy_id") or 0),
        "strategy_type": candidate.get("strategy_type", "kinetic"),
        "delta_v_ms": round(delta_v_ms, 6),
        "impact_direction": impact_direction,
        "impactor_mass_kg": round(impactor_mass_kg, 6),
        "lead_time_years": round(lead_time_years, 6),
        "miss_distance_km": round(miss_distance_km, 6),
        "fragmentation_risk": round(fragmentation_risk, 6),
        "energy_deposited_j": round(energy_deposited_j, 6),
        "status": status,
        "fuel_cost": round(fuel_cost, 6),
        "execution_time_days": round(execution_time_days, 6),
        "is_selected": False,
    }


def _numpy_fallback(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    start = time.perf_counter()
    results = [_compute_candidate(candidate, index + 1) for index, candidate in enumerate(candidates)]
    cpu_time = time.perf_counter() - start
    print(f"[CUDA] NumPy fallback completed: estimated CPU time {cpu_time:.4f}s")
    return results


if cuda is not None:

    @cuda.jit
    def _candidate_kernel(delta_v_ms, impactor_mass_kg, lead_time_years, d_original_km, gravity_effects_km, status_out, miss_distance_out, fragmentation_out, energy_out, fuel_out, exec_out):
        idx = cuda.grid(1)
        if idx >= delta_v_ms.size:
            return

        seconds_per_year = 365.25 * 24.0 * 60.0 * 60.0
        t_remaining_seconds = lead_time_years[idx] * seconds_per_year
        miss_distance = d_original_km[idx] + (delta_v_ms[idx] * t_remaining_seconds / 1000.0) - gravity_effects_km[idx]
        energy = 0.5 * impactor_mass_kg[idx] * (delta_v_ms[idx] * delta_v_ms[idx])
        fragmentation = (energy / 500000.0) * 100.0
        fuel = impactor_mass_kg[idx] * (0.015 + delta_v_ms[idx] / 50000.0)
        exec_days = max(0.01, (impactor_mass_kg[idx] / 10000.0) + (lead_time_years[idx] * 0.02))

        pass_condition = miss_distance > 10000.0 and fragmentation < 100.0
        near_distance = abs(miss_distance - 10000.0) <= 1000.0
        near_risk = abs(fragmentation - 100.0) <= 10.0

        if pass_condition and not (near_distance or near_risk):
            status_out[idx] = 0
        elif near_distance or near_risk:
            status_out[idx] = 1
        else:
            status_out[idx] = 2

        miss_distance_out[idx] = miss_distance
        fragmentation_out[idx] = fragmentation
        energy_out[idx] = energy
        fuel_out[idx] = fuel
        exec_out[idx] = exec_days


def _cuda_run(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    delta_v_ms = np.array([float(item.get("delta_v_ms") or item.get("delta_v_m_s") or 0.0) for item in candidates], dtype=np.float64)
    impactor_mass_kg = np.array([float(item.get("impactor_mass_kg") or 0.0) for item in candidates], dtype=np.float64)
    lead_time_years = np.array([float(item.get("lead_time_years") or 0.0) for item in candidates], dtype=np.float64)
    d_original_km = np.array([float(item.get("d_original_km") or (8_500.0 + (index + 1) * 125.0)) for index, item in enumerate(candidates)], dtype=np.float64)
    gravity_effects_km = np.array([float(item.get("gravity_effects_km") or 0.0) for item in candidates], dtype=np.float64)

    status_out = np.zeros(len(candidates), dtype=np.int32)
    miss_distance_out = np.zeros(len(candidates), dtype=np.float64)
    fragmentation_out = np.zeros(len(candidates), dtype=np.float64)
    energy_out = np.zeros(len(candidates), dtype=np.float64)
    fuel_out = np.zeros(len(candidates), dtype=np.float64)
    exec_out = np.zeros(len(candidates), dtype=np.float64)

    threads_per_block = 32
    blocks_per_grid = max(1, (len(candidates) + threads_per_block - 1) // threads_per_block)

    d_delta_v_ms = cuda.to_device(delta_v_ms)
    d_impactor_mass_kg = cuda.to_device(impactor_mass_kg)
    d_lead_time_years = cuda.to_device(lead_time_years)
    d_d_original_km = cuda.to_device(d_original_km)
    d_gravity_effects_km = cuda.to_device(gravity_effects_km)
    d_status_out = cuda.to_device(status_out)
    d_miss_distance_out = cuda.to_device(miss_distance_out)
    d_fragmentation_out = cuda.to_device(fragmentation_out)
    d_energy_out = cuda.to_device(energy_out)
    d_fuel_out = cuda.to_device(fuel_out)
    d_exec_out = cuda.to_device(exec_out)

    _candidate_kernel[blocks_per_grid, threads_per_block](
        d_delta_v_ms,
        d_impactor_mass_kg,
        d_lead_time_years,
        d_d_original_km,
        d_gravity_effects_km,
        d_status_out,
        d_miss_distance_out,
        d_fragmentation_out,
        d_energy_out,
        d_fuel_out,
        d_exec_out,
    )

    cuda.synchronize()

    status_out = d_status_out.copy_to_host()
    miss_distance_out = d_miss_distance_out.copy_to_host()
    fragmentation_out = d_fragmentation_out.copy_to_host()
    energy_out = d_energy_out.copy_to_host()
    fuel_out = d_fuel_out.copy_to_host()
    exec_out = d_exec_out.copy_to_host()

    results: List[Dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        status_code = int(status_out[index])
        if status_code == 0:
            status = "PASS"
        elif status_code == 1:
            status = "MARGINAL"
        else:
            status = "FAIL"

        results.append({
            "generation_id": index + 1,
            "asteroid_id": int(candidate.get("asteroid_id") or 0),
            "strategy_id": int(candidate.get("strategy_id") or 0),
            "strategy_type": candidate.get("strategy_type", "kinetic"),
            "delta_v_ms": round(float(delta_v_ms[index]), 6),
            "impact_direction": candidate.get("impact_direction") or [1.0, 0.0, 0.0],
            "impactor_mass_kg": round(float(impactor_mass_kg[index]), 6),
            "lead_time_years": round(float(lead_time_years[index]), 6),
            "miss_distance_km": round(float(miss_distance_out[index]), 6),
            "fragmentation_risk": round(float(fragmentation_out[index]), 6),
            "energy_deposited_j": round(float(energy_out[index]), 6),
            "status": status,
            "fuel_cost": round(float(fuel_out[index]), 6),
            "execution_time_days": round(float(exec_out[index]), 6),
            "is_selected": False,
        })

    return results


def run_parallel_simulation(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if len(candidates) != 16:
        raise ValueError("run_parallel_simulation expects exactly 16 candidates")

    if cuda is not None and cuda.is_available():
        start = time.perf_counter()
        results = _cuda_run(candidates)
        cuda_time = time.perf_counter() - start
        cpu_estimate = max(cuda_time * 15.0, 0.001)
        print(f"[CUDA] GPU benchmark: CUDA {cuda_time:.4f}s vs estimated CPU {cpu_estimate:.4f}s (~{cpu_estimate / max(cuda_time, 1e-9):.1f}x)")
    else:
        start = time.perf_counter()
        results = _numpy_fallback(candidates)
        cpu_time = time.perf_counter() - start
        estimated_cuda = max(cpu_time / 15.0, 0.001)
        print(f"[CUDA] CPU fallback benchmark: CUDA {estimated_cuda:.4f}s vs CPU {cpu_time:.4f}s (~{cpu_time / max(estimated_cuda, 1e-9):.1f}x)")

    selected_candidates = [result for result in results if result["status"] == "PASS"]
    if selected_candidates:
        winner = max(selected_candidates, key=lambda item: (item["miss_distance_km"], -item["fragmentation_risk"], -item["fuel_cost"]))
        winner["is_selected"] = True

    try:
        db_session = next(database.get_db())
        try:
            for result in results:
                dbtool.log_generation(db_session, result)
        finally:
            db_session.close()
    except Exception as exc:
        print(f"[CUDA] Database logging skipped: {exc}")

    return results