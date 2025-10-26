import asyncio
import json
import random
from livekit import api
from dotenv import load_dotenv

load_dotenv(".env.local")

async def trigger_feedback_call(phone_number: str, appointment_id: str):
    print(f"Triggering feedback call to {phone_number} for appointment {appointment_id}...")
    room_name = f"outbound-{''.join(str(random.randint(0,9)) for _ in range(10))}"
    metadata = json.dumps({"phone_number": phone_number, "appointment_id": appointment_id})

    async with api.LiveKitAPI() as lk:
        await lk.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="my-telephony-agent",
                room=room_name,
                metadata=metadata
            )
        )
    print("✅ Dispatch created successfully.")

if __name__ == "__main__":
    asyncio.run(trigger_feedback_call("+12096841862", "68fe1148af65e089f32fe5f5"))