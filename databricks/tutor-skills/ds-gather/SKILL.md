---
name: ds-gather
description: "Acquisition and selection-into-the-dataset intelligence: API/database/file/stream acquisition, web scraping, instrumentation/telemetry design, survey instrument design, unstructured-document extraction, sampling design, survivorship/selection-bias accounting, and multi-source join gates (same-semantics + cardinality)…"
---

# ds-gather

Runs immediately after `ds-scoping` writes the task card and before
`ds-pipelines` takes acquired data into orchestrated transforms. Full depth,
worked examples, and citations live in `references/`; this file is protocol
only.

## Subfields

- **Acquisition (API/database/file/stream)** — **ETL** (extract-transform-
  load). Trigger: task names a new external source to pull from. Kimball &
  Caserta, *The Data Warehouse ETL Toolkit* —
  https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-etl-toolkit/ :
  extraction, conforming, delivery are distinct disciplines — don't present
  ETL as one linear pipeline. Stops at extraction; conforming/delivery into
  a warehouse is `ds-pipelines`'. See
  `references/ds-gather.acquisition-and-instrumentation.md#acquisition`.
- **Web scraping** — trigger: source has no API/export, only a rendered
  page. "Web Scraping Techniques and Applications: A Literature Review" —
  https://publications.scrs.in/uploads/final_menuscript/863dc5628ae9215e611c22943d061742.pdf :
  scraping is not ethically/legally neutral by default — ToS/robots.txt
  compliance and reproducibility documentation are part of the discipline.
  See `references/ds-gather.acquisition-and-instrumentation.md#scraping`.
- **Instrumentation/telemetry design** — trigger: task asks what to log
  for a new product/system surface. **LITERATURE-THIN**: no established
  academic name for product-event instrumentation design. Nearest,
  adjacent-not-identical: Majors, Fong-Jones, Miranda, Parker,
  *Observability Engineering* — https://www.oreilly.com/library/view/observability-engineering-2nd/9781098179915/ :
  the "arbitrarily wide structured event" as the telemetry unit — written
  for systems/production observability, not product event-taxonomy design;
  treat as practice guidance, not settled literature. See
  `references/ds-gather.acquisition-and-instrumentation.md#instrumentation`.
- **Survey/questionnaire instrument design** — trigger: task requires
  fielding a new survey rather than reading existing data. **Total Design
  Method (TDM)** — "Utilizing the Total Design Method in medicine" —
  https://pmc.ncbi.nlm.nih.gov/articles/PMC5995290/ : Dillman's
  social-exchange method for response quality/non-response bias only —
  question-wording bias (leading questions, social desirability) is a
  distinct concern this citation does not cover. See
  `references/ds-gather.acquisition-and-instrumentation.md#survey`.
- **Unstructured-document extraction (OCR, PDF/table parsing, layout)** —
  trigger: source is a document corpus, not a table. **Document layout
  analysis** / **table extraction**. "PdfTable: A Unified Toolkit for
  Deep Learning-Based Table Extraction" — https://arxiv.org/abs/2409.05125 :
  accuracy is layout-dependent (scanned vs. digital-native, multi-column,
  nested tables). Stops at "text and structure extracted"; downstream
  modeling of that content (embeddings, classification) is `ds-text` /
  `ds-perception`, never this skill's concern. See
  `references/ds-gather.extraction-sampling-selection.md#extraction`.
- **Sampling design** — trigger: source is larger than what will be used,
  a frame/stratification/weighting decision needed before pulling. Kish,
  *Survey Sampling* — https://www.wiley.com/en-ae/Survey+Sampling-p-9780471109495 :
  foundational stratified/cluster/PPS design. More data is not a
  substitute for a valid frame. See
  `references/ds-gather.extraction-sampling-selection.md#sampling`.
- **Selection into the dataset (survivorship/selection bias)** — trigger:
  the acquisition process itself excludes population members
  (survivorship, opt-in, retention/outage effects). Heckman, "Sample
  Selection Bias as a Specification Error," Econometrica 47(1), 1979 —
  https://www.nber.org/papers/w0172 : non-random selection is a
  specification error, not fixable by more data or cleaning. Names the
  mechanism (writes `sampling_bias_note`); identification consequences for
  an effect estimate are `ds-causal`'s, never derived here. See
  `references/ds-gather.extraction-sampling-selection.md#selection-bias`.
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
  `references/ds-gather.joins-and-contracts.md#join-gates`.

`mandatory`: fires whenever `ds-gather` composes at
all — every acquisition path selects for or against something, unlike the
other seven, which fire only on their own trigger.

## Production considerations

Three deltas, all pointers: ongoing orchestration/scheduling of the
acquisition (backfills, incremental refresh) moves to `ds-pipelines`;
stateful streaming serving computation moves to `ds-mlops`, which also
owns continuous data-contract/schema-drift monitoring — seeded by the
`data_contract` this skill writes, the way `ds-clean`'s assertion suite
seeds it; acquisition cost economics (API rate/cost limits, scraping
infrastructure, stream throughput) read `references/doctrine-scale-cost.md`'s
threshold, recorded once in `ds-scoping`'s kill-check and never restated
here.
