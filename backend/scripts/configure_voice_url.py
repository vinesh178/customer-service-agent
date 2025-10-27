"""Configure Twilio phone number to route inbound calls to LiveKit SIP."""
import logging
import os
import urllib.parse

from dotenv import load_dotenv
from twilio.rest import Client


def configure_voice_url():
    """Set phone number Voice URL to dial LiveKit SIP inbound trunk."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    sip_uri = os.getenv("LIVEKIT_SIP_URI")

    # Create TwiML that dials LiveKit SIP
    # Format: sip:<trunk-id>@<sip-domain>
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Dial><Sip>{sip_uri};transport=tcp</Sip></Dial></Response>'
    voice_url = f"https://twimlets.com/echo?Twiml={urllib.parse.quote(twiml)}"

    client = Client(account_sid, auth_token)

    # Get the phone number
    numbers = client.incoming_phone_numbers.list(phone_number=phone_number)

    if not numbers:
        logging.error(f"Phone number {phone_number} not found!")
        return

    number = numbers[0]
    logging.info(f"Configuring phone number: {number.sid}")
    logging.info(f"SIP URI: {sip_uri}")

    # Update to use Voice URL (not trunk) for inbound calls
    number.update(
        voice_url=voice_url,
        voice_method="GET",
        trunk_sid=None,  # Remove trunk assignment
    )

    logging.info(f"✅ Phone number configured to route inbound calls to LiveKit")
    logging.info(f"   Voice URL: {voice_url}")
    logging.info(f"\nNow when someone calls {phone_number}:")
    logging.info(f"  1. Twilio executes TwiML")
    logging.info(f"  2. TwiML dials {sip_uri}")
    logging.info(f"  3. LiveKit creates room via dispatch rule")
    logging.info(f"  4. Agent joins room and handles call")


if __name__ == "__main__":
    configure_voice_url()
