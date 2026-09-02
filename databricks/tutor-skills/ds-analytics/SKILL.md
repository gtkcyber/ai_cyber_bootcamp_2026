---
name: ds-analytics
description: "Descriptive/product analytics and the metric layer: metric definition and lineage, grain and additivity in analytics practice, sessionization, cohorts, funnels, retention curves, segmentation validity, decomposition/driver analysis, dashboard and KPI-alert design. Owns \"what to alert on\"; detection mechanics are…"
---

# ds-analytics

## Subfields

- **Metric definition and lineage** — trigger: "what does this number mean"
  or any KPI is about to be reported. **LITERATURE-THIN**: no academic
  paper; canonical is an industry standard. dbt Labs, "Creating metrics" —
  https://docs.getdbt.com/docs/build/metrics-overview : a metric spec (type,
  aggregation, expression) belongs in a versioned, queryable semantic layer.
  A metric documented there still needs lineage back to the source events'
  Attest claim, not just a formula the tool can run; the metric layer here
  is the analytics-practice form built atop `ds-pipelines`' warehouse
  modeling — link, don't re-teach it.
- **Grain and additivity** — trigger: any measure is about to be aggregated
  or reported at a rollup level different from its source rows. Kimball
  Group, "Fact Tables and Dimension Tables" —
  https://www.kimballgroup.com/2003/01/fact-tables-and-dimension-tables/ :
  grain (the level of detail one fact row represents) is declared before
  choosing dimensions or facts; additive facts sum safely, semi-additive
  facts (balances, inventory levels) sum across some dimensions but not
  across time, and factless facts carry no numeric measure at all. This
  subfield does not classify a measure itself — additive/semi-additive/
  non-additive and ratio-of-averages-vs-average-of-ratios is
  `doctrine-repro-provenance.md`'s Additivity section, first executed by
  `ds-profile`; this family **cites that classification, never re-derives
  it** (`ds-profile` Gates). The delta is analytics practice: a metric's
  stated grain sets its denominator, and summing a semi-additive measure
  across time like an additive one is a grain violation, not a rounding
  error.
- **Sessionization** — trigger: "reconstruct user sessions from event/
  server logs." Cooley, Mobasher, Srivastava, "Data Preparation for Mining
  World Wide Web Browsing Patterns," Knowledge and Information Systems 1(1),
  1999 — https://link.springer.com/article/10.1007/BF03325089 :
  session-boundary heuristics (e.g. a 30-minute idle cutoff) are analyst
  conventions, not ground truth — changing the cutoff materially changes
  downstream funnel and retention numbers built on it. A session is not a
  new grain: it is the raw event grain **composed** with a stated boundary
  rule into a derived population statement — the cutoff belongs in that
  statement, not left implicit in a query.
- **Cohorts** — trigger: "compare groups defined by a shared, time-indexed
  starting event" (signup week, first-purchase month). Literature name:
  cohort analysis (demography, imported into product analytics).
  **LITERATURE-THIN direct-fetch note**: Ryder, "The Cohort as a Concept in
  the Study of Social Change," *American Sociological Review* 30(6), 1965,
  is the field's originating reference by title; JSTOR's bot-wall blocked
  every independent fetch attempt, so it is named for completeness only,
  not counted as independently confirmed. Canonical fetched source:
  "Cohort (statistics)" — https://en.wikipedia.org/wiki/Cohort_(statistics)
  (Wikipedia substitution — the originating paper was not independently
  confirmed). A cohort must share a time-indexed defining event — conflating
  cohort analysis with generic segmentation (below) loses the temporal
  alignment that makes cohort-over-cohort curves comparable at all.
- **Funnels** — trigger: "conversion rate through a sequence of steps."
  **LITERATURE-THIN**: no academic literature under this name;
  industry/practitioner concept only. Amplitude, "What Is Funnel Analysis?
  Definition, Examples, and Tools" —
  https://amplitude.com/blog/funnel-analysis. Funnel-step definitions
  (which events count, in what order, within what time window) are analyst
  choices — different, equally defensible funnel definitions over the same
  data yield different conversion rates; there is no canonical "correct"
  funnel to check a computed one against, so the definition itself must be
  stated alongside the number.
- **Retention curves** — trigger: "what fraction of a cohort is still
  active N periods later." Literature name: survival analysis, the
  Kaplan-Meier estimator. **LITERATURE-THIN direct-fetch note**: Kaplan &
  Meier, "Nonparametric Estimation from Incomplete Observations," JASA
  53(282), 1958, is the originating paper by title; JSTOR's bot-wall
  blocked fetch confirmation. Canonical fetched source: "Kaplan–Meier
  estimator" —
  https://en.wikipedia.org/wiki/Kaplan%E2%80%93Meier_estimator (Wikipedia
  substitution). Retention curves are survival curves: users who haven't
  churned by the observation cutoff are **right-censored**, not "retained"
  — a naive fixed-window retention rate that ignores censoring
  systematically understates retention for recently-joined cohorts.
