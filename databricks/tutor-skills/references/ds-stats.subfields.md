# Subfields — full depth

The seven `ds-stats` subfields. Each section: literature name, canonical
method, the failure mode it exists to prevent, and a worked micro-example.
Citations are carried in full in `SKILL.md`'s Subfields bullets; this file
does not repeat URLs, only the reasoning.

## Hypothesis testing

Null-hypothesis significance testing (NHST) is the umbrella term, but there
is no single settled textbook statement of correct use — the ASA's 2016
statement is the closest thing to an authoritative position, issued
precisely because misuse had become endemic. The statement names two
distinct errors that are often conflated: treating a p-value as "the
probability the null hypothesis is true" (a direct misreading of what a
p-value is — a tail probability under the null, not a posterior), and
"threshold-worship" — basing a scientific or business conclusion on
whether p crossed 0.05 rather than on the full evidentiary picture
(effect size, prior plausibility, design quality).

*Micro-example:* a task asks "did the new checkout flow change conversion."
A test returns p = 0.04. Reporting "significant, ship it" fails both named
failure modes — no effect size is stated, and the conclusion rests solely
on the threshold crossing. The gate in `SKILL.md` requires the effect size
and interval to accompany the p-value in `design_analysis_memo` for exactly
this reason.

## Power analysis

Cohen's contribution is a still-canonical primer, but its d = .2/.5/.8
small/medium/large conventions were proposed as a fallback for when *no
domain-specific effect-size estimate is available* — not as targets to
design a study around by default. Treating the "medium effect" convention
as the expected effect size, absent any comparable prior study or pilot
data, silently substitutes an arbitrary number for a domain judgment call.

*Micro-example:* a task asks "how many users do we need for the A/B test."
If no prior conversion-lift data exists for this surface, the design memo
must say so explicitly and flag that Cohen's convention was used as a
fallback — not report a sample size without saying where the assumed
effect size came from.

## Randomized experiment design (A/B, peeking, sequential/adaptive stopping)

The core failure mode here is temporal, not statistical: a fixed-horizon
significance test computes its guarantees under the assumption that the
sample size was fixed in advance and the data were examined exactly once,
at the end. Continuously monitoring a dashboard and stopping "as soon as it
looks significant" violates that assumption every time — the Johari,
Pekelis & Walsh result formalizes just how unreliable ordinary p-values
become under this practice, and always-valid / anytime-valid methods are
the deliberate fix: they compute intervals or p-values that remain
statistically valid *at every intermediate look*, not only at a
pre-committed endpoint.

This is why the peeking/optional-stopping gate (`SKILL.md` Gates) requires
a stopping rule to be on record *before* the first look, not narrated
after the fact once a result looks favorable. A stopping rule declared
after three days of dashboard-watching is not a pre-declared rule; it is a
post-hoc rationalization wearing the same words.

*Worked example of a compliant declaration:* "Stopping rule: check daily
starting day 3; stop for efficacy only if the always-valid confidence
sequence excludes 0 at any check; stop for futility at day 14 if the
interval still contains the pre-registered minimum detectable effect.
Declared 2026-08-19, before experiment start." A memo that instead reads
"we looked at the dashboard Tuesday and it was significant, so we stopped"
fails the gate regardless of the underlying test's correctness — the rule
was never pre-declared.

## Multiple comparisons

Benjamini & Hochberg's FDR control is routinely conflated with family-wise
error rate (FWER) control (e.g. Bonferroni), but the two guarantees differ:
FDR bounds the *expected proportion* of false discoveries among rejected
hypotheses, a weaker and less conservative guarantee than bounding the
*probability of any* false discovery. Choosing FDR control buys more power
at the cost of tolerating some false positives among many discoveries — an
appropriate tradeoff for, e.g., screening many feature/segment cuts for
follow-up, and an inappropriate one for a small number of high-stakes
confirmatory tests. The original procedure's guarantee also assumes
independence or positive dependence among test statistics; arbitrarily
correlated tests (e.g. overlapping user segments) need a corrected variant
(Benjamini–Yekutieli), not the base procedure applied blindly.

*Micro-example:* an evaluation tests 20 feature-slice conversion
differences at α = 0.05 each; treating any individually-significant slice
as a real finding without a correction ignores roughly one expected false
positive per test set at that count.

## Effect sizes

Lakens' primer targets a specific, common error: reporting eta-squared
(η²) as-is for small-sample or between-subjects comparisons, where it is
known to be upward-biased. The less-biased omega-squared (ω²) family
exists for exactly this reason and should be preferred for any claim that
will be compared across studies or samples. The conventional small/
medium/large benchmarks (from the same tradition as Cohen's d) were
derived for simple, unrestricted between-group comparisons — carrying them
over to a design with covariates or repeated measures without adjustment
silently misapplies a benchmark calibrated for a different design.

## Survival analysis

The Kaplan–Meier product-limit estimator's core assumption is that
censoring is *non-informative* — a subject's probability of being censored
at a given time must be independent of their (unobserved) future event
risk. This assumption is invisible in the data itself; it has to be
argued from the mechanism that produced the censoring. When it fails
(e.g. sicker patients leave a study before an outcome is recorded, users
who are about to churn stop using the app that would log churn), the
curve is biased in the direction the censoring mechanism favors, and there
is no diagnostic internal to the K-M estimator itself that flags this.
Two wrong shortcuts are common and are wrong in opposite directions:
treating every censored observation as if the event happened at censoring
time (overstates event rate), and dropping censored observations entirely
(understates event rate, and wastes information about survival up to the
censoring point).

## Design-based inference from complex samples

Calibration estimation (post-stratification and raking as special cases)
reweights a sample so its marginal totals on known auxiliary variables
(e.g. age, region) match the population's known totals. Two distinct
failure modes: first, calibration only corrects for imbalance on the
auxiliary variables actually used — an unmeasured non-response mechanism
(e.g. non-responders differ on an attribute not in the weighting model)
survives calibration completely, while the resulting smaller reported
variance can create false confidence that the correction "worked." Second,
even after correct calibration, a clustered or multi-stage sample design
(e.g. sampling clinics, then patients within clinics) still needs a
design-consistent variance estimator (linearization, replicate weights) —
plugging calibrated weights into an ordinary iid variance formula
understates the true sampling variance because it ignores the intra-
cluster correlation the design induced. Both corrections are declared in
the population statement (`ds-data-models`' Observe discipline), not
re-derived here.
