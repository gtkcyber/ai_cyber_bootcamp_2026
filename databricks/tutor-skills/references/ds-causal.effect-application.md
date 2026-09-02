# Effect application

Full depth and worked examples for `ds-causal`'s three application-facing
subfields — uplift/heterogeneity, off-policy/counterfactual evaluation, and
attribution modeling. Each builds on a base identification strategy from
`references/ds-causal.identification-strategies.md`; this file covers what's specific
to *applying* an effect estimate once identified.

## Uplift and heterogeneity

Athey & Imbens, "Recursive Partitioning for Heterogeneous Causal Effects,"
https://arxiv.org/abs/1504.01132 : the question shifts from "what is the
average effect" to "which subgroups benefit more, less, or not at all" —
targeting decisions (who to enroll in a program, who to send a discount)
need the second question answered, not the first.

**Honest estimation**: split the sample into two disjoint parts before
fitting anything — one part selects the partition (which splits define the
subgroups), the other estimates the treatment effect within each leaf of
that partition. Using the same data for both steps lets the tree chase
noise: it will find splits that *look* like they separate high- and
low-effect subgroups even when the true effect is constant, because it's
free to search over splits that happen to fit this particular sample's
noise. The honest-split requirement is not a generic train/test hygiene
note — it's structurally necessary for the reported heterogeneity to mean
anything, and it's additive to whatever split the task's family already
imposes (`SKILL.md`'s Edges).

**Inherited identification**: a causal forest's honest splitting solves the
overfitting problem, not the identification problem. If the base treatment
assignment isn't randomized, the forest still needs unconfoundedness (or
whichever assumption applies) to interpret the leaf-level estimates as
causal effects rather than differences correlated with unmeasured
confounders that happen to align with the found subgroups.

**Worked example**: a retention-offer targeting model. Splitting the
customer base into "responds positively," "no effect," and "responds
negatively" (sleeping-dog effect — the offer itself prompts churn
reconsideration) requires: (1) the base identification strategy for
"does the offer affect retention" at all (randomized if available,
otherwise matching/DiD per `identification-strategies.md`), and (2) honest
splitting so the three-way segmentation isn't itself an artifact of
in-sample noise. Reporting the segmentation without confirming (1) ships an
uplift claim with no identification behind it — the core gate failure.

## Off-policy evaluation

Dudík, Langford & Li, "Doubly Robust Policy Evaluation and Learning," ICML
2011, https://arxiv.org/abs/1103.4601 : evaluates what a *new* policy's
expected reward would have been, using data logged under a *different*
(logging) policy — no new experiment run.

Two ingredients, combined:

- **Reward model** — a supervised model predicting the outcome given
  context and action, used for the actions the new policy would have taken.
- **Importance weighting** — reweights the logged data by
  `new_policy_probability / logging_policy_probability` for the action
  actually taken, correcting for the logging policy's own choices.

**Doubly robust** means the combined estimator is consistent if *either*
ingredient is correctly specified — not both. That's real robustness, but
it is not a free pass on data quality: if both models are misspecified, or
if the logging policy assigned near-zero probability to actions the new
policy favors (**poor overlap**), the importance weights blow up and the
estimator's variance explodes — same failure mode as plain importance
sampling, doubly robust or not.

**Overlap is the gate, not the estimator choice**: before trusting a
doubly-robust off-policy estimate, check the distribution of importance
weights for extreme values. A new policy that would take actions the
logging policy almost never took cannot be reliably evaluated off-policy no
matter which estimator computes the number — that's a data problem, not an
estimator problem.

**Worked example**: evaluating a new ranking policy using logged
impressions from the current production ranker. If the new policy would
frequently surface items the current ranker almost never showed (say, items
ranked below position 50, rarely logged), the importance weights for those
actions are enormous and the resulting off-policy estimate is dominated by
a handful of rare logged events — reported confidence in the number should
reflect that, not just the point estimate. Ranking-specific application
mechanics (how the correction feeds back into the ranking system) are
`ds-ranking`'s; this skill owns the identification and overlap diagnostic
behind the number.

## Attribution modeling

Dalessandro, Perlich, Stitelman, Provost, "Causally Motivated Attribution
for Online Advertising," ADKDD 2012,
https://fosterprovost.com/publication/causally-motivated-attribution-for-online-advertising/
: frames multi-touch attribution explicitly as a causal-estimation problem
— "how much of this conversion is because of this touchpoint" is a
counterfactual question (would the conversion have happened without it),
not a description of the observed sequence of touches.

**Two different questions wearing one word**:

- **Attribution (associative)** — rule-based or model-based credit-splitting
  across observed touchpoints (last-touch, linear, position-based,
  data-driven/Shapley-value credit from a fitted model). Answers "who gets
  credit," computed from the observed sequence.
- **Incrementality (causal)** — what fraction of the conversion was actually
  *caused* by a given touchpoint, answerable only with an identification
  strategy: a randomized holdout (channel-level PSA-style holdout,
  `ds-stats`) or an observational strategy from
  `identification-strategies.md` (e.g. geo-level DiD if a channel's spend
  varies by region and time).

The paper's own approximations — used when full causal estimation isn't
feasible — reduce to variable-importance measures exactly when the causal
assumptions they'd otherwise rely on are violated. That's not a caveat
buried in a footnote; it's the mechanism by which an unlabeled "attribution
score" quietly becomes an association metric wearing causal language.

**The label is the gate**: any attribution number shipped downstream states
explicitly which of the two questions it answers. A causal-incrementality
label routes to whichever identification strategy (steps 2–3 of the
selection tree in `SKILL.md`) actually backs it; an associative-credit label
needs no further identification citation, but also may not be described
downstream as "impact" or "caused."

**Worked example**: a marketing dashboard reports "email drove 30% of
conversions" from a linear multi-touch attribution rule. That is a
description of the observed touch sequence, not a claim about what would
have happened without email — reporting it as "email caused a 30% lift"
without a holdout or an observational identification strategy behind it is
exactly the mislabeling this subfield exists to catch. Position-effect
correction in a ranked/recommended surface is `ds-ranking`'s application of
the same underlying identification-vs-association distinction.
