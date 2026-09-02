---
name: ds-stats
description: "Composes alongside any phase whenever a design or significance question surfaces, not just at its nominal lifecycle position."
---

# ds-stats

Full depth, worked examples, and citations live in `references/`. This file
is protocol only.

## Subfields

- **Hypothesis testing** — trigger: "is this difference real." NHST; the
  modern canonical statement is the ASA's official position, not one
  textbook. Wasserstein & Lazar, "The ASA's Statement on p-Values," *The
  American Statistician* 70(2), 2016 —
  https://www.tandfonline.com/doi/full/10.1080/00031305.2016.1154108 : a
  conclusion "should not be based only on whether a p-value passes a
  specific threshold" — threshold-worship is the named failure mode. See
  `references/ds-stats.subfields.md#hypothesis-testing`.
- **Power analysis** — trigger: a sample-size or power question, before a
  design commits or after a null result needs interpreting. Cohen, "A Power
  Primer," *Psychological Bulletin* 112(1), 1992 —
  https://www2.psych.ubc.ca/~schaller/528Readings/Cohen1992.pdf : the
  d = .2/.5/.8 conventions are defaults for when no comparable prior
  literature exists, not universal targets. See
  `references/ds-stats.subfields.md#power-analysis`.
- **Randomized experiment design (A/B, peeking, sequential/adaptive
  stopping)** — trigger: a randomized rollout is being designed, or results
  checked before the pre-declared horizon. Always-valid / anytime-valid
  sequential testing. Johari, Pekelis & Walsh, "Always Valid Inference," —
  https://arxiv.org/abs/1512.04922 : fixed-horizon p-values are "wholly
  unreliable" under continuous monitoring with adaptive stopping; always-
  valid methods must be adopted deliberately, not retrofitted. Peeking
  gate: see Gates, below. See
  `references/ds-stats.subfields.md#randomized-experiment-design`.
- **Multiple comparisons** — trigger: more than one test, metric, or
  variant evaluated in the same analysis. FDR control. Benjamini &
  Hochberg, "Controlling the False Discovery Rate," *JRSS B* 57(1), 1995 —
  http://www.math.tau.ac.il/~ybenja/MyPapers/benjamini_hochberg1995.pdf :
  a weaker guarantee than family-wise error rate control, assuming
  independence or positive dependence — violated by correlated tests
  without a corrected variant. See
  `references/ds-stats.subfields.md#multiple-comparisons`.
- **Effect sizes** — trigger: a significance claim ships without a
  magnitude. Lakens, "Calculating and Reporting Effect Sizes," *Frontiers
  in Psychology* 4:863, 2013 —
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3840331/ : biased η²
  overstates effect size in small samples (use ω² for cross-study
  comparison); benchmarks don't transfer to designs with covariates or
  repeated measures without adjustment. See
  `references/ds-stats.subfields.md#effect-sizes`.
- **Survival analysis** — trigger: outcome is time-to-event with
  censoring. Product-limit (Kaplan–Meier) estimator. Kaplan & Meier,
  "Nonparametric Estimation from Incomplete Observations," *JASA* 53,
  1958 — https://web.stanford.edu/~lutian/coursepdf/KMpaper.pdf : assumes
  non-informative censoring — dropout correlated with prognosis silently
  biases the curve; a censored observation treated as an event or as
  event-free is wrong either way, and differently wrong. See
  `references/ds-stats.subfields.md#survival-analysis`.
- **Design-based inference from complex samples** — trigger: data comes
  from a stratified, clustered, or weighted sample rather than iid draws.
  Calibration estimation / survey weighting and raking. Deville &
  Särndal, "Calibration Estimators in Survey Sampling," *JASA* 87(418),
  1992 — https://users.stat.umn.edu/~gmeeden/classes/5201/handouts/calibrate.pdf :
  corrects for known covariate imbalance, not unmeasured non-response;
  clustered-sample variance still needs a design-consistent estimator,
  never an iid formula. See
  `references/ds-stats.subfields.md#design-based-inference-complex-samples`.

None run `mandatory` — `ds-stats` is not in the always-mandatory set
(`ds-scoping`, `ds-data-models`, `ds-verify`); every subfield fires on its
own data condition.

## Production considerations

Production experimentation-platform mechanics — assignment service, event
logging, results dashboarding — are `ds-mlops`' serving concern; this skill
owns the statistical design/inference methodology only, not the platform
running it. `references/doctrine-scale-cost.md`'s threshold, recorded once in
`ds-scoping`'s kill-check, governs sample-size/duration economics at
production tier and is read here, never restated. Production-tier
continuous monitoring is the highest-stakes form of the peeking gate above
(daily-dashboard stakeholders) — the stopping-rule requirement does not
relax because monitoring is now continuous by design; that is exactly why
the gate exists. A production drift or monitoring trigger raising a new
significance question ("did the metric actually move") is a re-entry into
this skill, not a new artifact type.
