"""Assign the phone number to the LiveKit trunk for proper routing."""
import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client


def fix_phone_number_trunk():
    """Assign the phone number to the LiveKit trunk."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    # Find LiveKit trunk
    trunks = client.trunking.v1.trunks.list()
    livekit_trunk = next(
        (trunk for trunk in trunks if trunk.friendly_name == "LiveKit Trunk"),
        None,
    )

    if not livekit_trunk:
        logging.error("LiveKit Trunk not found!")
        return

    logging.info(f"Found LiveKit Trunk: {livekit_trunk.sid}")

    # Get the phone number
    numbers = client.incoming_phone_numbers.list(phone_number=phone_number)

    if not numbers:
        logging.error(f"Phone number {phone_number} not found!")
        return

    number = numbers[0]
    logging.info(f"Found phone number: {number.sid}")

    # Update the phone number to use the trunk
    number.update(
        trunk_sid=livekit_trunk.sid,
        voice_url="",  # Clear voice URL since we're using trunk
    )

    logging.info(f"✅ Phone number {phone_number} connected to LiveKit Trunk")
    logging.info("Calls to this number will now route to LiveKit SIP")


if __name__ == "__main__":
    fix_phone_number_trunk()
