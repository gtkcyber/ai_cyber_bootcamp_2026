# Operating-point selection and deployment-population reconciliation

Depth for the cost-sensitive-threshold and deployment-population-
reconciliation subfields. SKILL.md carries the protocol; this file carries
worked detail and full citations.

## Single-threshold/operating-point selection {#threshold}

**Literature**: Elkan, "The Foundations of Cost-Sensitive Learning" —
https://cseweb.ucsd.edu/~elkan/rescale.pdf. For a binary classifier with
**calibrated** probabilities, the cost-minimizing threshold is:

```
p* = C(FP) / (C(FP) + C(FN))
```

where `C(FP)` and `C(FN)` are the costs of a false positive and false
negative respectively. This is **not** the model's raw decision boundary —
it requires the scores to already be calibrated probabilities; applying the
formula to raw, uncalibrated scores silently miscalibrates the threshold.
Calibration itself is `ds-model`'s (pointer only).

**Generalized / base-rate-weighted form** (this skill's delta — the general
form; domain overlays supply the concrete cost taxonomy): expected cost per
decision is

```
E[cost | predict 1] = P(y=0|x) * C(FP)
E[cost | predict 0] = P(y=1|x) * C(FN)
```

`p*` is the point where these are equal. In low-prevalence decision
settings (e.g. any alert-triage-style workflow — a general pattern, not a
cyber peculiarity), the base rate is a first-class input, not an
afterthought: at a 0.1% base rate, even a well-calibrated model produces
far more false positives than true positives at any threshold below the
cost-optimal point, because the false-positive volume scales with the
(much larger) negative-class size, not with the (much smaller) positive
rate.

**Common failure mode**: `C(FP)` and `C(FN)` stated in mismatched units
(e.g. `C(FP)` in analyst-minutes, `C(FN)` in dollars-of-loss) — both costs
must be converted to a common unit before the formula is applied, or the
threshold it produces is not comparable to either cost as originally
stated. State the conversion, don't silently apply it.

**Gate tie**: `scorecard.operating_point` cites the explicit `C(FP)`/`C(FN)`
pair (in a stated common unit) and confirms calibration before applying the
formula — a threshold left at the 0.5 default with no stated cost matrix
fails the gate (SKILL.md).

## Deployment-population reconciliation {#reconciliation}

**Literature**: Zinkevich, "Rules of Machine Learning," Rule #37 —
https://developers.google.com/machine-learning/guides/rules-of-ml. Sculley
et al., "Hidden Technical Debt in Machine Learning Systems," NeurIPS 2015 —
https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf.

**Three-way skew measurement** (Rule #37) — a staged reconciliation that
separates distinct failure causes instead of collapsing an offline/online
metric gap into one:

1. **Train vs. holdout**: should already match if the pipeline (splitting,
   feature computation) is correct — a mismatch here is an engineering bug,
   not population drift.
2. **Holdout vs. next-day data**: isolates temporal population drift — the
   world moved between when the holdout was drawn and now.
3. **Next-day vs. live-serving**: isolates engineering/serving skew —
   features computed differently in the serving path than in the offline
   pipeline (training-serving skew, `ds-mlops`' parity-testing pointer).

Sculley et al. add two further causes to check before concluding "drift":
**external-world change** (the phenomenon being modeled genuinely shifted)
and **undeclared consumers** (something downstream started depending on
the model's output in a way that changes the population it's now scoring,
without that dependency being visible upstream).

**Reconciliation check** (this skill's gate, SKILL.md): compare the
scorecard's own evaluation-population statement against two named fields —
`ds-scoping`'s `intended_scoring_population` (the task card's target
population) and `ds-data-models`'s `population_statement` (what the
dataset actually contains, per its collector-coverage discipline). A
mismatch (e.g. the eval set covers one region but the intended scoring
population is global; the eval set predates a collector-configuration
change the population statement documents) is recorded as a finding, never
silently absorbed by scoring against whatever population the test set
happened to contain.
