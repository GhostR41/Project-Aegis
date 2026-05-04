import os
import json
import asyncio
import uuid
from typing import Any
from litellm import completion
from .tools import generate_simulation_space, calculate_deflection_parameters

def get_policy() -> str:
    policy_path = os.path.join(os.path.dirname(__file__), "agent2_policy.md")
    if not os.path.exists(policy_path):
        return "You are Agent 2, the Strategic Planner."
    with open(policy_path, "r") as f:
        return f.read()

async def handle_agent2_planning(asteroid_data_json: str) -> str:
    """
    Takes the structured output from Agent 1 and asks Agent 2 to generate a mission plan.
    """
    instructions = get_policy()

    tool_map = {
        "generate_simulation_space": generate_simulation_space,
        "calculate_deflection_parameters": calculate_deflection_parameters,
    }

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_simulation_space",
                "description": "Generate candidate deflection mission trajectories. Returns a file path to the generated candidates JSON.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_type": {"type": "string", "description": "Either 'kinetic' or 'gravity'"},
                        "min_velocity": {"type": "number", "description": "Minimum impact speed in km/s"},
                        "max_velocity": {"type": "number", "description": "Maximum impact speed in km/s"},
                        "min_angle": {"type": "number", "description": "Minimum approach angle in degrees"},
                        "max_angle": {"type": "number", "description": "Maximum approach angle in degrees"},
                        "sample_size": {"type": "integer", "description": "Number of candidates to generate (default 16)"}
                    },
                    "required": ["strategy_type", "min_velocity", "max_velocity", "min_angle", "max_angle"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_deflection_parameters",
                "description": "Calculate required delta-v and deflection angle for an asteroid.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asteroid_mass_kg": {"type": "number", "description": "Mass of the asteroid in kg"},
                        "days_until_impact": {"type": "integer", "description": "Days until predicted impact"},
                        "safety_margin_km": {"type": "number", "description": "Required deflection distance in km (default 12742)"}
                    },
                    "required": ["asteroid_mass_kg", "days_until_impact"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": (
            f"Asteroid Data (from Threat Assessment):\n{asteroid_data_json}\n\n"
            "PROCEDURE:\n"
            "1. Call calculate_deflection_parameters with the asteroid's mass and days_until_approach.\n"
            "2. Call generate_simulation_space with strategy_type='kinetic', reasonable velocity and angle ranges.\n"
            "3. Synthesize the results into a final mission plan with the following structure. Do NOT return raw JSON. Instead, return a formatted markdown report:\n"
            "   - Threat Assessment: Summarize the provided Asteroid Data (paragraph + table), and its Danger Classification.\n"
            "   - Deflection Plan Generation: Display all 16 calculated plans in a tabular form. Then point out the best one amongst it and show it in the form of a paragraph and a list.\n"
            "   - Physics Calculations: Show the physics formulas used and the step-by-step calculations made for the best plan.\n"
            "   - Scientific Justification: Support the final outcome with the help of physics laws and the calculations from the previous step.\n"
            "   - User Advisory: Explicitly advise the user to go through the final plan and not to follow the AI recommendations blindly."
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
            print(f"  [Agent 2] Tool call round {current_round}")
            messages.append(choice)
            for tool_call in choice["tool_calls"]:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"  [Agent 2] Calling {func_name}({args})")
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
        
        output = choice.content or "Agent 2 produced no output."
        print(f"  [Agent 2] Final output: {len(output)} chars")
        return output
    except Exception as e:
        error_msg = f"Error in Agent 2: {str(e)}"
        print(f"  [Agent 2] ERROR: {error_msg}")
        return error_msg
