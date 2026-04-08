# Project Aegis (Google ADK Version)

Project Aegis is a planetary-defense multi-agent Python system. It orchestrates three unique agents managing data processing, simulation generation, and safety valuation.

This version strictly follows the `google-adk` framework patterns and is entirely JSON-driven.

## Project Structure
```text
project_root/
├── agent_1/
│   ├── agent.py: Database Intelligence Officer logic
│   ├── tools.py: Asteroid lookups, Web Search fallback, and Threat Calculators
│   └── agent1_policy.md: Governing conversational/domain refusal bounds
├── agent_2/
│   ├── agent.py: Strategic Planner logic
│   └── tools.py: Simulation search space generator
├── agent_3/
│   ├── agent.py: Safety Validator logic
│   └── tools.py: Fragmentation checks and momentum tracking
├── data/
│   └── asteroids.json: Local static database fallback
├── shared/
│   ├── schemas.py: Data structuring types
│   └── utils.py: Utility loading logic
├── main.py: Central Python orchestrator routing modes
└── README.md
```

## How Agent 1 Routing Works
The `main.py` script routes based on an explicit user intent parameter (`mode`):
1. **`answer`**: Agent 1 handles the conversation using its LLM to either answer valid Domain space queries or strictly refuse out-of-domain requests without moving down the pipeline.
2. **`assess_threat`**: Agent 1 finds the asteroid data locally or acts on web fallback, calculates the threat result, and halts.
3. **`generate_plan`**: Agent 1 performs the same threat assessment and data ingestion, then explicitly hands off its structured output as the input prompt to Agent 2. Agent 2 computes strategies and passes them to Agent 3.

## What is Preserved
- All core agent responsibility tooling (JSON querying, Simulation Generation, Fragmentation Checking) operates using the exact scientific constraint matrices carried over from the legacy LangGraph build.
- The project is fully JSON-driven.

## Newly Added
- **Adk Compatibility**: The LLMs utilize explicit python definition mappings instead of abstract Graph flow loops.
- **Agent Policy File**: `agent1_policy.md` guides responses strictly to educational space info.
- **Web-search Fallback**: `search_web_for_asteroid` will utilize standard generic API wikipedia extractions if an asteroid does not reside in `data/asteroids.json`.

## Configuration
- An active `GOOGLE_API_KEY` must be mounted into the `.env` file since default constructors use `gemini-2.5-flash`.
- If migrating to Groq, developers must alter the `model` constructor parameter to `llama3...` inside `agent.py` generators.
