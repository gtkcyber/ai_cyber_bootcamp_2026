---
name: ds-domain-marketing
description: "Domain overlay for marketing/growth tasks (churn, customer lifetime value, uplift-targeted campaigns, multi-touch attribution): states only the marketing-specific deltas on assignment-unit interference, holdout economics, churn/LTV label conventions, uplift's dependence on a valid holdout, and attribution's…"
---

# ds-domain-marketing

## Subfields

- **Churn prediction** — trigger: "will this customer churn," "predict
  cancellation/lapse," an inactivity-window or subscription-lapse framing.
- **Customer lifetime value (LTV)** — trigger: "predict LTV," "customer
  value forecast," revenue-per-customer projected over a horizon.
- **Uplift-targeted campaign** — trigger: "who should we target," "the
  incremental lift of this promotion," a holdout/control group present or
  requested.
- **Multi-touch attribution** — trigger: "which channel gets credit,"
  "attribution model," a conversion path crossing multiple logged
  touchpoints.

## Deltas

- **Assignment units and interference** — general treatment: randomization-
  unit design as a consequence of grouping-variable/non-iid structure ·
  domain delta: marketing assignment units routinely violate SUTVA
  no-interference by construction — a household- level promotion reaches
  every member of a household regardless of individual-level assignment, and
  a referral or viral-loop campaign lets a treated unit's exposure spill
  into a nominally-control unit's outcome (a peer, not the platform,
  delivers the treatment). `ds-stats`' randomization-unit decision
  (cluster-randomize by household/geo/market rather than by row) is not
  optional tidiness here — it's the mechanism that keeps the no-interference
  assumption from being violated by the assignment scheme itself; a
  user-level random split under a household- shared or viral product
  silently contaminates the control arm.
- **Holdout economics** — general treatment: minimum detectable effect,
  power, randomization unit, and stopping rule for any randomized design ·
  domain delta: this overlay's job is stating what withholding treatment
  costs and why the business tolerates it — foregone revenue from a control
  group that would otherwise have converted on a withheld promotion, scaled
  by holdout size and duration — never re-deriving the power/MDE method
  itself; an overlay section that computes sample size or a stopping
  boundary inline, rather than citing `ds-stats`, is re-teaching a concept
  it does not own, per that same section's own dangling-delta framing.
- **Churn/LTV task shapes** — general treatment: GLM→GBM baseline-first
  ladder for churn's binary-classification framing, regression/quantile
  rungs for LTV's continuous-value framing; time-to-event/censoring
  discipline · domain delta: a churn label is a modeling convention, not an
  observed event — "no purchase in N days" is an inactivity-window
  definition the analyst chose, and `ds-data-models`' Attest register must
  record that window as the asserting mechanism, never as ground truth the
  way a completed transaction is; an LTV target is right-censored by
  construction for every still-active customer at the observation cutoff —
  the marketing instance of `ds-stats`' non- informative-censoring
  assumption — and a customer who churns for reasons correlated with low
  remaining value (exactly the population this overlay cares about) breaks
  non-informative censoring the way `ds-stats`' Kaplan–Meier caveat warns
  against.
- **Uplift-targeted campaign** — general treatment: honest-split treatment-
  effect heterogeneity · domain delta: the holdout/control group this
  overlay's holdout-economics delta justifies is the honest split's other
  half of the identification problem, not a separate concern — `ds-causal`'s
  honest-sample-splitting gate has nothing to say about whether a valid
  control group exists at all, only about how the sample already collected
  gets partitioned; an uplift model fit without this overlay's holdout
  design in place is estimating heterogeneity on a convenience sample of
  "customers who happened not to see the campaign," a selection problem this
  overlay's holdout-economics delta exists to rule out before the
  causal-forest step ever runs.
- **Multi-touch attribution** — general treatment: causally-motivated
  attribution identification composed with credit-assignment application
  over logged touchpoint sequences"; its Attribution application with
  `ds-causal` subfield) · domain delta: logged ad-exchange/campaign
  touchpoint data is never a randomized assignment of exposure order —
  position and presentation bias (which channel a user happens to see first
  or last) confounds naive last-touch or linear credit-split rules the same
  way uncorrected CTR confounds ranking evaluation; every attribution output
  ships labeled explicitly associative credit unless a `ds-causal`
  identification strategy is attached and its untestable assumption named,
  per both owning skills' gates — a dashboard reporting "channel X drove $Y
  in incremental revenue" from a rule-based credit split is exactly the
  mislabeled-causal-claim failure mode both gates exist to block.

## Standards catalog

Seeds for `ds-data-models` Research, not ceilings — confirm producer
version/dialect against the actual feed before relying on any entry.

- **UTM parameters** — no single standards body; a de facto convention
  (`utm_source`, `utm_medium`, `utm_campaign`, `utm_id`, `utm_term`,
  `utm_content`, newer `utm_source_platform`/`utm_creative_format`/
  `utm_marketing_tactic`) originating with Urchin/Google Analytics.
  Producer-adjacent reference: Google's consumer-side documentation
  (support.google.com/analytics/answer/10917952) — documents what one
  major consumer expects, not a governed standard; any ad platform can
  define its own reading of the same parameter names.
- **schema.org** — collaborative structured-data vocabulary (the
  `Product`, `Offer`, and `Event` types campaign/catalog data builds on),
  steered by a mixed company/W3C Community Group body, not a single
  producer. Producer: schema.org.
- **IAB Tech Lab adtech specs** (OpenRTB, ads.txt, VAST, etc.) — IAB Tech
  Lab (iabtechlab.com) is the closest thing to a unifying authority, but
  adtech is not one monolithic schema; each spec under its umbrella is
  separately versioned and separately governed by its own working group —
  treat any specific spec as its own citation target, this entry only
  seeds where to start.

### Uplift-targeted campaign

2. `ds-stats` — holdout design under this overlay's holdout-economics delta:
   minimum detectable incrementality, the randomization unit `ds-scoping`
   flagged, and a pre-declared stopping rule.
3. `ds-data-models` — Attest registers the churn/LTV outcome definition
   (inactivity-window convention, not an observed event) and the
   campaign-exposure event.
4. `ds-supervised` — churn/LTV outcome-model baseline (GLM→GBM ladder, or
   quantile rungs for LTV) that the uplift model's base learner builds on.
5. `ds-causal` — uplift/treatment-effect heterogeneity fit under honest
   sample-splitting, against the holdout `ds-stats` designed.
6. `ds-evaluate` — incrementality readout against the stated holdout base
   rate and cost.

### Multi-touch attribution

2. `ds-data-models` — fingerprints touchpoint-event fields against the
   catalog above (UTM/schema.org/adtech schemas); Attest registers what each
   touchpoint log actually proves (an impression served vs. a click observed
   vs. a conversion asserted by the ad platform),
   `data-models.attest_register`.
3. `ds-ranking` — attribution application over the logged touchpoint
   sequence, position-bias correction before any credit split is computed
   (this overlay's own delta on uncorrected raw sequences).
4. `ds-causal` — attribution-modeling identification: labels the output
   explicitly associative, or names the identification strategy and its
   untestable assumption if causal incrementality is claimed.
5. `ds-evaluate` — scorecard reporting the credit distribution against the
   population/baseline `ds-scoping` recorded.
7. `ds-communicate` — reports credit labeled associative unless the causal
   gate passed — never blending the two framings in one figure.
