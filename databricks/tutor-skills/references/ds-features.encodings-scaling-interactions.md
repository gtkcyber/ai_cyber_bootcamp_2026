# Encodings, scaling, interactions

Depth for the three transform-mechanics subfields that aren't primarily
about leakage timing (that's `references/ds-features.aggregation-leakage-selection.md`'s scope).

## Encodings

**Low cardinality (roughly < 10-15 categories).** One-hot. Ordinal
encoding is only correct when the categories have a genuine, stated order
(e.g. severity tiers) — an ordinal code on an unordered categorical
silently teaches a downstream linear/distance model a fake magnitude
relationship. scikit-learn's `OneHotEncoder` and `OrdinalEncoder` are the
practitioner-standard implementations (preprocessing docs, above).

**High cardinality.** One-hot blows up the column count and produces
mostly-zero columns; two options:

- **Target/mean ("likelihood") encoding** — replace each category with a
  (regularized) estimate of the target conditional on that category.
  Micci-Barreca's original formulation is an empirical-Bayes blend:
  `encoded = λ(n) * mean(target | category) + (1 - λ(n)) * mean(target)`,
  where `λ(n)` grows toward 1 as the category's sample count `n` grows —
  low-count categories shrink toward the global mean instead of
  overfitting to a handful of rows. **This encoding is target-leaking by
  construction if fit naively — see `#target-encoding` in
  `references/ds-features.aggregation-leakage-selection.md` before shipping it.**
- **Entity embeddings** — a dense per-category vector, learned jointly
  with a supervised NN (or trained separately and reused). Needs enough
  per-category data to learn a meaningful vector; sparse-tail categories
  fall back to a shared "unknown" embedding or roll up to a coarser
  category. Producing the embedding via a separately trained model is a
  composition, not a plain encoding — declare it per
  `ds-method-composition` and carry its provenance the way any composed
  model output does (`references/doctrine-repro-provenance.md`).

**Failure mode to check for**: an encoding fit that silently drops or
maps to a sentinel any category unseen in train but present at inference
— state the unseen-category policy explicitly (map to global mean / a
reserved "other" level / raise), don't let it default silently.

## Scaling

Applies when the downstream method is scale-sensitive: distance-based
(k-NN, k-means, SVM with an RBF kernel), gradient-based (neural nets,
gradient boosting is largely scale-invariant per split but benefits for
learning-rate stability), regularized-linear (L1/L2 penalties are
scale-dependent — an unscaled feature with large magnitude is
under-penalized relative to a small-magnitude one carrying equivalent
signal). Tree-based methods that split on raw thresholds (single decision
trees, random forests) generally don't need scaling — check the
downstream family skill before applying it by default.

- **StandardScaler** (zero mean, unit variance) — default choice, but
  outlier-sensitive: a single extreme value inflates the variance
  estimate and compresses the rest of the distribution.
- **MinMaxScaler** — bounds to a fixed range; same outlier sensitivity
  (the range is set by the extremes).
- **RobustScaler** — centers on the median, scales by IQR; preferred
  whenever `ds-clean`'s profiling flagged outliers that are a genuine
  distributional property (not data defects `ds-clean` already removed).

**Fit-on-train-only is not optional here** — see the Gates section in
`SKILL.md` and the pipeline-object mechanics in
`aggregation-leakage-selection.md#pipeline-object`; this file states only
which scaler to pick, not how to fit it safely.

## Interactions

No settled literature-backed method for *discovering* which interactions
matter exists in this brief (Friedman & Popescu's H-statistic is the
classical reference but its host blocked citation verification, so it is
not cited here from memory — flag as a future addition once fetchable).
What's available is mechanical construction once an interaction is
suspected:

- `PolynomialFeatures(degree=2, interaction_only=True)` generates
  pairwise products without same-feature powers (`x1*x2`, not `x1^2`).
  `interaction_only=False` adds the powers back in — usually not wanted
  for interaction terms specifically.
- Feature count grows combinatorially with degree and input-feature
  count (`C(n, degree)` new terms at minimum) — this is a compute-cost
  concern, not just a modeling one; check `references/doctrine-scale-cost.md`'s
  threshold before generating interactions over a wide feature set.
- Generated interaction terms are near-collinear with their parent
  features by construction — expect this to interact with feature
  selection (`aggregation-leakage-selection.md#selection`) and with any
  regularized-linear model's coefficient stability.

**Practice guidance, not literature**: absent a validated discovery
method, interactions here are driven by domain hypotheses stated by the
task or by post-hoc diagnostics run in `ds-evaluate`/`ds-explain`
(feeding back via `evaluate → features` if a diagnostic surfaces one) —
don't present blind, exhaustive interaction generation as a default
practice.
