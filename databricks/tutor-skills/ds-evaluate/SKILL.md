---
name: ds-evaluate
description: "Post-model evaluation intelligence: metric↔business-cost matching under imbalance, slice-wise error analysis, stability, comparison-with-uncertainty (applying the chosen CV scheme), dataset-shift diagnosis, robustness/adversarial evaluation, cost-sensitive operating-point selection, and deployment-population…"
---

# ds-evaluate

Runs after `ds-model` writes the model card and before `ds-verify`. Full
depth and citations live in `references/`; this file is protocol only.

## Subfields

- **Metric↔business-cost matching (imbalance)** — trigger: imbalanced or
  cost-asymmetric classification/ranking task. Saito & Rehmsmeier, PLOS ONE
  — https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0118432 :
  ROC overstates reliability on imbalanced data; PR-AUC preferred, but
  interpolation is non-linear (Davis & Goadrich —
  https://pages.cs.wisc.edu/~jdavis/davisgoadrichcamera2.pdf). See
  `references/ds-evaluate.metric-cost-and-slices.md#metric-cost`.
- **Slice-wise error analysis** — trigger: grouping variables exist or a
  segment is named. Mitchell et al., "Model Cards for Model Reporting" —
  https://arxiv.org/abs/1810.03993 : report by group and intersections —
  aggregate hides subgroup disparity; small-n slices are high-variance, not
  settled results. See `references/ds-evaluate.metric-cost-and-slices.md#slices`.
- **Stability** — **LITERATURE-THIN**: no canonical paper; seed-variance is
  mostly a DL-reproducibility topic, thin outside it. Trigger: any headline
  metric about to be reported as a point estimate. Raschka —
  https://arxiv.org/abs/1811.12808 : bias-variance of holdout/CV/bootstrap
  estimators (established) — reporting convention beyond that is practice
  guidance. See `references/ds-evaluate.metric-cost-and-slices.md#stability`.
- **Comparison-with-uncertainty** (applies the chosen CV scheme) — trigger:
  comparing ≥2 candidates, incl. vs. baseline. Demšar, JMLR 7 —
  https://jmlr.org/papers/v7/demsar06a.html : Wilcoxon signed-ranks (two),
  Friedman + post-hoc (3+); no paired t-test across datasets — enforces
  selection economics. See `references/ds-evaluate.comparison-and-shift.md#comparison`.
- **Dataset-shift diagnosis** (covariate shift, adversarial validation) —
  "covariate shift" is formal (Quiñonero-Candela et al., MIT Press 2009 —
  https://direct.mit.edu/books/edited-volume/3841/Dataset-Shift-in-Machine-Learning);
  "adversarial validation" is **LITERATURE-THIN** (Kaggle-origin term, no
  peer review — https://fastml.com/adversarial-validation-part-one/ :
  train-vs-test AUC as a heuristic, not a formal test — a high AUC alone
  doesn't identify which features drive it). Trigger: a gap between the
  train/eval population and the population being scored. See
  `references/ds-evaluate.comparison-and-shift.md#shift`.
- **Robustness and adversarial evaluation** — trigger: the model faces an
  adversary who can perturb inputs (general form; overlays add domain
  delta). Goodfellow et al. — https://arxiv.org/abs/1412.6572 : FGSM.
  Croce et al., RobustBench — https://arxiv.org/pdf/2010.09670 :
  standardized attacks against gradient-masking overestimation; worst-case,
  not average-case, metrics. **Edges**: deep adversarial-ML research beyond
  this is a research-escalation trigger. See
  `references/ds-evaluate.comparison-and-shift.md#robustness`.
- **Single-threshold/operating-point selection under a cost function** —
  trigger: one actionable threshold converts scores to decisions. Elkan —
  https://cseweb.ucsd.edu/~elkan/rescale.pdf : `p* = C(FP)/(C(FP)+C(FN))`
  for calibrated probabilities; no symmetric-cost (0.5) default without an
  explicit cost matrix. General form covers base-rate-weighted cost for
  low-prevalence decisions (e.g. alert triage) — domain overlays keep the
  specific taxonomy. See `references/ds-evaluate.threshold-and-reconciliation.md#threshold`.
- **Deployment-population reconciliation** — trigger: always (every task
  card carries `intended_scoring_population`). Zinkevich, Rule #37 —
  https://developers.google.com/machine-learning/guides/rules-of-ml :
  three-way skew (train-vs-holdout, holdout-vs-next-day, next-day-vs-live).
  Sculley et al. — https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf :
  don't collapse an offline/online gap into one cause. Reconciles against
  the task card's stated population, not just the training population. See
  `references/ds-evaluate.threshold-and-reconciliation.md#reconciliation`.

`mandatory` rows fire whenever `ds-evaluate` composes at all; the other
five fire only on their own trigger.

## Production considerations

Three deltas, pointers: the shift-diagnosis method here is what `ds-mlops`'s
production drift monitor should apply on a rolling basis once deployed —
`ds-mlops` owns ongoing monitoring, this skill only seeds the method (as
`ds-clean`'s assertion suite seeds monitoring).
