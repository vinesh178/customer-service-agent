import asyncio
import logging

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
    get_job_context,
)
from livekit.api import DeleteRoomRequest
from livekit.plugins import (
    deepgram,
    elevenlabs,
    openai,
    silero,
)
from livekit.plugins.turn_detector.english import EnglishModel

logger = logging.getLogger("customer_service_agent")
logger.setLevel(logging.INFO)

load_dotenv()


class Assistant(Agent):
    def __init__(self, ctx: JobContext) -> None:
        # Hardcode customer data for testing
        customer_name = "John Smith"
        service_type = "HVAC maintenance"

        # Determine call direction from room name
        is_outbound = ctx.room.name.startswith("outbound")

        if is_outbound:
            # Outbound call - agent is calling the customer
            instructions = f"You are Sarah from Dan and Dave's AI Consulting in Tahoe, CA. You are calling {customer_name} about their {service_type}.\n\nAfter your initial greeting, listen for the response:\n\n• LIVE CUSTOMER: If they respond conversationally, have a normal business conversation about their service.\n\n• VOICEMAIL: If you hear voicemail prompts ('at the tone', 'leave a message', 'please record'), use the leave_voicemail tool. Provide a complete professional message including: your name (Sarah), company (Dan and Dave's AI Consulting in Tahoe), reason for calling ({service_type}), and request to call back.\n\nSpeak directly to the customer, not about them."
            self.initial_prompt = "Greet the customer and introduce yourself as Sarah from Dan and Dave's AI Consulting calling about their service."
            tools = [leave_voicemail]
        else:
            # Inbound call - customer is calling the company
            instructions = "You are Sarah, a customer service representative for Dan and Dave's AI Consulting in Tahoe, CA. A customer has called and you need to help them.\n\nIntroduce yourself professionally and ask how you can help them today. Listen to their needs and provide helpful information about our AI consulting services, technical support, or connect them with the right person if needed.\n\nBe friendly, professional, and focused on solving their problem or answering their questions."
            self.initial_prompt = "Answer the phone professionally and introduce yourself as Sarah from Dan and Dave's AI Consulting, then ask how you can help them today."
            tools = []

        super().__init__(instructions=instructions, tools=tools)
        self.ctx = ctx
        self.is_outbound = is_outbound


@function_tool
async def leave_voicemail(run_ctx: RunContext, voicemail_message: str):
    """Leave a voicemail message after detecting a voicemail system. Use AFTER hearing the greeting/beep. The voicemail_message parameter should contain the complete message you want to leave for the customer."""
    ctx = get_job_context()
    await run_ctx.session.say(voicemail_message, allow_interruptions=False)
    await asyncio.sleep(1)

    # let the agent finish speaking
    current_speech = run_ctx.session.current_speech
    if current_speech:
        await current_speech.wait_for_playout()

    await ctx.api.room.delete_room(
        DeleteRoomRequest(
            room=ctx.room.name,
        )
    )
    await run_ctx.session.aclose()
    await ctx.shutdown("voicemail_left")


async def connect(ctx: JobContext, timeout: float = 3.0, max_retries: int = 3) -> bool:
    """Connect to LiveKit room with timeout, retries, and error handling."""
    logger.info(f"CONNECTING TO ROOM: '{ctx.room.name}'")

    for attempt in range(max_retries):
        try:
            await asyncio.wait_for(ctx.connect(), timeout=timeout)
            logger.info(f"CONNECTED TO ROOM: '{ctx.room.name}'")
            return True
        except TimeoutError:
            logger.warning(f"Connection attempt {attempt + 1} timed out")
            if attempt == max_retries - 1:
                logger.error("All connection attempts failed")
                ctx.shutdown("connection_timeout")
                return False
            await asyncio.sleep(2.0)  # Wait before retry
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            ctx.shutdown("connection_failed")
            return False

    return False


async def entrypoint(ctx: JobContext):
    session = AgentSession(
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(),
        vad=silero.VAD.load(),
        turn_detection=EnglishModel(),
    )

    assistant = Assistant(ctx)
    await session.start(
        room=ctx.room,
        agent=assistant,
        room_input_options=RoomInputOptions(),
    )

    if not await connect(ctx):
        return

    await session.generate_reply(
        instructions=assistant.initial_prompt,
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
