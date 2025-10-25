from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os

load_dotenv(".env.local")

@asynccontextmanager
async def lifespan(api: FastAPI):
    # Startup: Connect to MongoDB
    print("🚀 Connecting to MongoDB...")
    app.mongodb_client = AsyncMongoClient(os.environ["MONGODB_CONNECTION_STRING"])
    app.db = app.mongodb_client.healthcare_db
    print("✅ MongoDB connected")
    
    yield  # App runs here
    
    # Shutdown: Close MongoDB connection
    print("🔌 Closing MongoDB connection...")
    app.mongodb_client.close()
    print("👋 MongoDB disconnected")

# --- Create FastAPI app --- #
app = FastAPI(
    title="Healthcare AI API",
    lifespan=lifespan
)

@app.get("/")
async def index():
    return JSONResponse({"status": "ok", "message": "Healthcare assistant API running"})

@app.get("/health")
async def health():
    return JSONResponse({"status": "healthy"})

class LoginModel(BaseModel):
    """
    Container for login payload
    """
    email: str

@app.post("/login")
async def login(data: LoginModel):
    print("user: ", data.email)
    user = await app.db.users.find_one({"email": data.email})

    if user is not None:
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "id": str(user["_id"]), "type": user["type"]}
        )

    return JSONResponse(
        status_code=401,
        content={"status": "failed"}
    )

@app.get("/calendar/user")
async def user_calendar(id: str):
    calendars = await app.db.calendars.find({"user_id": id}).to_list(length=None)

    return JSONResponse(
        status_code=200,
        content={
            "appointments": [
                {
                    "issue": calendar["issue"],
                    "start_datetime": str(calendar["start_datetime"]),
                    "end_datetime": str(calendar["end_datetime"]),
                    "confirmation": calendar["confirmation"]
                } for calendar in calendars
            ]
        } if len (calendars) > 0 else []
    )

@app.get("/calendar/doctor")
async def doctor_calendar(id: str):
    calendars = await app.db.calendars.find({"doctor_id": id}).to_list(length=None)

    return JSONResponse(
        status_code=200,
        content={
            "appointments": [
                {
                    "user_id": calendar["user_id"],
                    "issue": calendar["issue"],
                    "start_datetime": str(calendar["start_datetime"]),
                    "end_datetime": str(calendar["end_datetime"]),
                    "confirmation": calendar["confirmation"]
                } for calendar in calendars
            ]
        } if len (calendars) > 0 else []
    )