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
  See `references/ds-scoping.framing-and-proxy.md#framing`.
- **Proxy statement** — name the construct, its operationalization, and the
  gap between them (`proxy_statement`): "churn" = 30-day inactivity; "fraud"
  = chargeback filed. Never treat the label as identical to the construct.
  See `references/ds-scoping.framing-and-proxy.md#proxy`.
- **Split design** — the initial holdout/split (`split_design`), decided
  before profiling or modeling, not derived from convenience once data is in
  hand. Doctrine principle taught once in `references/doctrine-leakage.md`;
  this skill's delta is timing (before Observe/Interpret run, and strictly
  before any target-relationship exploration). See
  `references/ds-scoping.split-design.md`.
- **Feasibility kill-check** — one artifact (`kill_check`) covering four
  axes: signal plausibility, data availability at prediction time,
  compute/cost economics, and data sufficiency (sample-size adequacy — the
  learning-curve *method* is `ds-model`'s; this subfield only judges whether
  to attempt, not computes the curve). If the ask implies a randomized
  experiment (not just a predictive task), the `ds-stats` skill covers
  power/randomization-unit/interference design — that method is
  `ds-stats`'s, this subfield only flags the need. See
  `references/ds-scoping.kill-check.md`.

## Production considerations

`ds-mlops` owns ongoing production cost/serving monitoring itself — this
skill only seeds the threshold it monitors against.
