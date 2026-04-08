import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import process_request
import uvicorn
from dotenv import load_dotenv

# Load env vars
load_dotenv()

app = FastAPI(title="Project Aegis Backend API")

# Enable CORS for frontend communication
# Since Vite usually runs on 5173, we allow that origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. In production, restrict to frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    mode: str
    query: str

@app.get("/")
async def root():
    return {"status": "online", "message": "Project Aegis Backend is live."}

@app.post("/api/process")
async def handle_request(body: RequestBody):
    try:
        # Call the existing orchestrator logic from main.py
        result = await process_request(body.mode, body.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server on all interfaces at port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
