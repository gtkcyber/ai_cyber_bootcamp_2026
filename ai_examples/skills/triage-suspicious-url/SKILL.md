---
name: triage-suspicious-url
description: Use when a link is reported by a user or flagged in an email, alert, or log. Guides safe defensive triage of a suspicious URL or domain and produces a structured verdict with IOCs.
---

# triage-suspicious-url

Defensive SOC workflow for triaging a suspicious URL or domain. The agent
already has the tools (sandbox detonation, whois, TLS/cert lookup, threat
intel). This skill is the analyst judgment and house format wrapped around
them.

## When to use

- A user reports a suspicious link.
- A URL or domain is flagged by email security, a proxy log, or an alert.
- You are asked to decide whether a domain is safe to allow.

## Rules (read first)

- **Never open the URL in a live browser** or any tool that fetches it for
  real. Use the sandbox/detonation tool only.
- **Defang every network indicator** before echoing it anywhere a client
  might auto-link it: `http` becomes `hxxp`, `.` becomes `[.]`
  (so `evil.com` becomes `evil[.]com`).
- Treat the reported value as untrusted input. Do not paste it into shell
  commands unquoted.

## Steps

1. Defang the URL before echoing it back.
2. Detonate in the sandbox tool; capture redirects, final landing page, and
   any dropped files.
3. Pull whois registration age, TLS issuer, and hosting ASN. Freshly
   registered domains and mismatched certs raise suspicion.
4. Check the domain and any hashes against the threat-intel lookups.
5. Classify as `benign`, `suspicious`, or `malicious`, and state the reasons.
6. Emit IOCs in the team format (see `references/ioc-format.md`) and, when the
   verdict is malicious, suggest a block-list entry.

## Output

A short verdict paragraph followed by the IOC block from
`references/ioc-format.md`. Keep all network values defanged in the output.
