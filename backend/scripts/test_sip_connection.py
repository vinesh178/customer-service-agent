"""Test SIP connection to LiveKit from production."""
import logging
import os
import socket
import urllib.parse

from dotenv import load_dotenv


def test_sip_connection():
    """Test if LiveKit SIP endpoint is reachable."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    sip_uri = os.getenv("LIVEKIT_SIP_URI")
    livekit_url = os.getenv("LIVEKIT_URL")

    print("\n=== LiveKit SIP Connection Test ===\n")

    if not sip_uri:
        print("❌ LIVEKIT_SIP_URI not set in environment")
        return

    print(f"SIP URI: {sip_uri}")
    print(f"LiveKit URL: {livekit_url}")

    # Extract host and port from SIP URI
    try:
        # Parse sip:host:port;transport=tcp
        sip_part = sip_uri.replace("sip:", "").split(";")[0]
        if ":" in sip_part:
            host, port = sip_part.split(":")
            port = int(port)
        else:
            host = sip_part
            port = 5060  # Default SIP port

        print(f"Host: {host}")
        print(f"Port: {port}")

        # Test TCP connection
        print(f"\nTesting TCP connection to {host}:{port}...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10 second timeout
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ TCP connection successful to {host}:{port}")
            else:
                print(f"❌ TCP connection failed to {host}:{port}")
                print(f"   Error code: {result}")
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")

        # Test DNS resolution
        print(f"\nTesting DNS resolution for {host}...")
        try:
            ip_addresses = socket.gethostbyname_ex(host)
            print(f"✅ DNS resolution successful:")
            for ip in ip_addresses[2]:
                print(f"   {host} -> {ip}")
        except Exception as e:
            print(f"❌ DNS resolution failed: {e}")

    except Exception as e:
        print(f"❌ Error parsing SIP URI: {e}")

    # Test LiveKit API connectivity
    if livekit_url:
        print(f"\nTesting LiveKit API connectivity...")
        try:
            import requests
            response = requests.get(f"{livekit_url}/", timeout=10)
            print(f"✅ LiveKit API reachable (status: {response.status_code})")
        except Exception as e:
            print(f"❌ LiveKit API unreachable: {e}")

    print("\n=== Connection Test Complete ===\n")


if __name__ == "__main__":
    test_sip_connection()
