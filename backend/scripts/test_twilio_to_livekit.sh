#!/bin/bash
# Test if Twilio can reach LiveKit SIP

echo "=== Testing Twilio → LiveKit SIP Connectivity ==="
echo ""

# Get SIP URI from .env
source .env 2>/dev/null || true

if [ -z "$LIVEKIT_SIP_URI" ]; then
    echo "❌ LIVEKIT_SIP_URI not set in .env"
    exit 1
fi

SIP_DOMAIN=$(echo $LIVEKIT_SIP_URI | sed 's/sip://' | sed 's/;.*//')

echo "SIP Domain: $SIP_DOMAIN"
echo ""

# Test DNS resolution
echo "1. DNS Resolution:"
dig +short $SIP_DOMAIN || nslookup $SIP_DOMAIN
echo ""

# Test SIP port connectivity
echo "2. SIP TCP Port 5060:"
timeout 3 bash -c "cat < /dev/null > /dev/tcp/$SIP_DOMAIN/5060" 2>&1 && echo "✅ Port 5060 is open" || echo "❌ Port 5060 is closed or unreachable"
echo ""

echo "3. SIP TLS Port 5061:"
timeout 3 bash -c "cat < /dev/null > /dev/tcp/$SIP_DOMAIN/5061" 2>&1 && echo "✅ Port 5061 is open" || echo "❌ Port 5061 is closed or unreachable"
echo ""

echo "4. Check Twilio Phone Number Configuration:"
uv run python scripts/check_twilio_config.py 2>&1 | grep -A 5 "Phone Number:"
echo ""

echo "=== Test Complete ==="
echo ""
echo "If all checks pass but calls still fail, check Twilio console for errors:"
echo "  https://console.twilio.com/us1/monitor/logs/calls"
