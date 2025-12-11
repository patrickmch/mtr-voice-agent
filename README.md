# MTR Voice Agent

**Call 518-930-9526** to try it out!

AI-powered voice agent for mid-term rental property inquiries. Built with LiveKit, Claude, and real-time speech processing.

## Background

**Mid-term rentals (MTR)** are furnished properties rented for 1-6 months, serving traveling healthcare professionals, remote workers, and people in transition.

**The problem:** Property managers spend hours answering repetitive inquiries—availability, pricing, pet policies, amenities—often outside business hours.

**The solution:** An AI voice agent that handles initial inquiries 24/7, answers questions from real property data, and captures leads for follow-up.

This is a standalone proof-of-concept that will be integrated into [Midway](https://github.com/patrickmch/midway), a property management platform.

## How It Works

1. Caller connects via LiveKit room
2. Speech-to-text converts voice to text (Deepgram)
3. Claude processes the query and calls property tools
4. Text-to-speech responds naturally (Cartesia)
5. Lead info is captured for follow-up

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | LiveKit Agents SDK (Python) |
| LLM | Claude Sonnet 4 (Anthropic) |
| STT | Deepgram Nova-3 |
| TTS | Cartesia |
| VAD | Silero |
| Database | PostgreSQL (Railway) |
| Hosting | Railway + LiveKit Cloud |

## Project Structure

```
mtr-voice-agent/
├── agent.py              # Voice agent with function tools
├── properties.py         # Database queries for property data
├── seed_properties.py    # One-time script to populate property data
├── requirements.txt      # Python dependencies
├── Procfile              # Railway deployment config
└── .env.example          # Environment variable template
```

## Setup

### Prerequisites
- Python 3.9+
- LiveKit Cloud account
- API keys: Anthropic, Deepgram, Cartesia
- PostgreSQL database (optional, for property data)

### Installation

```bash
git clone https://github.com/patrickmch/mtr-voice-agent.git
cd mtr-voice-agent

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and fill in your keys:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
ANTHROPIC_API_KEY=your_anthropic_key
DEEPGRAM_API_KEY=your_deepgram_key
CARTESIA_API_KEY=your_cartesia_key
MIDWAY_DATABASE_URL=postgresql://user:pass@host:port/db
```

### Running

```bash
# Development mode (local mic/speakers)
python agent.py dev

# Connect to LiveKit Cloud
python agent.py start
```

### Testing

Use the [LiveKit Agents Playground](https://agents-playground.livekit.io/) to interact with your agent.

## Deployment

Deployed on Railway with GitHub integration. Push to `master` triggers automatic deployment.

Environment variables must be configured in Railway dashboard.

## Demo Conversation

```
User: "Hi, I'm looking for a furnished rental."
Agent: [Greets, asks about preferences]

User: "What do you have available?"
Agent: [Calls list_available_properties, describes units]

User: "Tell me more about the Boulder place."
Agent: [Calls get_property_info, gives details]

User: "I'm interested. My email is john@example.com"
Agent: [Calls save_lead, confirms follow-up]
```
