# Geo/switchback designs and value attribution

## Geo-switchback

Two distinct literatures share a common trigger: the smallest unit that can
be randomized isn't the individual (a user, a request) but a coarser unit
(a market, a region, a time-slice) — usually because the treatment has
spillover at the individual level (pricing, ads, marketplace liquidity) or
because there's no addressable individual to randomize (offline/regional
rollouts).

- **Geo experiments** (spatial unit). Vaver & Koehler, "Measuring Ad
  Effectiveness Using Geo Experiments," Google 2011 —
  https://research.google/pubs/measuring-ad-effectiveness-using-geo-experiments/.
  Assumes negligible cross-region spillover — a national campaign that
  drives traffic across region boundaries (people traveling, national
  media) violates this and biases the estimate toward zero.
- **Switchback experiments** (temporal unit). Bojinov, Simchi-Levi, Zhao,
  "Design and Analysis of Switchback Experiments," Management Science —
  https://arxiv.org/abs/2009.00148. Assumes a bounded, known carryover
  order (how long yesterday's treatment state keeps affecting today's
  outcome) — an unbounded or misspecified carryover window invalidates the
  power calculation the design was built on, not just the point estimate.

Consult, cite, don't compute.

## Attribution

**Literature name**: multi-touch attribution (MTA) vs. incrementality
measurement.

- Dalessandro, Perlich, Stitelman, Provost, "Causally Motivated Attribution
  for Online Advertising," ADKDD 2012 —
  https://fosterprovost.com/publication/causally-motivated-attribution-for-online-advertising/.
- Bottou et al., "Counterfactual Reasoning and Learning Systems," JMLR 14,
  2013 — https://jmlr.org/beta/papers/v14/bottou13a.html.

The named failure mode both sources call out: **attribution answers "who
gets credit," incrementality answers "what was caused."** A last-touch or
multi-touch attribution model distributes 100% of observed conversions
across touchpoints by a chosen rule (linear, time-decay, position-based,
data-driven) — it always sums to the observed total, by construction. It
does not tell you what would have happened without any of those
touchpoints. Reporting an attribution split as if it measured incremental
lift is the standard misstatement this subfield exists to prevent.

MTA still needs an underlying causal/experimental identification strategy
to be trustworthy at all (Bottou et al.) — the same two routes as
realized-outcome reconciliation:

- No holdout, observational touchpoint logs → `ds-causal`
  (`identification_statement`).
- A holdout exists specifically for incrementality measurement (a
  public-service announcement / ghost-ad holdout, a geo-holdout) →
  `ds-stats` (`design_analysis_memo`).

`value_attribution` in the impact assessment always states which of the
two — associative credit or causal incrementality — it is reporting, and,
if incrementality, which identification source backs it.
