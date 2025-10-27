"""Check network connectivity and firewall for LiveKit."""
import socket
import subprocess
import sys


def check_dns_resolution(domain):
    """Check if domain resolves."""
    try:
        ip = socket.gethostbyname(domain)
        print(f"✅ DNS Resolution: {domain} → {ip}")
        return ip
    except socket.gaierror as e:
        print(f"❌ DNS Resolution failed for {domain}: {e}")
        return None


def check_tcp_port(host, port, timeout=5):
    """Check if TCP port is accessible."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"✅ TCP Port {port}: Accessible on {host}")
            return True
        else:
            print(f"❌ TCP Port {port}: NOT accessible on {host} (error code: {result})")
            return False
    except Exception as e:
        print(f"❌ TCP Port {port}: Error - {e}")
        return False


def check_udp_port(host, port):
    """Check if UDP port is open (basic check)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.sendto(b'', (host, port))
        sock.close()
        print(f"⚠️  UDP Port {port}: Cannot definitively test (UDP is stateless)")
        return True
    except Exception as e:
        print(f"⚠️  UDP Port {port}: {e}")
        return False


def check_websocket(url):
    """Check WebSocket connectivity."""
    try:
        # Extract host from wss:// URL
        host = url.replace('wss://', '').replace('ws://', '').split('/')[0].split(':')[0]
        port = 443 if 'wss://' in url else 80

        print(f"\nWebSocket: {url}")
        return check_tcp_port(host, port)
    except Exception as e:
        print(f"❌ WebSocket check failed: {e}")
        return False


def main():
    print("\n=== LiveKit Network Connectivity Check ===\n")

    # LiveKit domains
    livekit_cloud = "propelity-c34idwcr.livekit.cloud"
    sip_domain = "fj64knskkmf.sip.livekit.cloud"

    print("1. DNS Resolution:")
    livekit_ip = check_dns_resolution(livekit_cloud)
    sip_ip = check_dns_resolution(sip_domain)

    print("\n2. LiveKit WebSocket (for agent connection):")
    check_websocket("wss://propelity-c34idwcr.livekit.cloud")

    print("\n3. SIP Ports (for inbound calls):")
    print("   Checking common SIP ports on SIP domain:")

    if sip_ip:
        # SIP standard ports
        check_tcp_port(sip_ip, 5060)  # SIP TCP
        check_tcp_port(sip_ip, 5061)  # SIP TLS
        check_udp_port(sip_ip, 5060)  # SIP UDP

        # RTP ports (media)
        print("\n   Media (RTP) typically uses UDP 10000-20000")
        print("   (Not testing all RTP ports)")

    print("\n4. Firewall Check:")
    print("   If agent connects but calls fail, check:")
    print("   - Outbound: TCP 443 (WebSocket)")
    print("   - Outbound: TCP 5060, 5061 (SIP)")
    print("   - Outbound: UDP 5060 (SIP)")
    print("   - Outbound: UDP 10000-20000 (RTP media)")

    print("\n5. Required Firewall Rules:")
    print("   sudo ufw allow out 443/tcp    # WebSocket")
    print("   sudo ufw allow out 5060/tcp   # SIP TCP")
    print("   sudo ufw allow out 5061/tcp   # SIP TLS")
    print("   sudo ufw allow out 5060/udp   # SIP UDP")
    print("   sudo ufw allow out 10000:20000/udp  # RTP")

    print("\n=== Check Complete ===\n")


if __name__ == "__main__":
    main()
