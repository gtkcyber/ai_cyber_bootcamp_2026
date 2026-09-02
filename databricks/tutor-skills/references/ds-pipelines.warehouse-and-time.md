# Warehouse modeling, late-arriving records, and point-in-time reconstruction

Depth for the three time/grain-sensitive subfields: dimensional modeling,
late-arriving/restated records, and point-in-time reconstruction. SKILL.md
carries the protocol; this file carries worked detail and full citations.

## Warehouse/dimensional modeling {#dimensional-modeling}

**Literature**: dimensional modeling (Kimball). Kimball Group, "Fact Tables
and Dimension Tables" —
https://www.kimballgroup.com/2003/01/fact-tables-and-dimension-tables/ :
fact tables hold measurement events at one declared atomic grain;
dimension tables hold the descriptive context (who, what, where) those
measurements are analyzed by; conformed dimensions (the same dimension
table, same keys, shared across multiple fact tables) are the reuse
mechanism that lets facts from different processes be compared.

**Key failure mode**: grain must be declared *before* fact-table design,
not inferred afterward from what got loaded. Mixing grains in one fact
table — e.g. one row per order alongside rows per order-line — silently
breaks additive aggregation: a naive `SUM(amount)` double-counts the
order-level rows against the line-level rows with no error raised. This is
the same grain contract `ds-data-models` (Interpret) owns for any table,
not a warehouse-specific rule — cite that contract when declaring a fact
table's grain, never re-derive grain mechanics here.

**Worked example**: an `orders` fact at order-line grain (one row per
line item) conformed against a shared `dim_customer` and `dim_product` — a
`fct_order_total` view built as `GROUP BY order_id` from that same fact is
a derived, semi-additive rollup, not a second fact table at a different
grain; keeping it a view rather than a materialized table with its own
grain avoids the two tables silently drifting out of sync.

## Late-arriving and restated records {#late-arriving}

**Literature**: slowly changing dimensions (SCD), late-arriving fact
handling. Kimball Group, "Slowly Changing Dimensions" —
https://www.kimballgroup.com/2008/08/slowly-changing-dimensions/ : the
standard response types — Type 1 (overwrite, no history), Type 2 (new row
per change, date-range-bounded validity), Type 3 (limited history in
extra columns), plus extended types (0, 4, 5, 6, 7) for hybrid needs.

**Key failure mode**: active-row identification must use **date-range
validity** (`valid_from`/`valid_to` on each dimension row version), not a
single "current-record" boolean flag. A flag-only design has no way to
correctly join a late-arriving fact — one whose event timestamp falls
*before* the current flag was set — against the dimension version that was
actually true at that fact's event time; the join silently attaches the
fact to today's dimension state instead of the historically correct one.
Date-range validity makes that join correct by construction: join on
`fact.event_time BETWEEN dim.valid_from AND dim.valid_to`.

A **restated** record (the source revises a previously-delivered value, not
just arrives late) is handled the same way: a new dimension-row version
with its own validity range, never an in-place edit of the old version —
this is the same raw-immutability discipline `ds-gather` applies to
acquisition, carried through to the warehouse layer.

## Point-in-time reconstruction {#point-in-time}

**Literature**: point-in-time correctness (feature-store / ML systems
literature). Feast docs, "Point-in-time joins" —
https://docs.feast.dev/getting-started/concepts/point-in-time-joins :
for each entity/timestamp pair being featurized, retrieve the feature
value that was the *latest available at-or-before* that timestamp — never
a value that was only written later, even if it would have been "more
current" at query time.

**Mechanics**:
- **Snapshot tables**: materialize the dimension/feature state as of
  regular intervals (daily, hourly) rather than joining against a live
  mutable table — an as-of join against a live table is only
  point-in-time-correct if that table itself preserves history via the SCD
  date-range design above; a live table that overwrites in place cannot
  support a correct as-of join at all, because the value it held at the
  requested timestamp is gone.
- **As-of join**: for each event timestamp, select the snapshot/dimension
  row whose validity range contains that timestamp — identical mechanism
  to the late-arriving-fact join above, applied to feature construction
  instead of fact-to-dimension joins.
- **Restatement handling**: if a feature source restates a value after the
  fact, the point-in-time-correct answer is still "what was known at the
  original event timestamp" for any *already-trained* model's training set
  — a restatement changes what a *new* point-in-time reconstruction run
  today would retrieve for historical timestamps, but it must never be used
  to silently rewrite an already-frozen training set out from under a
  shipped model without an explicit re-training decision.

**Key failure mode**: a simple ID join (join `events` to `features` on
entity ID alone, no timestamp bound) is not equivalent to a
point-in-time-correct join — it silently pulls whatever the feature value
happens to be at query time, which is systematically *later* information
than was available at the event, producing training/serving skew and
leakage that inflates offline metrics without a compensating production
failure until the model actually serves.
