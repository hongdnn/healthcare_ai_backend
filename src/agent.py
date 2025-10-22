from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

import httpx  # for calling external APIs
import asyncio

load_dotenv(".env.local")


# --- Define tools --- #
# Tool: symptom check
@agents.function_tool
async def symptom_check_api(ctx: agents.RunContext, symptoms: str, feeling: str) -> dict:
    """
    Calls your external diagnosis API.
    Returns something like:
      { "probable_issue": "...", "urgency": "low|medium|high", "recommendation": "..."}
    """
    # Example HTTP call (you’ll replace with your real API)
    print(f"Calling symptom check API with symptoms: {symptoms}, feeling: {feeling}")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.myhealthsystem.com/diagnose",
                json={"symptoms": symptoms, "feeling": feeling}
            )
            resp.raise_for_status()
            result = resp.json()
    except Exception as e:
        print(f"Error calling symptom check API: {e}")
        result = {"probable_issue": "unknown", "urgency": "low", "recommendation": "Please consult a healthcare professional."}
    return result

# Tool: book appointment
@agents.function_tool
async def book_appointment(ctx: agents.RunContext, patient_name: str, issue: str, preferred_time: str) -> dict:
    """
    Calls your calendar booking service and returns booking confirmation.
    """
    print(f"Booking appointment for {patient_name} regarding {issue} at {preferred_time}")
    # async with httpx.AsyncClient() as client:
    #     resp = await client.post(
    #         "https://api.myhealthsystem.com/book",
    #         json={"patient": patient_name, "issue": issue, "time": preferred_time}
    #     )
    #     resp.raise_for_status()
    #     result = resp.json()
    return {"confirmation": "Appointment booked successfully for " + preferred_time}

# --- Define main Assistant agent --- #
class MainAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a friendly healthcare assistant. "
                "You will ask the user how they are feeling, what symptoms they have, "
                "then call a diagnosis tool (symptom_check_api) to get a probable issue. "
                "Then you will inform the user of the result and remind them to see a doctor in-person. "
                "If needed you can offer to book an in-person appointment by calling book_appointment. "
                "You can also hand over to a nurse agent if the urgency is high."
            ),
            tools=[symptom_check_api, book_appointment]
        )

    async def handle_input(self, user_input: str) -> None:
        # we could parse symptom input etc here or rely on LLM tool use
        await self.session.generate_reply()


# --- Entrypoint --- #
async def entrypoint(ctx: agents.JobContext):
    
    room_name = ctx.room or "web_room"
    print(f"Joining room: {room_name}")

    session = AgentSession(
        stt="assemblyai/universal-streaming:en",  # or your STT model
        llm="openai/gpt-4.1-mini",  # or your chosen LLM
        tts="cartesia/sonic-2",  # or chosen TTS model
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel()
    )

    await session.start(
        room=ctx.room,
        agent=MainAssistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        )
    )

    # initial greeting has already been done in on_enter, so no further call here
    await session.generate_reply(
        instructions="Greet the user that you are their healthcare assistant and ask how can you help them today."
    )

if __name__ == "__main__":
    # Run to test with web/mobile frontend
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    # Run to test with phone call
    #agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint, agent_name="my-telephony-agent"))