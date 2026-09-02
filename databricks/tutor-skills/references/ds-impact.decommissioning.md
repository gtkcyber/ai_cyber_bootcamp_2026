# Decommissioning and model sunset

**LITERATURE-THIN, explicit.** No established literature name or
peer-reviewed methodology base for retirement was found under any searched
name. The nearest academic anchor is Sculley et al., "Hidden Technical Debt
in Machine Learning Systems," NeurIPS 2015 —
https://research.google/pubs/hidden-technical-debt-in-machine-learning-systems/
— which frames retirement as one late stage of technical-debt accrual, not
a methodology in its own right. What exists in practice is vendor-specific
deprecation-policy pages and practitioner writing, not settled literature.
What follows is **practice protocol**, authored as such — do not cite it as
if it were literature-backed.

## Retirement criteria

A sunset review runs only under one of three stated criteria (this
skill's gate: an unstated criterion fails):

- **Sustained under-performance vs. cost** — the realized-outcome
  measurement (this skill's own primary subfield) has shown the metric
  move no longer clears the cost the deployment carries (serving,
  retraining, on-call load) over a sustained window, not a single bad
  period. Cites `doctrine-scale-cost.md`'s cost framing and the
  `impact_assessment.realized_outcome` history, not a fresh cost analysis.
- Cites the loop-back row and the resulting scoping section's iteration.
- **Replaced** — a successor system has already shipped and passed its own
  verification (`ds-verify`); the prior system's continued operation is
  redundant, not failing on its own terms.

## What gets archived

## What monitoring persists post-sunset

Ownership pointer, not this skill's mechanics: `ds-mlops` owns what
monitoring (if any) continues after a model stops serving — e.g. watching
for a successor's own drift against the retired model's last-known
baseline, or confirming no lingering traffic still hits a decommissioned
endpoint. This subfield only records, in `decommission_recommendation`,
that post-sunset monitoring was handed off and to what `ds-mlops`
`monitoring_spec` — it does not define the monitoring itself.
