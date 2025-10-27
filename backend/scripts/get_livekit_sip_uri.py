"""Get the LiveKit SIP inbound URI that Twilio should call."""
import asyncio
import logging
import os

from dotenv import load_dotenv
from livekit import api


async def get_livekit_sip_uri():
    """Get LiveKit's SIP URI for inbound calls."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")

    lk_api = api.LiveKitAPI(
        url=livekit_url,
        api_key=livekit_api_key,
        api_secret=livekit_api_secret,
    )

    try:
        # Get inbound trunk info
        list_req = api.ListSIPInboundTrunkRequest()
        trunks = await lk_api.sip.list_sip_inbound_trunk(list_req)

        if not trunks.items:
            print("❌ No inbound trunks found!")
            return

        for trunk in trunks.items:
            print(f"\n=== LiveKit Inbound Trunk ===")
            print(f"Trunk ID: {trunk.sip_trunk_id}")
            print(f"Name: {trunk.name}")
            print(f"Numbers: {', '.join(trunk.numbers)}")

            # Get trunk info which should have the SIP URI
            info_req = api.SIPTrunkInfo(sip_trunk_id=trunk.sip_trunk_id)

            print(f"\n📞 Configure Twilio phone number to call:")
            print(f"   Voice URL: Use the following SIP URI")
            print(f"   SIP URI format: Check LiveKit dashboard for inbound trunk URI")
            print(f"\n   The URI should look like:")
            print(f"   sip:<trunk-id>@<your-livekit-sip-domain>")

    except api.TwirpError as e:
        print(f"❌ Error: {e.message}")
    finally:
        await lk_api.aclose()


if __name__ == "__main__":
    asyncio.run(get_livekit_sip_uri())
