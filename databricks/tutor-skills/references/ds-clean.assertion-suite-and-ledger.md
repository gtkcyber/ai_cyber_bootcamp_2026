# Normalization, the validation assertion suite, and the ledger — depth

## Normalization (delta only)

Feature scaling/normalization (min-max rescaling, z-score standardization —
https://en.wikipedia.org/wiki/Feature_scaling) is established practice with
no single seminal citation. If a normalization pass happens here at all, it
is a lightweight, logged `cleaning_log` action (`issue_class:
normalization`) — the load-bearing output of this subfield is not the
scaling itself, it's the assertion suite described below, which fires
whether or not scaling was needed.

## The validation assertion suite

**Purpose.** Every subfield's finding — a missingness policy, an outlier
handling rule, a dedup equivalence decision, a normalization step, a
privacy-transform parameter — implies a checkable invariant the cleaned data
should satisfy going forward. The assertion suite is that set of invariants,
compiled once per `ds-clean` run and written as the `assertion_suite` ledger
field.

**Construction protocol** — for each `cleaning_log` entry, derive at least
one assertion:

| `cleaning_log.issue_class` | Typical derived assertion |
|---|---|
| `missingness` | null-rate ceiling on the field (the post-handling rate, not zero — some MAR/MNAR handling policies deliberately leave a residual null rate) |
| `outlier` | range/bound check matching the detection family's stated assumption (e.g. a distance-based flag → a bound on the metric used) |
| `duplicate` | uniqueness assertion on the Attest-equivalence key used for the merge decision |
| `normalization` | type/scale-range assertion (post-scaling bounds, or "field is untouched" if no scaling ran) |
| `privacy-transform` | structural assertion that the transform still holds (e.g. minimum group size ≥ k on the named quasi-identifier set) — this is the production-monitoring equivalent of the development-time utility-loss check |

An assertion with no `derived_from` link back to the `cleaning_log` entry
that produced it is not admissible — the suite is a compiled trace of
actions taken, not a separately invented checklist.

## Item schemas

## Why this seeds `ds-mlops`

An assertion suite where every entry is `seeds_monitoring: false` likely
means the suite was built as a checklist rather than a monitoring contract —
reconsider before writing it that way.
