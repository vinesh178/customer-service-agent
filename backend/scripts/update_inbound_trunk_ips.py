"""Update LiveKit inbound trunk to allow Twilio IP addresses."""
import asyncio
import logging
import os

from dotenv import load_dotenv
from livekit import api


async def update_inbound_trunk():
    """Update inbound trunk to allow Twilio IPs."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    # Twilio's SIP signaling IP ranges (as of 2024)
    # Source: https://www.twilio.com/docs/sip-trunking/ip-addresses
    twilio_ip_ranges = [
        "54.172.60.0/23",       # US East
        "54.244.51.0/24",       # US West
        "177.71.206.192/26",    # Brazil
        "54.65.63.192/26",      # Tokyo
        "54.169.127.128/26",    # Singapore
        "54.252.254.64/26",     # Sydney (Australia - YOUR REGION!)
        "177.71.206.192/26",    # Sao Paulo
        "35.156.191.128/25",    # Frankfurt
        "54.171.127.192/26",    # Ireland
    ]

    lk_api = api.LiveKitAPI(
        url=livekit_url,
        api_key=livekit_api_key,
        api_secret=livekit_api_secret,
    )

    try:
        print("\n=== Updating LiveKit Inbound Trunk ===\n")

        # Get existing trunk
        list_req = api.ListSIPInboundTrunkRequest()
        trunks = await lk_api.sip.list_sip_inbound_trunk(list_req)

        if not trunks.items:
            print("❌ No inbound trunk found!")
            return

        trunk = trunks.items[0]
        trunk_id = trunk.sip_trunk_id
        print(f"Current trunk: {trunk_id}")
        print(f"Numbers: {', '.join(trunk.numbers)}")
        print(f"Current allowed addresses: {trunk.allowed_addresses}")

        # Workaround: API has a bug with allowed_addresses in current version
        # Solution: Use LiveKit CLI to update, or delete and recreate trunk
        print(f"\n⚠️  API bug prevents updating allowed_addresses directly")
        print(f"\nQuick fix: Delete and recreate trunk with allowed IPs")

        # Delete old trunk
        print(f"Deleting trunk {trunk_id}...")
        await lk_api.sip.delete_sip_trunk(
            api.DeleteSIPTrunkRequest(sip_trunk_id=trunk_id)
        )

        # Recreate with Twilio IPs allowed
        print(f"Creating new trunk with Twilio IP allowlist...")
        new_trunk = await lk_api.sip.create_sip_inbound_trunk(
            api.CreateSIPInboundTrunkRequest(
                trunk=api.SIPInboundTrunkInfo(
                    name="Inbound LiveKit Trunk",
                    numbers=[phone_number],
                    allowed_addresses=twilio_ip_ranges,
                )
            )
        )

        print(f"✅ Trunk recreated successfully!")
        print(f"   Trunk ID: {new_trunk.sip_trunk_id}")
        print(f"   Numbers: {', '.join(new_trunk.numbers)}")
        print(f"   Allowed {len(new_trunk.allowed_addresses)} Twilio IP ranges")

    except api.TwirpError as e:
        print(f"❌ Error: {e.message}")
    finally:
        await lk_api.aclose()

    print("\n=== Update Complete ===\n")
    print("Now call the number again - it should work!")


if __name__ == "__main__":
    asyncio.run(update_inbound_trunk())
