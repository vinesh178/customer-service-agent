"""Fix phone number to use trunk only (remove Voice URL for Australian numbers)."""
import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client


def fix_phone_number_trunk():
    """Remove Voice URL and use trunk only for Australian numbers."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    # Get the phone number
    numbers = client.incoming_phone_numbers.list(phone_number=phone_number)

    if not numbers:
        logging.error(f"Phone number {phone_number} not found!")
        return

    number = numbers[0]
    logging.info(f"Fixing phone number: {number.sid}")
    logging.info(f"Current Voice URL: {number.voice_url}")
    logging.info(f"Current Trunk SID: {number.trunk_sid}")

    # Update to use trunk only (remove Voice URL)
    number.update(
        voice_url=None,  # Remove Voice URL
        voice_method=None,  # Remove Voice Method
        trunk_sid=number.trunk_sid,  # Keep trunk assignment
    )

    logging.info(f"✅ Phone number configured to use trunk only")
    logging.info(f"   Trunk SID: {number.trunk_sid}")
    logging.info(f"   Voice URL: None (using trunk)")
    logging.info(f"\nNow when someone calls {phone_number}:")
    logging.info(f"  1. Twilio routes call through trunk")
    logging.info(f"  2. Trunk forwards to LiveKit SIP")
    logging.info(f"  3. LiveKit creates room via dispatch rule")
    logging.info(f"  4. Agent joins room and handles call")


if __name__ == "__main__":
    fix_phone_number_trunk()