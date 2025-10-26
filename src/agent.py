import asyncio
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.rtc import Room, ConnectionState
import dateparser
from chroma.chroma_service import ChromaService
import re
from db.mongo_service import MongoService
from models.user import User

load_dotenv(".env.local")

chroma_service = ChromaService()
mongo_service = MongoService()

# --- Helper: simple text → list of symptoms --- #
def extract_symptoms(text: str) -> list[str]:
    """
    Convert free text like 'headache and a bit cold' → ['headache', 'cold']
    """
    tokens = re.split(r"[,\s]*(?:and|but|with|also|plus|,|\s)+[,\s]*", text, flags=re.IGNORECASE)
    return [t.strip().lower() for t in tokens if t.strip()]


# --- Tool: Symptom check --- #

        
# --- Tool: Parse datetime --- #
@agents.function_tool
async def parse_datetime(ctx: agents.RunContext, text: str) -> dict:
    """
    Converts natural language datetime into an ISO8601 timestamp.
    Example: "tomorrow 3pm" -> {"datetime": "2025-10-23T15:00:00-07:00"}
    """
    parsed = dateparser.parse(text)
    if not parsed:
        return {"error": "Could not parse date/time."}
    return {"datetime": parsed.isoformat()}

# --- Define main Assistant agent --- #
class MainAssistant(Agent):
    def __init__(self, user: User | None) -> None:
        self.user = user
        self.issue = ""
        self.symptoms = []
        self.recommendations = []
        self.appointment_id = None
        
        @agents.function_tool
        async def symptom_check_api(ctx: agents.RunContext, symptoms: str, n_result: int = 3) -> dict:
            """
            Uses Chroma to find the most similar known health issue based on symptoms.
            If multiple results are returned, suggest additional symptoms to the user to refine the query.
            """
            try:
                user_symptoms = extract_symptoms(symptoms)
                print(f"Extracted symptoms: {user_symptoms}")
                results = chroma_service.query(user_symptoms, n_results=n_result)
                if not results:
                    raise ValueError("No results from Chroma")

                # If only one result, return immediately
                if len(results) == 1:
                    self.issue = results[0].get("health_issue", "unknown")
                    self.symptoms = user_symptoms.copy()
                    self.recommendations = results[0].get("advice", "Please consult a healthcare professional.").split(',')
                    return {
                        "issue": results[0].get("health_issue", "unknown"),
                        "recommendation": results[0].get("advice", "Please consult a healthcare professional.")
                    }

                # Multiple results: extract unique symptoms not already mentioned
                additional_symptoms = set()
                for r in results:
                    symptom_str = r.get("symptoms", "")
                    # split by comma and strip whitespace
                    for s in symptom_str.split(","):
                        s_clean = s.strip().lower()
                        if s_clean and s_clean not in user_symptoms:
                            additional_symptoms.add(s_clean)

                # Pick up to 3 additional symptoms to suggest
                suggested_symptoms = list(additional_symptoms)[:3]

                return {
                    "issue": "I found several possible conditions.",
                    "recommendation": "",
                    "suggested_symptoms": suggested_symptoms  
                }

            except Exception as e:
                print(f"Error in symptom_check_api: {e}")
                return {
                    "issue": "unknown",
                    "recommendation": "Please consult a healthcare professional."
                }
        
        @agents.function_tool
        async def book_appointment(ctx: agents.RunContext, issue: str, preferred_time: str) -> dict:
            user_id = str(self.user._id) if self.user else "anonymous"
            print(f"📅 Booking appointment for {user_id} regarding {issue} at {preferred_time}")
            result = mongo_service.create_appointment(
                user_id=user_id,
                issue=f"Appointment regarding {issue}",
                datetime_iso=preferred_time,
                confirmation="confirmed"
            )
            if not result:
                return {"confirmation": "There was a scheduling conflict. Please choose a different time."} 
            self.appointment_id = result
            return {"confirmation": f"Appointment booked successfully for {preferred_time}"}
        
        super().__init__(
            instructions=(
                "You are a friendly healthcare assistant. "
                "You will ask the user how they are feeling. "
                "Then call the `symptom_check_api` tool to get the probable health issue and recommendation. "
                "If the `symptom_check_api` returns `suggested_symptoms`, ask the user about those additional symptoms to refine the diagnosis,"
                " then call `symptom_check_api` again with the updated symptoms and n_result = 1."
                "Once you get the result, generate a clear, natural sentence for the user using the fields: "
                "`issue` (the probable health problem) and `recommendation` (what they should do). "
                "Always remind the user to see a doctor for confirmation. "
                "If needed, offer to book an in-person appointment by calling `book_appointment`. "
                "If the user doesn't provide a full date and time, ask for missing parts, "
                "then call the `parse_datetime` tool to get the absolute timestamp. "
                "Confirm this time with the user in natural language before booking. "
                "After confirmation, call `book_appointment` with the ISO datetime and the user's id."
                "If `book_appointment` return conflict schedule, inform the user that there was a scheduling conflict and ask if they're available at a different time."
                "Then, try booking again."

                "Example:"
                "Assistant: How are you feeling today?"
                "User: I have fever and cough."
                "Assistant: (call `symptom_check_api` with 'fever, cough')"
                "Tool returns: {'issue': 'Covid', 'recommendation': 'isolate, drink water}"
                "Assistant: 'It looks like you may have Covid. I recommend you isolate and drink more water. "
                "However, please consult a healthcare professional to confirm. "
                "Would you like me to help you book an appointment?'"
                "User: Yes, please."
                "Assistant: 'Sure — when would you like the appointment?'"
                "User: Tomorrow around 4:30 PM"
                "Assistant: (combine 'tomorrow' + '4:30 PM', call `parse_datetime` → get ISO datetime)"
                "Assistant: 'Okay, so your appointment will be on October 24th at 4:30 PM, right?'"
                "User: Yes"
                "Assistant: (call `book_appointment` with the ISO datetime and user's id)"
                "Assistant: 'Your appointment has been booked successfully.'"
            ),
            tools=[symptom_check_api, book_appointment, parse_datetime]
        )

    async def handle_input(self, user_input: str) -> None:
        # we could parse symptom input etc here or rely on LLM tool use
        await self.session.generate_reply()


