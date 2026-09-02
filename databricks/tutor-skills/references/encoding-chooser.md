# Categorical encoding chooser

Routing table, not mechanics. Cardinality × model family × leakage risk →
encoding class and its owner. Mechanics for every row live in `ds-features`
(`references/ds-features.encodings-scaling-interactions.md#encodings` and
`references/ds-features.aggregation-leakage-selection.md#leak-safe-target-encoding`) — this file
only routes to the right one.

## Cardinality × model family → encoding

| Cardinality | Model family | Encoding | Failure mode | Owner |
|---|---|---|---|---|
| Low (roughly < 10-15 categories) | Any | One-hot. Ordinal only if the categories have a genuine, stated order (e.g. severity tiers) | Ordinal on an unordered categorical silently teaches a downstream linear/distance model a fake magnitude relationship | `ds-features` |
| High | Tree-based / boosted | Target/mean ("likelihood") encoding, leak-safe variant only (see Leakage below) | Smoothing/shrinkage alone controls variance for low-count categories — it does not prevent the leak (Micci-Barreca's empirical-Bayes blend) | `ds-features` |
| High | Neural-net / deep-learning | Entity embeddings, learned jointly with the supervised NN or trained separately | Needs enough per-category data to learn a meaningful vector; sparse-tail categories need an explicit shared "unknown" embedding or roll-up to a coarser category, not a silent default | `ds-features`; if the embedding is produced by a separately trained model, it's a composition (`ds-method-composition`), not a plain encoding |
| High, memory-constrained or streaming/online linear model | Sparse linear / online | Feature hashing | Exponential tail bounds show inter-hashed-subspace interaction is negligible with high probability (Weinberger, Dasgupta, Attenberg, Langford & Smola 2009, "Feature Hashing for Large Scale Multitask Learning," arXiv:0902.2206, confirmed via arXiv abstract page). Hash collisions confound distinct categories with no detection mechanism; state the hash space size, don't leave it at a library default | `ds-features` |

## Leakage risk

| Fix | Mechanism | Owner |
|---|---|---|
| Cross-fitting (`TargetEncoder`-style) | Split train into `k` folds; encode each fold using only the other `k-1` folds' target values | `ds-features` |
| Ordered target statistics | Process rows in a fixed order; encode each row using only the target statistics of rows before it in that order — avoids fold-boundary artifacts at small fold counts, at the cost of ordering-dependent quality for early rows (CatBoost) | `ds-features` |
| Regularized target encoding | Properly regularized/smoothed encodings beat naive ones on high-cardinality features (Pargent et al.) — but their benchmark still uses an out-of-fold protocol; regularization and leak-safety are different problems and **both** are required | `ds-features` |

At inference time, the encoding applied to new rows uses statistics fit
on the entire training set (all folds combined) — the fold-splitting is a
training-time-only device to avoid self-leakage, not a scheme that
persists at serving time.

## Cross-cutting gate

Every row above states its unseen-category policy explicitly (map to
global mean / a reserved "other" level / raise) — an encoding that
silently drops or sentinel-maps a category unseen in train but present at
inference fails this gate regardless of which encoding class was chosen.

## Escalation

An encoding (embedding or hashed representation) proposed as a feature
into a *second* downstream model, rather than consumed directly by the
model it was encoded for, is `ds-method-composition`'s
model-as-feature-extractor pattern — declare the composition and its
out-of-fold discipline, don't fold it back into this table's plain
encoding rows.
