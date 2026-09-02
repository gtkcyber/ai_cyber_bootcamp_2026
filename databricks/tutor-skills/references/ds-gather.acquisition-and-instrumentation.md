# Acquisition and instrumentation

Depth for the four "getting data in" subfields. SKILL.md carries the
protocol; this file carries worked detail and full citations.

## Acquisition (API/database/file/stream) {#acquisition}

**Literature**: ETL (extract-transform-load) — Kimball & Caserta, *The Data
Warehouse ETL Toolkit* —
https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-etl-toolkit/.

Treat extraction, conforming, and delivery as three distinct disciplines,
each with its own failure surface:

- **Extraction** (this skill's scope): connection/auth to the source,
  pagination/rate limits for APIs, incremental-vs-full pulls, checkpointing
  so a failed pull is resumable without re-pulling everything.
- **Conforming** (`ds-pipelines`): reconciling schema/format differences
  across sources into a common shape.
- **Delivery** (`ds-pipelines`): loading into the target store,
  idempotently.

Failure modes specific to extraction: source schema drift mid-pull
(hand off to `ds-data-models` on first contact with a changed shape, not
silently coerced); rate-limit-induced partial pulls masquerading as
complete ones; stream acquisition without a replay/backfill story for
gaps.

It does not own orchestration of what happens next (`ds-pipelines`) or
stateful serving computation over the stream (`ds-mlops`). A task that names
"streaming" without further qualification composes `ds-gather` for the
ingest leg and checks whether `ds-pipelines` or `ds-mlops` is also needed
for what follows.

## Web scraping {#scraping}

**Literature**: "Web Scraping Techniques and Applications: A Literature
Review" (2010–2023 systematic review) —
https://publications.scrs.in/uploads/final_menuscript/863dc5628ae9215e611c22943d061742.pdf.

Scraping is not ethically/legally neutral by default. Before scraping:

- Check robots.txt and Terms of Service; a source that disallows scraping
  is not made permissible by technical feasibility.
- Document the scrape's reproducibility posture explicitly: page structure
  changes silently, so a scraper's output needs a versioned selector set
  and a note on last-verified date, not an implicit assumption of
  stability.
- Rate-limit scraping the same way API acquisition rate-limits — scraping
  infrastructure has real cost and can be mistaken for an "unlimited"
  data faucet.

## Instrumentation/telemetry design {#instrumentation}

**LITERATURE-THIN.** No established academic name for product/user event
instrumentation design specifically. Nearest, adjacent-not-identical:
observability engineering — Majors, Fong-Jones, Miranda, Parker,
*Observability Engineering* —
https://www.oreilly.com/library/view/observability-engineering-2nd/9781098179915/,
which defines the "arbitrarily wide structured event" as the fundamental
telemetry unit. That source targets systems/production observability
(traces, logs, metrics for operating software), not the user/product
event-taxonomy design problem (deciding what business-meaningful events a
new surface should emit and what properties each carries). Treat the
following as practice guidance, not settled literature:

- Design the event taxonomy before the surface ships, not after — retrofit
  instrumentation loses the history it should have captured.
- Every event declares: name (stable, versioned), trigger condition,
  properties (typed), and the question it exists to answer. An event with
  no named question is speculative logging, not instrumentation design.
- State what a *new* surface's telemetry will and will not capture — this
  becomes the seed of `ds-data-models`' Observe discipline's population
  statement once the surface is live and data starts arriving.
- Volume/cardinality estimate before launch — an unbounded property
  (free-text, per-user IDs in event names) breaks downstream aggregation
  and cost.

## Survey/questionnaire instrument design {#survey}

**Literature**: Total Design Method (TDM) / Tailored Design Method
(Dillman) — "Utilizing the Total Design Method in medicine" —
https://pmc.ncbi.nlm.nih.gov/articles/PMC5995290/. Social-exchange-theory
method: respondents give higher-quality, higher-rate responses when the
survey minimizes perceived cost and maximizes perceived reward/trust
(personalization, follow-up timing, respondent-friendly design).

TDM addresses **response-rate / non-response bias**. It does not address
**question-wording bias** (leading questions, social desirability,
double-barreled questions) — a distinct failure mode requiring separate
question-design review (cognitive pretesting, pilot testing) before
fielding. Don't cite TDM compliance as evidence a survey's wording is
unbiased.

Before fielding: state the target population and the frame used to reach
it (this becomes part of `sampling_bias_note` if the frame excludes part
of the population); pretest the instrument; decide the non-response
follow-up protocol in advance, not reactively once response rates come in
low.
