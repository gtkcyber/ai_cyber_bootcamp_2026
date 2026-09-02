---
name: ds-uncertainty
description: "Probabilistic modeling and interval discipline: hierarchical/mixed-effects models, Bayesian workflow and MCMC diagnostics, prediction intervals, conformal prediction, multiple imputation under missingness, tail/extreme-value estimation, and uncertainty propagation into decisions. Owns every interval's…"
---

# ds-uncertainty

Full depth and citations: `references/subfields.md`.

**Core discipline, gated below:** every interval this skill produces or
reviews states its **type** (confidence / credible / prediction /
conformal), **nominal level**, and **assumption set backing coverage**. An
interval without its assumptions is a number with a plus-or-minus, not an
interval.

## Subfields

Load order is per-subfield (mirroring `ds-simulation`): each slots into
another skill's lifecycle position rather than owning one of its own.

- Canonical methods: the two-stage random-effects formulation (Laird & Ware,
  1982), classical (ML/REML) or Bayesian. Edges: `ds-stats` decides *that*
  clustering matters (design); this subfield owns *how* to model it —
  grouping variable sourced from `ds-profile`/ `ds-data-models`, never
  re-derived.
- Canonical methods: Bayesian Workflow (Gelman et al., 2020); rank-
  normalized, folded R-hat (Vehtari et al., 2021). Edges: a passing R-hat is
  necessary, not sufficient — the workflow demands prior/posterior
  predictive checks beyond one scalar diagnostic.
- Canonical methods: distributional/ probabilistic forecasting (Hyndman &
  Athanasopoulos, *FPP3* §5.5). Edges: not a confidence interval — includes
  both estimation and irreducible forecast-error variance; Gaussian-residual
  intervals understate width under heavy tails (tail/extreme-value
  estimation, below).
- Canonical methods: split/full conformal prediction (Angelopoulos & Bates,
  2021). Edges: the marginal-coverage guarantee holds under
  **exchangeability** of calibration and test data — weaker than iid, still
  an assumption; coverage degrades below nominal under distribution shift,
  with no built-in warning (`ds-mlops` monitors production, doesn't replace
  stating the assumption here).
- Canonical methods: Rubin's rules for pooling m complete-data analyses (van
  Buuren, *FIMD* §5.2). Edges: `ds-clean` decides whether/how to impute;
  this subfield propagates the resulting imputation uncertainty — the
  between-imputation variance term only correctly inflates SEs if the
  imputation model is at least as rich as the analysis model.
- Canonical methods: peaks-over-threshold / generalized Pareto distribution
  methods (Scarrott & MacDonald, 2012; Pickands, 1975). Edges: threshold
  choice trades fit bias against exceedance-count variance — no
  assumption-free choice, only a tradeoff that must be shown.
- Canonical methods: first-order (linearized) uncertainty propagation (JCGM
  100:2008, the GUM). Edges: assumes the output is approximately linear near
  the operating point — nonlinear decision functions (thresholds, ratios
  near zero, minima/maxima) need Monte Carlo propagation (`ds-simulation`)
  instead. Feeds `ds-optimize`'s prediction→decision bridge and
  `ds-communicate`'s uncertainty language — pointers, not this subfield's
  artifact.

## Selection tree

1. Groups/clusters drive per-group estimates or need partial pooling? →
   **hierarchical/mixed-effects models**; Bayesian estimation chosen for
   that fit (or any other model)? → also **Bayesian workflow and MCMC
   diagnostics**.
2. A point estimate exists and the ask is a range around it? Trusted iid
   error model → **prediction intervals**; untrusted, or coverage must hold
   distribution-free → **conformal prediction**.
3. Missingness was imputed upstream (`ds-clean`) and inference must account
   for imputation uncertainty → **multiple imputation**.
4. The question is about the extreme tail, not the center → **tail/
   extreme-value estimation**.
5. An estimate needs to flow into a decision → **uncertainty propagation
   into decisions** — nonlinear in the inputs → hand off to
   `ds-simulation`'s Monte Carlo subfield instead of linearizing.

## Family-specific pitfalls and evaluation

- **A convergence diagnostic passing is necessary, not sufficient** —
  R-hat alone does not certify a Bayesian fit.
- **Marginal coverage is not conditional coverage** — a conformal guarantee
  holds on average over calibration/test, not per subgroup or prediction.
- **Single-imputation reporting is not multiple imputation** — one imputed
  dataset treated as complete data understates variance.
- **Tail-estimation threshold choice is a bias-variance tradeoff, not a
  free parameter** — unstated, it makes the quantile unauditable.
- **Linearized propagation silently fails on nonlinear decision
  functions** — thresholds, ratios near zero, minima/maxima break it.

Evaluation delta to `ds-evaluate`'s scorecard: every interval carries its
type/level/assumption set in the scorecard entry, not a separate unaudited
caveat; empirical coverage is reported wherever checkable, never asserted
from the nominal level alone.

## Gates

- **Core gate.** Every interval states its type (confidence / credible /
  prediction / conformal), nominal level, and assumption set backing
  coverage — a value citing only a nominal level (e.g. "95% CI") fails.
- Hierarchical/mixed-effects claims cite the grouping variable from
  `ds-profile`'s `grouping_variables` finding (never re-derived) and state
  the random-effects distributional assumption.
- Bayesian-workflow claims state what convergence evidence was checked
  beyond R-hat, or flag that only R-hat was checked.
- Conformal claims state the exchangeability assumption and flag any known
  or suspected calibration/deployment shift.
- Multiple-imputation claims state `m` and the imputation model's
  compatibility with the analysis model — a point estimate with no
  imputation-variance component fails.
- Tail/extreme-value claims state the chosen threshold and its
  bias-variance tradeoff. Propagation claims state linearized vs. Monte
  Carlo and why — a nonlinear function with linearized-only propagation
  and no flag fails.

## Edges

Covered: hierarchical/mixed-effects fitting, Bayesian workflow and
convergence diagnostics, prediction intervals, conformal prediction,
multiple-imputation pooling, tail/extreme-value estimation, first-order
uncertainty propagation.

No spatiotemporal/temporal-graph/ multimodal-fusion pairing applies here;
the leakage constraint imposed whenever this skill composes is that any
generator/resampler it consumes (`ds-simulation`) is fit train-only per
`doctrine-leakage.md` — inherited, not re-stated.
