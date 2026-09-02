---
name: ds-simulation
description: "Monte Carlo and bootstrap resampling machinery; synthetic data generation with property-preservation validation; SMOTE-class imbalance-augmentation mechanics; differentially-private synthesis, re-identification risk measurement, and privacy-utility tradeoff evaluation. Executes and evaluates privacy decisions, never…"
---

# ds-simulation

Not re-entrant: each subfield composes once, at the lifecycle position its
trigger names. Full depth and citations live in `references/`; this file is
protocol only.

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

## Gates

- Every synthetic/augmented dataset's rows carry provenance class
  `derived` (`doctrine-repro-provenance.md`), and its population statement
  names the generator and validation results before any downstream skill
  consumes it — rows with no `generation_report` entry are blocked, not
  silently passed through.
- Any generative model producing rows a model will *train* on, and any
  SMOTE-class augmentation, is fit/run on the train split only
  (`doctrine-leakage.md`) — full-dataset fitting leaks held-out data into
  training via the synthetic rows it emits; pre-split augmentation lets
  near-duplicate neighbors land on both sides of the split.
- `property_preservation` names which properties were checked (marginals,
  correlations, constraint satisfaction) and the result for each — a claim
  that only asserts "preserves the distribution" fails. Imbalance entries
  never originate the whether/how-much decision — each cites the
  `ds-model` decision it executes.
- Every privacy-preserving generation entry names its (ε, δ) budget,
  states the accounting covers every training step, and is paired with a
  re-identification risk measurement and a privacy-utility tradeoff curve
  (never a single number) before release — any missing fails this gate.
- No entry may assert *what* must be protected or *to what standard* —
  every entry cites the upstream decision it executes, never its own.

## Edges

Covered: MC/MCMC sampling, nonparametric and block/cluster bootstrapping,
synthetic tabular generation with property-preservation validation,
SMOTE-class imbalance-augmentation mechanics, differentially-private
synthesis, re-identification risk measurement, privacy-utility tradeoff
measurement. Not covered, pointer only: MCMC convergence diagnostics/
Bayesian workflow and inferential interpretation (`ds-uncertainty`);
whether/how much to intervene for imbalance (`ds-model`); metric
selection under imbalance (`ds-evaluate`); generator architecture/
training mechanics for non-tabular modalities (`ds-deep-learning`);
anonymization/masking of real records (`ds-clean` — this skill produces
new rows, never transforms of existing ones); the privacy protection
decision itself; labeling caveats on synthetic rows (`ds-labeling`). No
spatiotemporal/temporal-graph/multimodal-fusion pairing applies here
(multi-family leakage-lead rule doesn't trigger); the leakage constraint
imposed whenever this skill composes is the train-split-only
generator-fit rule in Gates above.
