---
name: ds-optimize
description: "Optimization/decisioning method family: given a model of the world (predicted or simulated), choose the action that maximizes the objective under constraints. LP/IP, scheduling and routing, assignment/matching, queueing theory, optimal stopping, inventory/newsvendor, simulation-optimization, sequential decisions…"
---

# ds-optimize

Composes after a predictive or simulated model of the world exists
(`ds-model`, `ds-timeseries`, `ds-causal`, or `ds-simulation` has already
produced it) — this family turns that model into a chosen action, it does
not build the model. Full depth, citations, and failure modes:
`references/`; this file is protocol only.

## Subfields

- Canonical methods: simplex/interior-point (LP relaxation), branch-and-
  bound/branch-and-cut (IP). Edges: check the integrality gap before
  rounding a relaxation. See
  `references/ds-optimize.combinatorial-and-queueing.md#lp-ip`.
- Canonical methods: job-shop scheduling, vehicle routing (exact for small
  instances, heuristic beyond). Edges: state exact vs. heuristic and the
  accepted optimality gap. See
  `references/ds-optimize.combinatorial-and-queueing.md#scheduling-routing`.
- Canonical methods: Hungarian algorithm (balanced one-to-one);
  reformulation required for many-to-many/capacitated. Edges:
  record-identity matching ("is this the same real-world entity") is
  `ds-entity-resolution`'s, not this subfield's. See
  `references/ds-optimize.combinatorial-and-queueing.md#assignment-matching`.
- Canonical methods: M/M/1, M/M/c, Little's law. Edges: steady-state
  formulas don't cover a transient/bursty arrival regime. See
  `references/ds-optimize.combinatorial-and-queueing.md#queueing-theory`.
- Canonical methods: the classical 1/e stopping rule and its relaxations.
  Edges: the classical result requires fixed known N, random order,
  relative-rank-only, no recall — state which assumption the real decision
  relaxes. See `references/ds-optimize.combinatorial-and-queueing.md#optimal-stopping`.
- Canonical methods: critical-fractile solution (overage vs. underage cost).
  Edges: the whole demand distribution is the input, not its point forecast
  — see prediction→decision bridge. See
  `references/ds-optimize.combinatorial-and-queueing.md#inventory-newsvendor`.
- Canonical methods: replication-budgeted search loops. Edges:
  replication/sampling mechanics are `ds-simulation`'s; this subfield owns
  the search loop that consumes them. See
  `references/ds-optimize.sequential-and-decision-policies.md#simulation-optimization`.
- Canonical methods: regret-minimizing bandit algorithms. See
  `references/ds-optimize.sequential-and-decision-policies.md#sequential-decisions`.
- Canonical methods: simulated annealing, tabu search, evolutionary
  algorithms. Edges: no built-in optimality guarantee — validate against a
  bound or a smaller exact instance. See
  `references/ds-optimize.sequential-and-decision-policies.md#heuristics-metaheuristics`.
- Canonical methods: constrained-policy families per the stated risk
  formalization. See
  `references/ds-optimize.sequential-and-decision-policies.md#multi-action-constrained-policies`.
- **Prediction→decision bridge** — trigger: any subfield above consumes a
  predicted or simulated value as objective input. participation:
  `mandatory` (fires whenever this family composes at all). Canonical
  methods: Smart Predict-then-Optimize (decision-error training). Edges:
  this is a check, not an escalation path — it fires inline wherever a
  point estimate feeds an objective. See
  `references/ds-optimize.sequential-and-decision-policies.md#prediction-decision-bridge`.

## Selection tree

1. **Does a predicted or simulated value feed the objective?** Always
   check the **prediction→decision bridge** first, regardless of which
   subfield below fires alongside it.
2. **Repeated, with feedback per round?** → **sequential decisions**
   (bandit/RL framing); explore/exploit tradeoff, not a one-shot choice.
3. **One-shot decision — what shapes it?**
   - Linear/integer objective under stated constraints → **LP/IP**.
   - Pairing two sets under a cost/value matrix → **assignment/matching**.
   - A service system with arrivals and capacity → **queueing theory**.
   - Accept/reject now, no recall of a passed option → **optimal
     stopping**.
   - Stock/order quantity under uncertain demand → **inventory/
     newsvendor**.
   - Sequencing jobs or routing visits over time → **scheduling and
     routing**.
   - No closed-form objective, only simulatable → **simulation-
     optimization**.
4. **Is the one-shot problem NP-hard at the actual instance scale, with no
   exact solver finishing in budget?** → **heuristics/metaheuristics**,
   layered on top of whichever problem shape from step 3 applies.
5. **More than two actions, or more than one binding constraint (incl. a
   named risk metric)?** → **multi-action/constrained decision policies**;
   a single threshold under one cost function is not this family's — route
   to `ds-evaluate`.

## Family-specific pitfalls and evaluation

- **Deterministic optimization over point predictions** (signature
  pitfall): optimizing against a bare point estimate — a forecast, a
  reward estimate, a travel-time estimate — with no stated reason the
  point estimate suffices, silently drops the predicted quantity's
  uncertainty out of the decision. See prediction→decision bridge.
- **Heuristic solutions read as exact**: a converged metaheuristic or
  routing/scheduling heuristic run is not the same claim as an optimal
  solution; only a stated bound or a smaller-instance exact comparison
  closes that gap.
- **Distributional misspecification** (newsvendor, queueing): the
  solution is only as good as the assumed demand/arrival distribution,
  especially its tail — a distribution swapped for its mean silently
  degrades to a naive rule.
- **Bandit non-stationarity**: standard regret bounds assume a stationary
  reward distribution; reward drift breaks the guarantee and needs a
  drift-aware variant, stated explicitly.
- **Evaluation delta on `ds-evaluate`'s generic scorecard**: this family's
  output is scored by realized objective value (or simulated regret) under
  the actual imposed constraints — a model that wins on predictive
  accuracy is not thereby the best decision (prediction→decision bridge).
  When the objective's input is temporally-ordered (a forecast feeding
  inventory), the reported value follows `ds-timeseries`'s rolling-origin
  distribution, never a single backtest number.
