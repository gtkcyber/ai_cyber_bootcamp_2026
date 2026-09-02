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

- **LP/IP** — trigger: "maximize/minimize subject to linear constraints,"
  resource allocation with a linear or integer objective. participation:
  `conditional-on-data:resource-allocation-with-linear-constraints`.
  Canonical methods: simplex/interior-point (LP relaxation), branch-and-
  bound/branch-and-cut (IP). Edges: check the integrality gap before
  rounding a relaxation. See `references/combinatorial-and-queueing.md#lp-ip`.
- **Scheduling and routing** — trigger: "sequence/assign jobs to
  resources over time" or "route vehicles/visits." participation:
  `conditional-on-data:scheduling-or-routing-problem`. Canonical methods:
  job-shop scheduling, vehicle routing (exact for small instances,
  heuristic beyond). Edges: state exact vs. heuristic and the accepted
  optimality gap. See
  `references/combinatorial-and-queueing.md#scheduling-routing`.
- **Assignment/matching** — trigger: one-to-one (or many-to-many) pairing
  of two sets under a cost/value matrix. participation:
  `conditional-on-data:one-to-one-or-many-to-many-matching`. Canonical
  methods: Hungarian algorithm (balanced one-to-one); reformulation
  required for many-to-many/capacitated. Edges: record-identity matching
  ("is this the same real-world entity") is `ds-entity-resolution`'s, not
  this subfield's. See
  `references/combinatorial-and-queueing.md#assignment-matching`.
- **Queueing theory** — trigger: sizing/predicting behavior of a service
  system with arrivals, servers, and capacity. participation:
  `conditional-on-data:service-system-with-arrivals-and-capacity`.
  Canonical methods: M/M/1, M/M/c, Little's law. Edges: steady-state
  formulas don't cover a transient/bursty arrival regime. See
  `references/combinatorial-and-queueing.md#queueing-theory`.
- **Optimal stopping** — trigger: a sequential accept/reject decision with
  no recall of a passed-over option (interview/secretary-shaped).
  participation: `conditional-on-data:sequential-accept-reject-decision`.
  Canonical methods: the classical 1/e stopping rule and its relaxations.
  Edges: the classical result requires fixed known N, random order,
  relative-rank-only, no recall — state which assumption the real decision
  relaxes. See `references/combinatorial-and-queueing.md#optimal-stopping`.
- **Inventory/newsvendor** — trigger: a single-period stock/order-quantity
  decision under uncertain demand. participation:
  `conditional-on-data:stock-decision-under-uncertain-demand`. Canonical
  methods: critical-fractile solution (overage vs. underage cost). Edges:
  the whole demand distribution is the input, not its point forecast — see
  prediction→decision bridge. See
  `references/combinatorial-and-queueing.md#inventory-newsvendor`.
- **Simulation-optimization** — trigger: the objective has no closed form
  and is only evaluable by running a simulation. participation:
  `conditional-on-data:objective-only-evaluable-by-simulation`. Canonical
  methods: replication-budgeted search loops. Edges: replication/sampling
  mechanics are `ds-simulation`'s; this subfield owns the search loop that
  consumes them. See
  `references/sequential-and-decision-policies.md#simulation-optimization`.
- **Sequential decisions (bandit/RL framing)** — trigger: repeated action
  selection with feedback per round, an explore/exploit tradeoff.
  participation:
  `conditional-on-data:repeated-action-selection-with-feedback`. Canonical
  methods: regret-minimizing bandit algorithms. See
  `references/sequential-and-decision-policies.md#sequential-decisions`.
- **Heuristics/metaheuristics** — trigger: the problem is NP-hard at the
  actual instance scale and no exact solver finishes in budget.
  participation:
  `conditional-on-data:np-hard-combinatorial-no-exact-solver-at-scale`.
  Canonical methods: simulated annealing, tabu search, evolutionary
  algorithms. Edges: no built-in optimality guarantee — validate against a
  bound or a smaller exact instance. See
  `references/sequential-and-decision-policies.md#heuristics-metaheuristics`.
