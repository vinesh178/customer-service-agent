"""Check if Twilio trunk has termination URI configured for inbound calls."""
import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client


def check_trunk_termination():
    """Check Twilio trunk termination configuration."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    sip_uri = os.getenv("LIVEKIT_SIP_URI")

    client = Client(account_sid, auth_token)

    print("\n=== Twilio Trunk Termination Check ===\n")

    # Find LiveKit trunk
    trunks = client.trunking.v1.trunks.list()
    livekit_trunk = next(
        (trunk for trunk in trunks if trunk.friendly_name == "LiveKit Trunk"),
        None,
    )

    if not livekit_trunk:
        print("❌ LiveKit Trunk not found!")
        return

    print(f"Trunk: {livekit_trunk.friendly_name}")
    print(f"SID: {livekit_trunk.sid}")
    print(f"Domain: {livekit_trunk.domain_name}\n")

    # Check origination URLs (outbound)
    print("Origination URLs (for outbound calls):")
    origination_urls = livekit_trunk.origination_urls.list()
    if origination_urls:
        for url in origination_urls:
            print(f"  ✅ {url.sip_url} (enabled: {url.enabled})")
    else:
        print("  ❌ No origination URLs configured")

    # Check termination URIs (inbound)
    print("\nTermination URIs (for inbound calls):")
    try:
        termination_uris = client.trunking.v1.trunks(
            livekit_trunk.sid
        ).terminating_sip_domain_uris.list()

        if termination_uris:
            for uri in termination_uris:
                print(f"  ✅ {uri.sip_domain_uri}")
        else:
            print("  ⚠️  No termination URIs found!")
            print(f"\n  This is likely the problem. The trunk needs to route")
            print(f"  inbound calls to LiveKit's SIP domain.")
            print(f"\n  Expected termination URI: {sip_uri}")
            print(f"  or: {sip_uri.replace('sip:', '')}")
    except Exception as e:
        print(f"  ❌ Error checking termination URIs: {e}")

    print("\n=== End Check ===\n")


if __name__ == "__main__":
    check_trunk_termination()
