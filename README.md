# shelob

Service fingerprinter: grab a banner, parse product/version, look up known exploits with searchsploit.

## Usage

```bash
shelob <host> -p <port>
shelob scanme.nmap.org -p 22
shelob scanme.nmap.org -p 80 -t 3
```

## What I learned

- Banner grabbing (passive SSH vs active HTTP HEAD)
- Parsing product/version with regex
- Calling searchsploit from Python via subprocess (split args, don't pass one string)
- Mapping banner → version → exploit DB (CPTS enum workflow)

## Legal

Only use on systems you own or have explicit permission to test.