- **Multi-action/constrained decision policies** — trigger: more than two
  actions, or multiple simultaneous constraints (incl. a stated risk/safety
  metric). participation:
  `conditional-on-data:multiple-actions-or-constraints`. Canonical methods:
  constrained-policy families per the stated risk formalization. See
  `references/sequential-and-decision-policies.md#multi-action-constrained-policies`.
- **Prediction→decision bridge** — trigger: any subfield above consumes a
  predicted or simulated value as objective input. participation:
  `mandatory` (fires whenever this family composes at all). Canonical
  methods: Smart Predict-then-Optimize (decision-error training). Edges:
  this is a check, not an escalation path — it fires inline wherever a
  point estimate feeds an objective. See
  `references/sequential-and-decision-policies.md#prediction-decision-bridge`.

|---|---|---|---|
| LP/IP | analysis | no | conditional-on-data:resource-allocation-with-linear-constraints |
| Scheduling and routing | analysis | no | conditional-on-data:scheduling-or-routing-problem |
| Assignment/matching | quick-answer | no | conditional-on-data:one-to-one-or-many-to-many-matching |
| Queueing theory | quick-answer | no | conditional-on-data:service-system-with-arrivals-and-capacity |
| Optimal stopping | quick-answer | no | conditional-on-data:sequential-accept-reject-decision |
| Inventory/newsvendor | analysis | no | conditional-on-data:stock-decision-under-uncertain-demand |
| Simulation-optimization | analysis | no | conditional-on-data:objective-only-evaluable-by-simulation |
| Sequential decisions (bandit/RL) | analysis | yes, re-entrant when the exploration policy updates | conditional-on-data:repeated-action-selection-with-feedback |
| Heuristics/metaheuristics | analysis | no | conditional-on-data:np-hard-combinatorial-no-exact-solver-at-scale |
| Multi-action/constrained policies | analysis | no | conditional-on-data:multiple-actions-or-constraints |
| Prediction→decision bridge | quick-answer | yes, always-composed wherever a prediction/simulation feeds this family's objective | `mandatory` |

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

## Gates

- Every objective consuming a predicted or simulated input states whether
  that input's uncertainty (interval, distribution, or an explicit
  point-estimate-suffices rationale) was carried into the objective —
  unqualified deterministic optimization over a point estimate fails this
  gate (prediction→decision bridge).
- Every heuristic/metaheuristic solution states its optimality gap or a
  smaller-instance exact-solver comparison — an unqualified "near-optimal"
  claim fails.
- Every reported bandit/sequential-decision regret number states the
  stationarity assumption and whether the actual reward stream satisfies
  it.
- Fit-on-train-only (`ds-features` ownership) applies to any surrogate or
  predictive model this family fits as objective input (a demand model
  feeding newsvendor, a reward model feeding a bandit policy) — not to the
  optimization step itself, which has no train/test split of its own.
- Doctrine gates this family triggers, linked not restated: leakage
  (`doctrine-leakage.md` — chiefly via whatever upstream model supplied the
  objective input), provenance/additivity, scale/cost per router doctrine.

## Edges

Covered: the eleven subfields above.

Not covered: deep-RL architecture and training mechanics once a neural
policy is chosen — outside this family's cited coverage; research external
sources, verify the found method's stationarity/reward assumptions against
the actual data, and report provenance before adopting one, then hand
training mechanics to `ds-deep-learning`. Observational/quasi-experimental
identification and uplift is `ds-causal`'s (see Pairings below — this family
consumes a causal estimate as its prediction→decision bridge input, it does
not identify the effect itself). Off-policy logged-feedback correction and
its metrics are `ds-ranking`'s application (identification method:
`ds-causal`) — pointer only. Production serving of a deployed policy
(assignment service, monitoring) is `ds-mlops`' — pointer only.

Paired with `ds-timeseries` on a temporally-ordered forecast feeding an
inventory/newsvendor or queueing decision, `ds-timeseries` owns the
strongest constraint and leads (rolling-origin evaluation with an
embargo/purge gap, per its own Edges section) — this family's decision layer
consumes that forecast's output and never recomputes an independent split on
the same temporally-ordered data.