- **Segmentation validity** — trigger: "split the population into groups
  that behave/respond differently." Literature name: market segmentation.
  **LITERATURE-THIN direct-fetch note**: Smith, "Product Differentiation
  and Market Segmentation as Alternative Marketing Strategies," *Journal of
  Marketing* 21(1), 1956, is the originating paper by title; every
  hosted-PDF candidate fetched 404'd. Canonical fetched source: "Market
  segmentation" — https://en.wikipedia.org/wiki/Market_segmentation
  (Wikipedia substitution). Statistical separability (clusters exist in
  feature space — the clustering *method* itself is `ds-unsupervised`'s if
  this escalates past rule-based business segments) is not the same as
  segmentation validity in the actionability/stability/differential-
  response sense this literature requires — a segmentation can be
  statistically clean and still useless if the segments don't differ in
  the outcome that matters.
- **Decomposition/driver analysis** — trigger: "why did this metric move —
  break the change down by driver." Literature name: Shapley-value
  decomposition of aggregate metric changes. Shorrocks, "Decomposition
  procedures for distributional analysis: a unified framework based on the
  Shapley value," Journal of Economic Inequality 11, 2013 —
  https://link.springer.com/article/10.1007/s10888-011-9214-z (abstract/
  metadata page confirmed fetched; full text paywalled). This is
  **correlational decomposition, not causal attribution** — Shapley
  decomposition among correlated drivers can still assign credit to a
  driver merely correlated with the true cause. Causal attribution claims
  route to `ds-causal`; see Gates.
- **Dashboard and KPI-alert design** — trigger: "what should this dashboard
  show" or "when should this metric page someone." Literature name:
  statistical anomaly detection for time-series metrics. Vallis,
  Hochenbaum, Kejariwal (Twitter), "Automatic Anomaly Detection in the
  Cloud Via Statistical Learning," 2017 —
  https://arxiv.org/abs/1704.07706. This subfield owns **design**: which
  metrics surface, at what cadence, and the explicit false-positive/
  false-negative tradeoff a threshold has chosen — thresholds tuned to
  historical seasonality miss genuine regime changes, tuning the other way
  causes alert fatigue, and which side a given design picked must be
  stated, not defaulted. The underlying statistical detection **mechanics**
  (changepoint/anomaly detection itself) are `ds-timeseries`'s — this
  subfield consumes that mechanism, it does not reimplement it.

|---|---|---|---|
| Metric definition and lineage | quick-answer | yes, always-composed wherever a KPI is reported | `mandatory` |
| Grain and additivity | quick-answer | yes, always-composed wherever aggregation occurs | `mandatory` |
| Sessionization | analysis | no | `conditional-on-data:session-based-population` |
| Cohorts | analysis | no | `conditional-on-data:time-indexed-grouping-asked` |
| Funnels | analysis | no | `conditional-on-data:sequential-conversion-asked` |
| Retention curves | analysis | no | `conditional-on-data:cohort-persistence-asked` |
| Segmentation validity | analysis | no | `conditional-on-data:group-differentiation-asked` |
| Decomposition/driver analysis | analysis | no | `conditional-on-data:metric-change-explanation-asked` |
| Dashboard and KPI-alert design | analysis | yes, re-entrant per dashboard/alert published | `conditional-on-data:operational-surface-asked` |

`mandatory` here means: fires whenever `ds-analytics` composes at all, same
convention as `ds-gather`'s selection-into-the-dataset row — every metric
this family reports states its lineage and its grain, even a one-line
quick-answer rate.

## Selection tree

1. **Is any number about to be reported at all?** → **metric definition and
   lineage** and **grain and additivity** both run, unconditionally. Cite
   the defining computation, the source population statement, and (per
   `ds-profile`) the measure's additivity class before continuing.
