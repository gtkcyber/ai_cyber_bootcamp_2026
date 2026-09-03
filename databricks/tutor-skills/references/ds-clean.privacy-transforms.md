# Anonymization/masking mechanics — depth

## Scope boundary (read first)

The design's stated boundary: the *decision* that data must be protected,
and to what standard, is policy/ethics/legal — out of scope for this suite
entirely. Once that decision exists (a task card note, a compliance
requirement, an explicit instruction), the technical *execution* —
transform mechanics, re-identification risk measurement, utility-loss
quantification — is `ds-clean`'s. Never infer a protection standard from
data sensitivity on your own judgment; that inference is the out-of-scope
decision. A `cleaning_log` entry with `issue_class: privacy-transform` cites
the decision it executes and does not originate one.

## Mechanics

**k-anonymity** (Sweeney, "Achieving k-Anonymity Privacy Protection Using
Generalization and Suppression," Int'l J. Uncertainty, Fuzziness and
Knowledge-Based Systems 10(5), 2002 —
https://dataprivacylab.org/dataprivacy/projects/kanonymity/kanonymity2.pdf):
each record is indistinguishable from at least `k − 1` others on the named
**quasi-identifier** set (fields that, combined, could re-identify a
record: ZIP + birthdate + sex is the canonical textbook example). Achieved
by:

- **Suppression** — remove a value (or whole field) entirely.
- **Generalization** — replace a specific value with a coarser category
  (exact age → 5-year band; street address → ZIP3).
- **k-anonymity-style binning** — a generalization special case for
  continuous fields: bucket into ranges wide enough that each bucket holds
  ≥ k records.
- **Hashing** — replace an identifier with a one-way hash. Hashing alone
  does not achieve k-anonymity if the input space is small enough to
  brute-force (e.g. hashing a 9-digit SSN is reversible by dictionary
  attack) — pair with salting/keying decisions made by the upstream privacy
  decision, not invented here.

**Differential privacy** (Dwork, "Differential Privacy," ICALP 2006 —
https://www.microsoft.com/en-us/research/publication/differential-privacy/)
is named as the modern successor concept: it bounds how much any single
record's presence/absence can change an output, rather than syntactically
hiding quasi-identifiers. Cited for context — mechanism selection between
k-anonymity-family and DP-family techniques is part of the upstream privacy
decision (which standard to meet), not this subfield's to choose.

**What k-anonymity does not do**: it bounds re-identification only via the
*named* quasi-identifier set — a field left out of that set can still leak.
It does not bound **attribute disclosure** (all k members of a group
sharing the same sensitive value defeats the point even with k-anonymity
satisfied — the classic gap l-diversity was proposed to close). It does not
compose safely across multiple releases (an attacker intersecting two
k-anonymous releases of overlapping data can re-identify beyond either
release's individual guarantee). Every `privacy-transform` entry names its
quasi-identifier set and its parameter (`k`, generalization level, hash
scheme) explicitly — "anonymized" with no named mechanism is not a
verifiable claim.

## Utility-loss measurement

Reference: Brickell & Shmatikov, "The Cost of Privacy: Destruction of
Data-Mining Utility in Anonymized Data Publishing," KDD 2008 —
https://www.cs.cornell.edu/~shmat/shmat_kdd08.pdf. Their empirical finding:
generalization/suppression-style anonymization can destroy data-mining
utility almost completely for modest privacy gains — utility loss is not a
minor footnote to a privacy transform, it is a load-bearing measurement.

**No single universal metric exists.** Measure and report both quantities
separately, as curves across parameter settings where possible, never as a
single number:

1. **Re-identification risk** — under the stated attack model (what an
   attacker is assumed to know: the quasi-identifier set, possibly an
   auxiliary dataset), what fraction of records remain distinguishable.
2. **Downstream task performance** — the transformed data's performance on
   the *specific* task/metric it will be used for (a named model's
   accuracy, a named aggregate's error), before vs. after the transform.

Never write "utility preserved" without naming that task/metric. A
transform that preserves aggregate counts but destroys a specific
classifier's discriminative signal is not "utility preserved" for that
classifier's use case.

## Worked example

Task: publish a masked extract of a support-ticket dataset for an external
vendor. Upstream decision (cited, not made here): "protect customer PII to
a k=10 standard on `{zip, age_band, plan_tier}`."

- `cleaning_log`: `field: zip`, `issue_class: privacy-transform`,
  `action: generalize to ZIP3`, `new_provenance_class: privacy-transformed`,
  `rationale: cites upstream k=10 decision on {zip, age_band, plan_tier}`.
- Same for `age_band` (5-year bins) and `plan_tier` (kept as-is if already
  coarse enough to hold k=10 within each `{zip3, age_band, plan_tier}`
  combination — verified by grouping and checking minimum group size, not
  assumed).
- Utility-loss entry: re-identification risk (minimum group size across the
  quasi-identifier combination, post-transform) + downstream task
  performance (the vendor's stated use: ticket-volume forecasting by
  region — compare forecast error on raw vs. masked extract).
