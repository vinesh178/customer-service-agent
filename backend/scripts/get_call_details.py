"""Get detailed error information for failed Twilio calls."""
import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client


def get_call_details():
    """Get detailed information for failed calls."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    client = Client(account_sid, auth_token)

    print("\n=== Detailed Call Error Analysis ===\n")

    # Get the most recent failed call details
    failed_calls = client.calls.list(
        status="failed",
        limit=3
    )

    for call in failed_calls:
        print(f"Call SID: {call.sid}")
        print(f"Status: {call.status}")
        print(f"Start Time: {call.start_time}")
        print(f"End Time: {call.end_time}")
        print(f"From: {call.from_formatted}")
        print(f"To: {call.to_formatted}")
        print(f"Direction: {call.direction}")
        print(f"Duration: {call.duration}")
        
        # Get detailed call information
        try:
            detailed_call = client.calls(call.sid).fetch()
            print(f"Error Code: {detailed_call.error_code}")
            print(f"Error Message: {detailed_call.error_message}")
            print(f"Price: {detailed_call.price}")
            print(f"Price Unit: {detailed_call.price_unit}")
        except Exception as e:
            print(f"Error fetching details: {e}")
        
        print("-" * 50)

    # Check if there are any SIP-specific errors
    print("\n=== SIP Call Analysis ===")
    sip_calls = client.calls.list(
        to="sip:fj64knskkmf.sip.livekit.cloud",
        limit=5
    )
    
    for call in sip_calls:
        print(f"SIP Call SID: {call.sid}")
        print(f"Status: {call.status}")
        print(f"Start Time: {call.start_time}")
        print(f"From: {call.from_formatted}")
        print(f"To: {call.to_formatted}")
        
        try:
            detailed_call = client.calls(call.sid).fetch()
            print(f"Error Code: {detailed_call.error_code}")
            print(f"Error Message: {detailed_call.error_message}")
        except Exception as e:
            print(f"Error fetching SIP call details: {e}")
        
        print("-" * 30)

    print("\n=== Analysis Complete ===\n")


if __name__ == "__main__":
    get_call_details()
