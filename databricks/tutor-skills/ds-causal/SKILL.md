---
name: ds-causal
description: "Observational/quasi- experimental identification: DAGs and confounding, matching, difference-in-differences, instrumental variables, uplift/treatment-effect heterogeneity, off-policy/counterfactual evaluation, attribution modeling, collider/selection stratification, and the umbrella discipline of naming an…"
---

# ds-causal

Mirrors `ds-explain`'s fixed-position pattern, not `ds-method-composition`'s
hook mechanism. Full depth, worked examples, and citations live in
`references/`; this file is protocol only.

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
  `references/ds-causal.identification-strategies.md#dags-and-confounding`.
- **Matching** — trigger: a comparison group exists on observed
  covariates, no natural experiment. Propensity-score matching. Rosenbaum
  & Rubin, *Biometrika* 70(1), 1983 —
  https://www.stat.cmu.edu/~ryantibs/journalclub/rosenbaum_1983.pdf :
  removes bias from *observed* confounders only, under unconfoundedness —
  cannot address hidden confounders; balance diagnostics give no evidence
  for the untestable unconfoundedness assumption itself. See
  `references/ds-causal.identification-strategies.md#matching`.
- **Difference-in-differences** — trigger: repeated before/after
  observations, panel or repeated cross-section. DiD with staggered
  timing. Callaway & Sant'Anna — https://arxiv.org/abs/1803.09015 : rests
  on parallel trends; with staggered adoption and heterogeneous effects,
  classic two-way-fixed-effects DiD is contaminated by "forbidden
  comparisons" between already- and later-treated units — group-time
  estimators are the fix, not an optional refinement. See
  `references/ds-causal.identification-strategies.md#difference-in-differences`.
- **Instrumental variables** — trigger: a candidate shifts treatment but
  plausibly not the outcome directly. IV under potential outcomes.
  Angrist, Imbens & Rubin, NBER t0136 —
  https://www.nber.org/system/files/working_papers/t0136/t0136.pdf :
  requires relevance, exclusion, monotonicity — the estimate is a Local
  Average Treatment Effect (LATE) for compliers only, not the population
  ATE; a weak instrument inflates variance/small-sample bias even when
  technically valid. See
  `references/ds-causal.instruments-and-discipline.md#instrumental-variables`.
- **Uplift/treatment-effect heterogeneity** — trigger: who benefits, not
  just the average effect. Causal trees and forests. Athey & Imbens —
  https://arxiv.org/abs/1504.01132 : "honest" estimation splits the sample
  so the same data never both selects the partition and estimates the
  effect within it — one sample for both overstates precision and can
  manufacture spurious heterogeneity; still inherits the base estimator's
  identification assumption. See
  `references/ds-causal.effect-application.md#uplift-and-heterogeneity`.
- **Off-policy/counterfactual evaluation** — trigger: evaluate a
  policy/ranking against logged data from a different policy. Doubly
  robust estimation. Dudík, Langford & Li, ICML 2011 —
  https://arxiv.org/abs/1103.4601 : consistent if *either* the reward or
  the logging-propensity model is correctly specified, not both — but poor
  overlap (near-zero logged propensities) blows up variance regardless.
  Ranking application: `ds-ranking`. See
  `references/ds-causal.effect-application.md#off-policy-evaluation`.
- **Attribution modeling** — trigger: credit for an outcome split across
  touchpoints/channels. Causally motivated multi-touch attribution.
  Dalessandro et al., ADKDD 2012 —
  https://fosterprovost.com/publication/causally-motivated-attribution-for-online-advertising/
  : frames attribution as causal estimation; its own approximations reduce
  to variable-importance measures precisely when the causal assumptions
  are violated — a stated approximation must be labeled association, not
  causal credit. Position-effect application: `ds-ranking`. See
  `references/ds-causal.effect-application.md#attribution-modeling`.
- **Collider/selection stratification** — trigger: a stratification
  candidate is a common *effect* of treatment and outcome, or `ds-gather`
  flagged selection-into-the-dataset. Collider (selection) bias. Cole,
  Platt, Schisterman et al., *Int. J. Epidemiology* 39(2), 2010 —
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2846442/ : a confounder
  precedes both exposure and outcome; a collider is a common effect,
  posterior to both — conditioning on it induces a spurious association
  where none existed, the opposite fix from confounder adjustment. See
  `references/ds-causal.instruments-and-discipline.md#collider-and-selection-stratification`.
- **Identification without randomization** (umbrella discipline) —
  trigger: any of the above fired, or a causal claim is about to ship. No
  single field term; the identification-strategy literature spanning
  potential-outcomes and DAG traditions. Imbens —
  https://arxiv.org/abs/1907.07271 : every non-randomized strategy
  substitutes an *untestable* assumption for randomization — the
  discipline is naming that specific assumption (unconfoundedness,
  exclusion restriction, parallel trends) rather than asserting "we
  controlled for confounders" generically. See
  `references/ds-causal.instruments-and-discipline.md#identification-without-randomization`.

No fixed load-order rank — composes at the citing skill's position, per the
named entry points above.

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
