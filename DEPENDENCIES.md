# Dependencies Verification Checklist

## System Requirements
- ✅ Python 3.13+
- ✅ Node.js & npm
- ✅ Bash shell

## Backend Python Packages (Backend/.venv)
```bash
cd /home/pranjay/workspace/Projects/Aegis/no1
./.venv/bin/pip list | grep -E "fastapi|uvicorn|litellm|pydantic|python-dotenv"
```

Expected packages:
- ✅ fastapi (>=0.100)
- ✅ uvicorn (>=0.24)
- ✅ litellm (>=1.0)
- ✅ pydantic (>=2.0)
- ✅ python-dotenv (>=1.0)

## Frontend Node Packages
```bash
cd /home/pranjay/workspace/Projects/Aegis/no
npm list vite
```

Expected:
- ✅ vite (^5.0.0)

## Configuration Files
- ✅ `/home/pranjay/workspace/Projects/Aegis/no1/.env` - Contains 3 Groq API keys
- ✅ `/home/pranjay/workspace/Projects/Aegis/no1/main.py` - Orchestration with 15s delays
- ✅ `/home/pranjay/workspace/Projects/Aegis/no/public/working-soon.html` - Frontend dashboard

## Pre-Presentation Checks
```bash
# 1. Verify backend starts
cd /home/pranjay/workspace/Projects/Aegis/no1
./.venv/bin/python server.py &
sleep 3
curl http://localhost:8000/ && echo "✅ Backend OK" || echo "❌ Backend Failed"

# 2. Verify API responds
curl -X POST http://localhost:8000/api/process \
  -H 'Content-Type: application/json' \
  -d '{"mode":"assess","query":"test"}' && echo "✅ API OK" || echo "❌ API Failed"

# 3. Verify Groq keys are present
grep GROQ_API_KEY /home/pranjay/workspace/Projects/Aegis/no1/.env && echo "✅ Keys OK" || echo "❌ Keys Missing"
```

## Ports in Use
- **Backend API**: http://localhost:8000
- **Frontend Dev Server**: http://localhost:5173
- **Dashboard**: http://localhost:5173/working-soon.html

## Performance Notes
- **Assess Threat**: ~2-3 seconds
- **Generate Plan**: ~40 seconds (includes 15s delays between agents + LLM calls)

## Known Limitations
- Groq free tier: 12,000 TPM (tokens per minute) across all 3 keys
- Rate limiting handled by inter-agent delays
- Frontend is Vite dev server (not production build)

## Run for Presentation
```bash
cd /home/pranjay/workspace/Projects/Aegis
./run.sh
# Then visit http://localhost:5173/working-soon.html
```
