"""Check Twilio trunk configuration to verify it's routing to LiveKit."""
import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client


def check_twilio_config():
    """Check Twilio trunk and phone number configuration."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    print("\n=== Twilio Configuration Check ===\n")

    # Check trunks
    print("Trunks:")
    trunks = client.trunking.v1.trunks.list()
    for trunk in trunks:
        print(f"  - {trunk.friendly_name} (SID: {trunk.sid})")
        print(f"    Domain: {trunk.domain_name}")

        # Get origination URLs
        origination_urls = trunk.origination_urls.list()
        print(f"    Origination URLs:")
        for url in origination_urls:
            print(f"      - {url.sip_url} (enabled: {url.enabled})")

    # Check phone number
    print(f"\nPhone Number: {phone_number}")
    numbers = client.incoming_phone_numbers.list(phone_number=phone_number)

    for number in numbers:
        print(f"  - Friendly Name: {number.friendly_name}")
        print(f"  - Voice URL: {number.voice_url}")
        print(f"  - Voice Method: {number.voice_method}")
        print(f"  - Trunk SID: {number.trunk_sid}")

        if not number.trunk_sid:
            print("\n⚠️  WARNING: Phone number is NOT connected to a trunk!")
            print("    You need to assign the LiveKit trunk to this phone number.")

    print("\n=== End Configuration Check ===\n")


if __name__ == "__main__":
    check_twilio_config()