# --- Entrypoint --- #
async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    room = ctx.room

    print(f"Waiting for user to join room {room.name}...")

    participant = None
    for _ in range(15):
        if room.remote_participants:
            participant = next(iter(room.remote_participants.values()))
            break
        await asyncio.sleep(1)

    if not participant:
        print("⚠️ No remote participants joined in time.")
        return

    user_identity = participant.identity
    print(f"✅ User {user_identity} {participant.name} joined.")
    identity = participant.identity
    user = None

    if identity.startswith("sip_"):
        # Extract phone number after 'sip_'
        phone_number = identity.split("sip_")[1]
        user = mongo_service.fetch_user_by_phone(phone_number)
    else:
        user = mongo_service.fetch_user_by_id(identity)

    print(f"Fetched user from DB: {user.name} ({user.email})")

    session = AgentSession(
        stt="assemblyai/universal-streaming:en",  # or your STT model
        llm="openai/gpt-4.1-mini",  # or your chosen LLM
        tts="cartesia/sonic-2",  # or chosen TTS model
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel()
    )
    
    agent = MainAssistant(user=user)
    
        # --- Cleanup helper --- #
    async def cleanup_session():
        try:
            if hasattr(session, "_tasks"):
                for t in list(session._tasks):
                    if not t.done():
                        t.cancel()
            # disconnect room if still connected
            if room and room.connection_state == ConnectionState.CONN_CONNECTED:
                await room.disconnect()
            print("🧹 Session cleaned up successfully")
        except Exception as e:
            print(f"⚠️ Error during session cleanup: {e}")
            
            

    # Define the cleanup and save function
    async def on_participant_disconnected(p):
        print(f"📞 User {p.identity} disconnected.")
        
        # Save conversation summary
        if agent.appointment_id:
            print(f"Saving conversation summary for appointment {agent.appointment_id}...")
            mongo_service.save_conversation_summary(
                user_id=str(user._id),
                issue=agent.issue,
                symptoms=agent.symptoms,
                recommendations=agent.recommendations,
                appointment_id=agent.appointment_id,
            )
        
        # Cleanup
        await cleanup_session()
    
    # Register the event handler
    room.on("participant_disconnected", lambda p: asyncio.create_task(on_participant_disconnected(p)))

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        )
    )

    await session.generate_reply(
        instructions="Greet the user that you are their healthcare assistant and ask how can you help them today."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint, agent_name="my-telephony-agent"))