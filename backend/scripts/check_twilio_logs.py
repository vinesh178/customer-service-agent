"""Check Twilio logs for call failures and issues."""
import logging
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from twilio.rest import Client


def check_twilio_logs():
    """Check Twilio logs for recent call failures."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    print("\n=== Twilio Call Logs Analysis ===\n")

    # Check recent calls to your number
    print(f"Recent calls to {phone_number}:")
    try:
        calls = client.calls.list(
            to=phone_number,
            limit=10
        )
        
        if not calls:
            print("  No recent calls found")
        else:
            for call in calls:
                status_emoji = "✅" if call.status == "completed" else "❌" if call.status == "failed" else "⚠️"
                print(f"  {status_emoji} {call.start_time} - Status: {call.status}")
                if call.status == "failed":
                    print(f"      Error Code: {getattr(call, 'error_code', 'Unknown')}")
                    print(f"      Error Message: {getattr(call, 'error_message', 'Unknown')}")
                    print(f"      From: {call.from_formatted}")
                    print(f"      Call SID: {call.sid}")
                elif call.status == "completed":
                    print(f"      Duration: {call.duration}s")
                    print(f"      From: {call.from_formatted}")
                    
    except Exception as e:
        print(f"  Error fetching calls: {e}")

    # Check recent calls from your number (outbound)
    print(f"\nRecent calls from {phone_number}:")
    try:
        outbound_calls = client.calls.list(
            from_=phone_number,
            limit=5
        )
        
        if not outbound_calls:
            print("  No recent outbound calls found")
        else:
            for call in outbound_calls:
                status_emoji = "✅" if call.status == "completed" else "❌" if call.status == "failed" else "⚠️"
                print(f"  {status_emoji} {call.start_time} - Status: {call.status}")
                if call.status == "failed":
                    print(f"      Error Code: {getattr(call, 'error_code', 'Unknown')}")
                    print(f"      Error Message: {getattr(call, 'error_message', 'Unknown')}")
                    print(f"      To: {call.to_formatted}")
                    print(f"      Call SID: {call.sid}")
                    
    except Exception as e:
        print(f"  Error fetching outbound calls: {e}")

    # Check account status and balance
    print(f"\nAccount Information:")
    try:
        account = client.api.accounts(account_sid).fetch()
        print(f"  Account Status: {account.status}")
        print(f"  Account Type: {account.type}")
        
        # Check balance
        balance = client.balance.fetch()
        print(f"  Account Balance: ${balance.balance} {balance.currency}")
        
    except Exception as e:
        print(f"  Error fetching account info: {e}")

    # Check phone number status
    print(f"\nPhone Number Status:")
    try:
        numbers = client.incoming_phone_numbers.list(phone_number=phone_number)
        if numbers:
            number = numbers[0]
            print(f"  Number Status: Active")
            print(f"  Capabilities: Voice: {number.capabilities.get('voice', 'Unknown')}")
            print(f"  Capabilities: SMS: {number.capabilities.get('sms', 'Unknown')}")
            print(f"  Region: {number.region}")
            print(f"  Locality: {number.locality}")
        else:
            print(f"  ❌ Phone number not found!")
            
    except Exception as e:
        print(f"  Error fetching phone number info: {e}")

    print("\n=== End Log Analysis ===\n")


if __name__ == "__main__":
    check_twilio_logs()
