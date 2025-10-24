from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
import dateparser  
from chroma.chroma_service import ChromaService 
import re

load_dotenv(".env.local")

chroma_service = ChromaService()

# --- Helper: simple text → list of symptoms --- #
def extract_symptoms(text: str) -> list[str]:
    """
    Convert free text like 'headache and a bit cold' → ['headache', 'cold']
    """
    tokens = re.split(r"[,\s]*(?:and|but|with|also|plus|,|\s)+[,\s]*", text, flags=re.IGNORECASE)
    return [t.strip().lower() for t in tokens if t.strip()]


# --- Define tools --- #
# --- Tool: Symptom check --- #
@agents.function_tool
async def symptom_check_api(ctx: agents.RunContext, user_input: str) -> dict:
    """
    Uses Chroma to find the most similar known health issue based on symptoms.
    """
    symptoms = extract_symptoms(user_input)

    if not symptoms:
        return {
            "issue": "unknown",
            "recommendation": "Please describe your symptoms again more clearly."
        }

    print(f"Extracted symptoms: {symptoms}")

    result = chroma_service.query(symptoms)
    if not result:
        return {
            "issue": "unknown",
            "recommendation": "No matching cases found. Please consult a healthcare professional."
        }

    return {
        "issue": result.get("health_issue", "unknown"),
        "recommendation": result.get("advice", "Please rest and drink water.")
    }


# --- Tool: Symptom check --- #
@agents.function_tool
async def symptom_check_api(ctx: agents.RunContext, symptoms: str) -> dict:
    """
    Uses Chroma to find the most similar known health issue based on symptoms.
    """
    try:
        symptoms = extract_symptoms(symptoms)
        print(f"Extracted symptoms: {symptoms}")

        results = chroma_service.query(symptoms)

        if not results:
            raise ValueError("No results from Chroma")

        return {
            "issue": results[0].get("health_issue", "unknown"),
            "recommendation": results[0].get("advice", "Please consult a healthcare professional.")
        }

    except Exception as e:
        return {
            "issue": "unknown",
            "recommendation": "Please consult a healthcare professional."
        }

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
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a friendly healthcare assistant. "
                "You will ask the user how they are feeling and what symptoms they have. "
                "Then call the `symptom_check_api` tool to get the probable health issue and recommendation. "
                "Once you get the result, generate a clear, natural sentence for the user using the fields: "
                "`issue` (the probable health problem) and `recommendation` (what they should do). "
                "Always remind the user to see a doctor for confirmation. "
                "If needed, offer to book an in-person appointment by calling `book_appointment`. "
                "If the user doesn't provide a full date and time, ask for missing parts, "
                "then call the `parse_datetime` tool to get the absolute timestamp. "
                "Confirm this time with the user in natural language before booking. "
                "After confirmation, call `book_appointment` with the ISO datetime."

                "Example:"
                "Assistant: How are you feeling today? What symptoms do you have?"
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
                "Assistant: (call `book_appointment` with the ISO datetime)"
                "Assistant: 'Your appointment has been booked successfully.'"
            ),
            tools=[symptom_check_api, book_appointment, parse_datetime]
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