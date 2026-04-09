# Project Aegis - Quick Start Guide

## Prerequisites Check
Before running, ensure you have:
- Python 3.13+
- Node.js & npm
- Virtual environment activated: `./.venv/bin/python`
- `.env` file with 3 Groq API keys configured

## Quick Start (One Command)

```bash
cd /home/pranjay/workspace/Projects/Aegis
./run.sh
```

## Manual Start (If Script Fails)

### Backend (Terminal 1)
```bash
cd /home/pranjay/workspace/Projects/Aegis/no1
./.venv/bin/python server.py
# Should show: "Uvicorn running on http://0.0.0.0:8000"
```

### Frontend (Terminal 2)
```bash
cd /home/pranjay/workspace/Projects/Aegis/no
npm run dev
# Should show: "Local: http://localhost:5173"
```

## Access the App
Open browser: **http://localhost:5173/working-soon.html**

## Testing Endpoints

### Test "Assess Threat" Button
```bash
curl -X POST http://localhost:8000/api/process \
  -H 'Content-Type: application/json' \
  -d '{"mode":"assess","query":"Any asteroid in 2025?"}'
```

### Test "Generate Deflection Plan" Button
```bash
curl -X POST http://localhost:8000/api/process \
  -H 'Content-Type: application/json' \
  -d '{"mode":"plan","query":"Assess threat for Apophis-2026 and generate deflection plan."}'
# Note: This takes ~40 seconds (15s delays between agents)
```

## Backend Architecture

**Three-Agent Orchestration:**
1. **Agent 1 (Data Retrieval)** - Queries threat database
2. **Agent 2 (Strategic Planning)** - Generates deflection strategies  
3. **Agent 3 (Safety Validation)** - Validates mission safety

**Rate Limiting Workaround:**
- 15-second delays between agents allow TPM bucket to reset
- 3 separate Groq API keys from same account
- Each agent gets its own quota slot

## Configuration Files

- **Backend**: `/home/pranjay/workspace/Projects/Aegis/no1/server.py`
- **Orchestration**: `/home/pranjay/workspace/Projects/Aegis/no1/main.py`
- **Environment**: `/home/pranjay/workspace/Projects/Aegis/no1/.env`
- **Frontend**: `/home/pranjay/workspace/Projects/Aegis/no/public/working-soon.html`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | `pkill -f "python server.py"` |
| Port 5173 already in use | `pkill -f "npm"` |
| Rate limit errors | Ensure 15s+ delays are set in `main.py` |
| 404 on frontend | Access `/working-soon.html` not just `/` |
| Empty responses | Check `.env` has valid Groq API keys |

## Expected Behavior

✅ **Assess Button**: Returns threat data in ~2-3 seconds
✅ **Plan Button**: Returns full orchestration in ~40 seconds
✅ **Workflow Status**: Shows `AWAITING_HUMAN_APPROVAL` or `MISSION_REJECTED`

