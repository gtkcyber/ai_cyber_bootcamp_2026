---
name: ds-gather
description: "Acquisition and selection-into-the-dataset intelligence: API/database/file/stream acquisition, web scraping, instrumentation/telemetry design, survey instrument design, unstructured-document extraction, sampling design, survivorship/selection-bias accounting, and multi-source join gates (same-semantics + cardinality)…"
---

# ds-gather

Runs immediately after `ds-scoping` writes the task card and before
`ds-pipelines` takes acquired data into orchestrated transforms. Not
re-entrant: fires once per task; a later re-acquisition need routes
through the loop-backs in Edges, not a fresh entry. Full depth, worked
examples, and citations live in `references/`; this file is protocol only.

## Subfields

- **Acquisition (API/database/file/stream)** — **ETL** (extract-transform-
  load). Trigger: task names a new external source to pull from. Kimball &
  Caserta, *The Data Warehouse ETL Toolkit* —
  https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-etl-toolkit/ :
  extraction, conforming, delivery are distinct disciplines — don't present
  ETL as one linear pipeline. Stops at extraction; conforming/delivery into
  a warehouse is `ds-pipelines`'. See
  `references/acquisition-and-instrumentation.md#acquisition`.
- **Web scraping** — trigger: source has no API/export, only a rendered
  page. "Web Scraping Techniques and Applications: A Literature Review" —
  https://publications.scrs.in/uploads/final_menuscript/863dc5628ae9215e611c22943d061742.pdf :
  scraping is not ethically/legally neutral by default — ToS/robots.txt
  compliance and reproducibility documentation are part of the discipline.
  See `references/acquisition-and-instrumentation.md#scraping`.
- **Instrumentation/telemetry design** — trigger: task asks what to log
  for a new product/system surface. **LITERATURE-THIN**: no established
  academic name for product-event instrumentation design. Nearest,
  adjacent-not-identical: Majors, Fong-Jones, Miranda, Parker,
  *Observability Engineering* — https://www.oreilly.com/library/view/observability-engineering-2nd/9781098179915/ :
  the "arbitrarily wide structured event" as the telemetry unit — written
  for systems/production observability, not product event-taxonomy design;
  treat as practice guidance, not settled literature. See
  `references/acquisition-and-instrumentation.md#instrumentation`.
- **Survey/questionnaire instrument design** — trigger: task requires
  fielding a new survey rather than reading existing data. **Total Design
  Method (TDM)** — "Utilizing the Total Design Method in medicine" —
  https://pmc.ncbi.nlm.nih.gov/articles/PMC5995290/ : Dillman's
  social-exchange method for response quality/non-response bias only —
  question-wording bias (leading questions, social desirability) is a
  distinct concern this citation does not cover. See
  `references/acquisition-and-instrumentation.md#survey`.
- **Unstructured-document extraction (OCR, PDF/table parsing, layout)** —
  trigger: source is a document corpus, not a table. **Document layout
  analysis** / **table extraction**. "PdfTable: A Unified Toolkit for
  Deep Learning-Based Table Extraction" — https://arxiv.org/abs/2409.05125 :
  accuracy is layout-dependent (scanned vs. digital-native, multi-column,
  nested tables). Stops at "text and structure extracted"; downstream
  modeling of that content (embeddings, classification) is `ds-text` /
  `ds-perception`, never this skill's concern. See
  `references/extraction-sampling-selection.md#extraction`.
- **Sampling design** — trigger: source is larger than what will be used,
  a frame/stratification/weighting decision needed before pulling. Kish,
  *Survey Sampling* — https://www.wiley.com/en-ae/Survey+Sampling-p-9780471109495 :
  foundational stratified/cluster/PPS design. More data is not a
  substitute for a valid frame. See
  `references/extraction-sampling-selection.md#sampling`.
- **Selection into the dataset (survivorship/selection bias)** — trigger:
  the acquisition process itself excludes population members
  (survivorship, opt-in, retention/outage effects). Heckman, "Sample
  Selection Bias as a Specification Error," Econometrica 47(1), 1979 —
  https://www.nber.org/papers/w0172 : non-random selection is a
  specification error, not fixable by more data or cleaning. Names the
  mechanism (writes `sampling_bias_note`); identification consequences for
  an effect estimate are `ds-causal`'s, never derived here. See
  `references/extraction-sampling-selection.md#selection-bias`.
