---
name: ds-communicate
description: "Turns findings into the audience-tiered report: findings→narrative structure, honest uncertainty language, chart-type selection, and executive-summary/BLUF discipline, including the mandatory honest-limitations section."
---

# ds-communicate

Runs last among the lifecycle skills a composition selects — after
whichever of `ds-evaluate`/`ds-verify`/`ds-stats` wrote findings, before
`ds-mlops` at production tier. Not re-entrant: fires once per task; a later
reporting need routes through the loop-backs that mark `report` stale
(Edges), not a fresh entry. **This protocol turns ledger contents into
prose — it never introduces a claim the ledger doesn't already carry.**
Full depth and citations live in `references/`; this file is protocol only.

## Subfields

- **Findings→narrative** — **narrative visualization** (HCI/InfoVis).
  Trigger: any report is authored at all. Segel & Heer, "Narrative
  Visualization: Telling Stories with Data," IEEE InfoVis 2010 —
  http://vis.stanford.edu/files/2010-Narrative-InfoVis.pdf : author-driven
  vs. reader-driven structure is a real tradeoff, not a universal ranking —
  narrative structures interpretation, it doesn't decorate it. See
  `references/ds-communicate.narrative-uncertainty-charts.md#narrative`.
- **Honest uncertainty language** — **uncertainty communication /
  calibrated confidence language**. Trigger: any report is authored at all.
  Mastrandrea et al., "Guidance Note ... on Consistent Treatment of
  Uncertainties," IPCC AR5 —
  https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf :
  confidence (evidence/agreement quality) and likelihood (a calibrated
  probability scale) answer different questions — don't blend them, and
  don't imply numeric precision when only qualitative confidence was
  assessed. See `references/ds-communicate.narrative-uncertainty-charts.md#uncertainty`.
- **Chart-type selection** — no brief citation: this subfield has no
  literature entry of its own. Trigger: the deliverable includes a
  chart/figure. Mark/palette/layout mechanics are out of scope (use the
  runtime's charting facility); this subfield's own delta is choosing a chart *type* by
  the data relationship being shown (trend, comparison, distribution, part-
  to-whole, correlation), never by tool or stack preference. See
  `references/ds-communicate.narrative-uncertainty-charts.md#charts`.
- **Executive-summary discipline** — **Pyramid Principle** (Minto) /
  **BLUF**. Trigger: any report is authored at all. Minto, *The Minto
  Pyramid Principle* — https://www.barbaraminto.com/ ; Army Regulation
  25-50 — https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN42124-AR_25-50-007-WEB-13.pdf
  : lead with the governing finding, structure support top-down beneath it —
  "lead with the finding" must never mean "omit caveats." See
  `references/ds-communicate.structure-and-limitations.md#discipline`.

|---|---|---|
| Findings→narrative | quick-answer | mandatory |
| Honest uncertainty language | quick-answer | mandatory |
| Chart-type selection | analysis | conditional-on-data:visualization-included |
| Executive-summary discipline | quick-answer | mandatory |

`mandatory`: fires whenever `ds-communicate` composes at all — every report
needs a narrative structure, an honest uncertainty register, and a
lead-with-the-finding shape, even a one-line quick-answer report (compressed
form: don't overclaim precision no interval was computed for).

## Gates

- Every count/rate claim in `report` states its denominator and source
  population statement (`data-models.population_statement`, or
  `scoping.intended_scoring_population` for a deployment-scoped claim)
  **inline, in the reader-visible text** — recorded only in the ledger and
  not in the prose fails this gate.
- Attrition above the threshold recorded upstream (row-attrition ledger,
  `doctrine-repro-provenance.md`) surfaces in `report` — a report silent on
  attrition it inherited fails this gate.
- `scoping.proxy_statement`'s construct-operationalization gap is restated
  in `report` wherever a finding is decision-relevant to that gap — a
  proxy gap declared upstream but silently dropped here fails this gate.
- Every semantic caveat attached to a source artifact (a coverage gap in
  `population_statement`, an `asserted` `provenance_class` entry in the
  semantic dictionary feeding a headline claim) is restated in `report`,
  not dropped — silence is a failed gate, not a neutral default.

## Edges

Covered: findings→narrative structuring, honest uncertainty language, chart-
*type* selection by data relationship, executive-summary/BLUF discipline,
the honest-limitations section.

Not covered, pointer only: dashboard/KPI-alert *design* (`ds-analytics`);
model-card content (`ds-model`); chart mark/palette/layout mechanics
(out of scope — rendering belongs to the runtime's charting facility, not
this suite); interval/coverage
*computation* (`ds-uncertainty` computes it, this skill only surfaces it
with the claim); verification *computation* (`ds-verify` computes it, this
skill only cites `verification_record`).

Its `report` section goes `stale` in the transitive downstream closure
whenever a full-closure back-edge fires (`evaluate → features`, `evaluate →
labeling`, `data-models → scoping`, `drift → profile`, `production-feedback
→ labeling`, `monitoring → scoping`, `impact → scoping`, `cost-overrun →
scoping`, `mlops serving constraints → model selection`), since
`communicate` sits after every one of those rows' re-run targets in
`manifest.json`'s lifecycle order. The `verify → clean | features |
data-models` back-edge is entry-scoped (`status: stale-scoped`) and narrows
invalidation to the named upstream artifact alone — it does not by itself
mark `report` stale. When a full-closure back-edge fires, `ds-communicate`
re-runs as part of the normal forward cascade, not via a named back-edge of
its own.

## Audit mode

Input: an existing external report or deliverable authored outside this
skill (a slide deck, a written memo, a dashboard writeup). A claim in the
audited artifact that traces to no upstream ledger entry is treated as
unregistered under Gates: flagged, never assumed true.

## Production considerations

Two deltas, both pointers: recurring-report freshness/reconciliation and
dashboard-contract monitoring move to `ds-mlops`'s non-model production
analytics — this skill authors the one-time or per-run report, not its
ongoing freshness guarantee. `doctrine-scale-cost.md`'s threshold, recorded
once in `ds-scoping`'s kill-check, is restated in `report` only when the
finding itself surfaces a cost decision — never re-derived here.
