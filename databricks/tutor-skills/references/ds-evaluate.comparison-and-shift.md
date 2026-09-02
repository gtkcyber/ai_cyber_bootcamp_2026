# Comparison-with-uncertainty, dataset shift, and robustness

Depth for the comparison, dataset-shift-diagnosis, and robustness/
adversarial-evaluation subfields. SKILL.md carries the protocol; this file
carries worked detail and full citations.

## Comparison-with-uncertainty {#comparison}

**Literature**: Demšar, "Statistical Comparisons of Classifiers over
Multiple Data Sets," JMLR 7 — https://jmlr.org/papers/v7/demsar06a.html.
Argues against the paired t-test across datasets: CV-fold errors within a
dataset are not independent, so a classical paired t-test on fold-level
differences understates variance and overstates significance.

- **Two candidates**: Wilcoxon signed-ranks test on the paired per-fold (or
  per-dataset) metric differences.
- **Three or more candidates**: Friedman test (omnibus), followed by a
  post-hoc test (Nemenyi, or Bonferroni-Dunn against a control) with a
  critical-difference (CD) diagram to visualize which pairs differ
  significantly.
- **This skill's delta**: *uses* the CV/resampling scheme `ds-model`
  already chose (design choice: `ds-model`'s) to produce the fold-level
  metrics the test above consumes — it does not pick or redesign the CV
  scheme.
- **Selection economics**: a point-estimate delta with no significance test
  is not a declared winner. A "winner" inside the test's non-significant
  range fails the Gates check regardless of which point estimate is
  numerically higher.

## Dataset-shift diagnosis {#shift}

**Literature**: Quiñonero-Candela et al. (eds.), *Dataset Shift in Machine
Learning*, MIT Press 2009 —
https://direct.mit.edu/books/edited-volume/3841/Dataset-Shift-in-Machine-Learning
(bibliographic record corroborated cross-source; full text blocked
scraping). Defines the taxonomy formally: **covariate shift** (`P(X)`
changes, `P(Y|X)` stable), distinguished from prior-probability shift and
concept shift (`P(Y|X)` itself changes) — the diagnostic below targets
covariate shift specifically; a finding here does not by itself rule out
the other shift types.

**Adversarial validation** — "Adversarial validation, part one" —
https://fastml.com/adversarial-validation-part-one/. **LITERATURE-THIN**:
Kaggle-origin practitioner term, no peer-reviewed source.

Method: label training rows `0` and evaluation/scoring rows `1`, train a
classifier to distinguish them, and read the held-out AUC as a shift
signal:

- AUC near 0.5: the two sets are not distinguishable on the available
  features — no detected covariate shift.
- AUC near 1.0: the sets are easily distinguishable — strong covariate
  shift is present.
- The trained classifier's feature importances *hint at* which features
  drive the shift — this is a heuristic lead for investigation, not a
  causal identification of the shift's source. A high AUC alone does not
  identify which features drive it (SKILL.md).

**Threshold and loop-back**: state the AUC threshold above which a finding
counts as "shift detected" before running the check, not after seeing the
number.

## Robustness and adversarial evaluation {#robustness}

**Literature**: Goodfellow, Shlens, Szegedy, "Explaining and Harnessing
Adversarial Examples" — https://arxiv.org/abs/1412.6572 — introduces FGSM
(fast gradient sign method) and adversarial training as a countermeasure.
Croce et al., "RobustBench" — https://arxiv.org/pdf/2010.09670 —
standardizes evaluation via AutoAttack specifically to counter
**gradient-masking**: a defense can appear robust against a weak or
mis-tuned attack while remaining trivially breakable by a stronger one.

- **Attack budget**: state the perturbation budget (e.g. an L∞/L2 norm
  bound) explicitly — "robust" without a stated budget is not a claim,
  it's a fragment.
- **Attack strength**: prefer white-box gradient-based attacks when the
  model internals are available; when they aren't, use a transfer attack
  (craft on a substitute model) or a black-box baseline — this is what
  confirms the primary attack isn't gradient-masked (SKILL.md Gates).
- **Worst-case, not average-case**: report robust accuracy / attack success
  rate at the strongest attack considered, not accuracy against one weak
  attack relabeled as "robustness."
- **General form**: this evaluation logic is domain-agnostic (it
  originated in vision, but the framing — attacker perturbs input,
  defender reports worst-case performance under a stated budget —
  generalizes). Domain overlays (e.g. `ds-domain-cyber`, evasion of a
  security classifier) add the concrete threat model and cost taxonomy;
  this skill keeps the general evaluation form only.
- **Edges**: deep adversarial-ML research beyond FGSM/RobustBench-class
  evaluation (certified robustness, novel attack families) is a
  research-escalation trigger — consult `ds-method-composition`'s hook
  before escalating externally.
