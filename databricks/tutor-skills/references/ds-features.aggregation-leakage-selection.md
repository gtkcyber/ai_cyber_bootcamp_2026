# Aggregation, leak-safe target encoding, feature selection, pipeline object

## Aggregation/window features

Two ingredients: automated construction, and point-in-time correctness.

**Construction.** Deep Feature Synthesis (Kanter & Veeramachaneni, IEEE
DSAA 2015) automates building aggregate features across relational tables
by walking the relationship graph and applying a fixed set of aggregation
primitives (`sum`, `mean`, `count`, `max`, `min`, `std`, …) at each
group-by level. The mechanical part — enumerate primitives × relationship
paths — is the easy part; getting the *timing* right is the hard part,
below.

**Point-in-time correctness.** A window/aggregate feature computed for a
row must only use source rows timestamped at or before that row's own
event time — Feast's point-in-time join semantics are the practitioner
reference: join feature values as of the label's timestamp, never the
"latest available" value, which silently pulls in future information at
training time (the label's timestamp is in the past relative to now, but
the feature computation must respect *its* past, not the present).

- **TTL windows are relative to each row's own timestamp**, not to a
  fixed calendar cutoff — a naive `WHERE event_date >= (today - 30 days)`
  filter applied once for the whole dataset leaks future information into
  every row whose label predates today by less than the window.
- This is the mechanical enforcement of `doctrine-leakage.md`'s
  point-in-time-correctness principle — that principle is stated once
  there; this section is the how, not a restatement of the why.
- Additivity classification (additive/semi-additive/non-additive) happens
  **before** the aggregate is built, not after, because the aggregation
  primitive itself depends on the classification: a semi-additive measure
  (e.g. a distinct-count) does not compose the same way across a
  re-aggregation as a fully additive one (e.g. a sum), and
  ratio-of-averages vs. average-of-ratios must be resolved before any
  `mean`-of-a-ratio feature is constructed, not discovered as a bug
  afterward.

## Leak-safe target encoding

Naive target/mean encoding computes each category's target mean using
that category's own rows — including the row being encoded. That row's
own label leaks directly into its own feature value. Two fixes, not
interchangeable:

- **Smoothing/shrinkage** (the empirical-Bayes blend in
  `encodings-scaling-interactions.md#encodings`) controls *variance* for
  low-count categories. It does **not** prevent the leak — a
  high-count category still has its own row's label baked into its
  encoded value, just diluted by many other rows' labels instead of
  eliminated.
- **Out-of-fold / ordered target statistics** is the actual fix:
  - **Cross-fitting** (scikit-learn `TargetEncoder`): split train into
    k folds; for each fold, compute the encoding using only the *other*
    k-1 folds' target values, so no row's own label contributes to its
    own encoded value.
  - **Ordered target statistics** (CatBoost): process rows in a
    (typically random, fixed) order and encode each row using only the
    target statistics of rows that came *before* it in that order —
    avoids the fold-boundary artifacts cross-fitting can introduce at
    small fold counts, at the cost of encoding quality depending on
    position in the ordering for early rows.
- Regularized target encoding (Pargent et al.) shows properly
  regularized/smoothed encodings beat naive encodings on high-cardinality
  features — but their benchmark still uses an out-of-fold protocol;
  regularization and leak-safety are solving different problems and both
  are required.
- **At inference time**, the encoding applied to new rows uses the
  statistics fit on the *entire* training set (all folds combined) — the
  fold-splitting is a training-time-only device to avoid self-leakage,
  not a scheme that persists at serving time.

## Feature selection (pruning, not attribution)

Guyon & Elisseeff's taxonomy, still the standard reference frame:

- **Filter** methods score each feature independently of any model
  (correlation, mutual information, variance threshold) — fast, ignores
  interactions between features, so a feature useless alone but
  informative jointly with another gets dropped incorrectly.
- **Wrapper** methods search subsets by training and scoring a model on
  each candidate subset (forward selection, backward elimination,
  recursive feature elimination) — captures interactions the filter
  misses, but the search overfits the selection itself to the validation
  split used to score it if that split isn't held separate from the
  final evaluation split.
- **Embedded** methods select as a byproduct of fitting one model
  (L1/Lasso coefficients pushed to zero, tree-based importance
  thresholds) — cheap, but the selected set is specific to that model
  family and doesn't necessarily transfer to a different one under
  comparison.

**Pruning vs. attribution.** This subfield answers "should this feature stay
in the candidate set" — a binary/ranking decision made before `ds-model`
receives the final set. It is not answering "how much did this feature
contribute to this specific prediction" — that's
importance-for-interpretation, `ds-explain`'s question, asked *after* the
feature set is fixed.

## Pipeline object (fit-on-train-only mechanics)

The general mechanism every stateful subfield above (scaling, encoding,
target statistics) must satisfy, stated once here rather than per
subfield:

- Every stateful transform is an object with a `fit` step and a
  `transform` step, kept distinct. `fit` runs once, on the train split
  only, and learns whatever statistic the transform needs (scaler
  mean/std, encoding table, imputation value). `transform` applies that
  already-learned statistic to any split — train, validation, test, or a
  future production row — without re-learning it.
- Composing multiple stateful transforms (e.g. impute → encode → scale)
  into one pipeline object (scikit-learn's `Pipeline`/`ColumnTransformer`
  pattern is the practitioner-standard shape) guarantees the same
  `fit`-then-`transform` discipline applies uniformly and makes the
  object itself the artifact recorded as `pipeline_object` — not a
  narrative description of the steps.
- **Under cross-validation**, the pipeline refits per fold — each fold's
  training portion gets its own `fit`, applied to that fold's held-out
  portion. A single global `fit` before the CV loop starts is the same
  leakage bug as fitting on the full pre-split dataset, just harder to
  spot because it happens "before" the loop rather than visibly inside
  it.
- The persisted `pipeline_object` is what makes leak-safety
  *reproducible*, not just correct once: any consumer (a later `ds-model`
  run, a production inference call) that applies fresh data through the
  object gets the train-fit statistics, never a refit against whatever
  data happens to be present at call time.
