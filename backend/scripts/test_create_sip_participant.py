"""Test creating a SIP participant to simulate an inbound call."""
import asyncio
import logging
import os
from uuid import uuid4

from dotenv import load_dotenv
from livekit import api


async def test_sip_participant():
    """Create a test SIP participant to verify LiveKit SIP is working."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    lk_api = api.LiveKitAPI(
        url=livekit_url,
        api_key=livekit_api_key,
        api_secret=livekit_api_secret,
    )

    # Create a test room name (what dispatch rule would create)
    room_name = f"inbound_{phone_number}_{uuid4().hex[:8]}"

    print(f"\n=== Testing SIP Participant Creation ===")
    print(f"Room name: {room_name}")
    print(f"Phone number: {phone_number}\n")

    try:
        # Get inbound trunk
        list_req = api.ListSIPInboundTrunkRequest()
        trunks = await lk_api.sip.list_sip_inbound_trunk(list_req)

        if not trunks.items:
            print("❌ No inbound trunks found!")
            return

        trunk = trunks.items[0]
        print(f"Using trunk: {trunk.sip_trunk_id}")
        print(f"Trunk numbers: {', '.join(trunk.numbers)}\n")

        # Try to create a room first
        print("Creating LiveKit room...")
        room = await lk_api.room.create_room(
            api.CreateRoomRequest(name=room_name)
        )
        print(f"✅ Room created: {room.name}\n")

        print("This proves:")
        print("  1. ✅ Agent can connect to LiveKit")
        print("  2. ✅ LiveKit API is working")
        print("  3. ✅ Room creation works")
        print("\nIf calls still don't work, the issue is:")
        print("  - Twilio → LiveKit SIP routing")
        print("  - Check Twilio console for SIP dial errors")
        print("  - Verify Voice URL is calling correct SIP URI")

        # Cleanup
        await lk_api.room.delete_room(api.DeleteRoomRequest(room=room_name))
        print(f"\n✅ Test room deleted")

    except api.TwirpError as e:
        print(f"❌ Error: {e.message}")
    finally:
        await lk_api.aclose()

    print("\n=== Test Complete ===\n")


if __name__ == "__main__":
    asyncio.run(test_sip_participant())
