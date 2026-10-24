#!/usr/bin/env python3
import socket
import argparse
import subprocess
import re

def grab_banner(host, port, timeout=2.0):
    """Return the banner string, or None."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        try:
            data = s.recv(1024)
        except socket.timeout:
            s.sendall(f"HEAD / HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())
            data = s.recv(1024)
        s.close()
        text = data.decode(errors="ignore").strip()
        if not text:
            return None
        if any(c not in "\r\n\t" and not c.isprintable() for c in text):
            return None
        return text
    except OSError:
        return None

def extract_product(banner):
    """Pull a searchsploit-friendly product/version from a banner."""
    if not banner:
        return None

    # HTTP: prefer the Server header if present
    for line in banner.splitlines():
        if line.lower().startswith("server:"):
            banner = line.split(":", 1)[1].strip()
            break

    # OpenSSH: SSH-2.0-OpenSSH_6.6.1p1 ...
    m = re.search(r"OpenSSH[_/ ]([\d.]+)", banner, re.I)
    if m:
        return f"openssh {m.group(1)}"

    # Apache: Apache/2.4.7
    m = re.search(r"Apache/([\d.]+)", banner, re.I)
    if m:
        return f"apache {m.group(1)}"

    # fallback: first token-ish chunk
    return banner.split()[0][:40]


def search_vulns(query):
    """Run searchsploit and return matching lines."""
    if not query:
        return []
    try:
        result = subprocess.run(
            ["searchsploit", *query.split()],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        print("[!] searchsploit not found — install exploitdb or use Kali")
        return []
    except subprocess.TimeoutExpired:
        print("[!] searchsploit timed out")
        return []

    lines = []
    for line in result.stdout.splitlines():
        line = line.rstrip()
        if not line or set(line) <= {"-", " "}:
            continue
        if "Exploit Title" in line or "Shellcodes:" in line or "Papers:" in line:
            continue
        lines.append(line)
    return lines


def main():
    parser = argparse.ArgumentParser(description="Fingerprint a service and look up vulns")
    parser.add_argument("host", help="Target host")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to fingerprint")
    parser.add_argument("-t", "--timeout", type=float, default=2.0)
    args = parser.parse_args()

    print(f"[*] Fingerprinting {args.host}:{args.port}")
    banner = grab_banner(args.host, args.port, args.timeout)
    if not banner:
        print("[-] No banner")
        return

    print(f"[+] Banner: {banner.splitlines()[0]}")
    product = extract_product(banner)
    if not product:
        print("[-] Could not parse product/version")
        return

    print(f"[+] Product: {product}")
    print(f"[*] searchsploit {product}")
    hits = search_vulns(product)
    if not hits:
        print("[-] No exploit entries (or searchsploit missing)")
        return
    for line in hits[:15]:
        print(line)
    if len(hits) > 15:
        print(f"... and {len(hits) - 15} more")


if __name__ == "__main__":
    main()
