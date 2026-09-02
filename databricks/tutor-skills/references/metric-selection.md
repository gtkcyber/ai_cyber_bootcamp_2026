# Metric selection by task shape

Lookup table, not a tutorial. Per-task-shape primary metric(s), the
one-line failure mode each carries, and the mechanics owner. The
*procedure* for choosing among a task shape's metrics (imbalance
quantification, PR-vs-ROC selection, picking one headline metric) is
`ds-evaluate`'s (`references/metric-cost-and-slices.md#metric-cost` in
that skill) — this file is the catalog that procedure and every family
skill point into, not a restatement of it.

## Classification — binary, roughly balanced, symmetric cost

| Metric | Failure mode | Mechanics |
|---|---|---|
| Accuracy | Misleading under any class imbalance — not a default-safe choice | `ds-evaluate` |
| Precision / Recall / F1 | F1 assumes precision and recall are equally weighted; state the cost asymmetry explicitly if they aren't | `ds-evaluate` |
| ROC-AUC | Not imbalance-robust — overstates reliability on skewed classes (Saito & Rehmsmeier) | `ds-evaluate` |

## Classification — binary, imbalanced or cost-asymmetric

| Metric | Failure mode | Mechanics |
|---|---|---|
| PR-AUC | Preferred over ROC-AUC under low prevalence or asymmetric costs; curve interpolation is non-linear — don't linearly interpolate between two PR points (Davis & Goadrich) | `ds-evaluate` |
| Cost-sensitive single threshold (`p* = C(FP)/(C(FP)+C(FN))`) | Requires calibrated probabilities, not raw scores; no symmetric 0.5 default without an explicit cost matrix (Elkan) | `ds-evaluate` |

## Classification — multiclass

| Metric | Failure mode | Mechanics |
|---|---|---|
| Per-class precision/recall/F1 + macro/micro/weighted average | State which averaging scheme — macro weights every class equally and surfaces minority-class collapse that a micro/weighted average dilutes into the majority classes | `ds-supervised` (family delta) / `ds-evaluate` (generic scorecard) |

## Regression

| Metric | Failure mode | Mechanics |
|---|---|---|
| RMSE | Quadratic penalty on large errors — dominated by outliers `ds-clean` should already have resolved as error-outliers, not masked here | `ds-supervised` |
| MAE | Same units as RMSE, less sensitive to outliers, but state which was optimized against — the two rank models differently on skewed error distributions | `ds-supervised` |
| Quantile / pinball loss (per level) | Check for quantile crossing (a lower quantile predicted above a higher one) before reporting — enforced or verified, never assumed away | `ds-supervised` |

## Ranking

| Metric | Failure mode | Mechanics |
|---|---|---|
| NDCG | Graded relevance; the log-position discount is a modeling choice about attention decay, not a derived fact — different discount functions rank the same systems differently (Järvelin & Kekäläinen) | `ds-ranking` |
| MAP / MRR | Binary relevance only — silently discards graded-relevance information if applied to graded judgments | `ds-ranking` |
| Precision@k / Recall@k | Same binary-relevance caveat as MAP/MRR | `ds-ranking` |
| Any logged-click-derived metric (raw CTR, etc.) | Not reportable as relevance until a position-bias correction or interleaving design is stated — this is a gate, not an optional caveat | `ds-ranking` |

## Forecasting

| Metric | Failure mode | Mechanics |
|---|---|---|
| Point-forecast error (RMSE/MAE-family, per backtest fold) | Report per rolling-origin fold as a distribution across origins, never a single fixed-split number; state the rolling-origin scheme (expanding/rolling, window, step, number of origins) (Hyndman & Athanasopoulos §5.10) | `ds-timeseries` |
| Interval coverage (prediction intervals, conformal) | Not this family's metric — point-forecast error only; interval-coverage claims route to the family below | `ds-uncertainty` |

## Clustering — label-free

| Metric | Failure mode | Mechanics |
|---|---|---|
| Internal validation indices (silhouette, Dunn, Davies-Bouldin) | Encode a geometric assumption — typically convex, similarly-sized clusters. A high score on non-convex or unequal-density clusters is not evidence of a good partition; report the index's geometric bias alongside its value | `ds-unsupervised` |
| Stability (agreement across resamples/parameter perturbation) | Complements internal indices, never replaces them — a clustering can be perfectly stable and still geometrically wrong | `ds-unsupervised` |

## Anomaly — label-free

| Metric | Failure mode | Mechanics |
|---|---|---|
| (none intrinsic) | A detector's own score distribution is never self-validating — "top-scored 1%" is a selection rule, not evidence of anomalousness. Requires a ground-truth surrogate first: injected synthetic anomalies, held-out rare events, or expert audit of top-scored points | `ds-unsupervised` |
| Classification metrics against the surrogate, once one exists | Surrogate-derived positives are typically extremely imbalanced — apply the classification-imbalanced row above, not accuracy | `ds-evaluate` |

## Cross-cutting

Every metric above states its estimator and spread (holdout / k-fold /
bootstrap; fold range, CI, or multi-seed range) alongside the point value —
a bare point estimate fails `ds-evaluate`'s stability subfield regardless of
which row supplied the metric
(`references/metric-cost-and-slices.md#stability` in that skill). Slice-
wise breakdowns (by group and group intersections) apply on top of any row's
chosen metric, not instead of it.
