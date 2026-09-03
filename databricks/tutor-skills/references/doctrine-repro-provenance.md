# Doctrine: reproducibility and provenance

## Code, don't read

The agent programs the analysis; it never pulls raw data in bulk into its
context. All profiling, aggregation, and validation outputs are computed by
scripts, written in whatever language the runtime uses (stack-agnostic),
that return derived answers — counts, distributions, violations — never row
dumps.

Raw-row inspection is permitted but **bounded and deliberate**: a few random
rows, plus purposefully selected rows that ensure value-space
representation —

- populated examples of mostly-null columns (if any exist),
- an example per enumeration value,
- boundary/min-max rows,
- an example per detected schema version.

The selection itself is made by a script the agent writes (find-and-feed),
never by scrolling data. Every gate in the suite is phrased so it is
checkable by code — this is why.

## Population statements are composable artifacts

Every join, filter, aggregation, or dedup rewrites (or explicitly
reaffirms) the population statement of its output.

- Attrition above a stated threshold must surface in `ds-communicate`.
- Joins compose coverage: state intersection vs. union explicitly.

## Additivity

Every measure is classified **additive / semi-additive / non-additive**.
Ratio-of-averages vs. average-of-ratios is resolved before any aggregation.
Gated in `ds-profile`, `ds-features`, `ds-analytics`.

## Provenance classes

Field provenance classes — **observed / derived / enriched / defaulted /
asserted / privacy-transformed** — propagate through every transform. A
composite or derived feature inherits its weakest input's class.

- Unvalidated external model outputs (vendor scores, GeoIP, third-party
  enrichments) may not feed features, metrics, or reports without
  validation — suite-wide, not just `ds-features`.
- Internally composed model outputs are permitted when fit leak-safe within
  the pipeline and provenance is declared (`ds-method-composition`).

## Reproducibility and notebook hygiene

Seeds, pinned environments, data versioning. Notebooks explore; modules
ship. Restart-and-run-all before any notebook-derived claim is trusted.
