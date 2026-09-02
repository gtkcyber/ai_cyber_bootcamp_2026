---
name: ds-impact
description: "Realized-outcome measurement after deployment: did the business metric move, by how much, reconciled against the ds-scoping task card; value attribution (associative vs. causal); decommissioning and model sunset. Fires the mandatory impact→scoping back-edge when realized outcome contradicts the intended effect."
---

# ds-impact

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

`mandatory`: fires whenever `ds-impact` composes at all — every deployment
gets its realized outcome measured, unlike the other three, which fire only
on their own trigger.
