# Classification + regression methods

Full depth and citations for the GLM, GBM, and multi-class/multi-label
subfields, plus the citation grounding the family's escalation-ladder
motivation. `SKILL.md` states triggers and dispatch fields only; this file
carries the method detail.

## GLM {#glm}

**Literature name**: generalized linear models — unifies linear, logistic,
and Poisson/Gamma regression under one exponential-family framework via a
link function.

**Canonical methods**: linear regression (identity link, Normal), logistic
regression (logit link, Binomial), multinomial-logit (multi-class logit),
Poisson/Gamma regression (log link, count/rate data); regularized variants
(ridge, lasso, elastic net) as the practical default over unregularized
fits.

**Source**: Nelder & Wedderburn, "Generalized Linear Models," JRSS Series A
135(3), 1972 —
https://jhanley.biostat.mcgill.ca/bios601/Likelihood/NelderWedderburn1972.pdf.
Iteratively reweighted least squares gives max-likelihood estimates for any
exponential-family response linked to a linear predictor.

**Failure mode**: the link function encodes a distributional assumption
about the response, not a convenience transform. An identity link on count
data, or a logit link where the class-conditional variance structure
doesn't match Binomial, breaks the variance structure the model relies on —
not just the point-estimate fit. Every GLM baseline fit states its chosen
link and the response family it encodes (see `SKILL.md` Gates).

## GBM {#gbm}

**Literature name**: gradient boosting machines (functional gradient
descent) — the family's default workhorse for tabular classification and
regression past the GLM baseline.

**Canonical methods**: gradient-boosted decision trees (regression trees as
weak learners), with shrinkage (learning-rate) and row/column subsampling
as the standard regularization pair.

**Source**: Friedman, "Greedy Function Approximation: A Gradient Boosting
Machine," Annals of Statistics 29, 2001 —
http://luthuli.cs.uiuc.edu/~daf/courses/Opt-2017/Papers/2699986.pdf. Casts
boosting as stagewise steepest-descent in function space; derives TreeBoost
variants for regression and multiclass logistic loss.

**Failure mode**: greedy stagewise fitting means each tree only ever
corrects the current residual — without shrinkage/subsampling
regularization it overfits fast. Boosting is not robust to unbounded-
variance loss functions without an explicit robust loss choice (e.g.
Huber); a squared-error GBM on heavy-tailed targets inherits that
sensitivity silently.

## Escalation-ladder motivation {#ladder}

**Status**: practice protocol, not settled literature — flagged
literature-thin in the citation brief. This is the spine of `## Selection
tree`, not a separate dispatch subfield: it governs the *order* in which
this family's method classes are tried, not a method class of its own.
`ds-model`'s baseline-first-ladder subfield owns the cross-family
*procedure* (a comparably-tuned baseline on record before any complexity
claim, tie-break economics at indistinguishable performance) — this file
states only the family-specific rung order that procedure gets applied to.

**Source**: Lipton & Steinhardt, "Troubling Trends in Machine Learning
Scholarship" — https://arxiv.org/abs/1807.03341. Documents papers crediting
a new architecture for gains that were actually from extra
hyperparameter-tuning budget spent on the baseline.

**Failure mode**: a GBM beating a *quickly-tuned* GLM baseline is not
evidence the GBM's complexity was necessary — the GLM needs a comparable
tuning budget (regularization strength, interaction terms) before the ladder
step is justified. This is exactly the gate `ds-model`'s baseline-first
subfield checks; this family does not re-check it, only supplies the rung
order (GLM → GBM → escalate to `ds-deep-learning` past GBM) that the check
applies to.

## Multi-class / multi-label classification {#multiclass-multilabel}

**Literature name**: multi-class *reduction* (one-vs-all / one-vs-rest) is
distinct from multi-label classification (an instance may hold more than
one label simultaneously) — the two are not interchangeable framings of
"more than one label."

**Canonical methods**: one-vs-all / one-vs-rest reduction, native
multinomial-logit or multiclass-boosting objectives (multi-class); binary
relevance, classifier chains, label-powerset (multi-label
problem-transformation) vs. algorithm-adaptation methods (multi-label).

**Sources**:
- Rifkin & Klautau, "In Defense of One-Vs-All Classification," JMLR 5, 2004
  — https://jmlr.csail.mit.edu/papers/volume5/rifkin04a/rifkin04a.pdf.
  One-vs-all matches more elaborate multiclass reduction schemes in
  accuracy when the underlying binary classifiers are well-tuned.
- Tsoumakas & Katakis, "Multi-Label Classification: An Overview," Int'l J.
  Data Warehousing and Mining 3, 2007 —
  http://lpis.csd.auth.gr/publications/tsoumakas-ijdwm.pdf. Structures the
  field around problem-transformation (e.g. binary relevance) vs.
  algorithm-adaptation methods.

**Failure mode**: one-vs-all's accuracy-parity claim depends on each binary
classifier being independently well-regularized — a fast, undertrained
one-vs-all ensemble is not evidence against more elaborate multiclass
schemes. Binary relevance (multi-label) ignores label correlations by
construction; presenting it as correlation-aware misstates what the method
does. A task's label cardinality (>2, single label) is not sufficient
evidence it's multi-class rather than multi-label — check whether instances
can hold more than one label simultaneously before choosing the reduction.
