"""Configure Twilio trunk properly for Australian inbound calls."""
import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client


def configure_trunk_for_australia():
    """Configure trunk termination for Australian inbound calls."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    sip_uri = os.getenv("LIVEKIT_SIP_URI")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    print("\n=== Configuring Trunk for Australian Calls ===\n")

    # Find LiveKit trunk
    trunks = client.trunking.v1.trunks.list()
    livekit_trunk = next(
        (trunk for trunk in trunks if trunk.friendly_name == "LiveKit Trunk"),
        None,
    )

    if not livekit_trunk:
        print("❌ LiveKit Trunk not found!")
        return

    print(f"Configuring trunk: {livekit_trunk.friendly_name}")
    print(f"SID: {livekit_trunk.sid}")

    # Extract SIP domain from SIP URI
    sip_domain = sip_uri.replace("sip:", "").split(";")[0]
    print(f"SIP Domain: {sip_domain}")

    try:
        # Configure termination URI for inbound calls
        # This tells Twilio where to route inbound calls
        termination_uri = client.trunking.v1.trunks(livekit_trunk.sid).terminating_sip_domain_uris.create(
            sip_domain_uri=sip_domain
        )
        print(f"✅ Termination URI configured: {termination_uri.sip_domain_uri}")
        
    except Exception as e:
        print(f"⚠️  Termination URI configuration: {e}")
        # This might already be configured or not needed

    # Ensure phone number is properly configured
    numbers = client.incoming_phone_numbers.list(phone_number=phone_number)
    if numbers:
        number = numbers[0]
        print(f"\nPhone Number: {phone_number}")
        print(f"Current Voice URL: {number.voice_url}")
        print(f"Current Trunk SID: {number.trunk_sid}")
        
        # For Australian numbers, we should use trunk routing
        if number.trunk_sid != livekit_trunk.sid:
            print("Updating phone number to use LiveKit trunk...")
            number.update(trunk_sid=livekit_trunk.sid)
            print("✅ Phone number updated to use LiveKit trunk")
        else:
            print("✅ Phone number already using LiveKit trunk")

    print("\n=== Configuration Complete ===")
    print("Your Australian number should now work for inbound calls!")
    print(f"Test by calling: {phone_number}")


if __name__ == "__main__":
    configure_trunk_for_australia()
