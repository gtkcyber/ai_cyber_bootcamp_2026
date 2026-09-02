---
name: ds-communicate
description: "Turns findings into the audience-tiered report: findings→narrative structure, honest uncertainty language, chart-type selection, and executive-summary/BLUF discipline, including the mandatory honest-limitations section."
---

# ds-communicate

Runs last among the lifecycle skills a composition selects — after whichever
of `ds-evaluate`/`ds-verify`/`ds-stats` wrote findings, before `ds-mlops` at
production tier.

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

`mandatory`: fires whenever `ds-communicate` composes at all — every report
needs a narrative structure, an honest uncertainty register, and a
lead-with-the-finding shape, even a one-line quick-answer report (compressed
form: don't overclaim precision no interval was computed for).

## Production considerations

Two deltas, both pointers: recurring-report freshness/reconciliation and
dashboard-contract monitoring move to `ds-mlops`'s non-model production
analytics — this skill authors the one-time or per-run report, not its
ongoing freshness guarantee. `references/doctrine-scale-cost.md`'s threshold, recorded
once in `ds-scoping`'s kill-check, is restated in `report` only when the
finding itself surfaces a cost decision — never re-derived here.
