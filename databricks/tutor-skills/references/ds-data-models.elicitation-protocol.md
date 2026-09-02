# Elicit — the spec-less playbook

Applies whenever `Identify`/`Research` come up empty (no findable spec,
vendor doc, or standard for the data at hand — internal tables, ad-hoc CSV
exports, a one-off integration dump), *or* `Validate` finds the data
demonstrably contradicts a spec that does exist: a Validate nonconformance
finding is an explicit entry point into Elicit for the affected fields, not
just a data-quality footnote. Semantics are derived from observed behavior
instead. Every step here is **scripts-first**: the agent writes and runs
code that returns derived answers (counts, distributions, boundary values),
per the suite's code-don't-read doctrine. Raw-row inspection is permitted
only in the bounded, deliberate form in "Bounded row inspection" below.

## Order of computation

Run in this order — each stage's output can redirect or short-circuit a
later one, so don't skip ahead:

1. **Value boundaries.** For every candidate-semantic field: cardinality,
   min/max (numeric/date), the full value set if cardinality is low, and
   whether the value set looks like an enum, a free-text field, or an
   identifier. A field with exactly `{0, 1}` or `{"Y","N"}` is a boolean
   candidate; a field with a small closed set and no obvious ordering is an
   enum candidate needing per-value semantics (see decision points below).
2. **Update cadence.** Distribution of inter-record time deltas per key (if
   a timestamp exists): does this table get append-only inserts, periodic
   full refreshes, or in-place updates? A field that only ever moves forward
   in a monotonic sequence per key behaves differently (semantically and for
   join safety) than one that gets overwritten.
3. **Referential integrity.** For every field that looks like a foreign key
   (name pattern, or a value set that's a subset of another table's primary
   key): compute orphan rate in both directions. High orphan rate in one
   direction only is itself a semantic finding (e.g., a nullable optional
   relationship vs. a required one enforced only going forward from a given
   date). Run this step in candidate-key form — the referenced table's grain
   may not yet be confirmed at this point in the order — and treat the
   result as provisional until Interpret's grain-contract sub-check
   (`disciplines.md#interpret`) confirms the referenced table's declared
   grain and key uniqueness.
4. **Null patterns.** Null rate per column, and null rate *conditioned on*
   other fields (by another column's value, by time bucket, by source/batch
   if a source-identifying field exists). A column that's dense before date
   D and sparse after is a distribution-break candidate (next step), not
   independently-random missingness.
5. **Distribution breaks at policy changes.** Changepoint scan (rate of a
   value, shape of a distribution, or null rate over time) cross-referenced
   against any known operational dates (deploy log, migration ticket, policy
   change record, business calendar event) available to the agent. A
   changepoint with no available cross-reference is still recorded — as an
   unexplained break requiring a declared assumption or a routed question,
   not as noise to smooth over.

## Decision points

At each stage, three outcomes are possible for a given candidate semantic:

- **Resolved** — evidence unambiguously supports one interpretation
  (e.g., the `9`/`closed_at` co-occurrence example in `references/ds-data-models.disciplines.md`).
  Record it directly in the semantic dictionary, evidence attached.
- **Ambiguous but boundable** — evidence points toward an interpretation but
  doesn't rule out an alternative, or evidence is present but thin. Record
  as a **declared assumption** (format below) — never silently pick the
  more convenient reading and proceed as if it were resolved.
- **Unresolvable** — no available evidence bears on the question, or
  evidence conflicts with no tiebreaker available from the data itself.
  Route to the human; do not guess and do not leave the field silently
  unregistered (an unregistered field that later feeds a claim fails the
  SKILL.md semantic-dictionary gate).

## Declared-assumption format

Every declared assumption is a structured record — same shape whether it
lives inline in the semantic dictionary or as a standalone note the
dictionary references:

```
field:            <table>.<column>
assumption:       <the inferred semantic, stated as a claim>
evidence:         <what the script found, cite the specific computation>
confidence:       high | medium | low
downstream_impact: <what breaks, and how, if this assumption is wrong>
status:           declared | escalated-to-human | resolved
```

`confidence` is not decoration — `ds-verify` and any gate that reads the
semantic dictionary treats `low`-confidence assumptions as load-bearing
enough to require the citing claim to also surface the assumption, not just
the conclusion built on it.

## Bounded row inspection (find-and-feed)

Aggregate computation (steps 1-5) answers most elicitation questions without
ever pulling a raw row into context. When a question genuinely needs eyes on
example rows (confirming a suspected format, checking a free-text field's
actual content shape), selection is itself scripted — never scrolled or
paginated by hand:

- A small number of **random rows**, for a baseline sense of typical
  content.
- **Representation-selected rows**, chosen by a written script to guarantee
  value-space coverage: a populated example for any mostly-null column (if
  any exist), one example per detected enum value, boundary rows (the
  min/max found in step 1), and one example per detected schema version (if
  `Research`/`Validate` found version skew in this source).

The script does the selecting; the agent reads only what the script
returns. This keeps Elicit compliant with code-don't-read even at the one
point where raw content genuinely has to be looked at.

## Observe: scripts-first coverage checks

Coverage claims (`disciplines.md#observe`) are computed the same way
Elicit's semantics are — scripts return derived answers, never a read of
raw completeness by eye. Minimum battery, before any population statement:

- **Per-source record-rate time series** — a source that silently stops
  emitting looks identical to "nothing happened" without this; flag rate
  drops against the source's own historical baseline, not an absolute
  threshold.
- **Per-host (or per-key) last-seen gaps** — a coverage claim about "all
  hosts" needs each host's own last-seen timestamp checked, not just the
  aggregate record rate.
- **Emitting-collector cardinality vs. known asset population** — count of
  distinct source identifiers actually emitting, checked against an
  independent asset inventory; a shortfall is missing coverage, not absence
  of activity.
- **Truncation-length histograms** — a field with a hard length cutoff shows
  a spike at the cutoff; that spike is a collection artifact, not a real
  value-length distribution.
- **Retention-edge check** — the oldest record timestamp per source,
  checked against the configured retention window, to catch data that
  rolled off before the query ran.
- **Delivery semantics** — at-least-once pipelines (retries, replays,
  backfills) produce duplicate records by design; check for a native
  event-id/idempotency-key field the collector emits, and record in the
  population statement whether the count that follows is pre- or post-dedup.

Coverage that can't be verified this way (no independent asset inventory, no
accessible collector config) is a **declared assumption**, in the same
format as Elicit's (above) — never folded into the population statement as
if it were a verified claim.
