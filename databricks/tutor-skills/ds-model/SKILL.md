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
  *inputs*, not applied post-hoc — `doctrine-scale-cost.md`'s threshold,
  read from `ds-scoping`'s `kill_check`, never restated here. See
  `references/ds-model.selection-economics.md`.

| Subfield | Participation |
|---|---|
| Baseline-first ladder | mandatory |
| Tuning protocol | mandatory |
| CV design choice | mandatory |
| Imbalance intervention decision | `conditional-on-data:class-imbalance` |
| Calibration | `conditional-on-data:probability-output-consumed` |
| Learning-curve/data-sufficiency method | `conditional-on-data:sample-sufficiency-borderline` |
| Selection economics | mandatory |

`mandatory` here: runs whenever `ds-model` composes — every candidate
comparison needs a baseline, a tuning decision (even "defaults,
justified"), a CV design, and a cost accounting; the other three fire
only on their own data-triggered condition.

## Gates

- Split refinement: CV folds and nested resampling operate strictly within
  `ds-scoping`'s `split_design` train partition — model selection never
  enlarges the split boundary. Code-checkable: every fold's row indices
  are a subset of the recorded train partition, never the held-out test.
- CV design: a declared group key (from `ds-profile`'s `grouping_variables`)
  or an explicit "rows are independent" assertion is on record before any
  CV scheme runs — plain k-fold with neither present fails this gate.
- Baseline-first ladder: `selection_rationale` records a comparably-tuned
  baseline result before any complex-model claim — an untuned baseline
  compared against a tuned complex model fails.
- Tuning protocol: `selection_rationale` records the search method and
  budget for every compared candidate, or an explicit "defaults justified"
  statement — a chosen model with neither fails.
- Imbalance (when triggered): `selection_rationale` names the chosen
  intervention (resampling / algorithm-level / threshold-adjustment /
  none) and why — accuracy as the sole justification fails (metric
  selection under imbalance is `ds-evaluate`'s; this gate only requires
  the decision be named).
- Calibration (when triggered): `model_card` records a calibration check
  (reliability curve, Brier score, or ECE) computed on held-out data — a
  calibration claim evaluated on training data fails.
- Learning curve (when triggered): `model_card` records the curve result
  and states whether/how it was extrapolated — an extrapolation presented
  as a measured result fails.
- Selection economics: whenever `ds-evaluate`'s comparison-with-uncertainty
  finds candidates statistically indistinguishable, `selection_rationale`
  names the cost inputs that broke the tie — declaring a winner within
  noise with no cost rationale fails.

## Edges

Covered: cross-family baseline-first escalation ladder, tuning protocol,
CV design choice for the modeling loop (grouped/blocked/time-aware),
imbalance intervention decision, calibration, learning-curve/data-
sufficiency method, selection economics (cost as a selection input,
tie-breaking at statistically indistinguishable performance).

Not covered here, pointer only: family-specific selection trees and
actual model fitting (`ds-supervised`, `ds-deep-learning`,
`ds-timeseries`, etc. — this skill routes to Layer 2, never trains);
fit-on-train-only CV mechanics (`ds-features`); using the chosen CV
scheme for comparisons and the comparison-with-uncertainty significance
test (`ds-evaluate`, which also enforces selection economics at the
metric-comparison level); imbalance generation mechanics
(`ds-simulation`) and metric selection (`ds-evaluate`); serving/
retraining cost economics (`ds-mlops`, `doctrine-scale-cost.md`).

Not a `ds-scoping` loop-back — don't conflate it with the four rows that
re-run `ds-scoping`.

## Audit mode

Input: an existing external model artifact authored outside this skill (a
notebook, an experiment-tracker run, a prior analyst's writeup).
Undocumented claims are treated as unregistered under Gates: flagged, never
assumed.

## Production considerations

`doctrine-scale-cost.md` applies at every step touching selection
economics — this skill's delta is the selection *procedure* (baseline-
first ladder, tie-breaking at indistinguishable performance); the
doctrine and its cost threshold live there and in `ds-scoping`'s
`kill_check`, never restated here. `mlops serving constraints → model
selection` gains full loop-back eligibility at production tier
(`tiers.md`). `ds-mlops` owns ongoing serving/retraining cost,
compression when/why, and production drift monitoring — pointers only.
