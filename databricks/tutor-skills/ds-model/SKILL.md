---
name: ds-model
description: "Method-agnostic model- selection doctrine: baseline-first escalation ladder, tuning protocol, cross-validation design choice, class-imbalance intervention decision, calibration, learning-curve/data-sufficiency method, and selection economics (cost as a selection input, not an afterthought)."
---

# ds-model

Runs after `ds-features`, before `ds-evaluate` scores the selected
candidate. Method-agnostic: decides *how* to select a model, never
*which* algorithm family to try — that choice and the fitting route to
Layer 2 (`ds-supervised`, `ds-deep-learning`, `ds-timeseries`, etc.). Full
depth, worked examples, and citations live in `references/`; this file is
protocol only.

## Subfields

- **Baseline-first ladder** — no complexity claim survives without a
  comparably-tuned baseline on record; a tuned complex model beating an
  untuned baseline is not evidence the complexity was necessary. Lipton &
  Steinhardt, "Troubling Trends in Machine Learning Scholarship" —
  https://arxiv.org/abs/1807.03341. See
  `references/ds-model.baseline-tuning-cv.md#baseline`.
- **Tuning protocol** — hyperparameter optimization; random search
  matches/beats grid search in far less compute since few hyperparameters
  matter per dataset — grid search is not a safe default. Bergstra &
  Bengio, "Random Search for Hyper-Parameter Optimization," JMLR 13 —
  https://jmlr.org/papers/v13/bergstra12a.html. See
  `references/ds-model.baseline-tuning-cv.md#tuning`.
- **CV design choice (grouped/blocked CV)** — plain k-fold on grouped or
  temporal rows leaks and inflates scores even when correlation isn't
  visible in residuals. Roberts et al., "Cross-validation strategies for
  data with temporal, spatial, hierarchical or phylogenetic structure,"
  Ecography — https://www.ecography.org/appendix/ecog-02881; scikit-learn,
  "Cross-validation" —
  https://scikit-learn.org/stable/modules/cross_validation.html
  (`GroupKFold`, `TimeSeriesSplit`). Refines, never widens, `ds-scoping`'s
  `split_design`. See `references/ds-model.baseline-tuning-cv.md#cv-design`.
- **Imbalance intervention decision** — resampling isn't automatically the
  right fix; threshold/output adjustment competes and can outperform it;
  accuracy is misleading under imbalance regardless of intervention.
  Krawczyk, "Learning from imbalanced data: open challenges and future
  directions," Progress in Artificial Intelligence —
  https://link.springer.com/article/10.1007/s13748-016-0094-0. See
  `references/ds-model.imbalance-calibration-curve.md#imbalance`.
- **Calibration** — accuracy and calibration are orthogonal; Platt/isotonic
  are binary-only; must calibrate on held-out data, never train. Platt,
  "Probabilistic Outputs for SVMs" —
  https://www.cs.cornell.edu/courses/cs678/2007sp/platt.pdf; Zadrozny &
  Elkan, "Transforming Classifier Scores into Accurate Multiclass
  Probability Estimates" —
  http://www.cs.columbia.edu/~djhsu/coms4771-f25/handouts/zadrozny2002kdd.pdf;
  Guo et al., "On Calibration of Modern Neural Networks," ICML 2017 —
  https://proceedings.mlr.press/v70/guo17a/guo17a.pdf (modern NNs are
  systematically overconfident; temperature scaling fixes it). See
  `references/ds-model.imbalance-calibration-curve.md#calibration`.
- **Learning-curve/data-sufficiency method** — curves are noisy, can be
  non-monotonic at small N; extrapolation assumes a parametric (e.g.
  power-law) form not guaranteed to hold. Mohr & van Rijn, "Learning Curves
  for Decision Making in Supervised Machine Learning: A Survey" —
  https://arxiv.org/abs/2201.12150. Owns the *method*; `ds-scoping`'s
  kill-check only judges whether to attempt, never computes the curve. See
  `references/ds-model.imbalance-calibration-curve.md#learning-curve`.
- **Selection economics** — LITERATURE-THIN: no single established name;
  nearest concepts "cost-sensitive learning" and "Pareto-optimal model
  selection" (the latter not consolidated) — present as practice guidance,
  not settled theory. Elkan, "The Foundations of Cost-Sensitive Learning" —
  https://cseweb.ucsd.edu/~elkan/rescale.pdf (cost-matrix coherence,
  threshold conversion). At statistically indistinguishable performance,
  prefer the cheaper model (training cost, inference latency/throughput,
  hardware, retraining, operational complexity, debuggability); the ladder
  stops when the gain stops paying for itself. Cost/latency are selection
  *inputs*, not applied post-hoc — `references/doctrine-scale-cost.md`'s threshold,
  read from `ds-scoping`'s `kill_check`, never restated here. See
  `references/ds-model.selection-economics.md`.

`mandatory` here: runs whenever `ds-model` composes — every candidate
comparison needs a baseline, a tuning decision (even "defaults,
justified"), a CV design, and a cost accounting; the other three fire
only on their own data-triggered condition.

## Production considerations

`references/doctrine-scale-cost.md` applies at every step touching selection economics
— this skill's delta is the selection *procedure* (baseline- first ladder,
tie-breaking at indistinguishable performance); the doctrine and its cost
threshold live there and in `ds-scoping`'s `kill_check`, never restated
here. `ds-mlops` owns ongoing serving/retraining cost, compression when/why,
and production drift monitoring — pointers only.
