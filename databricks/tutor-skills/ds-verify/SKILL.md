---
name: ds-verify
description: "Mandatory verification gate before any artifact leaves the run: independent second-path reproduction of every quantitative claim, magnitude/sanity checks, join fan-out/denominator/attrition/double-filter audit, alternative-explanation survival, falsifiability."
---

# ds-verify

Runs against every quantitative claim, model or no model.

Full depth and worked examples live in `references/`. This file is
protocol only.

## Subfields

- **Independent second-path reproduction** — literature term:
  **reproducibility** (distinct from replicability). Trigger: any
  quantitative claim about to leave the run. NASEM, *Reproducibility and
  Replicability in Science*, 2019 — https://www.ncbi.nlm.nih.gov/books/NBK547546/
  : computational reproducibility (independent execution, same data/
  methods) is distinct from replicability (new data). Hardwicke et al.,
  "Analytic reproducibility in articles receiving open data badges" —
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7890505/ : independent
  reanalysis via a genuinely separate pipeline; "major discrepancy" defined
  at ≥10% error — precedent for an explicit numeric threshold, not a
  borrowed universal cutoff. See `references/ds-verify.reproduction-protocol.md#second-path`.
- **Magnitude/sanity checks** — **LITERATURE-THIN**; nearest is the **Fermi
  problem / Fermi estimate** (general pedagogy), treated as practice
  protocol, not settled literature. See
  `references/ds-verify.audit-checks.md#magnitude`.
- **Join fan-out, denominator, attrition, double-filter audit** — no single
  umbrella term: **fan trap/fan-out** (relational modeling; primary
  textbook source unreachable, cited secondhand) + **survivorship/attrition
  bias** (funnel literature). Trigger: computation crossed a join or filter
  chain, or states a count/rate. Holistics Docs, "Cannot combine fields due
  to fan-out issues?" — https://docs.holistics.io/docs/faqs/fan-out-issue :
  a one-to-many join duplicates the "one" side's aggregate once per
  matching "many" row; a shrinking funnel denominator with improving
  per-stage metrics is the classic survivorship signature. See
  `references/ds-verify.audit-checks.md#fan-out`.
- **Alternative-explanation survival** — literature term: **threats to
  validity** (internal validity), Campbell & Stanley tradition. Trigger:
  claim is observational/quasi-experimental, not a randomized design.
  Confirmed via citation in "A Simulation Study of Threats to Validity in
  Quasi-Experimental Designs" — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4910671/
  : taxonomy of history, maturation, testing, instrumentation, regression,
  selection, mortality threats; name the specific threat invoked, not
  "confounders" generically. See `references/ds-verify.audit-checks.md#alt-explanation`.
- **Falsifiability** — literature term: **falsifiability / demarcation
  criterion** (Popper). Trigger: claim states a general/universal pattern,
  not one isolated data point. Stanford Encyclopedia of Philosophy,
  "Karl Popper" — https://plato.stanford.edu/entries/popper/ : scientific
  iff capable of conflicting with possible observations; a single
  apparent counter-instance is never alone methodologically sufficient. See
  `references/ds-verify.audit-checks.md#falsifiability`.

|---|---|---|
| Independent second-path reproduction | quick-answer | mandatory |
| Magnitude/sanity checks | analysis | mandatory |
| Join fan-out, denominator, attrition, double-filter audit | quick-answer | mandatory |
| Alternative-explanation survival | analysis | mandatory |
| Falsifiability | analysis | mandatory |

`mandatory` = runs whenever `ds-verify` composes. At quick-answer, only
second-path reproduction and the fan-out/denominator/attrition audit fire —
in the compressed form below; the other three activate once the effective
tier reaches analysis (`SKILL.md`'s tier-floor reconciliation).

## Gates

Each phrased checkable against the `verification_record` (below):

- No claim leaves the run — `ds-communicate` report, `ds-mlops` promotion,
  `ds-analytics` publication — without a `verification_record` entry; an
  absent entry blocks the handoff, it is not a skipped check.
- `second_path` uses genuinely different code/tooling than `primary_path` —
  a copy-derived or identical path fails regardless of numeric agreement.
- `discrepancy` is checked against an explicit numeric threshold recorded in
  the same field — "close enough" with no stated number fails.
- `attest_alignment` is `true` only once both paths are confirmed to count
  the same `attest_id` (`ds-data-models`' Attest register) — numeric
  agreement with `attest_alignment` false or unchecked fails: shared-wrong-
  semantics agreement is not verification.
- `coverage_assumption_shared` is stated, not silent — a claim that never
  names whether the two paths share a collector/population blind spot fails.
- `denominator_basis` is present on every count/rate claim, citing the
  coverage basis (`ds-data-models`' population statement, or the
  reconciliation source's own).
- Any claim whose computation crossed a join or filter chain carries a
  non-empty `attrition_ledger_ref` — row counts audited before/after each
  step, never assumed.
- Compressed (quick-answer, `tiers.md`) form: `second_path` recount +
  `denominator_basis` + a population-statement citation — three separately
  checkable fields, not one sentence.

## Edges

Covered: the five subfields above, applied to every quantitative claim
about to leave the run. Not covered, pointer only: statistical significance/hypothesis-test
validity (`ds-stats` owns it — this skill verifies computational
correctness and population validity, never significance); whether the
reported metric was the right one to choose (`ds-evaluate` owns
metric↔cost matching — this skill verifies it was computed correctly, not
that it was the right choice); producing the row-attrition ledger's
underlying transform log (`ds-features`/`ds-pipelines`/`ds-clean` write it —
this skill reconciles against it, never originates it).

Its `verification_record` goes `stale` in the transitive downstream closure
whenever any upstream back-edge fires; `ds-verify` then re-runs as part of
the forward cascade in normal composition order, not a named back-edge of
its own.

## Audit mode

Input: an existing external verification artifact authored outside this
skill (a prior analyst's QA notes, a data-engineering validation report). An
unverified or undocumented claim fails Gates, never assumed passing.

## Production considerations

Production tier's effective floor (`SKILL.md` tier-floor reconciliation) is
always ≥ analysis, so all five subfields run in full form — no `n/a`
fields. `ds-mlops` retraining triggers must pass a tier-scaled `ds-verify`
before firing (quantitative drift triggers are themselves quantitative
claims, not exempt). `ds-analytics` dashboard publication passes this gate
at its own tier before going live. Ongoing monitoring for drift, contract
violations, and coverage/provenance drift is `ds-mlops`'; this skill
verifies a claim at the moment it ships, not continuously.
