# shelob — Cheat Sheet

> Service **fingerprinter**: grab one banner → parse product/version (OpenSSH, Apache) → `searchsploit` lookup.
> Repo: <https://github.com/BBARIBEAU1/shelob> · Authorized labs / own hosts only.

## Install / run
```bash
# source: ~/projects/fingerprinter/shelob.py   (needs: exploitdb → searchsploit)
sudo apt install exploitdb          # already on Kali
chmod +x ~/projects/fingerprinter/shelob.py
ln -sf ~/projects/fingerprinter/shelob.py ~/.local/bin/shelob
shelob -h
```

## Syntax
```text
shelob <host> -p PORT [-t SECS]
```

| Flag | Long | Default | Meaning |
|---|---|---|---|
| `host` | — | *(required)* | Target host / IPv4 |
| `-p` | `--port` | *(required)* | **One** TCP port (int) |
| `-t` | `--timeout` | `2.0` | Connect / recv timeout, seconds |
| `-h` | `--help` | — | Usage |

## Examples
```bash
sudo service ssh start && shelob 127.0.0.1 -p 22      # local OpenSSH
shelob 127.0.0.1 -p 8000                               # python http.server (Server: header)
shelob 127.0.0.1 -p 80 -t 3                            # local Apache, slower wait
shelob scanme.nmap.org -p 22                           # Nmap's permitted practice host
for p in 22 80; do shelob 127.0.0.1 -p $p; done        # several ports = loop
searchsploit openssh 9.6                               # re-run lookup by hand / tweak query
```

## Output
```text
[*] Fingerprinting 127.0.0.1:22
[+] Banner: SSH-2.0-OpenSSH_9.x ...
[+] Product: openssh 9.x
[*] searchsploit openssh 9.x
<up to 15 exploit-db lines>  ... and N more
```

## Workflow
1. **taran-tula** `-b` → open ports + raw banners.
2. `shelob host -p <port>` on each interesting one → product/version → exploit-db titles.
3. Verify versions manually (`searchsploit -x <id>` to read, not run) — CPTS enum habit.

## Gotchas
- One port per run. No range, no list — loop in bash.
- Parser knows **OpenSSH** and **Apache** only. Anything else → first word of banner (≤40 chars) as the query — often too vague.
- `Server:` header is preferred for HTTP; HTTP `HEAD` is sent only after a passive recv **times out** (so wait ≈ `-t`).
- Binary / non-printable banners → `[-] No banner`. TLS ports (443) usually give nothing.
- searchsploit matches text, not version ranges — "no hits" ≠ "not vulnerable"; distro backports (e.g. `OpenSSH_9.6p1 Ubuntu`) lie about patch level.
- Missing searchsploit → `[!] searchsploit not found` (install `exploitdb`).
