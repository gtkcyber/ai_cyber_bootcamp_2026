# Monitoring and retraining

Depth and worked examples for the "is it still working" subfields.
`SKILL.md` carries the protocol form; this file carries the reasoning
behind it.

## monitoring

TensorFlow Data Validation (Caveness, Zinkevich, Polyzotis et al., SIGMOD
2020) established schema-based validation at scale — that is the paper's
scope. The practice corollary (not TFDV's own claim): **schema drift and
concept drift are different failure classes** — a monitor built for one
silently misses the other:

- **Schema/contract drift** — structural: a field disappears, changes
  type, gains a new enum value, or a producer starts emitting a
  vendor-extension field. Caught by conformance checks against the pinned
  producer-emitted spec version (`ds-data-models`' Validate discipline).
- **Performance drift (concept drift)** — the input-label relationship
  itself changed; the model's predictions get quietly worse even though
  every input still parses cleanly. Requires a delayed-label feedback loop
  to detect directly, or a proxy (calibration drift, prediction
  distribution shift) when labels lag.
- **Coverage/population-statement drift** — a collector-configuration
  change (a new sampling rate, a filter added upstream, a retention policy
  change) that alters *what population the data represents* without
  breaking any schema. LITERATURE-THIN: no established name distinct from
  the structural-drift literature above. **Worked**: a logging pipeline
  adds a 10% sample-rate filter to cut cost; every record still parses,
  every field still conforms — but the population statement
  (`ds-data-models`' Observe discipline) the monitoring spec was written
  against is now false. This is a monitored *contract*, not merely a
  distribution shift: the population-statement change itself is the
  alertable event, before any statistical drift test would even fire.
- **Provenance drift** — an upstream source changes *how* it asserts a
  value (a vendor swaps its enrichment method, a field moves from
  `observed` to `derived` provenance class) without changing the field's
  name, type, or apparent values. Also LITERATURE-THIN. **Worked**: a
  GeoIP enrichment vendor changes its lookup database provider; IP-to-
  country values still populate the same field with the same type, but
  the falsifier behind the claim ("what would make this record wrong")
  changed. A distributional monitor sees nothing; a provenance monitor
  that re-checks the Attest register's `asserter`/`falsifier` fields
  (`ds-data-models`' artifact) catches it.

Don't design a separate production monitoring suite from scratch when the
dev-time contracts already name what "valid" means for this data; extend
them, don't replace them.

**Recurring re-checks.** A feed-version bump is first contact with a
"new" schema in every sense that matters — it re-triggers
`ds-data-models`' Validate discipline the same way a genuinely new source
would, not a lighter diff-only check.

**Adversarial framing.** An intentional, adversary-driven distribution
shift (evasion, poisoning) is a domain-overlay delta on top of this
general drift-monitoring form — `ds-domain-cyber` states what changes
under adversarial assumption (e.g., an attacker optimizing specifically
to stay under the alert threshold); this subfield's job is the general
statistical/contract form the overlay's delta sits on top of.

## retraining

Pham et al. (2024) frame the retraining decision as **blind** (retrain on
a fixed schedule, regardless of measured drift) vs. **informed** (retrain
when a statistical or performance-threshold trigger fires).

**The trap.** An "informed" trigger that fires on a performance metric
computed from delayed labels that never actually arrive (no real feedback
loop wired up) degrades silently into a blind trigger — it either never
fires, or fires on stale/proxy signal that isn't really measuring what it
claims to measure. Before calling a trigger "informed," confirm the
labels it depends on actually arrive, on what latency, and at what
completeness.

## non-model-analytics

Stancil (2021) names the metrics-layer gap: BI tools each compute "the
same" metric locally, and small definitional differences (does "active
user" include a trial account? is revenue gross or net of refunds?)
compound into dashboards that disagree with each other while each claims
to be right.

**The single-computation-point requirement.** A metrics layer only
prevents this drift if it is the *one* place the metric is computed and
every consumer reads the result — a metrics layer that exists alongside
tools still allowed to recompute locally reproduces the exact problem it
was built to solve, just with an extra layer of false confidence.

Three concerns, all non-model production artifacts:

- **Metric-definition versioning** — a metric's definition changes
  (a new exclusion rule, a currency conversion update); the version that
  produced a historical number must stay resolvable, the way a model
  version does in the registry.
- **Recurring-report freshness and reconciliation** — a report that runs
  on a schedule needs a staleness contract (how old is "too old") and a
  reconciliation check against its own source aggregates, the same
  discipline `ds-clean`'s assertion suite applies to model-bound data.
- **Dashboard contract monitoring** — a dashboard silently pointing at a
  stale or renamed upstream table is the non-model analog of schema
  drift; monitor it the same way.
