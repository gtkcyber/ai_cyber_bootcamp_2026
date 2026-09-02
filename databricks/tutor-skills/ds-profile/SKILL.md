---
name: ds-profile
description: "Structured EDA protocol producing a findings doc: distributions, missingness, typing, cardinality, duplicate-by-field-equivalence and outlier signal (flagged, not fixed), additivity classification, and grouping-variable identification (the keys — patient, account, device, session — that make rows non-iid). All…"
---

# ds-profile

Runs after `ds-data-models` establishes the semantic dictionary, Attest
register, and population statement, and before `ds-clean` decides
remediation. **Produces findings, never fixes** — a discovered problem is a
finding this skill records, not a transform this skill applies; remediation
is `ds-clean`'s. Full depth, worked examples, and citations live in
`references/`; this file is protocol only.

## Subfields

- **Structured EDA protocol** — Tukey, *Exploratory Data Analysis*,
  Addison-Wesley 1977: founding text, EDA as visual/robust pattern-detection
  distinct from confirmatory analysis, source of the box plot. NIST/SEMATECH
  e-Handbook, "Exploratory Data Analysis" —
  https://www.itl.nist.gov/div898/handbook/eda/eda.htm : freely accessible
  structured practitioner protocol descending from Tukey's framework. EDA is
  hypothesis-generating, not confirmatory — a profiling finding is never
  presented as a confirmatory statistical claim. This skill's delta over
  that doctrine is the ordered computation it runs — structure/shape →
  typing → missingness → cardinality/uniqueness → duplicate-by-field-
  equivalence signal → univariate distributions → outlier signal →
  additivity classification — not a re-teaching of EDA generally:
  `references/ds-profile.eda-protocol.md`.
- **Grouping-variable identification** — clustered / repeated-measures /
  hierarchical data-structure identification. Laird & Ware, "Random-Effects
  Models for Longitudinal Data," Biometrics 38, 1982 —
  https://www.stat.cmu.edu/~brian/720/week07/laird-ware-biometrics-1982.pdf :
  foundational two-stage random-effects model for correlated/clustered
  observations, extends to any cluster, not just repeated measures.
  "Repeated measures & clustered data," A Primer in Pediatric Biostatistics
  — http://www.chrim.ca/biostatistics-resources/primer/rmc.html :
  independence assumptions break under clustering — undetected clustering
  invalidates standard-error estimates (too small). Identifies the keys —
  patient, account, device, session — that make rows non-iid, derived from
  `ds-data-models`' grain contract (Interpret), never re-derived here:
  `references/ds-profile.grouping-variables.md`.

## Production considerations

Two deltas, both pointers: full-data profiling over datasets too large for
in-memory computation escalates only as far as forced, per
`references/doctrine-scale-cost.md`'s scale playbook (validity-preserving sampling
before out-of-core, out-of-core before distributed) — sampling that
compromises the population statement is not "cheaper," it is a different
population; and this skill's findings — the additivity classification and
the grouping-variable list in particular — seed `ds-mlops`'s production
distributional and drift monitoring the same way `ds-clean`'s assertion
suite seeds it, rather than that monitoring re-deriving either from
scratch.
