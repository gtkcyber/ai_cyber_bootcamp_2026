---
name: ds-data-models
description: "Schema, standard, and semantic intelligence for any dataset: fingerprints, researches, elicits, and interprets data models on the fly, including operational-event semantics, collection coverage, and field trust provenance."
---

# ds-data-models

**Re-entrancy trigger**: fire on first contact with any new schema, source,
feed version, or field, at any tier, mid-pipeline or not. Mandatory at every
composition tier per router doctrine.

Full depth for every discipline below, worked examples, and the standards
citations live in `references/ds-data-models.disciplines.md` and
`references/ds-data-models.standards-index.md`. The spec-less playbook lives in
`references/ds-data-models.elicitation-protocol.md`. This file is protocol only.

## Subfields

The nine disciplines. Run in rough order on first contact with a schema;
re-enter any one of them independently once its precondition changes.

- **Identify** — fingerprint the schema/standard from structural tells: OCSF
  `class_uid`/`category_uid`, Splunk CIM tags, ECS field-set names, vendor
  extension markers. Ambiguous fingerprint → treat as unidentified, not as
  the nearest guess. See `references/ds-data-models.disciplines.md#identify`.
- **Research** — find and pin the *producer-emitted* spec version, not the
  latest published one. Vendor extensions and nonconformance are what the
  data actually follows. Mid-stream schema migration within one source gates
  identically to a cross-source difference. See
  `references/ds-data-models.disciplines.md#research`.
- **Elicit** — for data with no findable spec, *or* a spec the data
  demonstrably contradicts (internal tables, CSV exports, or a nonconforming
  feed Validate already flagged), derive semantics from observable behavior,
  not documentation. A Validate nonconformance finding is an explicit entry
  point into Elicit for the affected fields, not just a data-quality
  footnote. Full scripts-first playbook: `references/ds-data-models.elicitation-protocol.md`.
  Unresolved semantic → declared assumption + stated impact; unresolvable →
  route to the human.
- **Observe** — collection coverage: audit policy, verbosity, sampling,
  filters, truncation, retention, and outages decide what exists in a
  dataset. Every dataset gets a population statement ("contains X, collected
  by Y, subject to Z") before any aggregate claim. Absence of records ≠
  absence of activity. See `references/ds-data-models.disciplines.md#observe`.
- **Interpret** — field semantics: composite decomposition (User-Agent →
  product/OS/engine/device), constrained values (domain-name structure,
  PSL/eTLD+1), enums, units, sentinel encodings (`0`, `-1`, `1970-01-01`);
  provenance class (observed/derived/enriched/defaulted/asserted/
  privacy-transformed) and its analytic consequences; nested/array fields
  declare cardinality semantics and whether analysis flattens/aggregates/
  picks-one; canonicalization (any field used for comparison/join/agreement
  declares its canonical form first); When (event vs ingest vs decision
  time, clock skew, as-of discipline); grain contract (declared grain + key
  uniqueness). See `references/ds-data-models.disciplines.md#interpret`.
- **Attest** — what a record *proves* happened, not what its columns
  suggest: actor(role)/action/mechanism/target decomposition; disaggregate
  unlike events before counting by the dataset's declared record-type
  discriminator (measurement vs meaning); asserter and incentive plus
  falsifier (who asserted this value, what would make it false). Worked
  example (required): Kerberos ticket issuance vs. an admin session — both
  "touch the DC," neither attests the other. See
  `references/ds-data-models.disciplines.md#attest`.
- **Leverage** — specs as feature-mines; cross-source disagreement between
  sources that *should* agree is itself a feature (DNS ↔ TLS SNI ↔ HTTP
  Host; inventory system A vs. B). General principle for any multi-source
  dataset. See `references/ds-data-models.disciplines.md#leverage`.
- **Translate** — cross-model mapping (OCSF ↔ CIM ↔ ECS) by semantics, never
  by field-name similarity. Record-level identity linkage is out of scope
  here → `ds-entity-resolution`. See `references/ds-data-models.disciplines.md#translate`.
- **Validate** — conformance as a data-quality signal: extension fields,
  deprecated values, version skew across the record set flag drift even when
  every record still parses. See `references/ds-data-models.disciplines.md#validate`.

## Gates

Each is phrased so a script can check it against the semantic dictionary and
Attest register:

- Every field consumed by an analytic claim has a semantic-dictionary entry
  or a declared assumption record — no unregistered field feeds a claim.
- Every dataset has a population statement recorded before its first
  aggregate claim.
- Every distinct value of a dataset's declared record-type discriminator
  (`class_uid`/`EventID`/tag set/`single-type`) included in a count has a
  matching Attest register entry (`attest_id` naming actor/action/mechanism/
  target) — the gate is a join between discriminator values and register
  entries, not a per-record check.
- Every join declares the grain of each side before executing (join gates at
  `ds-gather`/`ds-pipelines` cite this grain, not re-derive it).
- Every schema/standard claim cites a pinned producer-emitted version, not
  "latest" or an assumed default.

## Edges

Covered: fingerprinting, versioned research, spec-less elicitation, coverage
statements, field/event semantics, cross-model translation, conformance
checks — for data models encountered during a DS task.

Not covered, escalate with provenance: full ontology engineering; ground-up
wire-protocol reverse-engineering. State "outside coverage" explicitly,
research externally, verify the found method against the actual data, report
provenance — never silently stretch past what was verified.

Triggers to other skills: identity-key temporal validity →
`ds-entity-resolution`; observable-behavior statistics beyond elicitation
scope → `ds-profile` (Elicit computes only what's needed to assign a field
its semantic; characterizing data for modeling is `ds-profile`'s job, not
an extension of Elicit); missingness-mechanism hypotheses (MCAR/MAR/MNAR) →
`ds-clean`; producing (not consuming) privacy transforms → `ds-clean` /
`ds-simulation`; data can't support the requested framing → loop back to
`ds-scoping`.

## Audit mode

Input: existing external data documentation or a semantic dictionary
authored outside this skill (a wiki page, a vendor data dictionary, a prior
analyst's notes). Treat undocumented claims the same as unregistered fields
under Gates — flag, do not assume.

## Production considerations

Feed version bumps and vendor schema migrations re-trigger this skill —
treat a bump like first contact with a new schema, not a diff to shrug off.
The semantic dictionary is a monitored contract: schema/version drift in
production feeds `ds-mlops` monitoring the same way `ds-clean`'s assertion
suite does.
