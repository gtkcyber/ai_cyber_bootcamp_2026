# Bias and attribution

Full depth and citations for position/presentation bias, off-policy/
counterfactual evaluation application, and attribution application with
`ds-causal`. `SKILL.md` states triggers and dispatch fields only; this file
carries the method detail.

## Position and presentation bias {#position-bias}

**Literature name**: matches spec — click position-bias models.

**Canonical methods**: cascade model, examination hypothesis, and other
click position-bias models; interleaving as an alternative evaluation
design that sidesteps modeling the bias directly.

**Source**: Craswell, Zoeter, Taylor & Ramsey, "An Experimental Comparison
of Click Position-Bias Models," WSDM 2008 —
https://www.microsoft.com/en-us/research/publication/an-experimental-comparison-of-click-position-bias-models/.
Compares cascade, examination, and other position-bias models against real
click logs; no single model dominates across query types.

**Failure mode, stated as a gate**: treating raw click-through rate as a
relevance signal without a position-bias correction systematically favors
top-ranked (already-shown-more) results. This is a confound in the
*training* data itself when logged clicks feed a model, not just an
evaluation-time caveat — see `SKILL.md` Gates. It compounds with the
implicit-feedback trap (`recommendation-methods.md#implicit-feedback`): a
low position and non-exposure are different mechanisms for the same
observed absence of a click, and neither is a confirmed negative.

## Off-policy / counterfactual evaluation application {#ope}

**Literature name**: matches spec.

**Canonical methods**: replay-based offline evaluation for logged
contextual-bandit-style ranking/recommendation data.

**Source**: Li, Chu, Langford, Moon & Wang, "Unbiased Offline Evaluation of
Contextual-Bandit-Based News Article Recommendation Algorithms," WSDM 2011
— https://arxiv.org/abs/1003.5956. Replay-based offline evaluation gives an
unbiased estimate of a *new* logging policy's value from *old* policy's
logged data, under a random-assignment logging assumption.

**Failure mode**: unbiasedness depends on the logging policy's
action-selection being known and having full support over the evaluated
policy's actions. A deterministic or narrowly-exploring production logger
breaks the estimator — report the logging policy's exploration structure
alongside any off-policy estimate, not just the estimate itself. This
subfield owns the ranking-specific application only; the identification
theory (importance-sampling/IPW correctness conditions) is `ds-causal`'s
and is not re-derived here.

## Attribution application with `ds-causal` {#attribution}

**Literature name**: multi-touch attribution (MTA) vs. incrementality —
associative credit-assignment vs. causal lift. Reused from the `ds-impact`
brief's identical entry: ranking/recommendation systems are a primary site
where attribution claims get made about which position/impression "caused"
a conversion.

**Canonical methods**: causally-motivated attribution reframing, as an
alternative to rule-based credit-split heuristics (last-touch, linear,
time-decay).

**Source**: Dalessandro, Perlich, Stitelman & Provost, "Causally Motivated
Attribution for Online Advertising," ADKDD 2012 —
https://fosterprovost.com/publication/causally-motivated-attribution-for-online-advertising/.
Reframes attribution as a causal-inference problem rather than a
rule-based credit split, since correlational attribution models can assign
credit to touchpoints with zero incremental effect.

**Failure mode**: a ranking/recommendation system's logged impressions are
not a randomized assignment — attribution built on them inherits
observational-data confounding unless paired with an actual identification
strategy. Reporting attributed credit as causal lift without that strategy
is the exact error this citation exists to correct; this subfield's output
is credit-assignment association, not incrementality, until `ds-causal`
identification is attached.
