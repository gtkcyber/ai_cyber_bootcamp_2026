# Instruments and the identification discipline

Continues `references/ds-causal.identification-strategies.md`: instrumental
variables, collider/selection stratification, and the umbrella
identification-without-randomization discipline. `SKILL.md` carries the
citations and gate text; this file carries the mechanics.

## Instrumental variables

Angrist, Imbens & Rubin, NBER t0136,
https://www.nber.org/system/files/working_papers/t0136/t0136.pdf : an
instrument `Z` identifies a causal effect of `X` on `Y` under three
conditions:

1. **Relevance** — `Z` is correlated with `X` (testable: first-stage
   F-statistic; conventionally weak below ~10, though this is a rule of
   thumb, not a proof of validity above it).
2. **Exclusion restriction** — `Z` affects `Y` only through `X`, no direct
   path. Untestable — it is an assumption about the world, defended by
   argument, not by a diagnostic.
3. **Monotonicity** — no "defiers" (units that would do the opposite of
   what the instrument nudges them toward, relative to compliers).

Under these three, the IV estimate identifies the **Local Average Treatment
Effect (LATE)** — the effect for **compliers** (units whose treatment
status the instrument actually moves), not the population average
treatment effect. Reporting a LATE as if it generalized to always-takers,
never-takers, or the full population overstates external validity — the
brief's named failure mode.

**Worked example**: distance to the nearest clinic as an instrument for
clinic attendance, to estimate attendance's effect on a health outcome.
Relevance: distance plausibly predicts attendance (testable). Exclusion:
distance affects the outcome *only* through attendance — violated if
distance also correlates with neighborhood income, which independently
affects the outcome through channels other than this clinic. That
violation is not visible in any diagnostic; it must be argued from domain
knowledge. Even if valid, the recovered effect describes compliers (people
whose attendance responds to distance), not people who'd attend regardless
of distance.

## Collider/selection stratification

Cole, Platt, Schisterman et al. (2010),
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2846442/ : the DAG-theoretic
name for a mistake that looks identical in code to confounder adjustment
but produces the opposite bias.

**The temporal-order test** distinguishes a confounder from a collider: a
confounder is a common *cause* of exposure and outcome (temporally prior to
both); a collider is a common *effect* (temporally posterior to both).
Stratifying, restricting, or regression-adjusting on a collider *opens* a
spurious statistical path between exposure and outcome that did not exist
in the population — the opposite direction from the bias confounder
adjustment removes.

**Selection-into-the-dataset as a collider problem**: `ds-gather`'s
`sampling_bias_note` names *that* a selection mechanism exists (survivorship,
opt-in, retention effects). This subfield resolves the *identification
consequence*: if "present in the dataset" is itself caused by both the
exposure and the outcome (e.g., only customers who didn't already churn for
unrelated reasons are still around to be surveyed about a retention
intervention), restricting analysis to the observed sample conditions on a
collider by construction.

**Worked example**: studying whether a marketing campaign causes purchase,
using only customers who opened the campaign email. If both campaign
targeting and purchase propensity independently drive email-open rate,
"opened the email" is a collider — comparing purchase rates among openers
by campaign-arm assignment can show an association even if the campaign has
zero causal effect, because conditioning on opening has already induced a
spurious link between assignment and purchase-propensity within the opener
subgroup.

## Identification without randomization (the umbrella discipline)

Imbens, https://arxiv.org/abs/1907.07271 , surveys both the potential-
outcomes and DAG traditions' identification strategies side by side. The
paper's throughline, and this subfield's entire content: **every one of the
strategies above swaps one specific, named, untestable assumption in for
randomization** — unconfoundedness (matching), parallel trends (DiD),
exclusion restriction (IV), no-unmeasured-selection (collider/selection).
None of them are free; none of them are provable from the data being
analyzed.

The discipline this subfield enforces is entirely about the write-up, not a
new technique: an `identification_statement` must name *which* assumption
is being made, state whether it is testable (and report the test, e.g. a
pre-trend check or a balance diagnostic) or untestable (and give the
substantive argument for why it plausibly holds here), and stop short of
"we controlled for confounders" as if that phrase discharged the
obligation. A reader who disagrees with the untestable assumption should be
able to say exactly which one, and why, from the statement alone.
