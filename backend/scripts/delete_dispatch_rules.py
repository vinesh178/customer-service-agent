"""Delete all dispatch rules to allow recreation with correct settings."""
import asyncio
import logging
import os

from dotenv import load_dotenv
from livekit import api


async def delete_all_dispatch_rules():
    """Delete all dispatch rules."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([livekit_url, livekit_api_key, livekit_api_secret]):
        logging.error("Missing LiveKit environment variables")
        return

    lk_api = api.LiveKitAPI(
        url=livekit_url,
        api_key=livekit_api_key,
        api_secret=livekit_api_secret,
    )

    try:
        # List all dispatch rules
        list_request = api.ListSIPDispatchRuleRequest()
        response = await lk_api.sip.list_sip_dispatch_rule(list_request)

        if not response.items:
            logging.info("No dispatch rules found.")
            return

        # Delete each rule
        for rule in response.items:
            logging.info(f"Deleting dispatch rule: {rule.sip_dispatch_rule_id}")
            delete_request = api.DeleteSIPDispatchRuleRequest(
                sip_dispatch_rule_id=rule.sip_dispatch_rule_id
            )
            await lk_api.sip.delete_sip_dispatch_rule(delete_request)
            logging.info(f"Deleted: {rule.sip_dispatch_rule_id}")

        logging.info("All dispatch rules deleted successfully.")

    except api.TwirpError as e:
        logging.error(f"Error: {e.message}")
    finally:
        await lk_api.aclose()


if __name__ == "__main__":
    asyncio.run(delete_all_dispatch_rules())
