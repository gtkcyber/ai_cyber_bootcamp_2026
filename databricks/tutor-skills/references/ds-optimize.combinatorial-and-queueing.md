# Combinatorial and queueing decision problems

Full depth and citations for LP/IP, scheduling-and-routing,
assignment/matching, queueing theory, optimal stopping, and
inventory/newsvendor. `SKILL.md` states triggers and dispatch fields only;
this file carries the method detail. Domain-general and stack-agnostic per
spec — examples stay grocery-line/interview-stopping generic, never tied to
one stack.

## LP/IP {#lp-ip}

**Literature name**: linear programming / integer programming.

**Canonical methods**: simplex and interior-point methods for the LP
relaxation; branch-and-bound, branch-and-cut, cutting-plane methods for the
integer program.

**Source**: MIT OpenCourseWare, 15.053 "Optimization Methods in Management
Science," Lecture 1 (Prof. James Orlin) —
https://ocw.mit.edu/courses/15-053-optimization-methods-in-management-science-spring-2013/resources/mit15_053s13_lec1/.
Supplement: "Linear programming" —
https://en.wikipedia.org/wiki/Linear_programming (confirms the
simplex-method framing).

**Failure mode**: the LP relaxation of an integer program is not generally
tight — rounding a fractional relaxation solution to integers is not
guaranteed feasible or near-optimal. The integrality gap must be checked on
the actual instance, never assumed small by default.

## Scheduling and routing {#scheduling-routing}

**Literature name**: job-shop scheduling / vehicle routing.

**LITERATURE-THIN direct-fetch note**: Graham et al.'s scheduling survey
and Toth & Vigo's vehicle-routing survey are the field's standard
references by name; every hosted-PDF mirror fetched 404'd.

**Canonical methods/refs**: "Job-shop scheduling" —
https://en.wikipedia.org/wiki/Job_shop_scheduling ; "Vehicle routing
problem" — https://en.wikipedia.org/wiki/Vehicle_routing_problem.

**Failure mode**: both problem classes are NP-hard in general — exact
solvers don't scale past modest instance sizes, so practice relies on
heuristics/metaheuristics (`#heuristics-metaheuristics`). A
scheduling/routing solution must state whether it's exact or heuristic and
what optimality gap it accepts; an unqualified "optimal schedule" claim on
a nontrivial instance is almost always a heuristic result mislabeled.

## Assignment/matching {#assignment-matching}

**Literature name**: the assignment problem.

**LITERATURE-THIN direct-fetch note**: Kuhn, "The Hungarian Method for the
Assignment Problem," Naval Research Logistics 2(1), 1955, is the
originating paper; every hosted-PDF candidate fetched 404'd.

**Canonical methods/refs**: "Hungarian algorithm" —
https://en.wikipedia.org/wiki/Hungarian_algorithm : the polynomial-time
solution to the balanced, one-to-one linear assignment problem.

**Failure mode**: the classic algorithm doesn't directly extend to
many-to-many or capacitated matching without reformulation. The cost
matrix must be complete and finite — a missing entry needs an explicit
large-cost sentinel, not silent omission (silent omission reads as a free
match). Record/identity-level matching (who is the same real-world entity)
is a different problem — `ds-entity-resolution`'s, not this subfield's; see
`SKILL.md` Edges.

## Queueing theory {#queueing-theory}

**Literature name**: queueing theory.

**Canonical methods/refs**: "Queueing theory" —
https://en.wikipedia.org/wiki/Queueing_theory. Kleinrock's *Queueing
Systems* is the standard academic textbook but is not freely hosted; this
fetched entry corroborates the field's core results (M/M/1, M/M/c,
Little's law).

**Failure mode**: classical closed-form results (e.g. M/M/1) assume
Markovian, steady-state arrival/service processes. Real arrival processes
are often bursty/non-stationary (a lunch-rush grocery line, a diurnal
support-ticket queue), and transient (non-steady-state) behavior is a
materially different, harder problem than the steady-state formulas cover
— a steady-state sizing number reported during a transient period
understates the queue the system actually experiences.

## Optimal stopping {#optimal-stopping}

**Literature name**: optimal stopping theory — the secretary/interview
problem is its canonical worked case.

**Canonical methods/refs**: Ferguson, *Optimal Stopping and Applications*
— https://www.math.ucla.edu/~tom/Stopping/Contents.html (free online
textbook, UCLA), Ch. 2 "The Classical Secretary Problem."

**Failure mode**: the classical secretary-problem result (the 1/e stopping
rule) holds under specific assumptions — fixed known N, random arrival
order, only relative rank observable, no recall of rejected candidates.
Relaxing any one assumption (unknown N, ability to recall a passed-over
candidate, an absolute quality signal available rather than just relative
rank) changes the optimal rule; the classical 1/e result does not transfer
directly to a messier real "when do we stop looking and commit" decision
without re-deriving it against the actual assumptions in play.

## Inventory/newsvendor {#inventory-newsvendor}

**Literature name**: the newsvendor model (single-period stochastic
inventory).

**LITERATURE-THIN direct-fetch note**: Arrow, Harris, Marschak, "Optimal
Inventory Policy," Econometrica 19(3), 1951, is the originating paper;
JSTOR's bot-wall blocked fetch confirmation.

**Canonical methods/refs**: "Newsvendor model" —
https://en.wikipedia.org/wiki/Newsvendor_model : the critical-fractile
solution balancing overage cost against underage cost.

**Failure mode**: the model assumes a known demand distribution and
single-period, no-replenishment dynamics. Misspecifying the demand
distribution — especially its tail — directly biases the optimal order
quantity; a point demand forecast plugged in as if it were the whole
distribution silently drops the critical-fractile calculation back to a
naive rule (see `SKILL.md`'s prediction→decision bridge gate). Multi-period
replenishment dynamics are a different, harder model class than this
subfield's single-period case.
