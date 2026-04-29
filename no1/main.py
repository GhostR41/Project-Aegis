import json
import asyncio
import uuid
import os
from datetime import datetime
from typing import Dict, Any, Optional
from agent_1.agent import handle_agent1_routing
from agent_2.agent import handle_agent2_planning
from agent_2 import tools as agent2_tools
from agent_3.agent import handle_agent3_validation
from shared import dbtool, database
from dotenv import load_dotenv

load_dotenv()

# Support multiple API keys to avoid TPM rate limits
def set_agent_api_key(agent_num: int):
    """Set GROQ_API_KEY env var to agent-specific key if available, else use default."""
    key_var = f"GROQ_API_KEY_{agent_num}"
    if key_var in os.environ:
        os.environ["GROQ_API_KEY"] = os.environ[key_var]
        print(f"  [Orchestrator] Using {key_var} for Agent {agent_num}")
    elif agent_num > 1:
        # Fall back to default key
        os.environ["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY", "")
        print(f"  [Orchestrator] {key_var} not found, using default GROQ_API_KEY for Agent {agent_num}")

# Simple ephemeral state store for the demo
MISSION_STATE = {}

def extract_json(text: str) -> Dict[str, Any]:
    """Attempts to extract and parse JSON from a message string."""
    try:
        # Look for markdown code blocks
        if "```json" in text:
            content = text.split("```json")[1].split("```")[0].strip()
            return json.loads(content)
        # Try raw JSON
        return json.loads(text.strip())
    except:
        return {}


def format_plan_output(agent_1_data: Any, agent_2_data: Any, agent_3_data: Any, workflow_status: str) -> str:
    def normalize(value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=2)
        if value is None:
            return "N/A"
        return str(value)

    return (
        "ORCHESTRATION SUCCESS\n\n"
        f"WORKFLOW STATUS: {workflow_status}\n\n"
        f"[AGENT 1] THREAT DATA:\n{normalize(agent_1_data)}\n\n"
        f"[AGENT 2] STRATEGY:\n{normalize(agent_2_data)}\n\n"
        f"[AGENT 3] VALIDATION:\n{normalize(agent_3_data)}"
    )

