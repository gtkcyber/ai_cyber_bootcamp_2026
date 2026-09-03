# Attribution methods

Worked depth for the four attribution/interpretation subfields. `SKILL.md`
carries the protocol and full citations; this file carries the mechanics.

## SHAP {#shap}

Lundberg & Lee (2017) unify LIME, DeepLIFT, and layer-wise relevance
propagation under one framework: additive feature attribution built on
Shapley values from cooperative game theory. Each feature's SHAP value is
its average marginal contribution to the prediction, computed over every
possible ordering (coalition) of features being "added" to a baseline.

- **Exactness is exponential.** Computing the true Shapley value requires
  evaluating the model on 2^k feature subsets for k features. Every
  practical SHAP implementation (KernelSHAP, TreeSHAP, DeepSHAP) is an
  approximation, and each approximation makes a different tractability
  trade: TreeSHAP exploits tree structure for polynomial-time exact values
  *conditional on the tree's own feature-independence handling*;
  KernelSHAP samples coalitions and can assume feature independence when
  estimating the conditional expectation a masked feature would have
  taken.
- **The independence assumption is the failure point.** When two features
  are correlated, "removing" one and imputing its value from the marginal
  distribution (rather than the conditional one) evaluates the model on
  combinations that don't occur in the real data — the same off-manifold
  problem `#when-explanations-lie` names generally. A high SHAP value for
  a feature under this assumption can reflect the correlated pair's joint
  effect misattributed to one member, not that feature's real contribution.
- **Additive attribution is not additive causation.** SHAP values sum to
  (prediction − baseline) by construction; that additivity is an
  accounting identity of the game-theoretic decomposition, not evidence
  that features act independently or additively on the outcome in reality.

## Permutation importance {#permutation-importance}

The standard recipe: shuffle one feature's column, re-score the model,
measure the performance drop. A large drop means the model relied on that
feature's original values for its predictions *as fit*.

- **Model Class Reliance (Fisher, Rudin & Dominici 2019).** The paper's
  central move is to stop asking "how much did *this* fitted model rely on
  this feature" and instead compute the *range* of importance a feature
  could show across every model in a class that performs comparably well
  on the data (its Rashomon set). Two equally-accurate models can lean on
  a feature very differently — single-model permutation importance reports
  one point in that range and silently generalizes it to "this feature
  matters for this problem," which the range itself may contradict.
- **Correlated features split credit unpredictably.** Permuting one of two
  correlated features barely hurts performance if the model can still read
  the (unpermuted) correlated partner — importance appears low for both,
  or arbitrarily split between them, even when the pair jointly carries
  real signal.
- **This is importance-for-interpretation, not importance-for-pruning.**
  Same statistic, different question and different consumer:
  `ds-features`'s pruning use asks "can we drop this column and keep
  performance," already assuming the feature set will change.
  Interpretation asks "what did the model, on the fixed shipped feature
  set, actually lean on" — the feature set is not up for revision here.

## PDP/ICE {#pdp-ice}

A partial dependence plot (PDP) averages the model's predicted output over
the training distribution of every *other* feature, while sweeping one (or
two) features across their range — showing the population-average marginal
relationship. Individual Conditional Expectation (ICE, Goldstein, Kapelner,
Bleich & Pitkin 2015) plots the same sweep per observation instead of
averaging, so heterogeneous relationships that a PDP would average away
(e.g. the feature helps half the population and hurts the other half,
cancelling to a flat PDP) become visible as diverging ICE curves.

- **Marginalizing assumes independence.** Averaging over "every other
  feature's training distribution" while holding the swept feature fixed
  implicitly evaluates the model at combinations that may never occur
  jointly in real data (e.g. sweeping "house age" from 0 while holding
  "renovation year" at its typical value produces a combination — a brand
  new house renovated decades before it was built — with no real analog).
  This is the same extrapolation problem SHAP's independence-based
  approximations and permutation importance share; PDP/ICE do not avoid
  it, they just make it visually implicit rather than a numeric artifact.
- **Read ICE for heterogeneity before trusting a PDP.** A flat, unremarkable
  PDP can hide two strong, opposite-signed subpopulation effects. Report
  ICE (or a PDP grouped by an interacting variable) whenever a subgroup
  effect is plausible, not just when the PDP already looks interesting.

## Global vs local {#global-vs-local}

Every explanation this skill produces states which of these two questions
it answers, because the two are not interchangeable and a reader will
assume one from an unlabeled chart:

- **Global**: which features matter across the whole model/population
  (permutation importance, a full PDP, SHAP summary/beeswarm plots
  aggregated across many rows).
- **Local**: why did the model produce *this* prediction for *this*
  instance (a single row's SHAP values, LIME).

LIME (Ribeiro, Singh & Guestrin 2016) is the model-agnostic route to a
local explanation when no SHAP implementation exists for the model class:
perturb the instance, weight perturbations by proximity to the original,
fit an interpretable surrogate (typically sparse linear) on the weighted
perturbations, and read the surrogate's coefficients as the local
explanation.

- **Local fidelity is not explanation stability.** LIME's surrogate can fit
  the local neighborhood well (high local fidelity) while still being
  unstable — a small change to the instance, or to the random perturbation
  sample, can produce a materially different surrogate and thus a
  different explanation for what is, to a user, "the same" prediction. A
  LIME explanation reported without repeating the fit (or reporting
  variance across repeats) understates this.
- **A local explanation does not generalize into a global claim.** "This
  feature drove this prediction" is not "this feature matters for the
  model" — aggregating many local explanations into a global claim is
  exactly what SHAP's summary-plot construction does deliberately and
  LIME's per-instance surrogate does not support without that extra step.
