---
name: ds-clean
description: "Missingness, outlier, and dedup policy with logged rationale; normalization into a validation assertion suite that seeds ds-mlops monitoring; anonymization/masking transform mechanics (suppression, generalization, k-anonymity-style binning, hashing) with utility-loss measurement — executes a made privacy decision…"
---

# ds-clean

Runs after `ds-profile` writes its findings doc and before `ds-labeling` /
`ds-features` consume the cleaned data. Not re-entrant: fires once per task;
a later cleaning need routes through the loop-back in Edges. Full depth,
worked examples, and citations live in `references/`; this file is
protocol only.

## Subfields

- **Missingness handling** — Rubin's missing-data taxonomy, **MCAR/MAR/
  MNAR**. Trigger: a field feeding a downstream claim has null/absent
  values. Rubin, "Inference and Missing Data," Biometrika 63(3), 1976 —
  https://dash.harvard.edu/entities/publication/73120378-8764-6bd4-e053-0100007fdf3b :
  origin of MCAR/MAR/MNAR and "ignorability" — the conditions under which
  ignoring the missingness process yields correct inference. MAR is a
  property of the process, not testable from observed data alone; don't
  claim "MAR confirmed." Point-estimate imputation methods (mean/median/
  mode, model-based) are in scope; multiple imputation for inferential use
  is `ds-uncertainty`'s (see Edges). See
  `references/missingness-and-outliers.md#missingness`.
- Trigger: profiling flags extreme/implausible values that are data defects,
  not the analytic target itself. Chandola, Banerjee, Kumar, "Anomaly
  Detection: A Survey," ACM Computing Surveys 41(3), 2009 —
  https://conservancy.umn.edu/server/api/core/bitstreams/fbdbe084-f11f-45b1-856e-8c9d58091241/content
  : canonical taxonomy by assumption about "normal" (distance-based,
  density-based, statistical, classification-based). Outlier ≠ error —
  handling policy must be justified per case, never applied as ground truth.
  See `references/missingness-and-outliers.md#outliers`.
- **Dedup** — entity resolution / record linkage / deduplication
  literature. Trigger: candidate duplicate records (the same real-world
  entity represented more than once). Christen, *Data Matching*, Springer
  2012 —
  https://users.cecs.anu.edu.au/~Peter.Christen/publications/christen2012data-matching-book-preface-content-references.pdf :
  standard reference for blocking/indexing, similarity functions,
  candidate-pair classification — those matching *mechanics* are
  `ds-entity-resolution`'s; this subfield owns the equivalence standard
  (Attest-equivalence, below) and the merge/remove policy plus rationale.
  Naive all-pairs comparison is quadratic; exact-match dedup is not
  fuzzy/probabilistic matching, which needs an explicit threshold decision.
  See `references/missingness-and-outliers.md#dedup`.
- **Normalization → validation assertion suite** — feature scaling/
  normalization is established practice with no single seminal paper;
  "Feature scaling" — https://en.wikipedia.org/wiki/Feature_scaling :
  documents min-max and z-score scaling and why distance/gradient-based
  methods need it. This subfield's real job is compiling every action taken
  across the other five subfields into the `assertion_suite` — the artifact
  that seeds `ds-mlops` monitoring. See
  `references/assertion-suite-and-ledger.md`.
- **Anonymization/masking transform mechanics** — **k-anonymity** (Sweeney);
  differential privacy as the modern successor concept. Trigger: an
  upstream privacy decision names a protection standard to meet — this
  subfield executes it, never sets it. Sweeney, "Achieving k-Anonymity
  Privacy Protection Using Generalization and Suppression," Int'l J.
  Uncertainty, Fuzziness and Knowledge-Based Systems 10(5), 2002 —
  https://dataprivacylab.org/dataprivacy/projects/kanonymity/kanonymity2.pdf :
  defines k-anonymity and the generalization/suppression mechanics to
  achieve it (extended here to binning and hashing as sibling mechanics).
  Dwork, "Differential Privacy," ICALP 2006 —
  https://www.microsoft.com/en-us/research/publication/differential-privacy/ :
  bounded output-indistinguishability, the modern alternative to syntactic
  privacy. k-anonymity bounds re-identification only via the *named*
  quasi-identifier set — it doesn't bound attribute disclosure and doesn't
  compose across releases. See `references/privacy-transforms.md#mechanics`.
