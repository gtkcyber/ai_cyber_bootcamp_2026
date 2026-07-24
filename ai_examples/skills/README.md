# Example Agent Skills

Two real, working examples of the skill format from the "AI Skills vs. Tools"
talk. A skill is packaged know-how an agent loads on demand: a `SKILL.md` of
instructions plus optional reference files it opens only when needed.

## What's here

- **`triage-suspicious-url/`** — a defensive SOC workflow for triaging a
  suspicious URL or domain. Shows judgment (defang, detonate in a sandbox),
  tool orchestration (whois, TLS, threat intel), and a house output format.
  - `SKILL.md` — when to use it and the steps.
  - `references/ioc-format.md` — the IOC output spec, loaded only at the
    reporting step (progressive disclosure).

- **`commit-hygiene/`** — enforces a git commit format and splits unrelated
  changes.
  - `SKILL.md` — the procedure.
  - `references/conventional-commits.md` — the type-prefix table.

## The two moving parts of every skill

- **Frontmatter `description`** is the *trigger*. It is the only part always
  in context, so it must say exactly *when* to use the skill.
- **Reference files** hold the bulky, rarely-changing detail. They stay on
  disk until a step actually needs them, keeping the always-on footprint small.

To use one in Claude Code, copy a skill folder into `.claude/skills/` in your
project.
