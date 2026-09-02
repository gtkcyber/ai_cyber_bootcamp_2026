# Realized-outcome measurement and reconciliation

## Realized-outcome

**Literature name**: Online Controlled Experiments (OCE).

**Canonical reference**: Kohavi, Tang, Xu, *Trustworthy Online Controlled
Experiments*, Cambridge University Press 2020 — https://experimentguide.com/.

When the deployment shipped behind a randomized control (A/B, holdout,
shadow), realized-outcome measurement is an OCE readout, and this skill
inherits Kohavi et al.'s trust checks before treating any number as valid:

- **Randomization integrity** — assignment actually happened as designed;
  spot-check the split, don't assume the config matches reality.
- **SUTVA** (stable unit treatment value assumption) — one unit's outcome
  isn't contaminated by another unit's treatment. Violated routinely by
  shared inventory, social features, or a marketplace's two-sided market —
  flag rather than assume it holds.
- **Sample-ratio mismatch (SRM)** as a trust check — if the observed
  treatment/control split diverges from the designed ratio beyond chance,
  the whole readout is untrustworthy until the mismatch is explained, not
  just noted.
- **Statistical vs. practical significance** — a metric move can be
  statistically real and business-irrelevant, or the reverse in a
  low-power design. Report both, never one standing in for the other.

When the deployment shipped with no randomized control at all (a full
rollout, no holdout), there is no OCE to read — the realized-outcome number
is a pre/post comparison, and this skill's job is to say so explicitly
rather than let a pre/post delta pass as if it were an experiment result.
That's a distinct failure mode from SRM or SUTVA: it isn't a broken
experiment, it's the absence of one.

## Reconciliation protocol

The core of this subfield: compare what was measured (`realized_outcome`)
against what was intended.

- `target` — was the thing that moved the thing the task card named?
- `metric` — was the *metric* used to declare success the one the task
  card committed to, or did a different metric get substituted along the
  way (a common drift point between scoping and launch)?
- `baseline` — is the realized-outcome comparison against the baseline the
  task card fixed, or against some other reference point chosen after the
  fact (a form of post-hoc goalpost-moving)?

`reconciliation` states match or mismatch on each of the three, plainly.

## What this subfield does not compute

Reconciliation states whether the metric moved and whether that move matches
what was promised.

- Observational/quasi-experimental setting (no holdout, no randomized
  control) → `ds-causal`, cited via its `identification_statement`.
- A holdout or randomized control already exists as part of the rollout →
  `ds-stats`, cited via its `design_analysis_memo`.

This skill's gate requires the citation, not the derivation: a
reconciliation that asserts causal attribution without naming which of the
two supplied the identification fails the gate stated in `SKILL.md`.
