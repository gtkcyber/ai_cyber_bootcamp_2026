# Metric-cost matching and slice-wise analysis

Depth for the metric-selection, slice-wise, and stability subfields.
SKILL.md carries the protocol; this file carries worked detail and full
citations.

## Metric↔business-cost matching {#metric-cost}

**Literature**: classification metrics under imbalance — Saito &
Rehmsmeier, "The Precision-Recall Plot Is More Informative than the ROC
Plot," PLOS ONE —
https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0118432 ;
Davis & Goadrich, "The Relationship Between Precision-Recall and ROC
Curves" — https://pages.cs.wisc.edu/~jdavis/davisgoadrichcamera2.pdf.

**Selection procedure** (this skill's delta — the *procedure*, not a metric
catalog):

1. Identify task type (binary/multiclass classification, ranking,
   regression). Per-family metric definitions beyond this procedure — NDCG/
   MRR for ranking, RMSE/MAE/quantile loss for regression — are catalog
   material and family-skill (`ds-ranking`, `ds-supervised`,
   `ds-timeseries`) pointers, never restated here.
2. Quantify imbalance: class prevalence (classification) or cost-asymmetry
   magnitude (regression/ranking with asymmetric error costs).
3. Choose the curve family: prefer PR over ROC whenever prevalence is low
   or costs are asymmetric — ROC-AUC is not imbalance-robust (Saito &
   Rehmsmeier); ROC is retained only when classes are roughly balanced and
   costs are symmetric. Note PR-curve interpolation is non-linear, unlike
   ROC's (Davis & Goadrich) — don't linearly interpolate between two PR
   points to estimate a third.
4. Pick **one** headline metric for `scorecard.primary_metric` — not a
   metric zoo. Secondary metrics may be reported alongside it, but
   threshold selection and comparison decisions run against the primary
   metric only.
5. State the justification sentence naming the specific failure mode
   avoided — this is the exact string the Gates check reads (SKILL.md).

## Slice-wise error analysis {#slices}

**Literature**: Mitchell et al., "Model Cards for Model Reporting" —
https://arxiv.org/abs/1810.03993. Requires performance by group **and**
intersections of groups — a report of only marginal per-group metrics
(never intersections) does not satisfy the "model card" bar this subfield
targets.

- **Sourcing grouping variables**: use `ds-profile`'s `grouping_variables`
  (the keys that make rows non-iid) as the default slice candidates;
  operationally distinct segments named by the task (e.g. a stated
  regulatory or business segment) add to this set, they don't replace it.
- **Small-n caveat**: a slice metric computed over few rows is a
  high-variance estimate, not a settled result — report the slice's `n`
  alongside its metric, and prefer a variance/CI on small slices over a
  bare rate.
- **Slice-level population statements**: each slice's denominator is its
  own — a slice claim inherits nothing from the aggregate's population
  statement automatically. Example: "slice `region=EU`: n=340 of the
  `region=EU`-tagged rows; aggregate `population_statement` notes EU
  coverage gap during outage window `[t1,t2]` — this slice's numbers
  exclude that window" is a complete slice-level statement; "EU: 340 rows,
  87% precision" with no coverage note is not.
- Every slice cites the `ds-data-models` semantic-dictionary interpretation
  (or `attest_id`) of the field it slices on — a slice on a raw column with
  no interpretation on record is a slice on an unverified assumption about
  what that column means.

## Stability {#stability}

**LITERATURE-THIN.** No canonical single paper on evaluation stability
specifically; seed-variance reporting is mostly a deep-learning
reproducibility topic and thin outside it. What's established: Raschka,
"Model Evaluation, Model Selection, and Algorithm Selection in Machine
Learning" — https://arxiv.org/abs/1811.12808 — characterizes the
bias-variance tradeoff of holdout, k-fold CV, and bootstrap estimators:

- **Holdout**: highest variance, especially with small `n`; cheapest.
- **k-fold CV**: averages over folds, reducing variance relative to a
  single holdout, at `k`×  the compute cost.
- **Bootstrap** (incl. `.632`/`.632+` variants): further variance
  reduction with a pessimistic-bias correction term.

Beyond this — multi-seed variance for stochastic training algorithms,
specifically — is **practice guidance, not established literature**: treat
seed variance as a distinct source from resampling variance (a model
retrained on the identical split with a different seed can still move the
metric), and report both sources separately rather than conflating them
into one number.

**Reporting convention** (practice guidance): a headline metric is always
reported with its estimator (holdout / k-fold / bootstrap) and its
spread (fold range, CI, or multi-seed range) together — never a bare point
estimate. This is what `scorecard.primary_metric`'s and
`comparison_result`'s variance/spread field encodes (SKILL.md Gates).
