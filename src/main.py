from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
from datetime import datetime

import os

load_dotenv(".env.local")

# --- Create FastAPI app --- #
app = FastAPI(
    title="Healthcare AI API"
)
client = AsyncMongoClient(os.environ["MONGODB_CONNECTION_STRING"])
db = client.healthcare_db
user_collection = db.users
calendar_collection = db.calendars

@app.get("/")
async def index():
    return JSONResponse({"status": "ok", "message": "Healthcare assistant API running"})

@app.get("/health")
async def health():
    return JSONResponse({"status": "healthy"})
    
class UserModel(BaseModel):
    """
    Container for a single user record
    """
    name: str
    phone: str
    email: str
    type: str

class LoginModel(BaseModel):
    """
    Container for login payload
    """
    email: str

@app.post("/login")
async def login(data: LoginModel):
    print("user: ", data.email)
    user = await user_collection.find_one({"email": data.email, "type": "doctor"})

    if user is not None:
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "id": str(user["_id"])}
        )

    return JSONResponse(
        status_code=401,
        content={"status": "failed"}
    )

class CalendarModel(BaseModel):
    """
    Container for a single calendar record
    """
    doctor_id: str
    user_id: str
    issue: str
    start_datetime: datetime
    end_datetime: datetime
    confirmation: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


@app.get("/calendar/user/{user_id}")
async def user_calendar(user_id: str):
    calendars = await calendar_collection.find({"user_id": user_id}).to_list(length=None)

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


@app.get("/calendar/doctor/{doctor_id}")
async def doctor_calendar(doctor_id: str):
    calendars = await calendar_collection.find({"doctor_id": doctor_id}).to_list(length=None)

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