- **Multi-source joining** — trigger: any join, at ingest or anywhere
  downstream. Fellegi & Sunter, "A Theory for Record Linkage," JASA 64,
  1969 — http://www2.stat.duke.edu/~rcs46/linkage/presentations/01-baiLi_FelleigSunter1969.pdf :
  grounds matching on shared attributes as probabilistic, optimal only
  under conditional independence of comparison attributes — routinely
  violated by correlated key errors. Owns the operational **join gate**
  (same-semantics + cardinality, below); schema-level mapping is
  `ds-data-models`' Translate and record/identity-level linkage is
  `ds-entity-resolution`'s — the gate cites both, redoes neither. **Applies
  at any join site in the pipeline, not just here** — `ds-pipelines` and
  `ds-features` cite this gate rather than restating it. See
  `references/joins-and-contracts.md#join-gates`.

|---|---|---|
| Acquisition (API/DB/file/stream) | quick-answer | conditional-on-data:new-source |
| Web scraping | quick-answer | conditional-on-data:scrape-source |
| Instrumentation/telemetry design | analysis | conditional-on-data:new-instrumentation |
| Survey/questionnaire design | analysis | conditional-on-data:survey-instrument |
| Document extraction | quick-answer | conditional-on-data:unstructured-documents |
| Sampling design | quick-answer | conditional-on-data:sampling-required |
| Selection into the dataset | quick-answer | mandatory |
| Multi-source joining | quick-answer | conditional-on-data:join-present |

`mandatory`: fires whenever `ds-gather` composes at
all — every acquisition path selects for or against something, unlike the
other seven, which fire only on their own trigger.

## Gates

- Shape: `references/joins-and-contracts.md#contracts`.
- `sampling_bias_note` states what the acquisition process selects for and
  against (frame coverage, response mechanism, retention/outage effects) —
  a note that only asserts "may have some bias" fails this gate.
  Identification consequences of a named mechanism route to `ds-causal`;
  this gate only requires the mechanism be named, not resolved.
- **Raw immutability**: acquired raw data is written once and never
  mutated in place — every downstream transform produces a new artifact.
  The gate checks for absence of in-place raw mutation, not for
  correctness of what comes after.
- **Join gate**, at any join site: same-semantics check (same key name is
  not proof of same meaning — cite `ds-data-models`' semantic-dictionary
  entries for both sides) plus a lightweight cardinality check against the
  grain each side declared (`ds-data-models`' grain contract, cited, never
  re-derived here). Both checks run before the join executes, not audited
  after.
- Sampling design states the frame, selection mechanism, and (if
  stratified/weighted) the weighting scheme before collection executes — a
  sample drawn first and characterized after fails this gate.

## Edges

Covered: acquisition across API/DB/file/stream sources, web scraping,
instrumentation/telemetry design, survey/questionnaire instrument design,
unstructured-document extraction (text/structure only), sampling design,
selection-bias note authorship, join gates at any join site.

Population-statement composition through downstream transforms is router
doctrine (`doctrine-repro-provenance.md`), pointer only — this skill writes
the selection-bias note, not the population statement (`ds-data-models`'
Observe discipline owns that).

When scoping re-runs, `ds-gather` re-runs as part of the forward cascade in
normal composition order, not via a named back-edge of its own.

## Audit mode

Input: an existing external acquisition artifact authored outside this skill
(a data-engineering ingestion doc, a vendor onboarding spec, a prior ETL
job's config). An undocumented acquisition claim is treated as an
unregistered field under Gates: flagged, never assumed compliant.

## Production considerations

Three deltas, all pointers: ongoing orchestration/scheduling of the
acquisition (backfills, incremental refresh) moves to `ds-pipelines`;
stateful streaming serving computation moves to `ds-mlops`, which also
owns continuous data-contract/schema-drift monitoring — seeded by the
`data_contract` this skill writes, the way `ds-clean`'s assertion suite
seeds it; acquisition cost economics (API rate/cost limits, scraping
infrastructure, stream throughput) read `doctrine-scale-cost.md`'s
threshold, recorded once in `ds-scoping`'s kill-check and never restated
here.
