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
    parser.add_argument("phone_number", help="Phone number to call (e.g., +15551234567)")
    parser.add_argument("--customer-name", help="Customer name")
    parser.add_argument("--service-due", help="Service type due")
    parser.add_argument("--list-calls", action="store_true", help="List active calls")
    parser.add_argument("--hangup", help="Hang up call by participant ID")
    
    args = parser.parse_args()
    
    service = OutboundCallService()
    
    try:
        if args.list_calls:
            result = await service.get_active_calls()
            print(json.dumps(result, indent=2))
            return
        
        if args.hangup:
            result = await service.hangup_call(args.hangup)
            print(json.dumps(result, indent=2))
            return
        
        # Make outbound call
        customer_data = {}
        if args.customer_name:
            customer_data["name"] = args.customer_name
        if args.service_due:
            customer_data["service_due"] = args.service_due
        
        result = await service.make_call(args.phone_number, customer_data)
        print(json.dumps(result, indent=2))
        
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())