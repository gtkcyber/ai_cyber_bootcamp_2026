---
name: ds-mlops
description: "Production track for models and analytics: serving architecture (batch/online/streaming), model registry/versioning, feature stores, training-serving skew, progressive rollout and rollback, CI/CD, edge compression, production monitoring (performance/schema/coverage/provenance drift), retraining triggers, federated…"
---

# ds-mlops

Fixed lifecycle position, immediately before `ds-impact` and after
`ds-communicate` (`manifest.json`'s lifecycle list). Full depth, worked
examples, and citations live in `references/`. This file is protocol only.

## Subfields

- **Serving (batch/online/streaming)** — trigger: predictions run on a
  cadence (batch), per-request (online), or over an unbounded feed
  (streaming) — distinct latency/consistency contracts, never
  interchangeable. Crankshaw et al., "Clipper," NSDI 2017 —
  https://www.usenix.org/system/files/conference/nsdi17/nsdi17-crankshaw.pdf;
  Baylor et al., "TFX," KDD 2017 —
  https://research.google/pubs/tfx-a-tensorflow-based-production-scale-machine-learning-platform/.
  See `references/deployment-mechanics.md#serving`.
- **Model registry and versioning** — LITERATURE-THIN, no seminal paper.
  Sculley et al., "Hidden Technical Debt in ML Systems," NeurIPS 2015 —
  https://research.google/pubs/hidden-technical-debt-in-machine-learning-systems/ :
  pin weights + data version + config/code version together — versioning
  the artifact alone while data/config drift silently is the named failure.
  Registers `ds-model`'s model-card iterations (`model.model_card`,
  pointer, never re-derived). See `references/deployment-mechanics.md#registry`.
- **Feature stores** — trigger: features must compute once and serve
  consistently to training and serving paths. Uber, "Meet Michelangelo" —
  https://www.uber.com/us/en/blog/michelangelo-machine-learning-platform/;
  "Introducing Feast" —
  https://cloud.google.com/blog/products/ai-machine-learning/introducing-feast-an-open-source-feature-store-for-machine-learning.
  Point-in-time-correct joins and batch/online consistency are the hard
  problem. Feature *semantics* stay `ds-features`'; this owns only the
  serving-side store. See `references/deployment-mechanics.md#feature-stores`.
- **Training-serving skew / parity testing** — trigger: online predictions
  diverge from offline evaluation. Zinkevich, "Rules of Machine Learning" —
  https://developers.google.com/machine-learning/guides/rules-of-ml.
  Distinguish feature-computation discrepancy, time-based drift, and
  feedback loops — conflating them produces the wrong fix. See
  `references/deployment-mechanics.md#skew`.
- **Progressive rollout (shadow, canary) and rollback** — trigger: a new
  version replaces one already serving traffic. "Shadow deployment vs.
  canary release of ML models" —
  https://www.qwak.com/post/shadow-deployment-vs-canary-release-of-machine-learning-models :
  shadow → staged-traffic canary → full rollout, rollback on regression.
  Shadow can't validate outcomes dependent on the model's own action (e.g.
  CTR) — canary is required there. See `references/deployment-mechanics.md#rollout`.
- **CI/CD** — trigger: how model/pipeline changes ship safely and
  repeatably. Sato, Wider, Windheuser, "Continuous Delivery for Machine
  Learning," ThoughtWorks 2019 — https://martinfowler.com/articles/cd4ml.html :
  CD4ML, 8 components across data/model/code axes; CI on code alone while
  model/data ship out-of-band isn't CD4ML. See `references/deployment-mechanics.md#cicd`.
- **Model compression for edge** — trigger: a footprint/latency constraint
  rules out the full-size model. Han, Mao, Dally, "Deep Compression," ICLR
  2016 — https://arxiv.org/abs/1510.00149 : prune→quantize→Huffman stack,
  they don't substitute; skipping fine-tuning/QAT after pruning collapses
  accuracy. See `references/deployment-mechanics.md#compression`.
- **Monitoring — performance, schema/contract, coverage, provenance drift**
  — trigger: a model/analytic artifact is serving. Caveness, Zinkevich,
  Polyzotis et al., "TensorFlow Data Validation," SIGMOD 2020 —
  https://research.google/pubs/pub48974/ : schema/input-data validation at
  scale (that paper's actual scope). Practice corollary, not TFDV's claim:
  concept drift (input-label relationship) is a separate failure class
  needing outcome data — a monitor covering only schema misses it.
  Coverage/population-statement drift (collector-config change, no schema
  break) and provenance drift (upstream source changes its assertion method)
  are LITERATURE-THIN — same TFX anchor, practice guidance for these two
  dimensions. Adversarial/ intentional drift is domain-overlay delta —
  general form only, here. See
  `references/monitoring-and-retraining.md#monitoring`.
- **Retraining triggers** — LITERATURE-THIN. Pham et al., "Time to
  Retrain? Detecting Concept Drifts in ML Systems," 2024 —
  https://arxiv.org/abs/2410.09190 : blind (scheduled) vs. informed
  (statistical/performance-threshold); an informed trigger needs a working
  delayed-label feedback loop or it's a blind trigger in disguise.
  Quantitative values read `ds-evaluate`'s `scorecard` thresholds (pointer,
  never restated) and must pass a tier-scaled `ds-verify` before firing.
  See `references/monitoring-and-retraining.md#retraining`.
