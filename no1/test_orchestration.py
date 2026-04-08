import asyncio
import json
from main import process_request

async def test():
    print("Testing 'assess' mode (Threat level)...")
    res_assess = await process_request("assess", "Any asteroid in 2025?")
    print(f"Assess Result: {res_assess}\n")

    print("Testing 'plan' mode (Full Orchestration)...")
    res_plan = await process_request("plan", "Assess threat for Apophis-2026 and generate deflection plan.")
    print(f"Plan Result Keys: {list(res_plan.keys())}")
    print(f"Workflow Status: {res_plan.get('workflow_status')}")

if __name__ == "__main__":
    asyncio.run(test())
