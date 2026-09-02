---
name: ds-causal
description: "Observational/quasi- experimental identification: DAGs and confounding, matching, difference-in-differences, instrumental variables, uplift/treatment-effect heterogeneity, off-policy/counterfactual evaluation, attribution modeling, collider/selection stratification, and the umbrella discipline of naming an…"
---

# ds-causal

Unlike the re-entrant trio (`ds-data-models`, `ds-stats`,
`ds-entity-resolution`), this skill does not automatically recompose
wherever its axis condition recurs; it is consulted via a named pointer the
moment another skill's output would otherwise ship causal language with no
identification behind it (`ds-analytics`, `ds-explain`, `ds-ranking`,
`ds-impact`, `ds-gather`, `ds-stats` — see Edges for each boundary). Mirrors
`ds-explain`'s fixed-position pattern, not `ds-method-composition`'s hook
mechanism. Full depth, worked examples, and citations live in `references/`;
this file is protocol only.

**The core gate**: no causal language — "driver," "impact," "effect,"
"caused by," "incrementality" — ships without a cited
`identification_statement` naming the strategy, its assumptions, and which
are untestable. Association reported as association is fine anywhere;
association reported as causation without this citation fails at
`ds-verify`.

## Subfields

- **DAGs and confounding** — trigger: an adjustment set is needed to
  isolate an effect from observed covariates. DAGs synthesized with
  potential outcomes. Hernán & Robins, *Causal Inference: What If* —
  https://www.miguelhernan.org/whatifbook : a DAG only licenses adjustment
  if it correctly encodes the analyst's causal assumptions — a wrong edge
  silently reclassifies confounder vs. collider vs. mediator; adjusting for
  a collider is the opposite-direction error from missing a confounder
  (see collider/selection stratification). See
  `references/identification-strategies.md#dags-and-confounding`.
- **Matching** — trigger: a comparison group exists on observed
  covariates, no natural experiment. Propensity-score matching. Rosenbaum
  & Rubin, *Biometrika* 70(1), 1983 —
  https://www.stat.cmu.edu/~ryantibs/journalclub/rosenbaum_1983.pdf :
  removes bias from *observed* confounders only, under unconfoundedness —
  cannot address hidden confounders; balance diagnostics give no evidence
  for the untestable unconfoundedness assumption itself. See
  `references/identification-strategies.md#matching`.
- **Difference-in-differences** — trigger: repeated before/after
  observations, panel or repeated cross-section. DiD with staggered
  timing. Callaway & Sant'Anna — https://arxiv.org/abs/1803.09015 : rests
  on parallel trends; with staggered adoption and heterogeneous effects,
  classic two-way-fixed-effects DiD is contaminated by "forbidden
  comparisons" between already- and later-treated units — group-time
  estimators are the fix, not an optional refinement. See
  `references/identification-strategies.md#difference-in-differences`.
- **Instrumental variables** — trigger: a candidate shifts treatment but
  plausibly not the outcome directly. IV under potential outcomes.
  Angrist, Imbens & Rubin, NBER t0136 —
  https://www.nber.org/system/files/working_papers/t0136/t0136.pdf :
  requires relevance, exclusion, monotonicity — the estimate is a Local
  Average Treatment Effect (LATE) for compliers only, not the population
  ATE; a weak instrument inflates variance/small-sample bias even when
  technically valid. See
  `references/instruments-and-discipline.md#instrumental-variables`.
- **Uplift/treatment-effect heterogeneity** — trigger: who benefits, not
  just the average effect. Causal trees and forests. Athey & Imbens —
  https://arxiv.org/abs/1504.01132 : "honest" estimation splits the sample
  so the same data never both selects the partition and estimates the
  effect within it — one sample for both overstates precision and can
  manufacture spurious heterogeneity; still inherits the base estimator's
  identification assumption. See
  `references/effect-application.md#uplift-and-heterogeneity`.
