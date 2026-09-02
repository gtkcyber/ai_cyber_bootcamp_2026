# Sequential search and decision-policy problems

Full depth and citations for simulation-optimization, sequential decisions
(bandit/RL problem framing), heuristics/metaheuristics,
multi-action/constrained decision policies, and the prediction→decision
bridge. `SKILL.md` states triggers and dispatch fields only; this file
carries the method detail.

## Simulation-optimization {#simulation-optimization}

**Literature name**: simulation-optimization.

**Canonical methods/refs**: Fu, simulation-optimization tutorial, Winter
Simulation Conference 2002 —
https://www.informs-sim.org/wsc02papers/003.pdf.

**Failure mode**: simulation-optimization budgets compute across two
competing needs — simulation replications (accurate objective estimates at
one candidate point) and search iterations (exploring the decision space
across candidate points). Under-replicating gives noisy objective estimates
that mislead the search toward spurious local optima that look better than
they are purely from estimation noise. Replication mechanics themselves
(Monte Carlo, bootstrapping) are `ds-simulation`'s territory — this
subfield owns the search loop that consumes them, not the sampling
mechanics; state which side of that split a given task needs before
building a custom loop.

## Sequential decisions (bandit/RL problem framing) {#sequential-decisions}

**Literature name**: multi-armed bandit problems; sequential
decision-making under uncertainty.

**Canonical methods/refs**: Bubeck & Cesa-Bianchi, "Regret Analysis of
Stochastic and Nonstochastic Multi-Armed Bandit Problems," Foundations and
Trends in Machine Learning, 2012 — https://arxiv.org/abs/1204.5721.

**Failure mode**: standard regret bounds are typically asymptotic/
worst-case and assume a stationary reward distribution — non-stationary
environments (reward drift, e.g. a promotion changing conversion rates
mid-experiment) break standard bandit regret guarantees and require
drift-aware variants. Training a deep network as the policy function is
`ds-deep-learning`'s training mechanics; this subfield stops at the
algorithm/framing choice (see `SKILL.md` Edges — deep-RL architecture
research is out of coverage).

## Heuristics/metaheuristics {#heuristics-metaheuristics}

**Literature name**: metaheuristics for combinatorial optimization.

**LITERATURE-THIN direct-fetch note**: Blum & Roli, "Metaheuristics in
Combinatorial Optimization: Overview and Conceptual Comparison," ACM
Computing Surveys 35(3), 2003, is the field's standard survey; every
hosted-PDF mirror fetched 404'd.

**Canonical methods/refs**: "Metaheuristic" —
https://en.wikipedia.org/wiki/Metaheuristic (simulated annealing, tabu
search, evolutionary algorithms as the named families).

**Failure mode**: metaheuristics give no optimality guarantee by
construction — solution quality must be validated empirically against a
known bound or an exact solver's result on a smaller instance of the same
problem, never assumed close to optimal just because the search converged.
A converged metaheuristic run and an optimal solution are not the same
claim; only the smaller-instance benchmark or a bound closes that gap.

## Multi-action/constrained decision policies {#multi-action-constrained-policies}

**Literature name**: constrained/safe decision policies.

**Canonical methods/refs**: García & Fernández, "A Comprehensive Survey on
Safe Reinforcement Learning," JMLR 16(42), 2015 —
https://www.jmlr.org/papers/v16/garcia15a.html : two families — modifying
the optimality criterion with a safety factor, or modifying exploration via
external knowledge or a risk metric.

**Failure mode**: "safe" / "constrained" is defined relative to the chosen
risk formalization — a policy that is safe under one risk metric (e.g.
expected constraint violation) can still have unsafe tail behavior under a
different one (e.g. worst-case violation).

## Prediction→decision bridge {#prediction-decision-bridge}

**Literature name**: Smart "Predict, then Optimize" (SPO).

**Canonical methods/refs**: Elmachtoub & Grigas, "Smart 'Predict, then
Optimize'," 2017/2022 — https://arxiv.org/abs/1710.08005 : trains
prediction models against downstream decision error (SPO loss) rather than
prediction error alone.

**Failure mode**: the standard predict-then-optimize paradigm does not
account for how predictions are used downstream — a model that wins on
prediction-error benchmarks is not guaranteed to yield the best decision
("best model ≠ best decision," the spec's own framing). This is the
signature check for every subfield above: whenever a predicted or
simulated value feeds an objective (a demand forecast into newsvendor, a
reward estimate into a bandit policy, a travel-time estimate into
routing), the prediction's uncertainty must be carried into the objective
— deterministic optimization over a bare point estimate, with no stated
reason the point estimate suffices, is the named pitfall (see `SKILL.md`
Gates).