2. **Task intent** — characterize behavior over time, a process, the
   population, a change, or an operational surface?
   - Behavior grouped by a shared time-indexed starting event → **cohorts**;
     if the population is session-derived (web/app logs, not a single
     defining event), run **sessionization** first and state the boundary
     rule in the population statement it composes into.
   - Persistence of a cohort over subsequent periods → **retention curves**
     (survival framing; state the censoring treatment for recent cohorts).
   - Sequential conversion through defined steps → **funnels** (state the
     step definition alongside the rate — no canonical funnel exists to
     check it against).
   - Grouping by characteristics with a claimed differential response →
     **segmentation validity** (statistical separability alone doesn't
     clear this gate; escalate the clustering *method* itself to
     `ds-unsupervised` if it goes past rule-based business segments).
   - "Why did this metric move" → **decomposition/driver analysis**
     (correlational only — a causal "because" claim escalates to
     `ds-causal`, see Gates).
   - An operational, recurring surface is the deliverable →
     **dashboard and KPI-alert design** (state the alert threshold's
     false-positive/false-negative tradeoff; detection mechanics come
     from `ds-timeseries`, not reimplemented here).

## Family-specific pitfalls and evaluation

- **Metric-name collision**: two dashboards reporting the same metric name
  with different lineage/grain is not a display bug, it is a lineage
  failure — see Gates.
- **Grain violation**: a semi-additive measure (balance, inventory level,
  rate) summed across the time dimension like an additive one silently
  produces a meaningless total; the failure is invisible until someone
  cross-checks against a period-end snapshot.
- **Session-boundary arbitrariness**: an implicit or undocumented idle-
  cutoff choice makes cohort/funnel/retention numbers built on that
  sessionization irreproducible by a second analyst.
- **Right-censoring blindness**: treating "hasn't churned yet" as "retained"
  in a fixed-window retention calculation biases recent cohorts optimistic.
- **Segmentation validity gap**: statistically separable clusters reported
  as "segments" with no actionability/stability/differential-response
  evidence attached.
- **Correlational-decomposition overclaim**: driver analysis stated in
  causal language ("X drove the change") without an identification
  statement — see Gates.
- **Evaluation delta on `ds-evaluate`'s generic scorecard**: this family's
  outputs are rarely held-out predictive performance; "evaluation" here is
  the lineage/consistency check above plus, for retention curves and
  dashboard-alert thresholds specifically, the reproducibility discipline
  `doctrine-repro-provenance.md` states once — this family's delta is that
  the check runs per reported metric, not per fitted model.

## Gates

- **Metric-lineage gate**: every KPI cites both its defining computation
  (the metric-layer spec, per metric definition and lineage) and its source
  population statement — a bare number with neither citation fails this
  gate. Two dashboards disagreeing on the value of one metric name is a
  lineage failure, not a refresh-timing footnote.
- **Grain/additivity gate**: every metric declares its grain before
  aggregation, citing `ds-profile`'s additive/semi-additive/non-additive
  classification — this family never re-derives that classification; a
  metric aggregating a semi-additive measure the same way as an additive
  one fails this gate.
- **Driver-analysis gate**: any "driver," "cause," or "because" language
  attached to a decomposition result requires an identification statement —
  a decomposition presented in causal language with no identification
  statement on record is flagged, not published.
- **Censoring gate**: any reported retention rate for a cohort still within
  its observation window states the censoring treatment applied — an
  unqualified rate for a recent cohort fails this gate.
- Fit-on-train-only (`ds-features` ownership) applies to any family-
  specific transform that is *fit* rather than merely computed — a
  segmentation rule threshold learned from data (as opposed to a fixed
  business rule) is fit train-only, same as any other transform.
- Doctrine gates this family triggers, linked not restated: leakage
  (`doctrine-leakage.md`), provenance/additivity
  (`doctrine-repro-provenance.md`) and scale/cost per router doctrine.
- Dashboard publication passes `ds-verify` before going live (`ds-verify`
  Gates) — this family states the metric and its lineage, `ds-verify`
  computes the independent second-path check.

## Edges

Covered: metric definition and lineage, grain and additivity in analytics
practice, sessionization, cohorts, funnels, retention curves, segmentation
validity, decomposition/driver analysis, dashboard and KPI-alert design.

Not covered, pointer only: additive/semi-additive/non-additive
classification mechanics (`doctrine-repro-provenance.md`, executed first by
`ds-profile` — this family cites, never re-derives); the grain **contract**
and key uniqueness at the schema/record level (`ds-data-models`, Interpret —
this family's grain subfield is the analytics-practice delta only); causal
identification for any driver- analysis "because" claim (`ds-causal`); the
clustering *method* itself when segmentation escalates past rule-based
business segments (`ds-unsupervised`); statistical anomaly/changepoint
detection *mechanics* behind a dashboard alert (`ds-timeseries` — this
family owns alert *design*, not the detector); narrative report authoring —
dashboard/KPI- alert design is this family's, audience-tiered narrative
reports are `ds-communicate`'s (its own Edges points back here);
recurring-report freshness and dashboard-contract monitoring once published.
