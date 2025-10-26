# mongo_service.py
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from bson import ObjectId
import pytz

from models.user import User

load_dotenv(".env.local")

class MongoService:
    def __init__(self):
        logging.getLogger("pymongo").setLevel(logging.WARNING)
        mongo_url = os.getenv("MONGODB_URL")
        if not mongo_url:
            raise ValueError("MONGODB_URL not found in .env.local")

        self.client = MongoClient(mongo_url)
        self.db = self.client["healthcare_db"]
        self.users = self.db["users"]
        self.calendar = self.db["calendars"]
        self.conversations = self.db["conversations"]
        
    def fetch_user_by_id(self, user_id: str) -> User | None:
        """
        Fetch a user document by its string _id and return a User instance.
        """
        try:
            doc = self.users.find_one({"_id": ObjectId(user_id)})
            if not doc:
                print(f"⚠️ No user found with id: {user_id}")
                return None
            return User(
                _id=str(doc["_id"]),
                name=doc.get("name", ""),
                phone=doc.get("phone", ""),
                email=doc.get("email", ""),
                user_type=doc.get("type", "patient"),
            )
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
        
    def fetch_user_by_phone(self, phone_number: str) -> User | None:
        """
        Fetch a user document by phone number and return a User instance.
        """
        try:
            doc = self.users.find_one({"phone": phone_number})
            if not doc:
                print(f"⚠️ No user found with phone: {phone_number}")
                return None
            return User(
                _id=str(doc["_id"]),
                name=doc.get("name", ""),
                phone=doc.get("phone", ""),
                email=doc.get("email", ""),
                user_type=doc.get("type", "patient"),
            )
        except Exception as e:
            print(f"Error fetching user by phone: {e}")
            return None

    def create_appointment(self, user_id: str, issue: str, datetime_iso: str, confirmation: str):
        """Insert appointment record into MongoDB with 1-hour overlap protection and timezone-aware datetime."""
        # Set your local timezone
        local_tz = pytz.timezone("US/Pacific")

        # Parse ISO string and localize to Pacific time
        naive_dt = datetime.fromisoformat(datetime_iso)
        start_time = local_tz.localize(naive_dt)
        end_time = start_time + timedelta(hours=1)

        doctor_id = "68fc65ca4916df00cfe6ec9d"

        # Define protected window: ±55 minutes
        window_start = start_time - timedelta(minutes=55)
        window_end = start_time + timedelta(minutes=55)

        # MongoDB stores in UTC automatically
        conflict = self.calendar.find_one({
            "doctor_id": doctor_id,
            "start_datetime": {"$lte": window_end},
            "end_datetime": {"$gte": window_start},
        })

        if conflict:
            print(f"⚠️ Conflict detected: doctor already has an appointment at {conflict['start_datetime']}")
            return None

        appointment = {
            "user_id": user_id,
            "doctor_id": doctor_id,
            "issue": issue,
            "start_datetime": start_time,
            "end_datetime": end_time,
            "confirmation": confirmation,
            "created_at": datetime.now(pytz.utc),
        }

        result = self.calendar.insert_one(appointment)
        print(f"✅ Appointment created for {start_time} (ID: {result.inserted_id})")
        return str(result.inserted_id)

    def get_appointments(self, user_id: str):
        """Fetch all appointments for a user."""
        return list(self.calendar.find({"user_id": user_id}))

    def delete_appointment(self, appointment_id: str):
        """Remove appointment if needed."""
        return self.calendar.delete_one({"_id": ObjectId(appointment_id)})
    
    def save_conversation_summary(self, user_id: str, issue: str, symptoms: list[str], recommendations: list[str],appointment_id: str | None):
        """
        Save summarized conversation after call ends.
        """
        conversation = {
            "user_id": user_id,
            "issue": issue,
            "symptoms": symptoms,
            "recommendations": recommendations,
            "appointment_id": appointment_id,
            "created_at": datetime.now(),
        }

        result = self.conversations.insert_one(conversation)
        print(f"💾 Conversation saved (ID: {result.inserted_id})")
        return str(result.inserted_id)
    
    def fetch_appointment_by_id(self, appointment_id: str):
        """Fetch appointment by its ID."""
        return self.calendar.find_one({"_id": ObjectId(appointment_id)})