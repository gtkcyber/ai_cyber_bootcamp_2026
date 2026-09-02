# Doctrine: scale and cost

## Scale playbook

Escalate only as far as the data forces:

in-memory → validity-preserving sampling → out-of-core → distributed

Each step up carries cost implications (compute, latency, operational
complexity) — don't reach for distributed tooling because it's available;
reach for it because the prior step is provably insufficient.

## Cost doctrine

- Compute budget classes and cost-per-experiment awareness.
- Selection economics: compute/latency are **selection inputs**, not an
  afterthought applied post-hoc to whatever was already chosen.

## Referenced delta-only by

- `ds-scoping` — kill-check.
- `ds-model` — selection economics.
- `ds-mlops` — serving/retraining cost.

Each states only its delta against this doctrine and links back here — this
file is the one place the doctrine itself is taught.
