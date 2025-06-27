# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LiveKit-based customer service agent that handles phone calls through SIP integration with Twilio. The agent represents "Dan and Dave's AI Consulting" and uses AI for voice interactions via OpenAI GPT-4o-mini, ElevenLabs TTS, and Deepgram STT.

**Target Use Case:** HVAC company automation for maintenance reminder calls and appointment scheduling. The system automates mundane employee tasks while maintaining service quality through AI-driven conversations.

## Architecture

**Backend (Python):**
- `backend/agent.py` - Main voice AI agent with dual-mode behavior (inbound/outbound calls)
- `backend/api.py` - FastAPI server for web interface integration
- `backend/services/` - Service layer for outbound call management
- `backend/scripts/` - Setup scripts for LiveKit telephony and call testing

**Frontend (React):**
- `frontend/src/App.tsx` - Main React app for call monitoring interface
- `frontend/src/components/` - React components for transcription display and speaking indicators

**Key Dependencies:**
- Backend: `livekit-agents`, `fastapi`, `langfuse`, `python-dotenv`
- Frontend: React 19, `@livekit/components-react`, TypeScript, Vite

## Development Commands

### Backend (Python with uv)
```bash
cd backend
uv sync                    # Install dependencies
uv run python agent.py dev # Start the voice agent in dev mode
uv run python api.py       # Start the FastAPI server
uv run ruff check          # Lint code
uv run ruff format         # Format code
```

### Frontend (Node.js)
```bash
cd frontend
npm install                # Install dependencies
npm run dev               # Start development server (port 3000)
npm run build             # Build for production
```

### Testing
```bash
cd backend
uv run python scripts/make_outbound_call.py "+15551234567"  # Make test outbound call
uv run python scripts/setup_livekit_telephony.py           # Setup LiveKit SIP integration
```

## Call Behavior Logic

The agent automatically adapts behavior based on room naming conventions:
- **Inbound calls** (room name starts with `inbound*`): Acts as customer service representative
- **Outbound calls** (room name starts with `outbound*`): Proactive caller with voicemail detection

**Three Main Call Flow Scenarios:**
1. **Outbound to Voicemail**: Detects voicemail and leaves personalized maintenance reminder message
2. **Outbound to Live Person**: Conducts full scheduling conversation with customer data lookup
3. **Inbound Callback**: Handles customer callbacks, integrates with scheduling system

**Key Features:**
- **Voicemail Detection**: Automatically detects answering machines vs. live pickup
- **Customer Database Integration**: Phone number lookup for personalized conversations
- **Equipment-Specific Scheduling**: References HVAC, hot water heater, furnace maintenance history
- **Service Area Routing**: Technician assignment based on ZIP codes

## Configuration

Environment variables are managed in `backend/.env`:
- LiveKit and Twilio SIP credentials
- OpenAI, ElevenLabs, Deepgram API keys
- Langfuse for conversation observability (optional)

SIP configuration templates are in `livekit-telephony-templates/`:
- `dispatch_rule.json.template`
- `inbound_trunk.json.template` 
- `outbound_trunk.json.template`
- `participant.json.template`

## Web Monitoring Interface

The React frontend provides real-time call monitoring:
- Auto-discovers active customer service calls every 5 seconds
- Provides live audio and transcription for supervisors
- Visual indicators for speaking participants
- API endpoints: `/api/rooms` (list active rooms), `/api/join-token` (generate access tokens)

## Code Style

- Python: Uses Ruff for linting and formatting (line length 88, target Python 3.11+)
- TypeScript: Standard React/TypeScript patterns with Vite build system
- Backend follows async/await patterns with LiveKit agents framework

## Key Integration Points

- LiveKit SIP service handles telephony routing
- Twilio provides SIP trunking and phone number management
- Agent sessions connect to LiveKit rooms for voice processing
- Langfuse integration tracks conversation analytics and observability

## Demo Implementation Scope

**Currently Implemented:**
- Voice AI agent with dual-mode behavior (inbound/outbound)
- Web monitoring interface for call supervision
- Basic voicemail detection and handling
- Customer data lookup and personalization
- LiveKit/Twilio SIP integration

**Demo Features (from DEMO.md):**
- Customer database with service history tracking
- Equipment-specific maintenance scheduling (HVAC, hot water heater, furnace)
- Automated scheduling system with calendar integration
- Service area mapping and technician routing
- Quality control with human oversight capabilities
- Call recording and transcript management options

**Advanced Features (Discussed but not fully implemented):**
- Automated cron job system for maintenance reminders
- Full customer database with comprehensive service history
- Production-ready queue management system
- Complex IVR routing and human escalation
- Multi-channel confirmations (email, SMS, call)