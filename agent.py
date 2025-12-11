import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions, AgentServer
from livekit.plugins import deepgram, cartesia, silero, anthropic

from properties import get_all_properties, get_property_details, check_availability

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mtr-agent")

# Create server for explicit agent dispatch (required for telephony)
server = AgentServer()

# Store leads in memory (just for demo - logs to console)
leads = []


SYSTEM_PROMPT = """You work at Assurance Property Management answering calls about furnished rentals.

Talk like a normal person on the phone - brief, natural, helpful. No corporate speak or long explanations. One or two sentences max per response.

Use your tools to look up property info - don't guess or make things up. If asked about availability, check using the tools - properties have availability dates in the system.

These are furnished month-to-month rentals. To apply: online application, background check, first month plus deposit. We get back to people in a day or two.

If you can't help with something, offer to take a message for Patrick."""


class MTRAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=SYSTEM_PROMPT,
        )

    @agents.llm.function_tool
    async def list_available_properties(self) -> str:
        """Get a summary of all available rental properties."""
        logger.info("Tool called: list_available_properties")
        return get_all_properties()

    @agents.llm.function_tool
    async def get_property_info(self, property_name: str) -> str:
        """Get detailed information about a specific property.
        
        Args:
            property_name: The name or type of property (e.g., 'studio', '2-bedroom', 'downtown', 'north boulder')
        """
        logger.info(f"Tool called: get_property_info({property_name})")
        return get_property_details(property_name)

    @agents.llm.function_tool
    async def check_property_availability(
        self, 
        property_name: str, 
        move_in_date: str, 
        move_out_date: str
    ) -> str:
        """Check if a property is available for specific dates.
        
        Args:
            property_name: The name or type of property
            move_in_date: When the renter wants to move in
            move_out_date: When the renter plans to move out
        """
        logger.info(f"Tool called: check_property_availability({property_name}, {move_in_date}, {move_out_date})")
        return check_availability(property_name, move_in_date, move_out_date)

    @agents.llm.function_tool
    async def save_lead(
        self,
        name: str,
        email: str,
        property_interest: str = "",
        notes: str = ""
    ) -> str:
        """Save a potential renter's contact information for follow-up.
        
        Args:
            name: The renter's name
            email: The renter's email address
            property_interest: Which property they're interested in (optional)
            notes: Any additional notes about their inquiry (optional)
        """
        lead = {
            "name": name,
            "email": email,
            "property_interest": property_interest,
            "notes": notes
        }
        leads.append(lead)
        logger.info(f"Lead saved: {lead}")
        
        return f"I've saved your information. Someone from our team will reach out to {email} within 24 hours to help you with next steps for the {property_interest if property_interest else 'property'}."


@server.rtc_session(agent_name="mtr-voice-agent")
async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the voice agent."""

    logger.info(f"Agent starting for room: {ctx.room.name}")

    await ctx.connect()

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=anthropic.LLM(model="claude-sonnet-4-20250514"),
        tts=cartesia.TTS(),
    )

    await session.start(
        room=ctx.room,
        agent=MTRAgent(),
    )

    # Initial greeting
    await session.generate_reply(
        instructions="Answer the phone naturally: 'Hi, Assurance Property Management, how can I help you?'"
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
