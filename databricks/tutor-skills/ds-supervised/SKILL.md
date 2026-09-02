---
name: ds-supervised
description: "Classification and regression method/goal family: generalized linear models through gradient-boosted trees on a baseline-first escalation ladder; multi-class/multi-label classification, ordinal regression, quantile regression; classical online-learning training mechanics."
---

# ds-supervised

Composes after `ds-features` writes the feature dictionary and pipeline
object, alongside `ds-model` (wraps this family's candidates in the
cross-family selection procedure — baseline-tuning parity, CV design,
tie-break economics — never itself picks an algorithm class). Full depth,
citations, and failure modes: `references/`; this file is protocol only.

## Subfields

- **GLM (linear models)** — trigger: "linear/logistic/Poisson regression,"
  or any classification/regression task needing its baseline rung.
  participation: `mandatory` (the ladder's baseline rung). Canonical
  methods (not exhaustive): linear regression, logistic regression,
  multinomial-logit, Poisson/Gamma regression, regularized variants.
  Edges: link misspecification is a variance-structure error, not a
  fit-quality one — escalate to a distributional diagnostic, not a bigger
  model. See `references/classification-regression-methods.md#glm`.
- **GBM** — trigger: "gradient boosting," or the GLM baseline underperforms
  with a comparably-tuned candidate on record. participation: `mandatory`
  (the family's default tabular workhorse rung). Canonical methods:
  gradient-boosted decision trees with shrinkage and row/column
  subsampling. Edges: escalation past GBM is `ds-deep-learning`'s, not a
  deeper method here — requires data-shape or benchmark evidence, not just
  "still not good enough." See
  `references/classification-regression-methods.md#gbm`.
- **Multi-class / multi-label classification** — trigger: label cardinality
  above two, or an instance holding more than one label simultaneously.
  participation: `conditional-on-data:multiclass-or-multilabel`. Canonical
  methods: one-vs-all reduction, native multinomial objectives
  (multi-class); binary relevance, classifier chains, label-powerset
  (multi-label). Edges: don't infer multi-class vs. multi-label from label
  count alone — check co-occurrence first. See
  `references/classification-regression-methods.md#multiclass-multilabel`.
- **Ordinal regression** — trigger: target is an ordered categorical
  (severity scale, rating, Likert item), not nominal or continuous.
  participation: `conditional-on-data:ordinal-target`. Canonical methods:
  proportional-odds / cumulative-link models. Edges: don't silently reduce
  to plain-integer regression or nominal classification — either is a
  stated tradeoff. See `references/ordinal-quantile-online.md#ordinal`.
- **Quantile regression** — trigger: the ask names a specific quantile of
  the target (P90 demand, a lower/upper bound), not a general uncertainty
  statement. participation: `conditional-on-data:named-quantile-requested`.
  Canonical methods: linear quantile regression (pinball loss),
  quantile-loss GBM. Edges: general interval coverage (not a named
  quantile) routes to `ds-uncertainty`. See
  `references/ordinal-quantile-online.md#quantile`.
- **Online-learning training mechanics** — trigger: training runs
  incrementally against a stream, candidate model class is classical
  (non-deep). participation:
  `conditional-on-data:streaming-or-incremental-training`. Canonical
  methods: SGD-trained linear/logistic models, online GLM fitting. See
  `references/ordinal-quantile-online.md#online-learning`.

## Selection tree

1. **Target type.** Continuous → regression. Nominal categorical →
   classification. Ordered categorical → ordinal — never silently default
   an ordered target into either of the first two.
2. **(Classification) label shape.** Cardinality 2 → binary. >2, one label
   per instance → multi-class (one-vs-all default). >2, co-occurring
   labels possible → multi-label (problem-transformation vs.
   algorithm-adaptation) — check co-occurrence before choosing, don't
   infer it from cardinality.
3. **Distributional ask.** A specific named quantile requested → quantile
   regression, with a monotonicity check across requested levels before
   reporting. A general uncertainty/interval statement → `ds-uncertainty`.
4. **Baseline → workhorse → ceiling rung.** Fit the GLM matching the
   response's distributional family (identity/logit/multinomial-logit/log
   link as the target demands) — the ladder's first rung, motivated by the
   same tuning-parity finding `ds-model`'s baseline-first-ladder gate
   enforces (`references/classification-regression-methods.md#ladder`).
   Escalate to GBM only once that baseline is on record with comparable
   tuning effort. This family's ladder stops at GBM — escalating further is
   `ds-deep-learning`'s subfield, requiring data-shape or benchmark
   evidence, not residual dissatisfaction with GBM performance.
5. **Training cadence.** Static batch → standard fit. Streaming/incremental
   with a classical candidate → online-learning training mechanics rung;
   deep incremental training routes to `ds-deep-learning`.
6. **Temporal/panel structure.** If leakage depends on time ordering, the
   split/validation scheme is `ds-timeseries`'s (router multi-family rule,
   `SKILL.md` §1) — this family still fits the rungs above, it does not
   set the split when that structure is present.

