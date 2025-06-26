#!/usr/bin/env python3
"""
CLI script to make outbound calls using the OutboundCallService.
Replaces the need for `lk sip participant create`.
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.outbound_call_service import OutboundCallService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="Make outbound customer service calls")
    parser.add_argument(
        "phone_number", help="Phone number to call (e.g., +15551234567)"
    )
    args = parser.parse_args()

    service = OutboundCallService()
    try:
        result = await service.make_call(args.phone_number)
        print(json.dumps(result, indent=2))
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
