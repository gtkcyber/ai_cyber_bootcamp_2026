---
name: ds-features
description: "Feature engineering and the leak-safe transform pipeline: encodings, scaling, aggregation/window features, interactions, leak-safe target encoding, feature selection (pruning). Owns the fit-on-train-only pipeline-object mandate."
---

# ds-features

Full depth, worked examples, and citations live in `references/`; this file
is protocol only.

## Subfields

Six subfields. Each produces entries in the `feature_dictionary`, and
where stateful, fit logic in the `pipeline_object`.

- **Encodings** — categorical encoding: one-hot/ordinal for low
  cardinality, target/mean ("likelihood") encoding or entity embeddings
  for high cardinality. Trigger: a categorical feature feeds a model that
  requires numeric input. Micci-Barreca, "A Preprocessing Scheme for
  High-Cardinality Categorical Attributes," SIGKDD Explorations 3(1),
  2001: origin of target/mean encoding as an empirical-Bayes blend of
  category mean and global mean. "Entity Embeddings of Categorical
  Variables" — https://arxiv.org/abs/1604.06737 : dense per-category
  embeddings via a supervised NN, for cardinality one-hot can't scale to.
  scikit-learn, "Encoding categorical features" —
  https://scikit-learn.org/stable/modules/preprocessing.html. Edges: a
  target/mean scheme on a high-cardinality field hands off to Leak-safe
  target encoding below, not resolved here; a learned embedding produced
  by a composed model is `ds-method-composition`'s composition, not a
  plain encoding. See `references/ds-features.encodings-scaling-interactions.md#encodings`.
- **Scaling** — feature scaling for scale-sensitive downstream methods
  (distance-based, gradient-based, regularized-linear). Trigger: a
  composed family/model that is scale-sensitive (the family skill states
  this; not re-derived here). scikit-learn, "Preprocessing data" —
  https://scikit-learn.org/stable/modules/preprocessing.html :
  StandardScaler/MinMaxScaler/RobustScaler; robust scalers preferred
  under outliers. Edges: fit-on-train-only mechanics for the scaler is
  the general pipeline-object mandate (Gates), not a separate concern
  here; whether an outlier is a data defect to remove is `ds-clean`'s
  call. See `references/ds-features.encodings-scaling-interactions.md#scaling`.
- **Aggregation/window features** — automated aggregate construction over
  relational or temporal data. Trigger: the source has a group-by key (grain
  narrower than the modeling row) or a time axis. Kanter & Veeramachaneni,
  "Deep Feature Synthesis," IEEE DSAA 2015: automates aggregate feature
  construction over relational/temporal data. Feast, "Point-in-time joins" —
  https://docs.feast.dev/getting-started/concepts/point-in-time-joins : join
  only feature values timestamped ≤ event time. Additivity classification
  (Gates) runs before any aggregation-derived feature ships. See
  `references/ds-features.aggregation-leakage-selection.md#aggregation`.
- **Interactions** — explicit interaction/polynomial terms across two or
  more features. Trigger: domain knowledge or a diagnostic (not run by
  default) suggests a non-additive combination matters. LITERATURE-THIN:
  classical interaction-detection theory (Friedman & Popescu H-statistic)
  could not be verified by fetch and is excluded rather than cited from
  memory. scikit-learn `PolynomialFeatures` —
  https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html.
  Edges: degree/feature-count blow-up is a compute-cost matter
  (`references/doctrine-scale-cost.md`, pointer); treat as practice guidance, not a
  settled discovery method. See
  `references/ds-features.encodings-scaling-interactions.md#interactions`.
- **Leak-safe target encoding** — out-of-fold/ordered target statistics
  for a target/mean encoding on a high-cardinality categorical. Trigger:
  Encodings selected a target/mean scheme for a high-cardinality field.
  "CatBoost: unbiased boosting with categorical features" —
  https://arxiv.org/abs/1706.09516 : names target leakage/prediction
  shift in naive target statistics, fixes via ordered target statistics.
  scikit-learn `TargetEncoder` cross-fitting: k-fold cross-fitting to
  prevent target information leaking. Pargent et al., "Regularized
  target encoding" — https://arxiv.org/abs/2104.00629. Edges:
  smoothing/shrinkage reduces variance but does not by itself prevent
  leakage — only an out-of-fold/ordered scheme does; the general
  fit-on-train-only mandate (Gates) is necessary but not sufficient here,
  this subfield's delta is the in-fold leak specifically. See
  `references/ds-features.aggregation-leakage-selection.md#target-encoding`.
- **Feature selection (pruning, not attribution)** — filter/wrapper/
  embedded selection to finalize the candidate set before `ds-model`.
  Trigger: mandatory — every composition of this skill ends with a pruning
  decision, even "keep all." Guyon & Elisseeff, "An Introduction to Variable
  and Feature Selection," JMLR —
  https://www.jmlr.org/papers/special/feature03.html : seminal filter/
  wrapper/embedded taxonomy. See
  `references/ds-features.aggregation-leakage-selection.md#selection`.

`mandatory`: pruning (even a no-op "keep all" decision) is the one step
every composition of this skill takes, unlike the other five, which fire
only on their own trigger.

## Production considerations

Two deltas, both pointers: the **feature store** — versioned, served
feature values with training-serving parity — is `ds-mlops`'s (subfields:
serving, registry, training-serving skew); this skill still owns the
feature's *definition* that the store serves. **Coverage/provenance
drift** in a production feature (an upstream field's collector config or
asserter changes) is `ds-mlops`'s monitoring, seeded by this skill's
provenance classes the way `ds-clean`'s assertion suite seeds schema-drift
monitoring — re-validation of the affected feature loops back here via
`mlops-drift → features`, scoped to the affected entries only.
