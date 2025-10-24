import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from livekit import agents
from src.agent import entrypoint

# --- Lifespan for startup/shutdown --- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start agent(s)
    print("🚀 FastAPI starting... launching agents")
    
    # Create worker instances programmatically (not using CLI)
    worker_web = agents.Worker(
        opts=agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
    
    worker_phone = agents.Worker(
        opts=agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="my-telephony-agent"
        )
    )
    
    # Launch workers as background tasks
    app.state.web_agent_task = asyncio.create_task(worker_web.run())
    app.state.phone_agent_task = asyncio.create_task(worker_phone.run())

    yield  # App is running here

    # Shutdown: cancel agent tasks
    print("🛑 Shutting down agents")
    for task_name in ["web_agent_task", "phone_agent_task"]:
        task = getattr(app.state, task_name, None)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                print(f"{task_name} cancelled")


# --- Create FastAPI app --- #
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return JSONResponse({"status": "ok", "message": "Healthcare assistant API running"})


# Example health check endpoint
@app.get("/health")
async def health():
    return JSONResponse({"status": "healthy"})