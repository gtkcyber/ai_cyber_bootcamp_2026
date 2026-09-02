---
name: ds-simulation
description: "Monte Carlo and bootstrap resampling machinery; synthetic data generation with property-preservation validation; SMOTE-class imbalance-augmentation mechanics; differentially-private synthesis, re-identification risk measurement, and privacy-utility tradeoff evaluation. Executes and evaluates privacy decisions, never…"
---

# ds-simulation

Full depth and citations live in `references/`; this file is protocol only.

**Privacy boundary** (echoed from `ds-clean`): the protection *decision* —
what must be protected, to what standard — is policy, out of scope for
the whole suite. This skill executes and evaluates a decision already
made. A privacy transform on *real* records is `ds-clean`'s; generating
*synthetic* rows under a privacy constraint is this skill's.

## Subfields

Load order is per-subfield, not one skill-level value: the generation
cluster triggers alongside `ds-clean`'s data-prep slot, imbalance
augmentation alongside `ds-model`'s intervention decision, MC/bootstrap
alongside `ds-stats`/`ds-uncertainty`'s inferential-machinery slot. Full
citations: `references/ds-simulation.monte-carlo-and-bootstrap.md`,
`references/ds-simulation.synthetic-and-privacy-generation.md`.

- Canonical methods (examples, not exhaustive): Monte Carlo integration/
  expectation estimation; MCMC (Metropolis algorithm, 1953) when sampling an
  intractable target. Edges: convergence diagnostics and Bayesian workflow
  are `ds-uncertainty`'s — this subfield supplies the sampling mechanic
  only.
- Canonical methods: the nonparametric bootstrap (Efron, 1979); block/
  cluster bootstrap under dependence. Edges: multiple-imputation pooling and
  hierarchical-model interval claims are `ds-uncertainty`'s — this subfield
  supplies the resampling mechanic, not the interpretation.
- Canonical methods: deep generative modeling for tabular data (CTGAN,
  2019); simpler parametric/copula generators for lower-stakes needs. Edges:
  generator architecture/training mechanics for non-tabular modalities is
  `ds-deep-learning`'s; this subfield owns *validation* regardless of which
  generator produced the rows.
- Canonical methods: SMOTE and its neighbor-interpolation variants (Chawla,
  Bowyer, Hall & Kegelmeyer, 2002).
- Canonical methods: DP-SGD- trained generators / DP-GAN (Xie et al., 2018).
  Edges: the protection decision itself is out of scope (boundary statement
  above); anonymization/masking of real records is `ds-clean`'s.
- Canonical methods: population-uniqueness-based re-identification
  estimation (Rocher, Hendrickx & de Montjoye, 2019). Edges: measures risk;
  does not decide what risk level is acceptable (policy).
- Canonical methods: privacy-utility curve evaluation against a named
  downstream task (Stadler, Oprisanu & Troncoso, 2022). Edges: reports a
  curve against a named task, never a single number; does not decide which
  point on the curve is acceptable (policy).

## Selection tree

1. Quantifying/propagating uncertainty from data or a model already in
   hand, not generating new rows? Resampling the *observed sample* →
   **bootstrapping**; simulating from a *specified probabilistic model* →
   **Monte Carlo methods**.
2. Need more/different rows, reason is class imbalance with `ds-model`
   already having decided to intervene at the data level? → **imbalance
   augmentation mechanics**.
3. Need more/different rows, reason is privacy — real records must not
   leave, or a release must resist re-identification? → **privacy-
   preserving generation**, mandatorily paired with **re-identification
   risk measurement** and, when a release decision follows, **privacy-
   utility tradeoff measurement**.
4. Need more/different rows for any other reason → **synthetic data
   generation and its validation** — still with a full property-
   preservation check; "not for privacy" does not waive validation.

## Family-specific pitfalls and evaluation

- **Marginal fidelity is not joint fidelity** (Xu et al., 2019) — realistic
  column-by-column is not the same claim as "preserves what downstream
  analysis depends on"; check both.
- **Autocorrelated MC/MCMC draws are not iid** (understates MC error;
  correct for effective sample size), and **the bootstrap fixes nothing
  about a biased original sample** — plain iid resampling is invalid under
  dependence without a block/cluster variant.
- **SMOTE can manufacture label noise** in high-dimensional/noisy space —
  interpolated points can land inside the majority-class region; it
  competes with, not automatically beats, `ds-model`'s algorithm-level
  interventions.
- **DP composition failure** — noise calibrated per training step without
  accounting for the *total* budget across every step silently exceeds ε.
- **"Synthetic implies private" is unsupported** (Stadler et al., 2022);
  **"we only released a sample" is not a defense** (Rocher et al., 2019) —
  population uniqueness is estimable from a 1% sample.

Evaluation delta to `ds-evaluate`'s scorecard: report property-preservation
results per property (never a single "realistic" verdict) and, whenever a
privacy claim is made, the risk measurement plus the privacy-utility curve
against a named task, not a single number.
