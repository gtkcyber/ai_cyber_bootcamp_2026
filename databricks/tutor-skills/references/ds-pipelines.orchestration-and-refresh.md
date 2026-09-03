# Orchestration, refresh, backfills, and storage layout

Depth for the first four subfields: scheduling/DAG orchestration, the
incremental-vs-full-refresh decision, backfill/idempotency design, and
partitioning/storage-format choice. SKILL.md carries the protocol; this
file carries worked detail and full citations.

## Orchestration (DAGs, scheduling) {#orchestration}

**Literature**: workflow orchestration, DAG model. Apache Airflow,
"Architecture Overview" —
https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html :
a scheduler triggers task instances, a DAG processor parses task
dependency graphs, executors run the tasks — the model most orchestrators
(Airflow, Dagster, Prefect) share regardless of implementation.

**Key failure mode**: DAG orchestration guarantees execution *order*, not
data *correctness*. A DAG that completes green tells you every task ran in
dependency order — it says nothing about whether the data each task
produced is right. Treat "the DAG succeeded" and "the data is correct" as
two separate claims, verified by two separate mechanisms (this skill's
analysis-code-correctness subfield covers the second).

Trigger for this subfield specifically: the task involves an *ongoing*,
scheduled pipeline — a single one-off transform run, executed once and
never re-scheduled, doesn't need a DAG design, only the incremental/backfill
subfields below.

## Incremental vs full refresh {#incremental-vs-full}

**Literature**: no separate academic literature; canonical practitioner
reference is dbt's incremental-materialization model. dbt, "Configure
incremental models" — https://docs.getdbt.com/docs/build/incremental-models :
names three strategies — `append`, `merge` (upsert on a unique key), and
`delete+insert` (drop and reload a bounded window) — each with a stated
unique key and (for windowed strategies) a lookback predicate.

**Key failure modes**:
- A missing or wrong unique key on a `merge` strategy duplicates rows
  silently — the merge matches nothing, so it inserts instead of updating.
- A fixed lookback window (e.g. "last 3 days") silently drops any source
  change that lands *outside* that window — a record corrected five days
  late never gets picked up by the incremental job. This is why every
  incremental pipeline needs a periodic full-refresh reconciliation pass,
  not just the incremental job running forever unchecked.

State the choice explicitly in `refresh_backfill_state` even when the
answer is "full refresh, no incremental logic" — a pipeline with no stated
refresh strategy is indistinguishable, downstream, from one where the
question was never asked.

## Backfills and idempotency {#backfills-idempotency}

**Literature**: "functional data engineering" — Beauchemin's framing, the
dominant practitioner reference (not a formal academic term). Beauchemin,
"Functional Data Engineering — a modern paradigm for batch data
processing" —
https://maximebeauchemin.medium.com/functional-data-engineering-a-modern-paradigm-for-batch-data-processing-2327ec32c42a :
models a batch pipeline as a set of pure, idempotent tasks over immutable
partitions — a partition is the atomic unit of state, and a re-run of the
same task over the same partition with the same inputs always produces the
same output, achieved by always **overwriting the whole partition** rather
than issuing row-level UPDATE/DELETE/APPEND.

**Key failure mode**: idempotency is not automatic — it is a deliberate
design choice, and it breaks the moment a task does row-level appends or
upserts instead of whole-partition overwrites. A backfill re-run over a
partition that used row-level INSERT will double every row on the second
run; the same backfill using whole-partition overwrite is safe to re-run
any number of times.

**Design checklist** for a backfilled or reprocessed range: (1) is the unit
of reprocessing a whole partition, not a row range picked ad hoc; (2) does
re-running the same backfill twice, back to back, produce byte-identical
output; (3) is the write an overwrite of that partition, not an append.
Record the answer in `refresh_backfill_state` — an unstated idempotency
design is what the artifact gate (SKILL.md Gates) blocks on.

## Partitioning and storage formats {#partitioning-storage}

**Literature**: columnar storage. Melnik et al., "Dremel: Interactive
Analysis of Web-Scale Datasets," VLDB 2010 —
https://sfu-db.github.io/dbsystems/Lectures/Dremel.pdf : the record-
shredding/columnar-nested-data algorithm that Parquet (and similar formats)
implement — nested records are shredded into per-field columns so a query
touching a subset of fields reads only those columns.

**Key failure mode**: columnar format alone does not guarantee fast scans.
Partition pruning — skipping whole partitions a query can't match — only
works when the query's filter predicates align with the physical partition
key. A table partitioned by ingest date, queried by event date, prunes
nothing if the two diverge (late-arriving records land in a different
ingest-date partition than their event-date partition) — this is the same
failure surface the late-arriving-records subfield addresses from the
warehouse-modeling side (`warehouse-and-time.md#late-arriving`).

Choose the partition key from the query pattern the pipeline is actually
built to serve, not from whichever timestamp happens to be easiest to
write.
