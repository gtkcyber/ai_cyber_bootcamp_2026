---
name: ds-features
description: "Feature engineering and the leak-safe transform pipeline: encodings, scaling, aggregation/window features, interactions, leak-safe target encoding, feature selection (pruning). Owns the fit-on-train-only pipeline-object mandate."
---

# ds-features

Runs after `ds-labeling`, before `ds-model` (`manifest.json`'s lifecycle
list, position 8). Not re-entrant: fires once per task in normal
composition; loop-backs into it re-run it, they are not a second entry
point. Full depth, worked examples, and citations live in `references/`;
this file is protocol only.

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
  plain encoding. See `references/encodings-scaling-interactions.md#encodings`.
- **Scaling** — feature scaling for scale-sensitive downstream methods
  (distance-based, gradient-based, regularized-linear). Trigger: a
  composed family/model that is scale-sensitive (the family skill states
  this; not re-derived here). scikit-learn, "Preprocessing data" —
  https://scikit-learn.org/stable/modules/preprocessing.html :
  StandardScaler/MinMaxScaler/RobustScaler; robust scalers preferred
  under outliers. Edges: fit-on-train-only mechanics for the scaler is
  the general pipeline-object mandate (Gates), not a separate concern
  here; whether an outlier is a data defect to remove is `ds-clean`'s
  call. See `references/encodings-scaling-interactions.md#scaling`.
- **Aggregation/window features** — automated aggregate construction over
  relational or temporal data. Trigger: the source has a group-by key (grain
  narrower than the modeling row) or a time axis. Kanter & Veeramachaneni,
  "Deep Feature Synthesis," IEEE DSAA 2015: automates aggregate feature
  construction over relational/temporal data. Feast, "Point-in-time joins" —
  https://docs.feast.dev/getting-started/concepts/point-in-time-joins : join
  only feature values timestamped ≤ event time. Additivity classification
  (Gates) runs before any aggregation-derived feature ships. See
  `references/aggregation-leakage-selection.md#aggregation`.
- **Interactions** — explicit interaction/polynomial terms across two or
  more features. Trigger: domain knowledge or a diagnostic (not run by
  default) suggests a non-additive combination matters. LITERATURE-THIN:
  classical interaction-detection theory (Friedman & Popescu H-statistic)
  could not be verified by fetch and is excluded rather than cited from
  memory. scikit-learn `PolynomialFeatures` —
  https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html.
  Edges: degree/feature-count blow-up is a compute-cost matter
  (`doctrine-scale-cost.md`, pointer); treat as practice guidance, not a
  settled discovery method. See
  `references/encodings-scaling-interactions.md#interactions`.
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
  `references/aggregation-leakage-selection.md#target-encoding`.
- **Feature selection (pruning, not attribution)** — filter/wrapper/
  embedded selection to finalize the candidate set before `ds-model`.
  Trigger: mandatory — every composition of this skill ends with a pruning
  decision, even "keep all." Guyon & Elisseeff, "An Introduction to Variable
  and Feature Selection," JMLR —
  https://www.jmlr.org/papers/special/feature03.html : seminal filter/
  wrapper/embedded taxonomy. See
  `references/aggregation-leakage-selection.md#selection`.

| Subfield | Participation |
|---|---|
| Encodings | conditional-on-data:categorical-features-present |
| Scaling | conditional-on-data:scale-sensitive-method |
| Aggregation/window features | conditional-on-data:relational-or-temporal-structure |
| Interactions | conditional-on-data:interaction-suspected |
| Leak-safe target encoding | conditional-on-data:target-encoding-selected |
| Feature selection | mandatory |

`mandatory`: pruning (even a no-op "keep all" decision) is the one step
every composition of this skill takes, unlike the other five, which fire
only on their own trigger.

## Gates

- Every `feature_dictionary` entry states its semantic claim and cites
  the `ds-data-models` semantic-dictionary entry it derives from; an
  event-counting feature additionally cites the `attest_id` of the
  Attest-register entry that claim counts — a feature naming neither
  citation fails this gate.
- Every `feature_dictionary` entry declares a provenance class; a
  derived/composite feature inherits the weakest of its inputs' classes
  (`doctrine-repro-provenance.md`'s Provenance classes section — inherited
  here, not re-derived).
- External unvalidated enrichments (vendor scores, GeoIP, third-party
  scoring APIs) are rejected outright as feature inputs; internally
  composed model outputs are admitted only when fit leak-safe within the
  pipeline and the composition is declared per `ds-method-composition`
  (`doctrine-repro-provenance.md`'s validation requirement).
- Additivity (additive/semi-additive/non-additive) is classified for
  every measure before any aggregation-derived feature is built from it,
  ratio-of-averages vs. average-of-ratios resolved at classification time,
  not after the aggregate ships (`doctrine-repro-provenance.md`'s
  Additivity section, gated jointly with `ds-profile`/`ds-analytics`;
  this skill's delta is the per-feature step before shipping).
- Any join executed to build a feature — not only the ingest join — passes
  the same-semantics + cardinality join gate, and post-join cardinality
  matches the declared grain; join gates apply at every join site.
- `pipeline_object` fits every stateful transform (scaler, encoder,
  imputer-adjacent statistic) on the train split only — a statistic
  computed across train+test, or across the full pre-split dataset,
  fails this gate regardless of the downstream CV scheme
  (`doctrine-leakage.md`).
- Target encoding and any time-aware feature carry an explicit leakage
  treatment on record: out-of-fold/ordered target statistics for target
  encoding; a stated as-of timestamp discipline, provably bounded to ≤
  event time, for window features. A feature using naive in-fold target
  statistics, or a window with no stated bound, fails this gate.
- The `data-models` population statement is rewritten (never silently
  left stale) after any feature transform here that changes row coverage
  (drop-null policies, filtering joins) — cite the rewritten statement,
  don't restate the prior one.

## Edges

Covered: encodings, scaling, aggregation/window features, interactions,
leak-safe target encoding, feature selection for pruning, the
fit-on-train-only pipeline object.

Not covered, pointer only: CV design choice for the modeling loop
(`ds-model`); feature importance for interpretation on a fixed set
(`ds-explain`); stateful streaming *serving* computation of a window
feature already defined here (`ds-mlops`); model-as-feature-extractor
composition mechanics, e.g. embeddings as features
(`ds-method-composition`); observational identification/uplift if a
feature is meant to support a causal claim (`ds-causal`).

## Audit mode

Input: an existing external feature-engineering artifact authored outside
this skill (a feature-store definition file, a notebook's transform cell, a
prior analyst's pipeline script). An undocumented feature is treated as an
unregistered field under Gates: flagged, never assumed leak-safe.

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
