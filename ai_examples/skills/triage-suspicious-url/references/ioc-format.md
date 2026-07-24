# IOC Output Format

Emit one block per triage. Every network indicator MUST be defanged
(`hxxp`, `[.]`). No live or clickable links anywhere in the report.

## Fields (one object per indicator)

| field       | values / format                                  |
|-------------|--------------------------------------------------|
| type        | `url` \| `domain` \| `ipv4` \| `sha256` \| `sender` |
| value       | defanged string (`hxxp`, `[.]`)                  |
| verdict     | `benign` \| `suspicious` \| `malicious`          |
| confidence  | `low` \| `medium` \| `high`                      |
| tlp         | `CLEAR` \| `GREEN` \| `AMBER` \| `RED`            |
| first_seen  | ISO-8601 UTC, e.g. `2026-07-24T14:03:00Z`        |
| source      | where observed: `email`, `proxy log`, `user report` |

## Example

```json
{
  "type": "domain",
  "value": "evil[.]com",
  "verdict": "malicious",
  "confidence": "high",
  "tlp": "AMBER",
  "first_seen": "2026-07-24T14:03:00Z",
  "source": "reported-phish"
}
```

## Rules

- Prefer SHA-256 for file hashes. Include MD5 only if that is all the tool
  returned.
- When the verdict is `malicious`, append a suggested block-list line, e.g.
  `block: evil[.]com`.
- TLP defaults to `AMBER` unless the reporter specified otherwise.
