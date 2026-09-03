# Subfields — full depth

The seven `ds-uncertainty` subfields. Each section: literature name,
canonical method, the failure mode it exists to prevent, and a worked
micro-example. Citations are carried in full in `SKILL.md`'s Subfields
bullets; this file does not repeat URLs, only the reasoning.

## Hierarchical/mixed-effects models

Laird & Ware's two-stage random-effects formulation generalizes beyond
repeated measures to any clustered/nested structure — patient, account,
device, session — under either classical (ML/REML) or Bayesian estimation.
The model assumes the random effects are drawn from a specified
distribution, typically normal. Misspecifying that distribution, or the
clustering structure itself, understates standard errors just as ignoring
clustering entirely does — only less severely, which makes the failure
easier to miss.

*Micro-example:* `ds-profile` reports `grouping_variables: [account_id]`
and `ds-stats`' design memo says "analysis needs clustered SEs at the
account grain" (a design consequence, not a model spec). This subfield
picks the model form — a random-intercept-by-account model, say — states
the distributional assumption on the random intercepts, and fits it. It
does not re-derive that accounts are the grouping variable; that finding
is cited, not recomputed.

## Bayesian workflow and MCMC diagnostics

Gelman et al.'s Bayesian Workflow frames model-building as iterative:
prior predictive checks, fitting, posterior predictive checks, and
revision — not a single fit-and-report step. Vehtari et al.'s rank-
normalized, folded R-hat exists because the traditional Gelman-Rubin
R-hat "has serious flaws" — it fails to catch convergence failure when
chains have heavy tails or unequal within-chain variance. A single scalar
diagnostic passing is necessary evidence, never sufficient.

*Micro-example:* a hierarchical model's chains report R-hat = 1.01 for
every parameter. Reporting "converged" on that alone skips the workflow's
posterior predictive check — the fitted model might still poorly recover
known structure in held-out data despite chains that mixed well. The Gates
core-gate language ("interval without its assumptions fails") extends
here: a credible interval from an unchecked posterior fails the same way
an interval from a converged-in-name-only fit does.

## Prediction intervals

Hyndman & Athanasopoulos distinguish a prediction interval from a
confidence interval precisely: a confidence interval bounds a parameter
(e.g. the mean); a prediction interval bounds a future observation, and so
must include both parameter-estimation uncertainty and the outcome's own
irreducible variance. An interval computed under a Gaussian-residual
assumption is too narrow whenever the true residual distribution has
heavier tails than Gaussian — a fact invisible from the point forecast
alone.

*Micro-example:* a demand forecast reports "next week: 500 units, 80% PI:
[420, 580]" computed from in-sample residual standard deviation assuming
normality. If the residuals are actually heavy-tailed (occasional large
demand spikes), the true 80% interval is wider than [420, 580] — the
Gates core gate requires the interval to name that it assumed Gaussian
residuals, so a reviewer can flag the risk instead of discovering it after
a stockout.

## Conformal prediction

Angelopoulos & Bates's introduction to conformal prediction states the
marginal coverage guarantee's exact assumption: exchangeability of
calibration and test data — strictly weaker than iid (permutation-
invariance suffices; no independence assumption needed) but still an
assumption that can be violated. Under distribution shift between
calibration and deployment, coverage degrades below the nominal level
**silently** — there is no diagnostic internal to the conformal procedure
itself that flags the violation.

*Micro-example:* a model's conformal intervals are calibrated on last
year's data and deployed this year. If the input distribution shifted
(seasonality, a product launch, a population change), the stated 90%
coverage no longer holds at deployment time — nothing in the conformal
machinery raises an alarm. The Gates conformal-specific gate requires
flagging any known or suspected shift explicitly, because the method
cannot detect it for you.

## Multiple imputation and inference under missingness

Van Buuren's statement of Rubin's rules pools m complete-data analyses
into one estimate with an appropriately inflated variance — the pooled
variance has a **within-imputation** component (ordinary sampling
variance) and a **between-imputation** component (variance across the m
imputed datasets' point estimates), and it is the second component that
single-imputation analysis omits entirely. The rules assume the
complete-data estimates are approximately normally distributed around the
true parameter, and that the imputation model is compatible with — at
least as rich as — the analysis model; an imputation model missing an
interaction term the analysis model includes silently breaks this.

*Micro-example:* `ds-clean` imputes missing income values 20 times (m=20)
using a model that includes age and region but not the interaction the
downstream regression uses. Pooling the 20 point estimates with Rubin's
rules still understates variance, because the imputation model is *not*
as rich as the analysis model — the gate requires stating the compatibility
check, not just that m imputations were pooled.

## Tail/extreme-value estimation

Scarrott & MacDonald's review of peaks-over-threshold/generalized Pareto
methods states the central tension explicitly: every threshold-based
method requires choosing a threshold above which the asymptotic tail
approximation is assumed to hold, and there is no assumption-free way to
choose it — only a bias-variance tradeoff (too low biases the fit by
including non-tail data; too high leaves too few exceedances for a stable
fit). Pickands (1975) established the underlying limit result but the full
text could not be fetched past an anti-bot wall; existence is corroborated
bibliographically (consistent title/venue/volume/pages across independent
indexes), a companion source (Scarrott & MacDonald) is cited as
content-verified.

*Micro-example:* estimating the 99.9th-percentile loss from a claims
dataset, a GPD fit above the 95th-percentile threshold gives one quantile
estimate; fit above the 90th gives a different one. Reporting only the
final number ("99.9th percentile loss: $420K") without naming the
threshold used makes the estimate unauditable — a second analyst cannot
tell whether the discrepancy with their own estimate is a data difference
or a threshold-choice difference.

## Uncertainty propagation into decisions

The GUM's first-order (linearized) uncertainty-propagation law computes
output variance from input variances and a first-order Taylor expansion of
the output function around the operating point — valid when the function
is approximately linear there. For strongly nonlinear decision functions
(a threshold crossing, a ratio with a near-zero denominator, a minimum or
maximum over several noisy quantities), the linear approximation
understates the true output uncertainty, sometimes badly, because it
ignores curvature that a Monte Carlo propagation (`ds-simulation`) would
capture by simulating the actual nonlinear function on sampled inputs.

*Micro-example:* a go/no-go decision thresholds a ratio of two uncertain
estimates (e.g. cost/benefit) near 1.0 — exactly where a ratio's
sensitivity to input noise is highest and least linear. Linearized
propagation reports a symmetric interval around the point estimate; the
true sampling distribution of a ratio near a singularity is skewed and
can be much wider on one side. The Gates propagation gate requires stating
which method was used and why, precisely to catch this case before a
decision ships on an understated interval.
