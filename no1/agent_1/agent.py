import os
import json
import asyncio
import uuid
from typing import Dict, Any, Tuple
from litellm import completion
from .tools import lookup_asteroid, search_web_for_asteroid, threat_calculator_tool, query_asteroid_database

def get_policy() -> str:
    policy_path = os.path.join(os.path.dirname(__file__), "agent1_policy.md")
    if not os.path.exists(policy_path):
        return "You are Agent 1, the Data Retrieval Specialist."
    with open(policy_path, "r") as f:
        return f.read()

def _try_tool_call(tool_map, tools, messages):
    """
    Attempt LLM-driven tool calling.
    Returns (output_str, success_bool).
    """
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
            print(f"  [Agent 1] Tool call round {current_round}")
            messages.append(choice)
            for tool_call in choice["tool_calls"]:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"  [Agent 1] Calling {func_name}({args})")
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

        output = choice.content
        if output:
            return output, True
        return None, False
    except Exception as e:
        print(f"  [Agent 1] Tool calling failed: {e}")
        return None, False


async def handle_agent1_routing(mode: str, query: str) -> Dict[str, Any]:
    """
    Handles data retrieval and routing for Agent 1.
    Uses a hybrid approach: tries LLM tool calling first,
    falls back to direct Python tool execution if Groq fails.
    """
    instructions = get_policy()

    tool_map = {
        "lookup_asteroid": lookup_asteroid,
        "query_asteroid_database": query_asteroid_database,
        "search_web_for_asteroid": search_web_for_asteroid,
        "threat_calculator_tool": threat_calculator_tool
    }

    tools = [
        {
            "type": "function",
            "function": {
                "name": "lookup_asteroid",
                "description": "Look up a specific asteroid by name in the local database.",
                "parameters": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_asteroid_database",
                "description": "Query the asteroid database for a specific property or keyword (e.g. '2025', 'iron', 'hazardous'). Use this for searching, not just looking by name.",
                "parameters": {
                    "type": "object",
                    "properties": {"query_str": {"type": "string"}},
                    "required": ["query_str"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_web_for_asteroid",
                "description": "Search the web for asteroid data if not found locally.",
                "parameters": {
                    "type": "object",
                    "properties": {"asteroid_name": {"type": "string"}},
                    "required": ["asteroid_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "threat_calculator_tool",
                "description": "Calculate comprehensive threat assessment for an asteroid. Requires mass, velocity, diameter, impact_probability, and name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mass": {"type": "number", "description": "Mass in kg"},
                        "velocity": {"type": "number", "description": "Velocity in km/s"},
                        "diameter": {"type": "number", "description": "Diameter in meters"},
                        "impact_probability": {"type": "number", "description": "Probability of impact (0 to 1)"},
                        "name": {"type": "string", "description": "Asteroid name"}
                    },
                    "required": ["mass", "velocity", "diameter", "impact_probability"]
                }
            }
        }
    ]

    # ---- Build prompt based on mode ----
    if mode == "answer":
        prompt = (
            f"Query: {query}\n\n"
            "PROCEDURE:\n"
            "1. Search the local database (query_asteroid_database or lookup_asteroid) for relevant facts.\n"
            "2. If not found locally, search the web (search_web_for_asteroid).\n"
            "3. Answer the user based on retrieved data. If out of domain, politely refuse."
        )
    elif mode == "assess_threat":
        prompt = (
            f"Assess the threat level for: {query}.\n\n"
            "PROCEDURE:\n"
            "1. First call lookup_asteroid with the asteroid name to get its data from the local database.\n"
            "2. If not found locally, call search_web_for_asteroid.\n"
            "3. Once you have the data, call threat_calculator_tool with the asteroid's mass, velocity, diameter, impact_probability, and name.\n"
            "4. Present your findings to the user as a clear, human-readable report with the following structure:\n"
            "   - Asteroid Information: Provide in both a paragraph and tabular form.\n"
            "   - Physics Calculations: Show the exact physics formulas and step-by-step calculations performed.\n"
            "   - Danger Classification: Classify the threat level as <Low>, <High>, or <Critical>, and explain why this level was chosen based on your physics calculations.\n"
            "Do NOT return raw JSON."
        )
    else:
        prompt = (
            f"Retrieve data for: {query}.\n\n"
            "PROCEDURE:\n"
            "1. First call lookup_asteroid with the asteroid name to get its data from the local database.\n"
            "2. If not found locally, call search_web_for_asteroid.\n"
            "3. Once you have the data, call threat_calculator_tool with the asteroid's mass, velocity, diameter, impact_probability, and name.\n"
            "4. Return your findings as valid JSON."
        )

    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": prompt}
    ]

    # ---- Step 1: Try LLM-driven tool calling ----
    output, success = _try_tool_call(tool_map, tools, list(messages))

    if success and output:
        print(f"  [Agent 1] LLM tool calling succeeded ({len(output)} chars)")
        return {"status": "success", "agent_1_result": output, "response": output}

    # ---- Step 2: Fallback — do direct Python lookups, then pass context to LLM ----
    print("  [Agent 1] Falling back to direct Python tool execution")

    # Extract asteroid name from the query
    query_lower = query.lower()
    context_data = None

    # Try direct name lookup first
    words = query.split()
    for word in words:
        if len(word) > 2:
            result = lookup_asteroid(word)
            if result:
                context_data = result
                print(f"  [Agent 1] Fallback: Found '{word}' in database")
                break

    # If no name match, try keyword search
    if not context_data:
        db_results = query_asteroid_database(query)
        if db_results and "No records found" not in db_results:
            context_data = db_results
            print(f"  [Agent 1] Fallback: Keyword search returned results")

    # If still nothing, try web
    if not context_data:
        for word in words:
            if len(word) > 3:
                web_result = search_web_for_asteroid(word)
                if web_result and not web_result.get("error"):
                    context_data = web_result
                    print(f"  [Agent 1] Fallback: Web search returned results for '{word}'")
                    break

    # Build context-enriched prompt for LLM
    context_str = json.dumps(context_data, indent=2) if context_data else "No data found in database or web."

    fallback_messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": f"{prompt}\n\nHere is the raw data retrieved from tools:\n```json\n{context_str}\n```\n\nPlease use this data to answer the query."}
    ]

    try:
        # Call LLM WITHOUT tools (just interpret the data)
        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=fallback_messages,
        )
        output = response.choices[0].message.content or "Agent 1 produced no output."
        print(f"  [Agent 1] Fallback LLM response: {len(output)} chars")
        return {"status": "success", "agent_1_result": output, "response": output}
    except Exception as e:
        error_msg = f"Agent 1 error: {str(e)}"
        print(f"  [Agent 1] ERROR: {error_msg}")
        return {"status": "error", "agent_1_result": error_msg, "response": error_msg, "message": error_msg}