- **Off-policy/counterfactual evaluation** — trigger: evaluate a
  policy/ranking against logged data from a different policy. Doubly
  robust estimation. Dudík, Langford & Li, ICML 2011 —
  https://arxiv.org/abs/1103.4601 : consistent if *either* the reward or
  the logging-propensity model is correctly specified, not both — but poor
  overlap (near-zero logged propensities) blows up variance regardless.
  Ranking application: `ds-ranking`. See
  `references/effect-application.md#off-policy-evaluation`.
- **Attribution modeling** — trigger: credit for an outcome split across
  touchpoints/channels. Causally motivated multi-touch attribution.
  Dalessandro et al., ADKDD 2012 —
  https://fosterprovost.com/publication/causally-motivated-attribution-for-online-advertising/
  : frames attribution as causal estimation; its own approximations reduce
  to variable-importance measures precisely when the causal assumptions
  are violated — a stated approximation must be labeled association, not
  causal credit. Position-effect application: `ds-ranking`. See
  `references/effect-application.md#attribution-modeling`.
- **Collider/selection stratification** — trigger: a stratification
  candidate is a common *effect* of treatment and outcome, or `ds-gather`
  flagged selection-into-the-dataset. Collider (selection) bias. Cole,
  Platt, Schisterman et al., *Int. J. Epidemiology* 39(2), 2010 —
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2846442/ : a confounder
  precedes both exposure and outcome; a collider is a common effect,
  posterior to both — conditioning on it induces a spurious association
  where none existed, the opposite fix from confounder adjustment. See
  `references/instruments-and-discipline.md#collider-and-selection-stratification`.
- **Identification without randomization** (umbrella discipline) —
  trigger: any of the above fired, or a causal claim is about to ship. No
  single field term; the identification-strategy literature spanning
  potential-outcomes and DAG traditions. Imbens —
  https://arxiv.org/abs/1907.07271 : every non-randomized strategy
  substitutes an *untestable* assumption for randomization — the
  discipline is naming that specific assumption (unconfoundedness,
  exclusion restriction, parallel trends) rather than asserting "we
  controlled for confounders" generically. See
  `references/instruments-and-discipline.md#identification-without-randomization`.

No fixed load-order rank — composes at the citing skill's position, per the
named entry points above.

|---|---|---|
| DAGs and confounding | quick-answer | conditional-on-data:adjustment-set-needed |
| Matching | analysis | conditional-on-data:comparison-group-on-observables |
| Difference-in-differences | analysis | conditional-on-data:panel-or-repeated-cross-section |
| Instrumental variables | analysis | conditional-on-data:instrument-candidate |
| Uplift/treatment-effect heterogeneity | analysis | conditional-on-data:heterogeneous-effect-question |
| Off-policy/counterfactual evaluation | analysis | conditional-on-data:logged-policy-data |
| Attribution modeling | quick-answer | conditional-on-data:multi-touchpoint-credit-question |
| Collider/selection stratification | quick-answer | conditional-on-data:stratification-or-selection-flagged |
| Identification without randomization | quick-answer | `mandatory` |

`mandatory`: fires whenever `ds-causal` composes at all — the assumption
still gets named regardless of which concrete strategy fired. The other
eight fire only on their own trigger condition.

## Selection tree

2. Not randomized, adjustment set needed? → **DAGs and confounding** first:
   classify every candidate confounder/collider/mediator before choosing
   what to adjust for. Every path below inherits this framing.
3. Natural variation available: a comparison group on observed covariates,
   no natural experiment → **matching** (unconfoundedness). Repeated
   before/after observations, panel or repeated cross-section →
   **difference-in-differences** (check staggered timing before plain
   two-way fixed effects). A candidate shifts treatment but not the
   outcome directly → **instrumental variables** (check relevance,
   exclusion, monotonicity first). None cleanly available → outside
   current cited coverage; escalate per Edges rather than force-fitting.
4. Question is about *heterogeneity* (who benefits), not one average? →
   **uplift/treatment-effect heterogeneity**, inheriting step 3's base
   strategy; confirm honest sample-splitting before trusting it.
5. Evaluate a policy/ranking against logged data from a different policy,
   not fit a new randomized estimator? → **off-policy/counterfactual
   evaluation**; check overlap before trusting the variance.
