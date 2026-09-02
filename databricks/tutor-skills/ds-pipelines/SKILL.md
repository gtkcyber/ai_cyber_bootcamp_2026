---
name: ds-pipelines
description: "Orchestration and warehouse-delivery intelligence for data already acquired: DAG orchestration/scheduling, incremental vs full refresh, backfills and idempotency, partitioning and storage formats, warehouse/dimensional modeling, late-arriving and restated records, point-in-time reconstruction, analysis-code…"
---

# ds-pipelines

Runs after `ds-gather` writes the data contract and before the data enters
`ds-data-models`' semantic work: orchestrates, refreshes, and delivers
acquired data into whatever store the task lands on. Not re-entrant: fires
once per task; a later maintenance need routes through the loop-backs in
Edges, not a fresh entry. Full depth and citations live in `references/`;
this file is protocol only.

## Subfields

- **Orchestration (DAGs, scheduling)** — trigger: an ongoing, scheduled
  pipeline, not a single ad hoc run. Apache Airflow, "Architecture
  Overview" — https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html :
  scheduler/DAG-processor/executor model. DAG orchestration guarantees
  execution *order*, not data correctness. See
  `references/ds-pipelines.orchestration-and-refresh.md#orchestration`.
- **Incremental vs full refresh** — trigger: any pipeline composes; every
  refresh strategy is a decision, even "always full refresh." dbt,
  "Configure incremental models" —
  https://docs.getdbt.com/docs/build/incremental-models : insert/merge/
  delete+insert strategies. A fixed lookback window silently drops
  late-arriving changes past the window — reconcile with periodic full
  refresh. See `references/ds-pipelines.orchestration-and-refresh.md#incremental-vs-full`.
- **Backfills and idempotency** — trigger: reprocesses historical data or
  must tolerate re-runs. Beauchemin, "Functional Data Engineering — a
  modern paradigm for batch data processing" —
  https://maximebeauchemin.medium.com/functional-data-engineering-a-modern-paradigm-for-batch-data-processing-2327ec32c42a :
  overwrite whole partitions rather than UPDATE/DELETE/APPEND. Idempotency
  is deliberate design, not automatic. See
  `references/ds-pipelines.orchestration-and-refresh.md#backfills-idempotency`.
- **Partitioning and storage formats** — trigger: writes to partitioned or
  columnar storage. Melnik et al., "Dremel: Interactive Analysis of
  Web-Scale Datasets," VLDB 2010 —
  https://sfu-db.github.io/dbsystems/Lectures/Dremel.pdf : columnar-
  nested-data algorithm Parquet implements. Partition pruning only works
  if query predicates align with the physical partition key. See
  `references/ds-pipelines.orchestration-and-refresh.md#partitioning-storage`.
- **Warehouse/dimensional modeling** — trigger: delivers into a
  fact/dimension warehouse schema. Kimball Group, "Fact Tables and
  Dimension Tables" — https://www.kimballgroup.com/2003/01/fact-tables-and-dimension-tables/ :
  facts as measurement events at atomic grain; conformed dimensions as
  reuse. Grain must be declared before design — cite `ds-data-models`'
  grain contract (Interpret), never re-derive. See
  `references/ds-pipelines.warehouse-and-time.md#dimensional-modeling`.
- **Late-arriving and restated records** — trigger: source data revises or
  arrives after initial load. Kimball Group, "Slowly Changing Dimensions" —
  https://www.kimballgroup.com/2008/08/slowly-changing-dimensions/ :
  Types 1/2/3 (the cited article; extended types 0/4–7 appear in later
  Kimball Group material, not that page). Active-row identification uses
  date-range validity, not a "current-record" flag, or historical joins
  mis-join against the wrong dimension version. See
  `references/ds-pipelines.warehouse-and-time.md#late-arriving`.
- **Point-in-time reconstruction** — trigger: feature/label construction
  needs an as-of-correct view across time. Feast docs, "Point-in-time joins"
  — https://docs.feast.dev/getting-started/concepts/point-in-time-joins :
  retrieves the latest feature value at-or-before the event timestamp. See
  `references/ds-pipelines.warehouse-and-time.md#point-in-time`.
- **Analysis-code correctness (property tests, golden-row regression,
  idempotency tests)** — trigger: any pipeline composes; every transform
  needs a checkable correctness claim. Claessen & Hughes, "QuickCheck: A
  Lightweight Tool for Random Testing of Haskell Programs," ICFP 2000 —
  https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf :
  universally-quantified properties over random inputs. Falco, "Approval
  Tests" — http://llewellynfalco.blogspot.com/2008/10/approval-tests.html :
  compares output against a stored "approved" reference. A golden file
  blindly re-approved on diff becomes a no-op. Artifact-bearing: writes
  `transform_test_suite`. See
  `references/ds-pipelines.testing-and-integrity.md#analysis-code-correctness`.
