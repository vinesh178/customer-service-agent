"""Try different SIP URI formats to find the correct one."""
import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client


def test_sip_uri_formats():
    """Test different SIP URI formats to find the correct one."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    sip_uri = os.getenv("LIVEKIT_SIP_URI")

    client = Client(account_sid, auth_token)

    print("\n=== Testing SIP URI Formats ===\n")

    trunk_id = "ST_QFAtMWoaYMyq"
    sip_domain = sip_uri.replace("sip:", "").split(";")[0]
    
    # Different SIP URI formats to try
    formats_to_test = [
        f"sip:{trunk_id}@{sip_domain};transport=tcp",  # With trunk ID
        f"sip:{sip_domain};transport=tcp",              # Without trunk ID
        f"sip:{sip_domain}",                            # Without transport
        f"sip:{trunk_id}@{sip_domain}",                 # With trunk ID, no transport
    ]

    # Find LiveKit trunk
    trunks = client.trunking.v1.trunks.list()
    livekit_trunk = next(
        (trunk for trunk in trunks if trunk.friendly_name == "LiveKit Trunk"),
        None,
    )

    if not livekit_trunk:
        print("❌ LiveKit Trunk not found!")
        return

    print(f"Testing formats for trunk: {livekit_trunk.friendly_name}")
    print(f"Current SIP URI: {sip_uri}")
    print()

    # Get current origination URL
    origination_urls = livekit_trunk.origination_urls.list()
    if not origination_urls:
        print("❌ No origination URLs found!")
        return

    current_url = origination_urls[0]
    print(f"Current origination URL: {current_url.sip_url}")

    # Test each format
    for i, test_uri in enumerate(formats_to_test, 1):
        print(f"\n{i}. Testing: {test_uri}")
        try:
            # Try to update the origination URL
            updated_url = current_url.update(sip_url=test_uri)
            print(f"   ✅ SUCCESS! Updated to: {updated_url.sip_url}")
            
            # If successful, this is the correct format
            print(f"\n🎉 CORRECT SIP URI FORMAT FOUND: {test_uri}")
            print("This format works with Twilio!")
            return
            
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)[:100]}...")

    print("\n❌ None of the tested formats worked.")
    print("The issue might be with the SIP domain itself.")
    print("Let's check if we need to use a different LiveKit SIP domain.")


if __name__ == "__main__":
    test_sip_uri_formats()
