# Deployment mechanics

Depth and worked examples for the "how do I ship it" subfields. `SKILL.md`
carries the protocol form; this file carries the reasoning behind it.

## serving

Batch, online, and streaming are not points on one dial — they are distinct
consistency/latency contracts (Crankshaw et al., Clipper, NSDI 2017;
Baylor et al., TFX, KDD 2017):

- **Batch**: predictions computed on a schedule, read at request time from
  a materialized table. Staleness is bounded by the schedule interval, not
  by request latency. Cheapest, but wrong for anything needing a fresh
  input (a just-submitted form, a live session).
- **Online**: predictions computed per request, synchronously. Latency
  budget (p99, not just average) drives the whole architecture — feature
  lookups, model inference, and any downstream logging all compete for the
  same budget.
- **Streaming**: predictions computed over an unbounded, ordered feed with
  windowed or incremental state. Consistency semantics (at-least-once vs.
  exactly-once) determine whether a duplicate event double-counts into
  state — a correctness property, not a performance tuning knob.

**Worked example.** A fraud model needs a decision before checkout
completes (online, tight latency budget) but its risk-score *feature*
aggregates the last 30 days of activity (a streaming windowed feature,
computed continuously, read not recomputed at serving time). Two modes
coexist in one deployment; don't force one architecture to do both jobs.

**Four concerns, one stream.** `ds-gather` gets the stream *into* the
system; `ds-pipelines` transforms/orchestrates it once ingested;
`ds-features` owns what a windowed feature *means* (semantics,
cardinality, staleness); this skill owns the *compute* that turns a window
into a served value under a latency contract.

**Online-learning serving wrapper.** When a model updates from live
traffic, the *training* update rule belongs to
`ds-supervised`/`ds-deep-learning` — this skill owns only how the running
update is exposed to serving (buffering, apply cadence, rollback of a bad
online update). Never re-derive the update rule here.

## registry

Sculley et al. (2015) frame ML technical debt as entanglement and
undeclared consumers — a model silently depended on by five downstream
systems that nobody tracked. A registry is the mitigation: every deployed
artifact is versioned as a **triple** — model weights, the data version
that produced them, and the config/code version that trained them — pinned
together, not independently. **Worked**: a team ships model v12 (retrained
weekly) but the feature-computation config lags a week behind on a
separate deploy schedule — v12's weights trained against config v11's
features. Nothing crashes; predictions are just quietly wrong. Versioning
weights alone would have looked "current."

## feature-stores

The hard problem is **point-in-time-correct joins**: at training time, a
feature value must reflect only what was knowable as of the label's
timestamp; at serving time, the same feature computation must be available
online with acceptable latency. A feature store's storage layer (Michelangelo,
Feast) is the easy 80% — the point-in-time join logic and batch/online
parity are the 20% that determines whether the store actually prevents
leakage or just relocates it. This subfield owns the serving-side store
(materialization, online/offline consistency, staleness contracts).
Feature *definitions* — meaning, provenance class, window semantics — are
`ds-features`'; a store with no upstream semantic dictionary entry is
storage with nothing trustworthy in it.

## skew

Zinkevich's Rule of ML dedicates a section to training-serving skew because
it manifests as three different bugs that look identical from the outside
(a serving-time metric quietly diverging from the offline eval number):

1. **Feature-computation discrepancy** — offline and online paths compute
   "the same" feature differently (join order, rounding, library version).
   Fix: shared feature code/config, not two implementations "kept in sync."
2. **Time-based drift** — the world changed since training; nothing is
   miscomputed, the input distribution moved. Fix: monitoring + retraining.
3. **Feedback loops** — the model's own predictions change what data
   arrives next (a ranker that suppresses low-scored items starves itself
   of feedback on them). Fix: exploration/logging design.

Parity testing (running the same input through both paths and diffing
output) catches (1) only — "parity test passed, so skew is resolved" is a
common wrong inference.

## rollout

Shadow deployment: the new version receives a copy of live traffic, its
predictions logged but never acted on. Canary: the new version receives a
small, real, acted-upon percentage of traffic, ramped on healthy signal.

**Worked**: a new ranking model is shadow-deployed; its predicted order is
logged. CTR is only observable for items actually shown in that order —
shadow never puts the new ordering in front of users, so its own outcome
metric can't be measured there. Canary is required once the outcome
depends on the model's own action, not just its prediction being logged.

Rollback criteria (a regression threshold on the monitored metric,
`references/ds-mlops.monitoring-and-retraining.md`) are decided *before* rollout starts, never
improvised after a canary looks bad.

## cicd

CD4ML (Sato, Wider, Windheuser, 2019) extends continuous delivery across
three axes that must move together: **data**, **model**, and **code**.
Versioning/testing code alone while model and data ship on a separate,
undisciplined cadence is not CD4ML — it's CI for the part that was already
easiest to test. Its eight components (reproducibility, data/model
versioning, automated testing per axis, deployment automation, quality/
fairness gates, monitoring, governance) are a checklist for whether a
pipeline claiming "CI/CD" covers the axis that usually breaks production.

## compression

Deep Compression's three-stage pipeline — prune (remove low-magnitude
weights) → quantize (reduce weight precision) → Huffman-encode (compress
the quantized representation) — addresses three *different* bottlenecks:
prune reduces compute/FLOPs, quantize reduces memory footprint and often
latency, Huffman reduces storage/transfer size. Stacking them compounds
the reduction; treating any one as a complete substitute for the others
under-delivers on whichever bottleneck it doesn't address. **Worked**: a
team prunes 40% of weights and ships without fine-tuning afterward —
accuracy collapses because pruning removed weights the network hadn't
adapted to compensate for. The fix is fine-tune (or quantization-aware
training, QAT) after pruning, every time, not an optional follow-up.

## federated

FedAvg (McMahan et al., 2017) trains a shared model by averaging locally
computed updates without centralizing raw client data — a data-locality
guarantee, not a privacy guarantee: updates themselves can leak
information about the data that produced them (gradient inversion). Secure
aggregation (Bonawitz et al., 2017) is the additional cryptographic layer
that prevents the aggregator from seeing any individual update, only the
sum — a separate mechanism, never implied by "federated" alone.

State which is actually deployed: FedAvg only (data locality, no
individual-update privacy), or FedAvg + secure aggregation (both). Local
optimization/communication-round mechanics are `ds-deep-learning`'s; this
subfield owns the architecture decision — whether to federate at all, and
whether to add the aggregation layer.