- **Training-data integrity checks (poisoning surface)** — trigger: training
  data sourced from external, crowd-sourced, or user-influenced channels.
  Biggio & Roli, "Wild Patterns: Ten Years After the Rise of Adversarial
  Machine Learning," Pattern Recognition 84, 2018 —
  https://arxiv.org/abs/1712.03141 : training-time (poisoning) vs.
  test-time (evasion) attacks are distinct. Flags the surface at
  pipeline-delivery only; labeling strategy/quality response is
  `ds-labeling`'s. See
  `references/ds-pipelines.testing-and-integrity.md#training-data-integrity`.

|---|---|---|
| Orchestration (DAGs, scheduling) | analysis | conditional-on-data:scheduled-orchestration |
| Incremental vs full refresh | quick-answer | mandatory |
| Backfills and idempotency | analysis | conditional-on-data:backfill-or-reprocessing |
| Partitioning and storage formats | analysis | conditional-on-data:partitioned-storage-target |
| Warehouse/dimensional modeling | analysis | conditional-on-data:warehouse-target |
| Late-arriving and restated records | analysis | conditional-on-data:late-arriving-or-restated-source |
| Point-in-time reconstruction | analysis | conditional-on-data:point-in-time-join-required |
| Analysis-code correctness | quick-answer | mandatory |
| Training-data integrity checks | analysis | conditional-on-data:external-or-crowd-sourced-training-data |

`mandatory`: fires whenever `ds-pipelines` composes — every pipeline picks a
refresh strategy and needs a checkable correctness claim, unlike the other
seven, which fire only on their own trigger.

## Gates

- `refresh_backfill_state` states a whole-partition-overwrite (or equally
  deterministic) design for any backfilled/reprocessed range — row-level
  UPDATE/DELETE/APPEND without a documented dedup/merge key fails this gate.
- Every `transform_test_suite` entry states the invariant or golden fixture
  it checks — a test-file name alone fails; a golden fixture re-approved
  without recording why the transform changed fails too.
- Any join constructing a point-in-time feature or label states its as-of
  timestamp bound explicitly — an unstated bound fails per
  `references/doctrine-leakage.md`.
- **Join gate**, at any join site in the pipeline: cite `ds-gather`'s
  same-semantics + cardinality gate — never restated, only applied here.
- A warehouse fact table states its grain before design — cite
  `ds-data-models`' grain contract (Interpret); never re-derived here.
- Late-arriving/restated dimension handling uses date-range validity for
  active-row identification — a current-flag-only design fails this gate
  for historical joins.
- A training set from an external/crowd-sourced/user-influenced channel
  states its poisoning-surface assessment before it feeds model training —
  an unassessed external-source set fails this gate.

## Edges

Covered: orchestration/scheduling design, incremental-vs-full-refresh
choice, backfill/idempotency design, partitioning/storage-format choice,
warehouse/dimensional modeling at a declared grain, late-arriving/restated-
record handling, point-in-time reconstruction mechanics, analysis-code
correctness (property tests, golden-row regression, idempotency tests),
training-data poisoning-surface flagging.

Its artifact goes `stale` in the transitive downstream closure whenever a
scoping-targeted back-edge fires (`data-models → scoping`, `monitoring →
scoping`, `impact → scoping`, `cost-overrun → scoping`), since `pipelines`
sits immediately after `gather` in `manifest.json`'s lifecycle list. When
scoping re-runs, `ds-pipelines` re-runs as part of the forward cascade in
normal composition order, not via a named back-edge of its own.

## Audit mode

Input: an existing external orchestration/warehouse artifact authored
outside this skill (an Airflow DAG repo, a dbt project, a warehouse ERD, an
existing test suite). An undocumented pipeline claim is treated as an
unregistered field under Gates: flagged, never assumed compliant.

## Production considerations

Three deltas, all pointers: stateful streaming serving computation and its
production drift/schema monitoring move to `ds-mlops`, which also owns
continuous orchestration-health and contract-drift monitoring — seeded by
this skill's `refresh_backfill_state` and `transform_test_suite`, the way
`ds-clean`'s assertion suite seeds it; window-feature definition/semantics
for streaming pipelines stays `ds-features`' (streaming row split); pipeline
compute/storage economics read `doctrine-scale-cost.md`'s threshold,
recorded once in `ds-scoping`'s kill-check and never restated here.
