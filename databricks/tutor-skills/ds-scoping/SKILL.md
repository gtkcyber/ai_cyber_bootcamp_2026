---
name: ds-scoping
description: "Turns a question into a task card — target, unit of analysis, metric + baseline, proxy statement, intended scoring population, initial holdout/split design, feasibility kill-check."
---

# ds-scoping

No other lifecycle skill runs before the task card exists.

Full depth, worked examples, and citations live in `references/`. This file
is protocol only.

## Subfields

- **Question-task framing** — translate the ask into `target`, `unit` of
  analysis, `metric`, and `baseline`; select task type (classification,
  regression, similarity, clustering, link prediction, causal). This
  translation is ad hoc in the literature — don't imply a settled procedure.
  See `references/framing-and-proxy.md#framing`.
- **Proxy statement** — name the construct, its operationalization, and the
  gap between them (`proxy_statement`): "churn" = 30-day inactivity; "fraud"
  = chargeback filed. Never treat the label as identical to the construct.
  See `references/framing-and-proxy.md#proxy`.
- **Split design** — the initial holdout/split (`split_design`), decided
  before profiling or modeling, not derived from convenience once data is in
  hand. Doctrine principle taught once in `references/doctrine-leakage.md`;
  this skill's delta is timing (before Observe/Interpret run, and strictly
  before any target-relationship exploration). See
  `references/split-design.md`.
- If the ask implies a randomized experiment (not just a predictive task),
  consult `ds-stats` for power/randomization-unit/interference design — that
  method is `ds-stats`'s, this subfield only flags the need. See
  `references/kill-check.md`.

## Gates

- `proxy_statement` names the construct, the operationalization, and the
  gap — a value that only restates the label fails this gate.
- `split_design` is recorded before `ds-profile` or any skill examines
  target-relationship data; full-data profiling limited to structure,
  typing, and missingness until then (`doctrine-leakage.md`).
- `kill_check` states an explicit, checkable cost/feasibility threshold —
  a qualitative judgment with no threshold value fails this gate, because
  `cost-overrun → scoping` has nothing to compare against.
- `intended_scoring_population` is on record before `ds-evaluate`'s
  deployment-population reconciliation gate can run.

## Edges

Covered: task framing, proxy statement, initial split design, feasibility
kill-check with an explicit cost threshold.

Not covered here, pointer only: classical experiment power/randomization
design (`ds-stats` owns it — consulted, not run, when the ask implies an
experiment); the learning-curve/data-sufficiency computation itself
(`ds-model` owns the method; this skill's kill-check only judges "sufficient
to attempt").

Each re-run scope is `ds-scoping` itself: the task card gets a fresh,
higher-iteration write, not a full section replace. `ds-verify` fails any
claim citing a section still marked stale after the bump.

Not a scoping loop-back: `mlops serving constraints → model selection`
stays at `ds-model` — don't conflate it with the four rows above.

## Audit mode

Input: an existing external framing document authored outside this skill (a
ticket, a PRD, a prior analyst's brief). Undocumented framing claims are
treated as unregistered fields under Gates: flagged, never assumed.

## Production considerations

Production tier adds two deltas, both pointers: `doctrine-scale-cost.md`
applies at every step touching selection economics, reading the threshold
this skill's `kill_check` declared; and `impact → scoping` becomes a
mandatory back-edge check, not merely an available one (`tiers.md`
production example). `ds-mlops` owns ongoing production cost/serving
monitoring itself — this skill only seeds the threshold it monitors
against.
