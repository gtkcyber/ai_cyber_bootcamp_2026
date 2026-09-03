# Monte Carlo and bootstrap

Depth for the two resampling/simulation subfields. SKILL.md carries the
protocol; this file carries worked detail and full citations.

## Monte Carlo methods {#monte-carlo}

**Literature**: the Monte Carlo method / Metropolis algorithm (origin of
MCMC) — Metropolis, Rosenbluth, Rosenbluth, Teller & Teller, "Equation of
State Calculations by Fast Computing Machines," *J. Chem. Phys.* 21(6),
1953 — https://bayes.wustl.edu/Manual/EquationOfState.pdf (fetched,
existence and authorship confirmed via embedded PDF metadata).

Two distinct things travel under "Monte Carlo" and are routinely
conflated:

- **Plain Monte Carlo**: independent random sampling to estimate an
  integral or expectation. Draws are iid; standard-error formulas that
  assume independence are valid as written.
- **MCMC (Metropolis and descendants)**: dependent samples from a Markov
  chain constructed so the target distribution is its stationary
  distribution — used when sampling directly from the target is
  intractable. Draws are **autocorrelated**.

**Key failure mode**: applying iid-style variance estimates to MCMC chain
output understates the true Monte Carlo error, because consecutive draws
are correlated and therefore carry less independent information than
their raw count suggests. Report the **effective sample size** (ESS), not
the raw draw count, when characterizing MCMC precision. This subfield
supplies the sampling mechanic (drawing the chain); MCMC convergence
diagnostics (has the chain actually reached its stationary distribution)
and the surrounding Bayesian-workflow judgment calls are `ds-uncertainty`'s
— see its "Bayesian workflow and MCMC diagnostics" subfield (Gelman et al.
"Bayesian Workflow"; Vehtari et al.'s rank-normalized R-hat).

Uncertainty-propagation use case: when a decision function is nonlinear
near its operating point (a threshold, a ratio near zero, a min/max), the
standard first-order linearized uncertainty-propagation law (JCGM 100:2008
GUM) understates the true output uncertainty — Monte Carlo propagation
(simulate inputs from their distributions, push each draw through the
function, characterize the output empirically) is the correct method in
that regime, not an optional refinement.

## Bootstrapping {#bootstrap}

**Literature**: the nonparametric bootstrap — Efron, "Bootstrap Methods:
Another Look at the Jackknife," *Annals of Statistics* 7(1), 1979.
Existence corroborated bibliographically (consistent title/venue/volume/
pages across independent indexes); full-text fetch blocked at five
independent hosts (anti-bot walls / DNS failures), so not cited as
content-verified here. Fetched, content-confirmed companion: NIST/
SEMATECH e-Handbook, "Bootstrap and Jackknife Techniques" —
https://www.itl.nist.gov/div898/handbook/eda/section3/eda3721.htm
(fetched, full text confirmed): practitioner-level description of the same
resampling-with-replacement procedure and its use for standard-error/CI
estimation.

**Mechanic**: resample the observed dataset with replacement (same size as
the original), recompute the statistic on each resample, and characterize
its distribution across resamples — used for standard errors and
confidence intervals when no closed-form formula exists for the
statistic's sampling distribution.

**Key assumptions/failure modes**:

- The bootstrap assumes the observed sample is **representative of the
  population** — resampling *from the sample* stands in for resampling
  from the population. It does not fix a biased or non-representative
  original sample; a systematically skewed sample produces a
  systematically skewed bootstrap distribution.
- Plain iid resampling is **invalid under dependence** — clustered data
  (repeated measurements per unit) or time-series data (autocorrelated
  observations) requires a **block bootstrap** (time series: resample
  contiguous blocks, not individual points) or **cluster bootstrap**
  (clustered data: resample whole clusters, not individual rows) instead
  of the plain iid variant. Using plain iid resampling on dependent data
  understates the true variability.
- Bootstrap-derived intervals are not automatically valid for every
  statistic (e.g., extreme order statistics can behave pathologically
  under the standard bootstrap) — this is a known edge case, not a reason
  to distrust the method generally, but a reason to check before applying
  it to an unfamiliar statistic.

**Edge to `ds-uncertainty`**: this subfield supplies bootstrap resampling
as a mechanic. Multiple imputation's pooling rules (Rubin's rules) and
hierarchical/mixed-effects model interval claims are `ds-uncertainty`'s —
when those methods call for a resampling step internally, this subfield
supplies it; the inferential interpretation of the result stays with
`ds-uncertainty`.
