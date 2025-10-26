import asyncio
import json
from datetime import datetime
import random
from dotenv import load_dotenv
from livekit import agents, api
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.rtc import ConnectionState
from db.mongo_service import MongoService
from utils.time_utils import format_datetime_natural

load_dotenv(".env.local")

mongo_service = MongoService()

# --- Feedback Agent --- #
class FeedbackAgent(Agent):
    def __init__(self, user, appointment):
        self.user = user
        self.appointment = appointment
        self.feedback = None
        self.improvement = None
        self.additional_notes = None

        @agents.function_tool
        async def record_feedback(ctx: agents.RunContext, feedback: str, improved: bool, notes: str = "") -> dict:
            """Store patient's feedback after follow-up call"""
            try:
                mongo_service.save_feedback(
                    appointment_id=self.appointment["_id"],
                    user_id=str(self.user["_id"]),
                    feedback=feedback,
                    improved=improved,
                    notes=notes,
                    timestamp=datetime.now()
                )
                return {"result": "Feedback recorded successfully."}
            except Exception as e:
                print(f"Error saving feedback: {e}")
                return {"result": "There was an error saving feedback."}

        super().__init__(
            instructions=(
                "You are Cura’s healthcare follow-up assistant. "
                "You are calling the patient one week after their appointment to check how they’re doing. "
                "Start the call by greeting the patient warmly and confirming their name and recent appointment. "
                "Then ask them if they feel any improvement in their condition since the visit. "
                "If they say yes, record the improvement and thank them. "
                "If they say no, ask politely what symptoms persist or if they need help scheduling a follow-up appointment. "
                "At the end, summarize their feedback and call the `record_feedback` tool to store it in the database. "
                "Be empathetic and use natural human tone."
            ),
            tools=[record_feedback],
        )


# --- Entrypoint --- #
async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    room = ctx.room

    # --- Step 1: Parse metadata for outbound call ---
    phone_number = None
    appointment = None
    try:
        if ctx.job.metadata:
            data = json.loads(ctx.job.metadata)
            print(f"Parsed metadata: {data}")
            phone_number = data.get("phone_number")
            appointment = mongo_service.fetch_appointment_by_id(data.get("appointment_id"))
    except Exception as e:
        print(f"Error parsing metadata: {e}")

    print(f"Using phone number: {phone_number}, appointment: {appointment}")
    if not phone_number or not appointment:
        print("⚠️ Missing phone number or appointment info.")
        await ctx.shutdown()
        return

    # --- Step 2: Place outbound call ---
    try:
        await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
            room_name=ctx.room.name,
            sip_trunk_id="ST_6xaaSRD7hsnH", 
            sip_call_to=phone_number,
            participant_identity=phone_number,
            wait_until_answered=True,
        ))
        print(f"📞 Outbound call to {phone_number} picked up successfully.")
    except api.TwirpError as e:
        print(f"❌ Error creating SIP participant: {e.message}")
        await ctx.shutdown()
        return

    # --- Step 3: Wait for participant ---
    participant = None
    for _ in range(10):
        if room.remote_participants:
            participant = next(iter(room.remote_participants.values()))
            break
        await asyncio.sleep(1)

    if not participant:
        print("⚠️ No participant joined the follow-up call.")
        return

    print(f"✅ Patient {participant.identity} joined the feedback call.")

    user = mongo_service.fetch_user_by_phone(phone_number)
    print(f"Fetched user: {user.name} ({user.email})")

    # --- Step 4: Start AgentSession ---
    session = AgentSession(
        stt="assemblyai/universal-streaming:en",
        llm="openai/gpt-4.1-mini",
        tts="deepgram/nova-3-general",
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel()
    )

    agent = FeedbackAgent(user=user, appointment=appointment)

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        )
    )

    # Outbound call: let the agent start conversation
    await session.generate_reply(
        instructions=f"Call the patient to check on their recovery after their visit on {format_datetime_natural(appointment['datetime'])}."
    )

    # --- Step 5: Cleanup on disconnect ---
    async def cleanup():
        try:
            if hasattr(session, "_tasks"):
                for t in list(session._tasks):
                    if not t.done():
                        t.cancel()
            if room and room.connection_state == ConnectionState.CONN_CONNECTED:
                await room.disconnect()
            print("🧹 Feedback session cleaned up successfully")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

    room.on("participant_disconnected", lambda p: asyncio.create_task(cleanup()))

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint, agent_name="my-telephony-agent"))