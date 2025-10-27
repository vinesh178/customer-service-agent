#!/bin/bash
# Fix inbound trunk to allow Twilio IPs using lk CLI

set -e

source .env

echo "=== Fixing LiveKit Inbound Trunk to Allow Twilio IPs ==="
echo ""

# Get current trunk ID
TRUNK_ID=$(lk sip inbound list --json | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['sip_trunk_id'] if data else '')" 2>/dev/null || echo "")

if [ -z "$TRUNK_ID" ]; then
    echo "❌ No inbound trunk found!"
    exit 1
fi

echo "Current trunk: $TRUNK_ID"
echo ""

# Delete old trunk
echo "Deleting old trunk..."
lk sip inbound delete $TRUNK_ID

# Create new trunk with Twilio IPs allowed
echo "Creating new trunk with Twilio IP allowlist..."

# Twilio SIP IP ranges
cat > /tmp/inbound_trunk_twilio.json << 'EOF'
{
  "trunk": {
    "name": "Inbound LiveKit Trunk",
    "numbers": ["${TWILIO_PHONE_NUMBER}"],
    "allowedAddresses": [
      "54.172.60.0/23",
      "54.244.51.0/24",
      "177.71.206.192/26",
      "54.65.63.192/26",
      "54.169.127.128/26",
      "54.252.254.64/26",
      "35.156.191.128/25",
      "54.171.127.192/26"
    ]
  }
}
EOF

# Replace placeholder with actual phone number
sed -i.bak "s/\${TWILIO_PHONE_NUMBER}/$TWILIO_PHONE_NUMBER/g" /tmp/inbound_trunk_twilio.json

# Create trunk
NEW_TRUNK_ID=$(lk sip inbound create /tmp/inbound_trunk_twilio.json | grep -o 'ST_[A-Za-z0-9]*')

echo ""
echo "✅ Trunk created: $NEW_TRUNK_ID"
echo "   Twilio IPs are now allowed!"
echo ""
echo "Now recreate the dispatch rule..."

# Cleanup
rm -f /tmp/inbound_trunk_twilio.json /tmp/inbound_trunk_twilio.json.bak

# Run the setup script to recreate dispatch rule
uv run python scripts/setup_livekit_telephony.py

echo ""
echo "=== Fix Complete! ==="
echo "Try calling $TWILIO_PHONE_NUMBER now!"
