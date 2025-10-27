import asyncio
import logging
import os

from dotenv import load_dotenv
from livekit import api
from twilio.rest import Client


def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        logging.error(f"Environment variable '{var_name}' not set.")
        exit(1)
    return value


def create_livekit_trunk(client, sip_uri):
    domain_name = f"livekit-trunk-{os.urandom(4).hex()}.pstn.twilio.com"
    trunk = client.trunking.v1.trunks.create(
        friendly_name="LiveKit Trunk",
        domain_name=domain_name,
    )
    trunk.origination_urls.create(
        sip_url=sip_uri,
        weight=1,
        priority=1,
        enabled=True,
        friendly_name="LiveKit SIP URI",
    )
    logging.info("Created new LiveKit Trunk.")
    return trunk


async def create_inbound_trunk(lk_api, phone_number):
    """Create inbound SIP trunk using LiveKit API."""
    trunk_request = api.CreateSIPInboundTrunkRequest(
        trunk=api.SIPInboundTrunkInfo(
            name="Inbound LiveKit Trunk",
            numbers=[phone_number],
        )
    )

    try:
        trunk = await lk_api.sip.create_sip_inbound_trunk(trunk_request)
        logging.info(f"Created inbound trunk with ID: {trunk.sip_trunk_id}")
        return trunk.sip_trunk_id
    except api.TwirpError as e:
        logging.error(f"Error creating inbound trunk: {e.message}")
        return None


async def create_dispatch_rule(lk_api, trunk_id):
    """Create dispatch rule using LiveKit API."""
    dispatch_request = api.CreateSIPDispatchRuleRequest(
        name="Inbound Dispatch Rule",
        trunk_ids=[trunk_id],
        rule=api.SIPDispatchRule(
            dispatch_rule_individual=api.SIPDispatchRuleIndividual(
                room_prefix="inbound-",
            )
        ),
    )

    try:
        rule = await lk_api.sip.create_sip_dispatch_rule(dispatch_request)
        logging.info(f"Created dispatch rule with ID: {rule.sip_dispatch_rule_id}")
        return rule.sip_dispatch_rule_id
    except api.TwirpError as e:
        logging.error(f"Error creating dispatch rule: {e.message}")
        return None


async def setup_telephony():
    """Main setup function."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    # Get environment variables
    account_sid = get_env_var("TWILIO_ACCOUNT_SID")
    auth_token = get_env_var("TWILIO_AUTH_TOKEN")
    phone_number = get_env_var("TWILIO_PHONE_NUMBER")
    sip_uri = get_env_var("LIVEKIT_SIP_URI")
    livekit_url = get_env_var("LIVEKIT_URL")
    livekit_api_key = get_env_var("LIVEKIT_API_KEY")
    livekit_api_secret = get_env_var("LIVEKIT_API_SECRET")

    # Setup Twilio trunk
    twilio_client = Client(account_sid, auth_token)
    existing_trunks = twilio_client.trunking.v1.trunks.list()
    livekit_trunk = next(
        (trunk for trunk in existing_trunks if trunk.friendly_name == "LiveKit Trunk"),
        None,
    )

    if not livekit_trunk:
        livekit_trunk = create_livekit_trunk(twilio_client, sip_uri)
    else:
        logging.info("LiveKit Trunk already exists. Using the existing trunk.")

    # Setup LiveKit inbound trunk and dispatch rule
    lk_api = api.LiveKitAPI(
        url=livekit_url,
        api_key=livekit_api_key,
        api_secret=livekit_api_secret,
    )

    try:
        # Check if inbound trunk already exists
        list_request = api.ListSIPInboundTrunkRequest()
        existing_inbound_trunks = await lk_api.sip.list_sip_inbound_trunk(list_request)
        inbound_trunk_id = None

        for trunk in existing_inbound_trunks.items:
            if phone_number in trunk.numbers:
                logging.info(
                    f"Inbound trunk already exists for {phone_number}: {trunk.sip_trunk_id}"
                )
                inbound_trunk_id = trunk.sip_trunk_id
                break

        if not inbound_trunk_id:
            inbound_trunk_id = await create_inbound_trunk(lk_api, phone_number)

        if inbound_trunk_id:
            # Check if dispatch rule exists
            list_rules_request = api.ListSIPDispatchRuleRequest()
            dispatch_rules_response = await lk_api.sip.list_sip_dispatch_rule(list_rules_request)
            rule_exists = any(inbound_trunk_id in rule.trunk_ids for rule in dispatch_rules_response.items)

            if not rule_exists:
                await create_dispatch_rule(lk_api, inbound_trunk_id)
            else:
                logging.info("Dispatch rule already exists for this trunk.")

        logging.info("\n=== Setup Complete ===")
        logging.info(f"Twilio phone number: {phone_number}")
        logging.info(f"Inbound trunk ID: {inbound_trunk_id}")
        logging.info("Call the Twilio number to connect to your agent.")

    finally:
        await lk_api.aclose()


def main():
    asyncio.run(setup_telephony())


if __name__ == "__main__":
    main()