- **Federated learning and secure aggregation** — trigger: training/serving
  must not centralize raw client data. McMahan et al., "Communication-
  Efficient Learning of Deep Networks from Decentralized Data," AISTATS
  2017 — https://arxiv.org/abs/1602.05629; Bonawitz et al., "Practical
  Secure Aggregation for Federated Learning," ACM CCS 2017 —
  https://arxiv.org/abs/1611.04482. FedAvg alone gives no privacy
  guarantee; secure aggregation is a separate layer and doesn't prevent
  gradient-inversion on individual updates. Owns deployment/training
  *architecture*; training mechanics stay `ds-deep-learning`'s. See
  `references/deployment-mechanics.md#federated`.
- **Non-model production analytics** — LITERATURE-THIN, practitioner-only
  by design. Stancil, "The missing piece of the modern data stack," 2021 —
  https://benn.substack.com/p/metrics-layer : the metrics-layer only solves
  the problem if it's the single computation point for every consumer —
  letting any tool recompute locally reproduces the drift it's meant to
  prevent. Covers metric-definition versioning, recurring-report
  freshness/reconciliation, dashboard contract monitoring. See
  `references/monitoring-and-retraining.md#non-model-analytics`.

| Subfield | Participation |
|---|---|
| Serving | mandatory |
| Model registry and versioning | mandatory |
| Monitoring | mandatory |
| Feature stores | conditional-on-data:feature-store-backed |
| Training-serving skew / parity testing | conditional-on-data:parity-check-required |
| Progressive rollout and rollback | conditional-on-data:version-replacing-traffic |
| CI/CD | conditional-on-data:automated-pipeline |
| Model compression for edge | conditional-on-data:edge-footprint-constraint |
| Retraining triggers | conditional-on-data:informed-retraining |
| Federated learning and secure aggregation | conditional-on-data:federated-deployment |
| Non-model production analytics | conditional-on-data:non-model-artifact |

`mandatory`: fires whenever `ds-mlops` composes at all — every production
deployment needs a serving decision, a registered/versioned artifact, and
an ongoing monitoring spec; the other eight fire only on their own trigger.

## Gates

- Monitoring's drift coverage cites the specific `ds-clean` `assertion_suite`
  entries it was seeded from, or the gate fails.
- A feed-version bump re-triggers `ds-data-models`' Validate before the
  monitoring spec is current for that feed — a spec carrying a stale schema
  assumption fails this gate.
- Retraining triggers state blind vs. informed; informed with no named
  delayed-label feedback loop fails. Quantitative values cite `ds-evaluate`'s
  `scorecard` thresholds, never restate a number independently.
- A compression claim names its bottleneck (footprint/latency/cost) and
  states whether fine-tuning/QAT ran after pruning — no post-compression
  accuracy check fails this gate.
- A federated claim states its privacy mechanism precisely ("aggregation
  only" vs. "+ secure aggregation") — "federated, therefore private" with
  no named mechanism fails.

## Edges

Covered: serving architecture selection, registry/versioning, feature
stores (serving side), training-serving skew/parity testing, progressive
rollout/rollback, CI/CD, edge compression (when/why), production
monitoring across performance/schema/coverage/provenance drift, retraining
triggers, federated learning/secure aggregation (architecture), non-model
production analytics.

Not covered, pointer only: distillation training mechanics
(`ds-deep-learning`); feature *semantics* (`ds-features`); development-time
dataset-shift diagnosis (`ds-evaluate`) and detection mechanics
(`ds-timeseries`); model-card content and selection rationale (`ds-model`);
adversarial/intentional drift framing (domain-overlay delta); anomaly
framings outside production monitoring — error-outliers (`ds-clean`),
anomaly-as-the-task (`ds-unsupervised`), temporal/contextual mechanics
(`ds-timeseries`).

| Signal | Edge |
|---|---|
| Model performance degrades in production | `drift → profile` — fires the same row `ds-evaluate`'s development-time diagnosis fires |
| A specific feature's distribution shifts | `mlops-drift → features`, entry-scoped (`status: stale-scoped`, affected entries only) |
| Coverage/population-statement or provenance drift invalidates the framing | `monitoring → scoping` |
| Serving constraints (latency, footprint, cost) rule out the deployed model class | `mlops serving constraints → model selection` |
| Analyst dispositions or user corrections arrive from production | `production-feedback → labeling` |

## Audit mode

Input: an existing external deployment/monitoring artifact authored outside
this skill (a platform's deployment config, an existing dashboard/alerting
setup, a model registry's own records). An undocumented deployment claim is
treated as an unregistered field under Gates: flagged, never assumed
compliant.

## Production considerations

This skill *is* the suite's production-delta layer — every other lifecycle
skill's "Production considerations" section points here rather than
restating deployment/monitoring concerns; this section states this skill's
own remaining pointers instead of deferring further. Serving/retraining
cost economics read `doctrine-scale-cost.md`'s threshold, recorded once in
`ds-scoping`'s kill-check and never restated here. `ds-data-models`'
Production considerations names this skill as the destination for
feed-version-bump monitoring (mirrored above, under Monitoring) — the
pointer is reciprocal, not duplicated content.
