"""Test LiveKit SIP authentication and configuration."""
import logging
import os
import requests

from dotenv import load_dotenv


def test_livekit_sip_auth():
    """Test LiveKit SIP authentication and configuration."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    sip_uri = os.getenv("LIVEKIT_SIP_URI")

    print("\n=== LiveKit SIP Authentication Test ===\n")

    print(f"LiveKit URL: {livekit_url}")
    print(f"SIP URI: {sip_uri}")
    print(f"API Key: {livekit_api_key[:10]}..." if livekit_api_key else "Not set")
    print(f"API Secret: {'Set' if livekit_api_secret else 'Not set'}")

    # Test LiveKit API connectivity with proper URL
    if livekit_url and livekit_api_key and livekit_api_secret:
        # Convert WebSocket URL to HTTP URL
        http_url = livekit_url.replace("wss://", "https://").replace("ws://", "http://")
        
        print(f"\nTesting LiveKit API at: {http_url}")
        
        try:
            # Test basic connectivity
            response = requests.get(f"{http_url}/", timeout=10)
            print(f"✅ LiveKit API reachable (status: {response.status_code})")
            
            # Test SIP configuration via API
            headers = {
                "Authorization": f"Bearer {livekit_api_key}:{livekit_api_secret}"
            }
            
            # Try to list SIP trunks
            sip_response = requests.get(f"{http_url}/twirp/livekit.SIPService/ListSIPInboundTrunk", 
                                      headers=headers, timeout=10)
            
            if sip_response.status_code == 200:
                print("✅ SIP API accessible")
                data = sip_response.json()
                print(f"   Found {len(data.get('items', []))} inbound trunks")
            else:
                print(f"⚠️  SIP API returned status: {sip_response.status_code}")
                print(f"   Response: {sip_response.text[:200]}")
                
        except Exception as e:
            print(f"❌ LiveKit API test failed: {e}")

    # Check SIP URI format
    print(f"\nSIP URI Analysis:")
    if sip_uri.startswith("sip:"):
        print("✅ SIP URI format is correct")
        
        # Extract components
        sip_part = sip_uri.replace("sip:", "").split(";")[0]
        if ":" in sip_part:
            host, port = sip_part.split(":")
            print(f"   Host: {host}")
            print(f"   Port: {port}")
        else:
            print(f"   Host: {sip_part}")
            print(f"   Port: 5060 (default)")
            
        # Check for transport
        if "transport=tcp" in sip_uri:
            print("✅ TCP transport specified")
        else:
            print("⚠️  No transport specified (defaults to UDP)")
            
    else:
        print("❌ SIP URI format is incorrect")

    print("\n=== Authentication Test Complete ===\n")


if __name__ == "__main__":
    test_livekit_sip_auth()
