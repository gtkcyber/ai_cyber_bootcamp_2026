# Missingness, outliers, dedup — depth

## Missingness

**Protocol:** for every field with null/absent values feeding a downstream
claim, state a mechanism hypothesis before choosing a handling method.

1. **Classify** the missingness against Rubin's taxonomy:
   - **MCAR** (missing completely at random) — missingness independent of
     both observed and unobserved values. Strongest assumption; rarely
     defensible without instrumentation evidence.
   - **MAR** (missing at random) — missingness depends only on *observed*
     values (e.g. a survey skip-pattern conditioned on a prior answer).
     **Not testable from the observed data alone** — it is an assumption
     about the generating process, argued from operational knowledge, never
     "confirmed" statistically.
   - **MNAR** (missing not at random) — missingness depends on the
     unobserved value itself (e.g. high earners skip an income field).
     MNAR-valid handling requires an explicit model of the missingness
     mechanism; naive imputation under an MNAR process is biased.
2. **State the operational cause** alongside the statistical class: a sensor
   outage, a form skip-logic branch, a post-2019 schema change, a collector
   sampling filter. The cause is what makes the hypothesis falsifiable — a
   class with no cause is a guess.
3. **Choose the action** — drop (row or column), impute (mean/median/mode,
   model-based single-point), or flag-and-carry. Log `rationale`.
4. **Declare the new provenance class.** An imputed value is no longer
   `observed`; per `references/doctrine-repro-provenance.md`'s classes it is typically
   `derived` (rule-based fill) or `enriched` (model-based fill) — never left
   silently as `observed`.
5. **Route to `ds-uncertainty`** before any imputed column feeds a
   confidence interval, hypothesis test, or other interval/inferential
   claim — single-point imputation understates variance; multiple
   imputation is `ds-uncertainty`'s mechanic, not this skill's.

Reference: Rubin, "Inference and Missing Data," Biometrika 63(3), 1976 —
https://dash.harvard.edu/entities/publication/73120378-8764-6bd4-e053-0100007fdf3b.

## Outliers (error-outliers only)

It does not own anomaly as the analytic target (`ds-unsupervised`),
temporal/contextual detection mechanics (`ds-timeseries`), or production
distributional monitoring (`ds-mlops`). Choose intent before method: is this
value wrong, or is it the thing being studied?

**Detection families** (Chandola, Banerjee, Kumar, "Anomaly Detection: A
Survey," ACM Computing Surveys 41(3), 2009 —
https://conservancy.umn.edu/server/api/core/bitstreams/fbdbe084-f11f-45b1-856e-8c9d58091241/content):

- **Distance-based** — far from neighbors in some metric.
- **Density-based** — in a low-density region relative to its neighborhood.
- **Statistical** — improbable under a fitted distribution (z-score, IQR
  fences, robust variants).
- **Classification-based** — a model trained on "normal" flags departures.

Each family encodes an assumption about what "normal" means. State which
family and assumption produced a flag before acting on it — a flag
presented as ground truth, with no stated assumption, is not admissible
evidence for a handling decision.

**Handling policy**: cap/winsorize, drop, or flag-and-carry, justified per
case in `cleaning_log.rationale`. A blanket policy ("drop everything past 3
sigma") applied without checking whether the mechanism is a real data
defect fails the same standard as an unstated missingness cause.

## Dedup

`ds-clean` owns the **dedup policy decision** — declaring two records
equivalent and choosing merge/remove/keep-both — not the matching
*mechanics*.

Reference: Christen, *Data Matching: Concepts and Techniques for Record
Linkage, Entity Resolution, and Duplicate Detection*, Springer 2012 —
https://users.cecs.anu.edu.au/~Peter.Christen/publications/christen2012data-matching-book-preface-content-references.pdf.
Naive all-pairs comparison is quadratic — real dedup needs blocking/
indexing first. Exact-match dedup (same key, same value) is a different,
easier problem than fuzzy/probabilistic matching, which needs an explicit
similarity threshold decided in advance, not tuned post hoc to the result
you want.

**Attest-equivalence, not field-equivalence.** Two records sharing field
values are not necessarily the same event/entity — `ds-data-models`' Attest
discipline exists precisely because columns can suggest more than a record
proves. A dedup decision cites a matching `attest_id` from the Attest
register (same actor/action/mechanism/target) or makes an explicit
event-semantic-equivalence argument when no register entry exists yet.
Merging on matching field values alone — two rows with the same
`user_id`/`timestamp` that in fact attest different actions — is the
canonical failure mode this gate exists to catch.
