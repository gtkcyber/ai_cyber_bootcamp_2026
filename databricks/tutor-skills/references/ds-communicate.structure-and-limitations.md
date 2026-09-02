# Executive-summary discipline and the honest-limitations section

## Discipline

**Literature name**: **Pyramid Principle** (Minto) / **BLUF** (bottom line
up front — military/gov doctrine, independently converged on the same
structure).

**Canonical methods/refs**:
- Minto, *The Minto Pyramid Principle* — https://www.barbaraminto.com/ —
  lead with the governing thought; structure supporting arguments top-down
  beneath it, grouped and summarized at each level.
- Army Regulation 25-50 —
  https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN42124-AR_25-50-007-WEB-13.pdf
  — codifies BLUF as doctrine: main point first, active voice, no burying
  the conclusion under method narration the reader has to wade through.

**Failure modes**: both sources are a *presentation* discipline applied
after the analysis is done, not a brainstorming or analysis method — don't
let "lead with the finding" creep backward into skipping analysis rigor.
More importantly: both sources pair the lead conclusion with full
supporting structure underneath it, never with suppressed uncertainty or
omitted caveats. "State the finding first" and "state the finding only"
are different instructions — this protocol requires the first, never
allows the second.

## Audience-tiered structure

Three tiers, in this order, in every `report`:

2. **Evidence** — the headline numbers that support the finding, each
   carrying its denominator, population statement, and uncertainty inline
   (per `SKILL.md` Gates) — enough for a reader to judge whether the
   finding follows from the evidence, without re-deriving it themselves.

A tier may compress (a quick-answer report can fold Evidence and Method
into one short line) but never disappears outright — a Finding with no
Evidence trail is an assertion, not a report.

## Honest-limitations section

The `SKILL.md` Gates require a "what would change this conclusion" section
in every `report`.

- `scoping.proxy_statement`'s construct-operationalization gap,
- `gather.sampling_bias_note`'s named selection mechanism,
- `data-models.semantic_dictionary` entries with `provenance_class:
  asserted` or `defaulted` that feed a headline claim,
- any `stale` or `stale-scoped` section still cited by a claim (which
  `ds-verify` should already have blocked, but the limitations section
  restates the invalidation reason if verification ran in compressed form),
- `evaluate.scorecard`'s slice-wise findings where a subgroup materially
  underperforms the headline number.

Each becomes one sentence: *what* was assumed, and *what evidence, if it
arrived, would overturn or narrow the finding*.

**Worked example**: a churn-model report's finding is "at-risk segment X
churns at 3x baseline." Its limitations section states: "`proxy_statement`
defines churn as 30-day inactivity; a customer on a documented seasonal
pause reads as churned under this definition — if seasonal accounts were
systematically overrepresented in segment X, the 3x figure would narrow."
That sentence is auditable against `scoping.proxy_statement` directly; a
sentence that instead says "our data may have limitations" is not.
