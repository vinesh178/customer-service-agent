"""
Outbound call service to replace lk CLI usage.
Provides programmatic API for initiating customer service calls.
"""

import json
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

    async def make_call(
        self,
        phone_number: str,
        customer_data: dict | None = None,
        room_name: str | None = None,
    ) -> dict:
        """
        Initiate an outbound call to a customer.

        Args:
            phone_number: Customer's phone number (e.g., "+15551234567")
            customer_data: Optional customer information for agent context
            room_name: Optional room name, auto-generated if not provided

        Returns:
            Dict with call details including room_name and participant_id
        """
        if not room_name:
            # Format room name to match dispatch rule pattern: call-_<caller>_<random>
            caller_clean = phone_number.replace("+", "").replace("-", "")
            room_name = f"call-_{caller_clean}_{uuid4().hex[:8]}"

        # Prepare metadata for agent context
        metadata = {
            "phone_number": phone_number,
            "customer_data": customer_data or {},
            "call_type": "outbound_service",
        }

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
                # Pass customer data as metadata
                participant_metadata=json.dumps(metadata),
            )

            participant = await self.lk_api.sip.create_sip_participant(sip_request)

            logger.info(f"SIP participant created: {participant.participant_id}")

            return {
                "success": True,
                "room_name": room_name,
                "participant_id": participant.participant_id,
                "phone_number": phone_number,
                "customer_data": customer_data,
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

    async def get_active_calls(self) -> dict:
        """Get list of active SIP participants."""
        try:
            participants = await self.lk_api.sip.list_sip_participant(
                api.ListSIPParticipantRequest()
            )

            active_calls = []
            for participant in participants.sip_participants:
                active_calls.append(
                    {
                        "participant_id": participant.participant_id,
                        "phone_number": participant.sip_call_to,
                        "room_name": participant.room_name,
                        "call_status": participant.sip_call_status,
                    }
                )

            return {
                "success": True,
                "active_calls": active_calls,
                "count": len(active_calls),
            }

        except Exception as e:
            logger.error(f"Error getting active calls: {e}")
            return {"success": False, "error": str(e)}

    async def hangup_call(self, participant_id: str) -> dict:
        """Hang up a specific call by participant ID."""
        try:
            await self.lk_api.sip.delete_sip_participant(
                api.DeleteSIPParticipantRequest(sip_participant_id=participant_id)
            )

            logger.info(f"Hung up call for participant: {participant_id}")
            return {"success": True, "participant_id": participant_id}

        except Exception as e:
            logger.error(f"Error hanging up call {participant_id}: {e}")
            return {"success": False, "error": str(e)}

    async def close(self):
        """Clean up API client connections."""
        await self.lk_api.aclose()


# Convenience functions for direct usage
async def make_customer_call(phone_number: str, customer_data: dict = None) -> dict:
    """
    Simple function to make an outbound customer service call.

    Example:
        result = await make_customer_call(
            "+15551234567",
            {"name": "John Doe", "service_due": "HVAC maintenance"}
        )
    """
    service = OutboundCallService()
    return await service.make_call(phone_number, customer_data)
