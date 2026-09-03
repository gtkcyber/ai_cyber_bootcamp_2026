# Composition patterns — imputer, feature-extractor, residual, ensembles

Worked examples and full citation context for `SKILL.md`'s Subfields.
Diagram notation used throughout: `[component]: fit_on=<split/description>
→ outputs=<typed output> → visible_to=<downstream components/splits>`.

## model-as-imputer

van Buuren & Groothuis-Oudshoorn, "mice: Multivariate Imputation by Chained
Equations in R," JSS 45(3), 2011 — https://www.jstatsoft.org/article/view/v045i03 .
MICE imputes each variable conditional on the others via chained
regression equations, iterating to convergence; run *m* times with
different random draws to produce *m* imputed datasets, then pool via
Rubin's rules — the pooling mechanics and their variance decomposition are
`ds-uncertainty`'s (its multiple-imputation subfield); this pattern's own
delta is only the composition contract: the imputer is a fitted component
with its own leakage boundary, and single-pass point-estimate imputation
(mean/median/mode, or one MICE draw treated as final) silently discards
the uncertainty `ds-uncertainty` would have propagated.

```
[imputer]: fit_on=train split only, non-target columns, MAR assumption
  stated → outputs=imputed column (provenance: derived) →
  visible_to=downstream feature/model steps on the SAME split only
  (imputer refit per split — never fit on pooled train+test)
```

Failure mode: if the task can't afford *m*-way pooling, name that as an
accepted limitation in `leakage_boundaries` — don't silently drop the
uncertainty term and present the imputed column as if it were observed.

## model-as-feature-extractor (stacking)

Wolpert, "Stacked Generalization," Neural Networks 5(2), 1992 —
http://machine-learning.martinsewell.com/ensembles/stacking/Wolpert1992.pdf .
Level-0 base learners each produce out-of-fold (OOF) predictions on the
training set via k-fold cross-validation — every training row's level-0
prediction comes from a model that never saw that row during its own fit.
The level-1 combiner trains on those OOF predictions, never in-sample
ones. At inference, level-0 models are refit on the full training data to
predict on genuinely new instances, and the level-1 combiner applies to
those.

```
[base-model-k]: fit_on=train folds ≠ k → outputs=OOF prediction
  (provenance: derived) → visible_to=[combiner]'s training rows for fold k
  only
[combiner]: fit_on=OOF predictions across all folds → outputs=stacked
  prediction → visible_to=evaluation/serving
```

## residual-as-signal

Vallis, Hochenbaum, Kejariwal (Twitter), "Automatic Anomaly Detection in
the Cloud Via Statistical Learning," 2017 — https://arxiv.org/abs/1704.07706 .
Fit an expected-behavior model (seasonal decomposition, forecast), take
the forecast residual (observed − expected) as the anomaly/drift score.
The residual is a *derived* signal whose validity is entirely inherited
from the expected-behavior model's own assumptions.

```
[expected-behavior-model]: fit_on=train/history window, assumptions=
  <seasonality period, trend form — stated explicitly> → outputs=forecast
[residual]: computed=observed − forecast → outputs=residual (provenance:
  derived, inherits expected-behavior-model's assumption risk) →
  visible_to=anomaly detector / drift monitor
```

Failure mode: a wrong seasonality period doesn't just weaken the residual
— it manufactures periodic spurious "anomalies" out of the misfit itself.
State the assumption in the diagram, not just the residual's alert
threshold.

## detector ensembles

Zimek, Campello, Sander, "Ensembles for Unsupervised Outlier Detection:
Challenges and Research Questions," ACM SIGKDD Explorations 15(1), 2014 —
https://www.kdd.org/exploration_files/V15-01-02-Zimek.pdf . Unlike
supervised ensembles, unsupervised outlier ensembles have no ground truth
to validate the combination rule against. Diversity mechanisms: feature
bagging (each member sees a different feature subset), algorithm-family
diversity (density-based + distance-based + isolation-based members,
rather than the same algorithm with different seeds), or subsampling.
Combination rules: averaging, max, rank-based voting. Diversity helps only
if member errors aren't systematically correlated — members sharing a
feature space or an upstream data source can produce "different"
algorithms that still fail on the same records.

```
[detector-i, i=1..k]: fit_on=<own feature subset/algorithm/seed, stated> →
  outputs=member score (provenance: derived) → visible_to=[combiner]
[combiner]: fit_on=member scores → outputs=ensemble score/vote →
  diversity_check=<member score correlation measured, not assumed>
```