- **Utility-loss measurement** — privacy-utility tradeoff literature.
  Trigger: any anonymization/masking transform applied (pairs with the
  subfield above). Brickell & Shmatikov, "The Cost of Privacy: Destruction
  of Data-Mining Utility in Anonymized Data Publishing," KDD 2008 —
  https://www.cs.cornell.edu/~shmat/shmat_kdd08.pdf : empirically shows
  generalization-style anonymization can destroy data-mining utility for
  modest privacy gains. No single universal privacy-utility metric —
  measure both re-identification risk and downstream task performance,
  compare curves, never single numbers; never report "utility preserved"
  without naming the specific downstream task/metric. See
  `references/privacy-transforms.md#utility-loss`.

|---|---|---|
| Missingness handling | quick-answer | conditional-on-data:missing-values-present |
| Outlier handling | quick-answer | conditional-on-data:outliers-present |
| Dedup | quick-answer | conditional-on-data:duplicate-risk |
| Normalization → assertion suite | quick-answer | mandatory |
| Anonymization/masking mechanics | analysis | conditional-on-data:privacy-transform-required |
| Utility-loss measurement | analysis | conditional-on-data:privacy-transform-required |

`mandatory`: the assertion suite compiles every action taken, even a
trivial pass with none — the other five fire only on their own trigger.

## Gates

- Every `cleaning_log` entry with `issue_class: missingness` states a
  mechanism hypothesis (MCAR/MAR/MNAR) plus an operational cause — an entry
  that only names the action fails this gate.
- Every imputed or otherwise created/altered value declares its new
  `new_provenance_class` (`doctrine-repro-provenance.md`'s classes) in the
  same entry.
- An imputed column feeding an inferential or interval-producing claim
  routes to `ds-uncertainty` (multiple imputation) before that claim is
  made — a single-point-imputed column feeding a confidence interval or
  hypothesis test fails this gate.
- Every `outlier` entry states the detection family/assumption used and
  justifies the handling action for that case — a flag with no stated
  "normal" assumption fails.
- Every `duplicate` entry cites a matching `attest_id` (or an explicit
  event-semantic-equivalence argument) from `ds-data-models`' Attest
  register — a merge justified only by matching field values fails this
  gate (dedup requires Attest-equivalence, not field-equivalence).
- `assertion_suite` is non-empty whenever `ds-clean` composes, and every
  entry's `derived_from` traces to a `cleaning_log` entry or normalization
  step — an untraceable assertion fails.
- Every `privacy-transform` entry names its quasi-identifier set and
  mechanism parameter (`k`, generalization level, hash scheme), and is
  paired with a utility-loss measurement (re-identification risk + a
  named downstream task/metric) before the data is released — an entry
  claiming "anonymized" with no named parameter, or with no paired
  measurement, fails.
- No `cleaning_log` entry may assert *what* must be protected or *to what
  standard* — out of scope for this skill; the entry cites the upstream
  decision it executes, never originates one.

## Edges

Covered: missingness policy with a stated mechanism hypothesis and logged
rationale; error-outlier detection/handling policy; dedup at
Attest-equivalence; normalization delta plus validation assertion-suite
construction; anonymization/masking transform mechanics; utility-loss
measurement.

Synthetic-release privacy transforms → `ds-simulation`;
consuming/interpreting a privacy-transformed field downstream →
`ds-data-models`' Interpret discipline. Missingness-mechanism-hypothesis
routing boundary: `ds-profile` and `ds-data-models` both route MCAR/MAR/MNAR
hypotheses here rather than forming them (mirrored in `ds-data-models`' own
Edges). Raw-immutability pointer: `ds-gather`'s gate — every action here
produces a new, `cleaning_log`-tracked artifact, never a silent overwrite of
raw data.

No other loop-back re-runs `ds-clean`; `drift → profile` reaches this skill
only through the normal forward-composition cascade.

## Audit mode

Input: an existing external cleaning script, notebook, or data-quality
report authored outside this skill. An undocumented cleaning action is
treated as an unregistered field under Gates: flagged, never assumed
compliant.

## Production considerations

Production-scale privacy transforms re-measure utility-loss against the
production population, not the development sample the transform was designed
against. A `drift → profile` loop-back re-triggers this skill's
missingness/outlier/dedup policy against the new profile findings before
assertions re-validate. `ds-mlops` owns ongoing monitoring execution and
alerting — this skill only seeds the contract.
