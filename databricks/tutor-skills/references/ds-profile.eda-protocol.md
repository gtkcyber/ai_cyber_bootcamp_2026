# Structured EDA protocol

This file is `ds-profile`'s delta: the order to compute in, and what each
step outputs.

Every step below runs as a script, per the code-don't-read doctrine. The
script's *output* — a count, a table of quantiles, a violation list — is
what enters the findings doc; the raw frame it ran over never does.

## Order

1. **Structure/shape.** Row count, column count, per-column dtype as
   observed vs. the type `ds-data-models`' Interpret discipline declared
   for that field. A mismatch is a finding here, not a fix — resolution
   (coerce, reject, re-elicit the semantic) is `ds-clean`'s or a re-entry
   into `ds-data-models`' Elicit, never this skill's call.
2. **Typing.** Same check extended to declared enums, units, and sentinel
   encodings (`0`, `-1`, `1970-01-01`, etc.) from Interpret: does the
   observed value space match the declared one? A sentinel masquerading as
   a real value (e.g. `-1` averaged into a numeric mean) is exactly the
   kind of finding this step exists to catch before it corrupts a
   downstream aggregate.
3. **Missingness.** Per-field null/sentinel rate. This step reports rate
   and pattern (which fields co-occur missing, whether missingness
   clusters by another field) — it does **not** hypothesize a mechanism
   (MCAR/MAR/MNAR). That hypothesis, and any imputation, is `ds-clean`'s.
4. **Cardinality/uniqueness.** Distinct-value counts per field; key-
   uniqueness checked against the grain contract `ds-data-models`'
   Interpret discipline declared (cited, never re-derived — if no grain
   contract exists yet, that is a missing-input case routing back to
   `ds-data-models`, not a guess made here).
5. **Duplicate-by-field-equivalence signal.** Count of rows that are
   field-equivalent (identical on every observed field) at the declared
   grain.
6. **Univariate distributions.** Quantiles/histograms per field, computed
   by script. Full-data distributions are permitted for non-target fields;
   any distribution conditioned on, or correlated with, the target is
   target-relationship exploration and runs train-split-only
   (`references/doctrine-leakage.md`) — a full-data class-conditional histogram is a
   leakage-doctrine violation, not a convenience.
7. **Outlier signal.** Descriptive flagging only (quantile/box-plot-style,
   per Tukey) — a value's position relative to the rest of its field's
   distribution, reported as a finding. Outlier ≠ error — the finding states
   the flag and its detection rule, not a verdict.
8. **Additivity classification.** For every measure that will feed an
   aggregation anywhere downstream, classify additive / semi-additive /
   non-additive, and resolve ratio-of-averages vs. average-of-ratios
   before any aggregation runs. Written once here; `ds-features` and
   `ds-analytics` cite this classification rather than re-deriving it
   (`references/doctrine-repro-provenance.md`'s additivity principle, gated at these
   three skills).

## Findings-doc shape

Each finding is one line: the step that produced it, the field(s)
involved, the computed value, and the population statement's coverage
basis it's scoped to (`ds-data-models`' Observe discipline). A finding with
no coverage basis is incomplete, not just terse — the denominator gate in
`SKILL.md` reads this field.
