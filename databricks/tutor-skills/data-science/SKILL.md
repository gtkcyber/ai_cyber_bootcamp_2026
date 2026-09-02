---
name: data-science
description: "Guidance for any data science, analytics, statistics, or machine learning task: exploratory analysis, model building/evaluation, experiment design, forecasting, clustering, anomaly detection, recommendation/ranking, NLP, vision, graph analysis, optimization/decisioning, causal inference, production ML/analytics…"
---

# data-science

Guidance for the data-science skill suite. Classify before acting.

## 1. Classify: three axes

- **Lifecycle phase** — where in scoping → gather → pipelines → data-models
  → profile → clean → labeling → features → model → evaluate → verify →
  stats → communicate → mlops → impact the task sits.
- **Method/goal family** — the modeling/analytics goal (supervised,
  unsupervised, timeseries, graph, text, geospatial, perception,
  deep-learning, ranking, llm-systems, analytics, optimize). Selection
  mechanics live per-family; cross-family concerns (explain, causal,
  simulation, uncertainty, entity-resolution, method-composition) compose
  alongside any family.
- **Domain overlay** — cyber / finance / healthcare / marketing, or none.

**Tie-break rule.** Lifecycle phase of the ask beats a method keyword in the
ask.

**Multi-family rule.** For multi-family tasks (spatiotemporal, temporal
graphs, multimodal fusion), the family owning the strongest leakage
constraint sets the split/validation scheme; other families contribute
features only. Confirm via each family skill's Edges (known pairings).

Never force-fit the nearest overlay; never skip domain reasoning.
