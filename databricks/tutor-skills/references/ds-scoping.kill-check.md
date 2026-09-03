# Feasibility kill-check

One artifact (`kill_check`), four axes. All four are judged together — a
task can fail on any one of them, and the kill-check exists to say so before
any downstream skill spends effort.

## Signal plausibility

**LITERATURE-THIN.** No peer-reviewed canonical source; nearest is the
practitioner "ML feasibility study" plus CRISP-ML(Q)'s Go/No-Go checkpoints.

**Canonical methods/refs**:
- Google, "Feasibility | Managing ML Projects" —
  https://developers.google.com/machine-learning/managing-ml-projects/feasibility
  — structured feasibility checklist (data availability, cost,
  prediction-quality bar); explicit kill-the-project guidance.
- Studer et al., "Towards CRISP-ML(Q)" — https://arxiv.org/pdf/2003.05155 —
  frames feasibility as an explicit quality-assurance checkpoint, not a
  one-time judgment call.

**Failure modes**: these are industry references, not academic ones — don't
cite as if formal theory exists here. Judge plausibility against a
mechanism ("is there a reason this signal would predict the target"), not
against whether data happens to be available.

## Data availability at prediction time

Not a separate literature entry — this is the leakage doctrine's
point-in-time-correctness principle (`references/doctrine-leakage.md`) applied at
scoping time, before any data has been touched: would the features this
task implies even exist, unlagged, at the moment a prediction is needed in
production? A signal that's plausible in hindsight but unavailable at
decision time kills the task here, not three skills downstream in
`ds-features`.

## Compute/cost economics

Delta-only pointer: `references/doctrine-scale-cost.md` is where the cost doctrine
itself is taught (scale playbook, selection economics). This skill's only
job is to **declare the escalation threshold** and record it in the task
card's `kill_check` field — a number or an explicit rule, not a vague budget
sense.

## Data sufficiency (sample-size adequacy)

**Literature name**: **learning curves** / **neural scaling laws**.

**Canonical methods/refs**: Hestness et al., "Deep Learning Scaling Is
Predictable, Empirically" — https://arxiv.org/abs/1712.00409 —
generalization error follows a power law in training-set size across four
domains; the exponent is not predictable from theory, only measurable
empirically.

**Failure modes**: no universal fixed sample-size rule exists ("10x
features" is folklore, not a result of this literature). The actual result
is a domain-specific power-law curve, measurable only empirically — which
is why *computing* the curve is `ds-model`'s job (it needs a trained model
to fit against), while this subfield only records the prior judgment: is
the available row count in the plausible range to attempt the task at all.

## Experiment-design hook (pointer, not owned)

This subfield names the need; it does not perform the design.
