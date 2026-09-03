# Data contracts, raw immutability, and join gates

Depth for the artifact-level gates: the `data_contract` schema shape, the
raw-immutability rule, and the join gate that applies at any join site in
the pipeline. SKILL.md carries the protocol; this file carries worked
detail and full citations.

## Data contracts {#contracts}

**Literature**: no academic literature; canonical is an industry
standard — Open Data Contract Standard (ODCS), Linux Foundation/Bitol —
https://bitol-io.github.io/open-data-contract-standard/v3.1.0/.
**LITERATURE-THIN** on academic grounding; practitioner standard, not
peer-reviewed, cited as the shape to conform to rather than as research
evidence.

- **Schema**: field names, types, nullability, as the producer actually
  emits them — not an aspirational or documented-but-unobserved shape.
- **SLA**: freshness, completeness, and availability commitments the
  source makes (or the acquisition job makes, if this skill is producing
  the contract for a downstream consumer).
- **Quality rules**: checkable assertions the acquired data must satisfy
  (uniqueness, range, referential expectations) — these seed
  `ds-clean`'s assertion suite and, in production, `ds-mlops`' contract
  monitoring.
- **Versioning**: how a breaking schema change is signaled and handled —
  this is what production drift monitoring watches for.

A contract with an empty or aspirational schema section (documenting what
the source is *supposed* to emit rather than what a pull actually
returned) fails the artifact gate — the contract describes observed
reality, the same discipline `ds-data-models`' Research step applies to
pinning a producer-emitted spec version over the latest published one.

## Raw immutability {#immutability}

Acquired raw data is written once, at acquisition time, and never mutated
in place afterward. Every cleaning, normalization, or transform step
downstream (`ds-clean`, `ds-pipelines`) reads the raw artifact and writes
a new one — it never edits the raw capture.

Why this is a gate and not a preference: without it, a bug discovered
three steps downstream has no way to distinguish "the source was wrong" from
"a transform corrupted the source," and reproducibility (re-run this
pipeline from scratch, get the same answer) breaks silently. The gate
checks for the *absence* of in-place raw mutation (raw storage
location/permissions are write-once, or a checksum of the raw artifact is
unchanged across the run) — it does not audit whether downstream
transforms are correct, only that they had an untouched source to start
from.

## Join gates {#join-gates}

Two checks, required before any join executes — at ingest in `ds-gather`,
and identically at any later join site (`ds-pipelines`, `ds-features`, or
anywhere else two datasets combine).

**Same-semantics check.** Same key name across two sources is not evidence
of same meaning — a `user_id` in a billing system and a `user_id` in a
support ticketing system may key different entities (billing account vs.
individual contact) despite the identical field name. Before joining, cite
both sides' `ds-data-models` semantic-dictionary entries
(`<dataset>.<field-path>` → `interpretation`) and confirm the
interpretations actually match. A join whose key semantics were never
looked up, only assumed from the name, fails this check regardless of
whether the join executes without error — a join can complete cleanly
while joining apples to oranges.

**Cardinality check.** Confirm the expected row-multiplication behavior of
the join (one-to-one, one-to-many, many-to-many) against the grain each
side declared (`ds-data-models`' grain contract — cited here, never
re-derived). A join expected to be one-to-one that silently fans out
one-to-many inflates every downstream count; this is a lightweight
pre-join check (compare declared grain and key uniqueness on each side),
not a full post-join row-count audit — that fuller audit is
`ds-verify`'s join fan-out check, which this gate feeds into rather than
duplicates.

**What this gate does not do**: it does not perform record/identity-level
linkage (matching two records that represent the same real-world entity
despite non-identical keys — probabilistic matching, fuzzy join). That
mechanic belongs to `ds-entity-resolution`; this gate's semantics check
only confirms that when keys *do* match, they mean the same thing. It also
does not perform schema-level field mapping across differently-modeled
sources (OCSF ↔ CIM-style translation) — that is `ds-data-models`'
Translate discipline, consulted before this gate runs when the two sides
use different data models.
