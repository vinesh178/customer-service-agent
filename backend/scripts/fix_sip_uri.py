"""Fix the SIP URI to include the trunk ID."""
import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client


def fix_sip_uri():
    """Update Twilio trunk with correct SIP URI including trunk ID."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    sip_uri = os.getenv("LIVEKIT_SIP_URI")

    client = Client(account_sid, auth_token)

    print("\n=== Fixing SIP URI with Trunk ID ===\n")

    # The correct SIP URI should include the trunk ID
    # Current: sip:fj64knskkmf.sip.livekit.cloud
    # Correct: sip:ST_QFAtMWoaYMyq@fj64knskkmf.sip.livekit.cloud;transport=tcp
    
    trunk_id = "ST_QFAtMWoaYMyq"  # From the get_livekit_sip_uri.py output
    sip_domain = sip_uri.replace("sip:", "").split(";")[0]
    correct_sip_uri = f"sip:{trunk_id}@{sip_domain};transport=tcp"
    
    print(f"Current SIP URI: {sip_uri}")
    print(f"Correct SIP URI: {correct_sip_uri}")

    # Find LiveKit trunk
    trunks = client.trunking.v1.trunks.list()
    livekit_trunk = next(
        (trunk for trunk in trunks if trunk.friendly_name == "LiveKit Trunk"),
        None,
    )

    if not livekit_trunk:
        print("❌ LiveKit Trunk not found!")
        return

    print(f"\nUpdating trunk: {livekit_trunk.friendly_name}")
    print(f"Trunk SID: {livekit_trunk.sid}")

    # Update origination URL with correct SIP URI
    origination_urls = livekit_trunk.origination_urls.list()
    
    for url in origination_urls:
        print(f"Current origination URL: {url.sip_url}")
        
        # Update the URL
        url.update(sip_url=correct_sip_uri)
        print(f"✅ Updated origination URL: {correct_sip_uri}")

    print("\n=== SIP URI Fix Complete ===")
    print("The trunk now has the correct SIP URI with trunk ID!")
    print("Try calling your number again.")


if __name__ == "__main__":
    fix_sip_uri()
