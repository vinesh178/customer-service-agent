"""
Outbound call service to replace lk CLI usage.
Provides programmatic API for initiating customer service calls.
"""

import logging
import os
from uuid import uuid4

from dotenv import load_dotenv
from livekit import api

load_dotenv()

logger = logging.getLogger(__name__)


class OutboundCallService:
    def __init__(self):
        self.livekit_api_key = os.getenv("LIVEKIT_API_KEY")
        self.livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
        self.livekit_url = os.getenv("LIVEKIT_URL")
        self.sip_trunk_id = os.getenv("LIVEKIT_SIP_TRUNK_ID")

        if not all([self.livekit_api_key, self.livekit_api_secret, self.livekit_url]):
            raise ValueError("Missing required LiveKit environment variables")

        self.lk_api = api.LiveKitAPI(
            url=self.livekit_url,
            api_key=self.livekit_api_key,
            api_secret=self.livekit_api_secret,
        )

    async def make_call(self, phone_number: str) -> dict:
        """
        Initiate an outbound call to a customer.

        Args:
            phone_number: Customer's phone number (e.g., "+15551234567")

        Returns:
            Dict with call details including room_name and participant_id
        """
        # Format room name to match dispatch rule pattern: outbound_<caller>_<random>
        caller_clean = phone_number.replace("-", "")
        room_name = f"outbound_{caller_clean}_{uuid4().hex[:8]}"

        try:
            logger.info(
                f"Initiating outbound call to {phone_number} in room {room_name}"
            )

            # Create SIP participant for outbound call
            # The agent should be dispatched automatically via dispatch rules
            sip_request = api.CreateSIPParticipantRequest(
                room_name=room_name,
                sip_trunk_id=self.sip_trunk_id,
                sip_call_to=phone_number,
                participant_identity=f"caller-{phone_number}",
                participant_name=f"Customer {phone_number}",
                wait_until_answered=True,
            )

            participant = await self.lk_api.sip.create_sip_participant(sip_request)

            logger.info(f"SIP participant created: {participant.participant_id}")

            return {
                "success": True,
                "room_name": room_name,
                "participant_id": participant.participant_id,
                "phone_number": phone_number,
            }

        except api.TwirpError as e:
            logger.error(f"LiveKit API error: {e.message}")
            return {
                "success": False,
                "error": f"API Error: {e.message}",
                "phone_number": phone_number,
            }
        except Exception as e:
            logger.error(f"Unexpected error making call to {phone_number}: {e}")
            return {"success": False, "error": str(e), "phone_number": phone_number}

    async def close(self):
        """Clean up API client connections."""
        await self.lk_api.aclose()
