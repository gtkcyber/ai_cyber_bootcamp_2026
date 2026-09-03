# Ordinal regression, quantile regression, online-learning mechanics

Full depth and citations for the three subfields covering ordered targets,
distributional/quantile targets, and streaming training. `SKILL.md` states
triggers and dispatch fields only; this file carries the method detail.

## Ordinal regression {#ordinal}

**Literature name**: proportional-odds / cumulative-link models
(McCullagh) — the target is an ordered categorical (ratings, severity
scales, Likert items), not nominal-categorical or continuous.

**Canonical methods**: cumulative-link / proportional-odds models; ordinal
variants of standard classifiers (threshold/rank-based reductions) where
the parallel-lines assumption is checked rather than assumed.

**Source**: McCullagh, "Regression Models for Ordinal Data," JRSS Series B
42(2), 1980 —
https://rss.onlinelibrary.wiley.com/doi/10.1111/j.2517-6161.1980.tb01109.x.
**Paywall-corroborated**: full text blocked (403) behind Wiley;
bibliographic existence and abstract independently corroborated via
Scientific Research Publishing's reference index and Semantic Scholar's
paper record, both cross-checked against the JRSS-B volume/page citation.

**Failure mode**: proportional-odds assumes the effect of each predictor is
constant across all cutpoints (the "parallel lines" assumption) — asserting
proportional-odds without testing parallelism overstates what's been shown.
Treating ordinal labels as plain integers for a regression loss, or as
unordered classes for a nominal classifier, discards the ordinal structure
without this model's guarantees either way; either choice is a stated
tradeoff, never a silent default (see `SKILL.md` Gates).

## Quantile regression {#quantile}

**Literature name**: matches spec — fits a specific named conditional
quantile of the target directly, distinct from a general uncertainty
interval built around a point estimate.

**Canonical methods**: linear quantile regression via asymmetrically
weighted absolute-error (pinball) loss; quantile variants of GBM (quantile
loss as the boosting objective) for the non-linear case.

**Source**: Koenker & Bassett, "Regression Quantiles," Econometrica 46,
1978 — https://people.eecs.berkeley.edu/~jordan/sail/readings/koenker-bassett.pdf.
Generalizes the sample-quantile minimization problem to the linear model,
yielding a full family of conditional-quantile estimators via pinball loss.

**Failure mode**: fitting quantiles independently at different levels
doesn't guarantee monotonicity — a naive multi-quantile model can predict a
lower quantile above a higher one (quantile crossing). This must be checked
or enforced (e.g. sorting/isotonic post-processing across levels) before
the result is reported, not assumed away by the fitting procedure. A
request for "how uncertain is this prediction" in general, rather than a
specific named quantile, routes to `ds-uncertainty` — this subfield owns
fitting a named quantile directly, not general interval coverage.

## Online-learning training mechanics {#online-learning}

**Literature name**: online / stochastic gradient learning. Either way, the
**serving wrapper is `ds-mlops`'s** — this subfield owns only training-time
mechanics.

**Canonical methods**: SGD-trained linear/logistic models, online variants
of GLM fitting, streaming-mini-batch training loops.

**Source**: Bottou, "Large-Scale Machine Learning with Stochastic Gradient
Descent," COMPSTAT 2010 —
https://leon.bottou.org/publications/pdf/compstat-2010.pdf. SGD's
asymptotic *training*-error rate is worse than batch methods, but its
*generalization*-error-per-unit-of-compute is better for large-scale
problems — justifying online learning outside pure streaming-data settings
too.

**Failure mode**: the compute-efficiency argument for SGD assumes
i.i.d.-ish data arrival. A non-stationary stream (concept drift) breaks the
convergence guarantee that argument relies on. Diagnosing and monitoring
that failure mode in production is `ds-mlops`'s job, not this subfield's —
an online-training run must not imply the drift problem is solved just
because the training mechanics are online.
