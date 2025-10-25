import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from livekit import agents
from src.agent import entrypoint

# --- Create FastAPI app --- #
app = FastAPI()

# Index endpoint
@app.get("/")
async def root():
    return JSONResponse({"status": "ok", "message": "Healthcare assistant API running"})


# Example health check endpoint
@app.get("/health")
async def health():
    return JSONResponse({"status": "healthy"})