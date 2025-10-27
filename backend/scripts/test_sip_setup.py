"""Test the complete SIP setup end-to-end."""
import asyncio
import logging
import os

from dotenv import load_dotenv
from livekit import api


async def test_sip_setup():
    """Verify all SIP components are properly configured."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    print("\n=== LiveKit SIP Configuration Test ===\n")

    lk_api = api.LiveKitAPI(
        url=livekit_url,
        api_key=livekit_api_key,
        api_secret=livekit_api_secret,
    )

    try:
        # Check inbound trunks
        print("Inbound Trunks:")
        list_trunk_req = api.ListSIPInboundTrunkRequest()
        trunks = await lk_api.sip.list_sip_inbound_trunk(list_trunk_req)

        if not trunks.items:
            print("  ⚠️  No inbound trunks found!")
        else:
            for trunk in trunks.items:
                print(f"  - ID: {trunk.sip_trunk_id}")
                print(f"    Name: {trunk.name}")
                print(f"    Numbers: {', '.join(trunk.numbers)}")

        # Check dispatch rules
        print("\nDispatch Rules:")
        list_rules_req = api.ListSIPDispatchRuleRequest()
        rules = await lk_api.sip.list_sip_dispatch_rule(list_rules_req)

        if not rules.items:
            print("  ⚠️  No dispatch rules found!")
        else:
            for rule in rules.items:
                print(f"  - ID: {rule.sip_dispatch_rule_id}")
                print(f"    Name: {rule.name}")
                print(f"    Trunk IDs: {', '.join(rule.trunk_ids)}")
                if rule.rule.dispatch_rule_individual:
                    print(f"    Room Prefix: {rule.rule.dispatch_rule_individual.room_prefix}")
                    print(f"    Pin Required: {rule.rule.dispatch_rule_individual.pin_required}")

        # Verify configuration
        print("\n=== Configuration Verification ===")

        trunk_has_number = any(
            phone_number in trunk.numbers for trunk in trunks.items
        )
        if trunk_has_number:
            print(f"✅ Phone number {phone_number} is in an inbound trunk")
        else:
            print(f"❌ Phone number {phone_number} NOT found in any trunk")

        if rules.items:
            rule = rules.items[0]
            if rule.rule.dispatch_rule_individual:
                prefix = rule.rule.dispatch_rule_individual.room_prefix
                print(f"✅ Dispatch rule will create rooms: {prefix}<phone_number>")

                if prefix == "inbound_":
                    print("✅ Room prefix matches agent expectations (inbound_)")
                else:
                    print(f"⚠️  Room prefix '{prefix}' may not match agent expectations")
        else:
            print("❌ No dispatch rules configured")

        print("\n=== Test Complete ===\n")

    except api.TwirpError as e:
        print(f"❌ Error: {e.message}")
    finally:
        await lk_api.aclose()


if __name__ == "__main__":
    asyncio.run(test_sip_setup())