## Family-specific pitfalls and evaluation

Pitfalls (full detail, citations: `references/`):

- One-vs-all's accuracy-parity claim depends on each binary classifier
  being independently well-tuned — an undertrained ensemble beating a
  fancier scheme isn't evidence against it.
- Binary relevance (multi-label) ignores label correlations by
  construction; presenting it as correlation-aware misstates the method.
- Proportional-odds' parallel-lines assumption needs testing, not
  assertion; plain-integer/nominal reductions of an ordinal target discard
  structure either way.
- Quantile crossing (a lower quantile predicted above a higher one) is
  checked or enforced, never assumed away.
- Online-learning's compute-efficiency case assumes near-i.i.d. arrival;
  concept drift breaking that is `ds-mlops`'s monitoring concern, not
  solved by training mechanics alone.
- GLM link misspecification breaks the variance structure, not just the
  point fit.

**Evaluation delta.** `ds-evaluate` owns the generic scorecard; this
family's delta is metric family by target type — classification
(accuracy/precision/recall/F1/AUC, per `ds-model`'s imbalance decision),
regression (RMSE/MAE), quantile (pinball loss per level, plus the
monotonicity check above), multi-label (subset accuracy vs. per-label
metrics aren't interchangeable — state which), ordinal (near-miss-aware
rank metrics, not plain accuracy).

## Gates

- Every GLM fit records its link function and response family — an
  unstated link fails (`references/classification-regression-methods.md#glm`).
- Multi-class-vs-multi-label is recorded explicitly, never inferred
  silently from label cardinality.
- An ordinal target modeled via proportional-odds records whether
  parallel-lines was tested; a plain-integer/nominal reduction records
  that as a stated tradeoff.
- Any multi-quantile output records a monotonicity check (or enforcement)
  across requested levels before being reported.
- Any online/incremental run states its i.i.d.-ish convergence assumption
  is monitored downstream (`ds-mlops`), not presumed solved.
- Fit-on-train-only compliance (`ds-features`) and the baseline-first-
  ladder gate (comparably-tuned baseline, tuning parity, tie-break
  economics; `ds-model`) — cited, neither re-checked here.
- Doctrine gates triggered: leakage, provenance/additivity, scale/cost
  (`references/doctrine-leakage.md`, `doctrine-repro-provenance.md`,
  `doctrine-scale-cost.md`) — linked, not restated.

## Edges

Covered: GLM/GBM ladder, multi-class/multi-label, ordinal regression,
named-quantile regression, classical online-learning training mechanics.

Not covered here, pointer only: imbalance decision, CV design, tuning
protocol (`ds-model`); fit-on-train-only mechanics (`ds-features`); generic
evaluation scorecard (`ds-evaluate`); general interval/uncertainty coverage
(`ds-uncertainty`); escalation past GBM and deep online/ incremental
training (`ds-deep-learning`); online-learning serving wrapper (`ds-mlops`).