async def process_request(mode: str, query: str, session_id: Optional[str] = None) -> dict:
    """
    Main orchestration loop for Project Aegis.
    """
    if not session_id:
        session_id = str(uuid.uuid4())
    started_at = datetime.utcnow().isoformat() + "Z"
    
    print(f"\n--- Aegis Orchestration (ID: {session_id}) ---")
    
    # Map frontend modes to backend logic
    api_mode = mode
    if mode == "assess": api_mode = "assess_threat"
    elif mode == "plan": api_mode = "generate_plan"

    if api_mode == "answer":
        res = await handle_agent1_routing(api_mode, query)
        output = res.get("response") or res.get("agent_1_result") or res.get("message") or "System error: Agent 1 failed to generate a response."
        return {"final_output": output, "session_id": session_id}
        
    elif api_mode == "assess_threat":
        res = await handle_agent1_routing(api_mode, query)
        output = res.get("agent_1_result") or res.get("response") or res.get("message") or "System error: Agent 1 failed to return threat data."
        return {
            "final_output": output,
            "session_id": session_id
        }
        
    elif api_mode == "generate_plan":
        # Phase 1
        print("-> Agent 1: Retrieving Data")
        a1_res = await handle_agent1_routing(api_mode, query)
        a1_raw = a1_res.get("agent_1_result")
        a1_data = extract_json(str(a1_raw)) or {"name": "Unknown", "raw": a1_raw}
        
        if a1_res.get("status") != "success" or not a1_raw:
            fallback_output = a1_raw or a1_res.get("message") or "System error: Agent 1 failed to return threat data."
            return {"final_output": fallback_output, "status": "error", "session_id": session_id}

        if "apologize" in str(a1_raw).lower() or "cannot assist" in str(a1_raw).lower():
            return {"final_output": a1_raw, "status": "refused", "session_id": session_id}

        asteroid_id = 0
        strategy_id = 0
        pre_db_gen = database.get_db()
        pre_db = next(pre_db_gen)
        try:
            asteroid_id = dbtool.ensure_asteroid(pre_db, a1_data, fallback_name="Agent 1 Asteroid")
            strategy_id = dbtool.ensure_strategy(pre_db, asteroid_id, method="kinetic", status="Proposed")
            pre_db.commit()
        except Exception as exc:
            pre_db.rollback()
            print(f"[Orchestrator] Pre-strategy initialization failed: {exc}")
        finally:
            pre_db.close()
            pre_db_gen.close()

        agent2_tools.set_db_context(asteroid_id=asteroid_id, strategy_id=strategy_id)

        # Phase 2
        print("-> Agent 2: Strategic Planning")
        print("  [Orchestrator] Waiting 15s before Agent 2 (TPM rate limit reset for shared organization)...")
        await asyncio.sleep(15)
        set_agent_api_key(2)
        a2_res = await handle_agent2_planning(str(a1_raw))
        cuda_results = getattr(agent2_tools, "LAST_CUDA_RESULTS", [])
        agent2_tools.set_db_context()

        # Phase 3
        print("-> Agent 3: Safety Validation")
        print("  [Orchestrator] Waiting 15s before Agent 3 (TPM rate limit reset for shared organization)...")
        await asyncio.sleep(15)
        set_agent_api_key(3)
        a3_res = await handle_agent3_validation(a2_res)
        ended_at = datetime.utcnow().isoformat() + "Z"

        # HITL Logic
        is_approved = "APPROVE" in str(a3_res)
        workflow_status = "AWAITING_HUMAN_APPROVAL" if is_approved else "MISSION_REJECTED"
        
        # Store for approval step
        MISSION_STATE[session_id] = {
            "session_id": session_id,
            "status": workflow_status,
            "asteroid_id": asteroid_id,
            "strategy_id": strategy_id,
            "a1_data": a1_data,
            "a2_plan": a2_res,
            "a3_verdict": a3_res,
            "cuda_results": cuda_results,
            "started_at": started_at,
            "ended_at": ended_at,
            "transaction_status": "PENDING"
        }

        transaction_status = "PENDING"
        db_session_generator = database.get_db()
        db_session = next(db_session_generator)
        try:
            dbtool.log_mission_run(db_session, MISSION_STATE[session_id])
            transaction_status = "COMMITTED"
        except Exception as exc:
            transaction_status = "ROLLED_BACK"
            print(f"[Orchestrator] Mission log rollback: {exc}")
        finally:
            db_session.close()
            db_session_generator.close()

        MISSION_STATE[session_id]["transaction_status"] = transaction_status

        return {
            "mode": mode,
            "status": "success",
            "workflow_status": workflow_status,
            "final_output": format_plan_output(a1_data, extract_json(a2_res) or a2_res, extract_json(a3_res) or a3_res, workflow_status),
            "agent_1_threat_data": a1_data,
            "agent_2_strategy": extract_json(a2_res) or a2_res,
            "agent_3_validation": extract_json(a3_res) or a3_res,
            "generations": cuda_results,
            "transaction_status": transaction_status,
            "session_id": session_id
        }
        
    elif api_mode == "approve_mission":
        state = MISSION_STATE.get(session_id)
        if state and state["status"] == "AWAITING_HUMAN_APPROVAL":
            state["status"] = "MISSION_EXECUTED"
            return {
                "status": "success",
                "workflow_status": "MISSION_EXECUTED",
                "message": "Orbital deflection sequence initiated. DART-class impactors deployed."
            }
        return {"status": "error", "message": "Mission not awaiting approval."}

    return {"status": "error", "message": "Mode not recognized"}

if __name__ == "__main__":
    pass
