import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import deepgram, openai, cartesia, silero

from properties import get_all_properties, get_property_details, check_availability

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mtr-agent")

# Store leads in memory (just for demo - logs to console)
leads = []


SYSTEM_PROMPT = """You are a friendly leasing assistant for Boulder Mid-Term Rentals. You help prospective tenants learn about available furnished rental properties.

## Your personality
- Warm, helpful, and efficient
- Conversational but professional
- Keep responses concise (1-3 sentences) since this is voice

## What you can help with
- Describe available properties (we have a downtown studio and a North Boulder 2-bedroom)
- Answer questions about rent, amenities, pet policies, availability dates
- Collect contact information from interested renters

## What you should know
- All properties are furnished mid-term rentals (1-11 month stays)
- We cater to traveling professionals, remote workers, and people in transition
- Application process: online application, background check, first month + security deposit
- We respond to applications within 24-48 hours

## Conversation flow
1. Greet warmly and ask how you can help
2. Answer their questions using the property tools
3. If they're interested, collect their name and email
4. Confirm next steps and end professionally

If someone asks something you can't help with, politely say you're just the leasing assistant and can take a message for the property manager."""


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


async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the voice agent."""
    
    logger.info(f"Agent starting for room: {ctx.room.name}")
    
    await ctx.connect()
    
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o"),
        tts=cartesia.TTS(),
    )
    
    await session.start(
        room=ctx.room,
        agent=MTRAgent(),
    )
    
    # Initial greeting
    await session.generate_reply(
        instructions="Greet the user warmly and ask how you can help them with their housing search today."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
