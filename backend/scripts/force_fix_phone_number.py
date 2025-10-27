"""Force remove Voice URL and ensure trunk-only configuration."""
import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client


def force_fix_phone_number():
    """Force remove Voice URL and ensure trunk-only configuration."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    print("\n=== Force Fixing Phone Number Configuration ===\n")

    # Get the phone number
    numbers = client.incoming_phone_numbers.list(phone_number=phone_number)

    if not numbers:
        print(f"❌ Phone number {phone_number} not found!")
        return

    number = numbers[0]
    print(f"Phone Number SID: {number.sid}")
    print(f"Current Voice URL: {number.voice_url}")
    print(f"Current Voice Method: {number.voice_method}")
    print(f"Current Trunk SID: {number.trunk_sid}")

    # Force update with explicit None values
    try:
        updated_number = number.update(
            voice_url="",  # Empty string instead of None
            voice_method="",  # Empty string instead of None
            trunk_sid=number.trunk_sid,  # Keep trunk
        )
        
        print("✅ Phone number updated successfully")
        print(f"New Voice URL: '{updated_number.voice_url}'")
        print(f"New Voice Method: '{updated_number.voice_method}'")
        print(f"Trunk SID: {updated_number.trunk_sid}")
        
    except Exception as e:
        print(f"❌ Error updating phone number: {e}")

    # Verify the update
    print("\nVerifying configuration...")
    updated_numbers = client.incoming_phone_numbers.list(phone_number=phone_number)
    if updated_numbers:
        updated_number = updated_numbers[0]
        print(f"Verified Voice URL: '{updated_number.voice_url}'")
        print(f"Verified Voice Method: '{updated_number.voice_method}'")
        print(f"Verified Trunk SID: {updated_number.trunk_sid}")
        
        if not updated_number.voice_url and updated_number.trunk_sid:
            print("✅ Configuration is correct - using trunk only")
        else:
            print("⚠️  Configuration may still have issues")

    print("\n=== Fix Complete ===")
    print("Try calling your number now!")


if __name__ == "__main__":
    force_fix_phone_number()