6. Credit split across touchpoints/channels? → **attribution modeling** —
   state explicitly associative credit or causal incrementality; a causal
   claim routes back through steps 2–3 for its own strategy.
7. A stratification candidate is a common *effect* of treatment and
   outcome, or `ds-gather` flagged selection-into-the-dataset? →
   **collider/selection stratification** — check temporal order first;
   the opposite-direction mistake from step 2, not a variant of it.
8. Whatever strategy steps 2–7 selected, name its untestable assumption —
   **identification without randomization**. Never skipped; a generic "we
   controlled for confounders" fails it regardless of technique.

## Family-specific pitfalls and evaluation

- DAG availability is not DAG correctness — a wrong edge silently swaps a
  confounder for a collider or vice versa.
- Matched-covariate balance is evidence about observed covariates only,
  never for the untestable unconfoundedness assumption itself.
- Staggered-adoption DiD run as plain two-way fixed effects is contaminated
  by forbidden comparisons between already- and later-treated units — the
  regression still runs and produces a number; the bias is silent.
- A weak-but-valid instrument inflates variance/small-sample bias; the
  estimate is a LATE for compliers, not a population ATE — reporting it as
  the latter overstates external validity.
- Heterogeneity estimated on the sample that selected its own partition
  overstates precision and can manufacture heterogeneity that isn't there.
- Poor overlap (near-zero logged propensities) blows up a doubly robust
  estimator's variance same as plain importance sampling — "doubly robust"
  is not immunity from the overlap requirement.
- An attribution approximation reduces to variable importance the moment
  its causal assumptions are violated — shipping it labeled as causal
  credit anyway is the literature's named failure mode.
- Conditioning on a collider induces a spurious association where none
  existed — the opposite-direction error from omitting a confounder.
- "We controlled for confounders" with no named assumption is not an
  identification statement — the specific untestable assumption must be
  named, not implied.

Evaluation delta from `ds-evaluate`'s generic scorecard: a causal estimate
is evaluated on assumption plausibility and robustness (placebo tests,
sensitivity to the untestable assumption, overlap diagnostics), not
predictive accuracy alone — a model can fit the outcome well and still
identify the wrong quantity.

## Gates

- No causal-language claim ("driver," "impact," "effect," "caused by,"
  "incrementality") ships without a cited `identification_statement` — an
  association reported as causation with no citation fails at `ds-verify`.
- `identification_statement` names the strategy — unnamed fails.
- Every adjustment-set variable is classified confounder/collider/mediator
  before it is adjusted for; matching claims cite balance diagnostics
  labeled as evidence for observed covariates only, never unconfoundedness.
- Staggered-timing DiD states whether a group-time estimator was used or
  justifies plain two-way fixed effects.
- IV claims state relevance, exclusion, monotonicity, the weak-instrument
  diagnostic, and whether the estimate is LATE or extrapolated to ATE.
- Heterogeneity claims confirm honest sample-splitting (partition-selection
  and effect-estimation on disjoint samples); off-policy claims state the
  overlap diagnostic and which model (reward or propensity) is trusted.
- Attribution claims are labeled explicitly associative or causal, citing
  its own identification strategy if causal; collider/selection claims
  record the temporal-order check before any stratification executes.
- `identification_statement` separates assumptions into testable (with the
  test run) and untestable (with why) — undistinguished fails outright.

## Edges

Covered: the nine subfields above, wherever a non-randomized causal
question or a causal-language claim surfaces.

**Split discipline**: this skill does not set a task's primary split scheme
(multi-family rule, router `SKILL.md` §1) — the task's family owns
leakage-driving split discipline; a subfield's own sample-partition
requirement here (honest splitting for heterogeneity) is additive to it,
never a replacement, mirroring `ds-method-composition`'s per-component-
boundary stance.

Research-escalation trigger: regression discontinuity design, synthetic
control, and other non-randomized strategies outside the nine subfields
above are outside current cited coverage — declare it, research
externally, verify the found method's assumptions against the actual
data, report provenance, per router doctrine, before adopting one.
