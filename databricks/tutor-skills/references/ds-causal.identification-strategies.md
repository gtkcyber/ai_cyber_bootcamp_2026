# Identification strategies

Full depth and worked examples for `ds-causal`'s adjustment- and
design-based subfields. `SKILL.md` carries the citations and gate text;
this file carries the mechanics. Instrumental variables, collider/selection
stratification, and the umbrella naming discipline continue in
`references/ds-causal.instruments-and-discipline.md`.

## DAGs and confounding

Hernán & Robins, *Causal Inference: What If* (https://www.miguelhernan.org/whatifbook)
synthesizes the DAG and potential-outcomes traditions: a DAG is a claim
about the world, not a computed object — it encodes which variables the
analyst believes cause which others, and everything downstream (which
adjustment set is valid) follows from that claim being right.

Three roles a variable can play relative to a treatment→outcome pair:

- **Confounder** — causes both treatment and outcome, temporally prior to
  both. Must be adjusted for (or the analysis is biased).
- **Mediator** — sits on the causal path from treatment to outcome.
  Adjusting for it blocks part of the effect you're trying to measure —
  a distinct error from confounding, in the opposite direction of
  usefulness.
- **Collider** — a common *effect* of two other variables in the DAG
  (treatment and outcome, or two of their causes), temporally posterior to
  both. Must *not* be adjusted for — see collider/selection stratification,
  below.

**Worked example**: "does a loyalty program cause retention?" Draw the DAG
before touching data: `signup_propensity → {enrolled_in_program,
retention}` (a confounder — customers already inclined to stay are also
more likely to enroll) vs. `enrolled_in_program → engagement_score →
retention` (engagement is a mediator on the causal path — do not adjust
for it if the target estimate is the *total* effect of the program) vs.
`{enrolled_in_program, retention} → churned_before_survey_close` (a
collider if survey timing depends on both — conditioning on "still in the
dataset at survey close" induces a spurious enrolled/retention association
among survivors even if none exists in the population).

Failure mode from the brief: a missing or wrongly-directed edge silently
changes a variable's classification. Practically — before adjusting for
anything, write down the claimed edges and have a second person (or a
second pass) check whether any "obviously fine to adjust for" variable is
actually downstream of treatment.

## Matching

Rosenbaum & Rubin (1983), https://www.stat.cmu.edu/~ryantibs/journalclub/rosenbaum_1983.pdf
: the propensity score — P(treatment | observed covariates) — is a
balancing score; matching or stratifying on it, under unconfoundedness
(no unmeasured confounders), yields unbiased comparisons on average.

Mechanics: estimate the propensity score, match treated to control units
on it (nearest-neighbor, caliper, or full matching), check covariate
balance post-match (standardized mean differences near zero across the
matched sample), then estimate the treatment effect on the matched sample.

**What balance diagnostics can and cannot show**: post-match balance on
*observed* covariates demonstrates the matching procedure worked
mechanically. It says nothing about whether an *unmeasured* confounder
remains imbalanced — unconfoundedness is not testable from the data at
hand. A sensitivity analysis (how large an unmeasured confounder's effect
would have to be to overturn the result — e.g. Rosenbaum bounds) is the
honest way to characterize this risk, not a claim that balance "confirms"
unconfoundedness.

**Worked example**: comparing customers who enrolled in a program vs. those
who didn't, matched on tenure, prior spend, and acquisition channel.
Balance on those three looks clean post-match. That says nothing about an
unmeasured variable like "received a personal outreach call" if it wasn't
recorded — if outreach both drove enrollment and drove retention
independent of the program itself, the matched estimate is still biased.

## Difference-in-differences

Callaway & Sant'Anna, https://arxiv.org/abs/1803.09015 : the classic
2x2 DiD estimator (treated vs. control, before vs. after) identifies the
average treatment effect on the treated under **parallel trends** — absent
treatment, treated and control groups would have moved in parallel. This
assumption is as untestable as unconfoundedness; pre-trend checks (do the
groups move in parallel *before* treatment) are suggestive, not proof,
since parallel pre-trends don't guarantee parallel counterfactual
post-trends.

**The staggered-adoption trap**: when different units adopt treatment at
different times (a rolling product launch by market, a policy phased in by
region), the standard two-way-fixed-effects (TWFE) regression silently uses
*already-treated* units as part of the comparison group for *later-treated*
units — a "forbidden comparison" that can bias the pooled estimate, even
flip its sign, when treatment effects are heterogeneous over time. This
happens without any error message; the regression runs and reports a
number.

Callaway & Sant'Anna's group-time estimator (`ATT(g,t)` — average effect
for the cohort that started treatment in period `g`, measured at period
`t`) aggregates only valid not-yet-treated or never-treated comparisons,
then lets the analyst aggregate across cohorts explicitly (simple average,
event-time average, calendar-time average) rather than implicitly via TWFE
weights.

**Worked example**: five regions roll out a new checkout flow across six
months. Plain TWFE pools all region-months and implicitly compares
March-launched regions against already-launched January regions in later
months — contaminated. A group-time estimator computes each region-cohort's
effect against still-not-yet-launched regions only, then aggregates.
