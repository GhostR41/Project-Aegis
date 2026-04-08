import os
import json
import asyncio
import uuid
from typing import Dict, Any
from litellm import completion
from .tools import calculate_fragmentation_risk, calculate_deflection_distance, evaluate_safety_score

def get_policy() -> str:
    policy_path = os.path.join(os.path.dirname(__file__), "agent3_policy.md")
    if not os.path.exists(policy_path):
        return "You are Agent 3, the Safety Validator."
    with open(policy_path, "r") as f:
        return f.read()

async def handle_agent3_validation(mission_plan: str) -> str:
    """
    Takes the mission plan from Agent 2 and validates safety.
    """
    instructions = get_policy()

    tool_map = {
        "calculate_fragmentation_risk": calculate_fragmentation_risk,
        "calculate_deflection_distance": calculate_deflection_distance,
        "evaluate_safety_score": evaluate_safety_score
    }

    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate_fragmentation_risk",
                "description": "Assess the risk of asteroid fragmentation from kinetic impact.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "velocity_km_s": {"type": "number", "description": "Impact velocity in km/s"},
                        "impactor_mass_kg": {"type": "number", "description": "Mass of the impactor spacecraft in kg"},
                        "asteroid_mass_kg": {"type": "number", "description": "Mass of the asteroid in kg"},
                        "asteroid_diameter_m": {"type": "number", "description": "Diameter of the asteroid in meters"},
                        "composition": {"type": "string", "description": "Asteroid composition (e.g. 'stony', 'iron', 'carbonaceous', 'rubble pile')"}
                    },
                    "required": ["velocity_km_s", "impactor_mass_kg", "asteroid_mass_kg", "asteroid_diameter_m", "composition"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_deflection_distance",
                "description": "Calculate the deflection distance achieved by a kinetic impactor.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "velocity_km_s": {"type": "number", "description": "Impact velocity in km/s"},
                        "impactor_mass_kg": {"type": "number", "description": "Mass of the impactor spacecraft in kg"},
                        "asteroid_mass_kg": {"type": "number", "description": "Mass of the asteroid in kg"},
                        "time_to_impact_days": {"type": "integer", "description": "Days until the asteroid's predicted impact"}
                    },
                    "required": ["velocity_km_s", "impactor_mass_kg", "asteroid_mass_kg", "time_to_impact_days"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "evaluate_safety_score",
                "description": "Calculate the overall mission safety score based on fragmentation risk and deflection distance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fragmentation_risk_pct": {"type": "number", "description": "Fragmentation risk percentage from calculate_fragmentation_risk"},
                        "deflection_distance_km": {"type": "number", "description": "Deflection distance in km from calculate_deflection_distance"},
                        "quantum_confidence": {"type": "number", "description": "Confidence level (0 to 1), default 0.85"}
                    },
                    "required": ["fragmentation_risk_pct", "deflection_distance_km", "quantum_confidence"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": (
            f"Proposed Mission Plan:\n{mission_plan}\n\n"
            "PROCEDURE:\n"
            "1. Call calculate_fragmentation_risk to check if the impactor will fragment the asteroid.\n"
            "   Use typical impactor mass of 610 kg (DART-class) if not specified.\n"
            "2. Call calculate_deflection_distance to verify sufficient deflection.\n"
            "3. Call evaluate_safety_score with the two results and a confidence of 0.85.\n"
            "4. Return your final verdict as JSON with is_approved, safety_score, and rationale."
        )}
    ]

    try:
        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        choice = response.choices[0].message
        max_rounds = 5
        current_round = 0
        while choice.get("tool_calls") and current_round < max_rounds:
            current_round += 1
            print(f"  [Agent 3] Tool call round {current_round}")
            messages.append(choice)
            for tool_call in choice["tool_calls"]:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"  [Agent 3] Calling {func_name}({args})")
                if func_name in tool_map:
                    try:
                        result = tool_map[func_name](**args)
                    except Exception as tool_err:
                        result = {"error": f"Tool {func_name} failed: {str(tool_err)}"}
                    content = json.dumps(result) if not isinstance(result, str) else result
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": content})
                else:
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": f"Unknown tool: {func_name}"})

            next_res = completion(model="groq/llama-3.3-70b-versatile", messages=messages, tools=tools, tool_choice="auto")
            choice = next_res.choices[0].message

        output = choice.content or "Agent 3 produced no output."
        print(f"  [Agent 3] Final output: {len(output)} chars")
        return output
    except Exception as e:
        error_msg = f"Error in Agent 3: {str(e)}"
        print(f"  [Agent 3] ERROR: {error_msg}")
        return error_msg
