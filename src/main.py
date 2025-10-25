from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from dotenv import load_dotenv

import os

load_dotenv(".env.local")

# --- Create FastAPI app --- #
app = FastAPI(
    title="Healthcare AI API"
)
client = AsyncMongoClient(os.environ["MONGODB_CONNECTION_STRING"])
db = client.healthcare_db
user_collection = db.users

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
            content={"status": "ok", "message": "Login successful", "id": str(user["_id"])}
        )

    return JSONResponse(
        status_code=401,
        content={"status": "failed", "message": "Login failed"}
    )
