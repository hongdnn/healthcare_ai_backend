from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from bson import ObjectId
import os
import smtplib
from email.message import EmailMessage

load_dotenv(".env.local")

@asynccontextmanager
async def lifespan(api: FastAPI):
    # Startup: Connect to MongoDB
    print("🚀 Connecting to MongoDB...")
    app.mongodb_client = AsyncMongoClient(os.environ["MONGODB_URL"])
    app.db = app.mongodb_client.healthcare_db
    print("✅ MongoDB connected")
    
    yield  # App runs here
    
    # Shutdown: Close MongoDB connection
    print("🔌 Closing MongoDB connection...")
    await app.mongodb_client.close()
    print("👋 MongoDB disconnected")

# --- Create FastAPI app --- #
app = FastAPI(
    title="Healthcare AI API",
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # (optional) to allow all
    ],
    allow_credentials=True,
    allow_methods=["*"],      # MUST include OPTIONS
    allow_headers=["*"],
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

    if len(calendars) > 0:
        # Format data
        appointments = []
        for calendar in calendars:
            user = await app.db.users.find_one({"_id": ObjectId(calendar["user_id"])})
            print(user)
            
            appointments.append({
                "user": {
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "phone": user["phone"],
                    "email": user["email"],
                },
                "details": {
                    "id": str(calendar["_id"]),
                    "issue": calendar["issue"],
                    "start_datetime": str(calendar["start_datetime"]),
                    "end_datetime": str(calendar["end_datetime"]),
                    "confirmation": calendar["confirmation"],
                },
            })

        # Return data
        return JSONResponse(
            status_code=200,
            content={
                "appointments": appointments
            }
        )

    # Return empty appointments
    return JSONResponse(
        status_code=200,
        content={
            "appointments": []
        }
    )

class EmailModel(BaseModel):
    """
    Container for email payload
    """
    email: str
    subject: str
    content: str

@app.post("/email")
async def email(data: EmailModel):
    try:
        msg = EmailMessage()
        msg.set_content(data.content)
        msg["Subject"] = data.subject
        msg["From"] = os.environ["EMAIL"]
        msg["To"] = data.email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(os.environ["EMAIL"], os.environ["EMAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()

        # Return success
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok"
            }
        )
    except Exception as e:
        print("error: ", e)
        return JSONResponse(
            status_code=500,
            content={
                "status": "failed"
            }
        )
    
@app.get("/conversations")
async def conversations(appointment_id: str):
    conversation = await app.db.conversations.find_one({"appointment_id": appointment_id})

    if conversation is not None:
        calendar = await app.db.calendars.find_one({"_id": ObjectId(appointment_id)})
        return JSONResponse(
            status_code=200,
            content={
                "conversation": {
                    "detail": {
                        "appointment": {
                            "doctor_id": calendar["doctor_id"],
                            "issue": calendar["issue"],
                            "start_datetime": str(calendar["start_datetime"]),
                            "end_datetime": str(calendar["end_datetime"]),
                            "confirmation": calendar["confirmation"],
                            "created_at": str(calendar["created_at"])
                        },
                        "ai_summary": {
                            "issue": conversation["issue"],
                            "symptoms": conversation["symptoms"],
                            "recommendations": conversation["recommendations"]
                        }
                    }
                }
            }
        )

    return JSONResponse(
        status_code=200,
        content={
            "conversations": None
        }
    )