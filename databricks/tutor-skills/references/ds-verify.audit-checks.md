# Magnitude, fan-out, alternative-explanation, and falsifiability checks

Depth for `ds-verify`'s four non-reproduction subfields — all tier-floored
at analysis, all bound-checks rather than proofs. SKILL.md carries the
protocol; this file carries worked detail and full citations.

## Magnitude/sanity checks {#magnitude}

**LITERATURE-THIN** for a data-science-specific standard — no
peer-reviewed source establishes this as a formal DS practice. Nearest:
"Fermi problem" — https://en.wikipedia.org/wiki/Fermi_problem — the
**Fermi estimate** tradition: bound a quantity by decomposing it into
factors each independently estimable to within an order of magnitude, then
multiplying. Treat this as practice protocol borrowed from general
pedagogy, never cite it as settled data-science literature.

Applied here: before accepting a headline number, show a decomposition
that bounds it independently of the pipeline that produced it — e.g. "we
have ~500K customers, a plausible churn rate is 2–8%/month, so 10K–40K
churned events/month is the sane range" — computed from separately known
facts, not derived from the same query being checked. A number the
decomposition can't bound within roughly an order of magnitude either gets
explained (a real reason the base rate is unusual) or blocks the gate. This
is a bound-check only: passing it does not prove the number correct, only
that it isn't obviously wrong; a number that passes the bound-check can
still fail reproduction.

## Join fan-out, denominator, attrition, double-filter audit {#fan-out}

No single umbrella term in the literature. Two components:

- **Fan trap/fan-out** (relational modeling terminology). The primary
  academic/textbook source (Connolly & Begg) could not be independently
  fetched for this brief and is not cited directly; the mechanism is
  confirmed via a practitioner source instead — Holistics Docs, "Cannot
  combine fields due to fan-out issues?" —
  https://docs.holistics.io/docs/faqs/fan-out-issue — a one-to-many join
  duplicates every row on the "one" side once per matching row on the
  "many" side, silently inflating any aggregate computed after the join
  (SUM, COUNT) unless the aggregate was computed *before* the join or the
  duplication is explicitly deduplicated after.
- **Survivorship/attrition bias** (funnel-analysis literature, no single
  canonical citation in the brief). A funnel with a shrinking denominator
  at each stage, paired with an *improving* per-stage rate, is the classic
  signature: the population getting smaller isn't random, it's
  systematically excluding the cases that would have failed the metric.

**The audit**: for every join and filter in the chain that produced the
claim, record row counts immediately before and immediately after that
step. A chain audited only at its start and end (not per-step) cannot
distinguish "the whole pipeline lost 40% of rows for a good reason" from
"one silent fan-out inflated one intermediate count, masked by a filter
that happened to bring the total back down" — record per-step, not just
start/end. This is the fuller audit that `ds-gather`'s join gate (same-
semantics + lightweight pre-join cardinality check) feeds into, not
duplicates — the join gate runs *before* a join executes and checks
expected cardinality; this audit runs *after*, on the actually observed
row counts, at every join or filter site in the realized chain.

## Alternative-explanation survival {#alt-explanation}

**Literature term**: **threats to validity** (internal validity),
Campbell & Stanley tradition, confirmed via citation in "A Simulation
Study of Threats to Validity in Quasi-Experimental Designs" —
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4910671/ — which taxonomizes
threats across four validity types (internal, external, construct,
statistical-conclusion) and, within internal validity, names history,
maturation, testing, instrumentation, statistical regression, selection,
and mortality (differential attrition) as the classic threats.

Applied here: for a claim that implies "X caused Y" or "X explains Y" —
not just "X happened" — name the specific threat a rival explanation would
invoke (e.g. "selection: the treated group differs systematically from
the comparison group on an unmeasured trait" — not "there might be
confounders somewhere"). A vague acknowledgment that fails to name a
concrete threat does not pass this check. This subfield does not require
(or claim) RCT-grade internal validity for observational analysis — it
requires naming which threats were considered and why they don't explain
the result away.

## Falsifiability {#falsifiability}

**Literature term**: **falsifiability / demarcation criterion**, Karl
Popper — Stanford Encyclopedia of Philosophy, "Karl Popper" —
https://plato.stanford.edu/entries/popper/ — a theory or claim is
scientific to the extent it is capable, in principle, of conflicting with
possible observations; a claim compatible with every conceivable outcome
asserts nothing testable.

Applied here: state what observation, if it turned up, would refute the
claim as stated — for a general/universal claim ("customers who do X churn
less"), name the pattern of counter-evidence that would overturn it. This
applies to general claims, not to a single data point: one anomalous row
is never, by itself, sufficient to refute a population-level claim
(observation is theory-laden — an outlier needs its own explanation before
it counts as a counter-instance). A claim with no stated falsification
condition, or one phrased so broadly nothing could ever satisfy it, fails
this check.
