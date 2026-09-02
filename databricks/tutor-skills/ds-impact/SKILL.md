---
name: ds-impact
description: "Realized-outcome measurement after deployment: did the business metric move, by how much, reconciled against the ds-scoping task card; value attribution (associative vs. causal); decommissioning and model sunset. Fires the mandatory impact→scoping back-edge when realized outcome contradicts the intended effect."
---

# ds-impact

Composes only once a production deployment exists — the production-tier
worked example (`tiers.md`) is the only composition that includes this
skill. Runs last in `manifest.json`'s lifecycle order, after `ds-mlops`.
Full depth, worked examples, and citations live in `references/`; this file
is protocol only.

## Subfields

- **Realized-outcome measurement** — **Online Controlled Experiments
  (OCE)**. Trigger: a deployed system has run long enough to measure the
  business metric. Kohavi, Tang, Xu, *Trustworthy Online Controlled
  Experiments*, Cambridge University Press 2020 —
  https://experimentguide.com/ : randomization integrity/SUTVA, sample-ratio
  mismatch as a trust check, statistical vs. practical significance — don't
  conflate a pre/post observational comparison with a controlled experiment.
  See `references/ds-impact.realized-outcome-and-reconciliation.md#realized-outcome`.
- **Geo-test / switchback experiment designs** — two distinct literatures.
  Trigger: unit-level randomization isn't available (a market/region or a
  time-slice is the smallest randomizable unit). Vaver & Koehler, "Measuring
  Ad Effectiveness Using Geo Experiments," Google 2011 —
  https://research.google/pubs/measuring-ad-effectiveness-using-geo-experiments/
  (geo, assumes negligible cross-region spillover); Bojinov, Simchi-Levi,
  Zhao, "Design and Analysis of Switchback Experiments," Management Science
  — https://arxiv.org/abs/2009.00148 (switchback, assumes bounded/known
  carryover). See
  `references/ds-impact.experiment-designs-and-attribution.md#geo-switchback`.
- **Value attribution** — multi-touch attribution (MTA) vs. incrementality.
  Trigger: value/credit must be assigned across multiple touchpoints or
  channels. Dalessandro, Perlich, Stitelman, Provost, "Causally Motivated
  Attribution for Online Advertising," ADKDD 2012 —
  https://fosterprovost.com/publication/causally-motivated-attribution-for-online-advertising/ ;
  Bottou et al., "Counterfactual Reasoning and Learning Systems," JMLR 14,
  2013 — https://jmlr.org/beta/papers/v14/bottou13a.html. Attribution
  answers "who gets credit" (associative); incrementality answers "what was
  caused" (causal) — reporting one as the other is the literature's named
  failure mode. Either answer needs an underlying identification strategy
  this skill doesn't own: observational/quasi-experimental →
  `ds-causal`'s `identification_statement`; a holdout already exists →
  `ds-stats`'s `design_analysis_memo`. See
  `references/ds-impact.experiment-designs-and-attribution.md#attribution`.
- **Decommissioning and model sunset** — **LITERATURE-THIN**: no established
  literature name for retirement methodology. Nearest academic anchor,
  Sculley et al., "Hidden Technical Debt in Machine Learning Systems,"
  NeurIPS 2015 —
  https://research.google/pubs/hidden-technical-debt-in-machine-learning-systems/ —
  addresses debt accrual, not a retirement method; treat this subfield as
  practice protocol, not literature. Trigger: a sunset review is requested
  (sustained under-performance vs. cost, the framing invalidated by an
  `impact → scoping` firing, or a replacement already shipped). See
  `references/ds-impact.decommissioning.md`.

| Subfield | Participation |
|---|---|
| Realized-outcome measurement | `mandatory` |
| Geo-test/switchback designs | `conditional-on-data:no-unit-level-randomization` |
| Value attribution | `conditional-on-data:multi-touchpoint` |
| Decommissioning and model sunset | `conditional-on-data:sunset-review` |

`mandatory`: fires whenever `ds-impact` composes at all — every deployment
gets its realized outcome measured, unlike the other three, which fire only
on their own trigger.

## Gates

- Any causal/attributable claim in the assessment cites either `ds-causal`'s
  `identification_statement` or `ds-stats`'s `design_analysis_memo` as its
  identification source — this skill reconciles and attributes, it never
  identifies; a causal claim with neither citation fails.
- Value attribution states explicitly whether it reports associative credit
  (MTA) or causal incrementality — an unlabeled number fails this gate,
  per the brief's named failure mode.
- Decommissioning proceeds only under a stated criterion (sustained
  under-performance vs. cost, framing invalidated, or replacement shipped)
  — an unstated criterion ("this model feels old") fails the gate.
- Geo/switchback identification consults `ds-stats` for the concrete design
  before the assessment reports a lift number from it — a number with no
  cited design source fails.

## Edges

Covered: realized-outcome measurement and reconciliation against the task
card; flagging (not computing) geo/switchback experiment design need;
value-attribution framing (associative vs. causal) and citing the
identification source; decommissioning criteria, final ledger compaction on
archive, and what monitoring persists post-sunset.

No back-edge re-runs `ds-impact` itself — every scoping-targeted back-edge
(`data-models → scoping`, `monitoring → scoping`, `impact → scoping`,
`cost-overrun → scoping`) lists the impact assessment last in its
invalidates column because `impact` is the final section in the lifecycle
order; when scoping re-runs, `ds-impact` re-runs as part of the normal
forward cascade, not via a named back-edge of its own.

## Audit mode

Input: an existing external post-launch report or dashboard authored outside
this skill (a launch retro, a BI dashboard export, a prior analyst's
write-up). An undocumented realized-outcome claim is treated as an
unregistered field under Gates: flagged, never assumed.

## Production considerations

This skill has no non-production form — `tiers.md`'s production worked
example is the only composition that includes it; quick-answer and analysis
tasks never reach it.
