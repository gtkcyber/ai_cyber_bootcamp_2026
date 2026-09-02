# Independent second-path reproduction

Depth for `ds-verify`'s core gate: what "second path" means, how the
threshold is set, and the three checks a raw numeric match does not
substitute for. SKILL.md carries the protocol; this file carries the
worked detail and full citations.

## What counts as a second path {#second-path}

**Literature**: NASEM, *Reproducibility and Replicability in Science*, 2019
— https://www.ncbi.nlm.nih.gov/books/NBK547546/ — defines **computational
reproducibility**: an independent party, given the same data and methods,
obtains a consistent result. This is distinct from **replicability** (new
data, same question) — `ds-verify` performs the former, never claims the
latter. Hardwicke et al., "Analytic reproducibility in articles receiving
open data badges" — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7890505/ —
reanalyzed 25 published papers via a genuinely separate pipeline; only 36%
were fully reproducible before contacting the original authors, and the
paper's operational threshold for a **major discrepancy** was set at ≥10%
error. That 10% figure is a precedent for *having* an explicit threshold,
not a value to import wholesale — `discrepancy_threshold` is set per claim,
scaled to what the downstream decision can tolerate (a headline metric in
an executive report tolerates less slack than an exploratory finding).

A second path is genuinely different when it changes at least one of:
the query/aggregation logic (a different groupby/join order, not a
copy-pasted query), the tool or library (a different aggregation engine, a
hand-rolled loop instead of a vectorized call), or the intermediate
artifact it reads from (recomputing from a raw extract instead of from a
already-aggregated table the first path also read). Re-running the exact
same script and calling the identical output "confirmed" fails the gate —
it establishes determinism, not correctness.

## The three checks a numeric match does not replace {#three-checks}

A matching number from two paths is necessary, not sufficient. Three
additional checks, all cited from the design spec, must also pass:

- **Same record-semantic (Attest) claim.** Both paths must count the same
  thing, per the `ds-data-models` Attest register: two paths that agree
  numerically while one counts "sessions" and the other counts "session
  starts including retries" are agreeing on a coincidence, not verifying a
  claim. Cite both paths' `attest_id` and confirm they match before
  trusting the discrepancy check at all.
- **Shared coverage assumption.** If both paths read from the same
  upstream collector (the same log source, the same event stream), a gap
  in that collector's coverage (an outage, a sampling rate, a filter) is
  invisible to both paths equally — they will agree with each other while
  both being wrong relative to the true population. State explicitly
  whether the two paths share a collector, and if so, name what blind spot
  that sharing could hide. A second path drawn from a genuinely
  independent collection mechanism (a different log source, a manual spot
  count against source systems) breaks this failure mode; a second path
  that only reruns different code against the same table does not.
- **Reconciliation source's own population statement.** When the second
  path draws from a different source than the first (the strongest form of
  independence), that source carries its own population statement
  (`ds-data-models`' Observe discipline) — record it. A reconciliation
  source with an unstated population statement cannot support a coverage-
  assumption claim either way.

## Compressed (quick-answer) form

Per `tiers.md`: one line each for `second_path` (what was recounted and
how), `denominator_basis` (the count/rate's coverage basis), and a
population-statement citation. This is still three separately checkable
fields — a single sentence asserting "verified" without naming what was
recomputed fails the gate even at quick-answer tier.
