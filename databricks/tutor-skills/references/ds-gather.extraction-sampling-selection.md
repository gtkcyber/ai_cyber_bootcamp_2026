# Extraction, sampling, and selection

Depth for the three "getting data right" subfields. SKILL.md carries the
protocol; this file carries worked detail and full citations.

## Unstructured-document extraction (OCR, PDF/table parsing, layout) {#extraction}

**Literature**: document layout analysis / table extraction — "PdfTable: A
Unified Toolkit for Deep Learning-Based Table Extraction" —
https://arxiv.org/abs/2409.05125 (unifies 7 table-recognition models, 4 OCR
tools, 3 layout-analysis models under one interface).

Extraction quality is layout-dependent, not uniform:

- Scanned images require OCR first (introduces character-level error);
  digital-native PDFs can skip OCR but still need layout analysis for
  multi-column or nested-table structure.
- Table extraction accuracy drops sharply on nested tables, merged cells,
  and tables spanning page breaks — validate extracted structure against a
  sample of source pages before trusting a full-corpus run, not after.
- Layout analysis (reading order, header/footer exclusion, figure/caption
  association) is a separate step from OCR/table recognition — a pipeline
  that skips it silently mis-orders multi-column text.

**Own edges**: this subfield's output is extracted text and structure
(tables as tabular data, body text as text, layout metadata). It does not
classify, embed, summarize, or otherwise model that content — those are
`ds-text` (NLP) or `ds-perception` (vision, if the task is about the
document's images) concerns, downstream of this skill's output. A task
that asks "what does this contract say" needs both: `ds-gather` extracts,
`ds-text` interprets.

## Sampling design {#sampling}

**Literature**: survey sampling — Kish, *Survey Sampling* —
https://www.wiley.com/en-ae/Survey+Sampling-p-9780471109495 (foundational
stratified/cluster/probability-proportional-to-size design, still
canonical).

Decide before pulling, not after:

- **Frame**: the enumerable list sampling draws from. State what the frame
  covers and what it excludes — a frame gap is a selection mechanism
  (feeds `sampling_bias_note`), not a sampling-design detail to bury.
- **Method**: simple random, stratified (by what variable, and why),
  cluster (what's the cluster unit, and does it introduce dependence a
  downstream model must account for — flag to `ds-model`'s CV design if
  so), or PPS (probability-proportional-to-size, when units vary widely in
  weight/volume).
- **Weighting**: if the draw is not uniform-probability, state the weight
  each sampled unit carries back to the population it represents before
  any aggregate is computed on the sample — an unweighted aggregate over a
  non-uniform sample silently overrepresents whatever was oversampled.
- More data from a bad frame is still a bad frame — sample size does not
  substitute for frame coverage or method soundness.

## Selection into the dataset (survivorship/selection bias) {#selection-bias}

**Literature**: sample selection bias — Heckman, "Sample Selection Bias as
a Specification Error," Econometrica 47(1), 1979 —
https://www.nber.org/papers/w0172. Frames non-random selection as a
specification error affecting what an estimator identifies — not a
data-quality nuisance fixable by cleaning or more data.

This subfield's job is narrow and specific: **name the mechanism** by
which the acquisition process includes some population members and
excludes others. Examples of the mechanism statement `sampling_bias_note`
must contain:

- Survivorship: "only accounts still active at pull time are captured —
  churned accounts before period end are absent."
- Opt-in: "only users who enabled telemetry sharing are captured — this
  selects for [whatever correlates with opting in]."
- Outage/retention: "collector was down from `<date>` to `<date>`; source
  retention window is 90 days, so events before `<date>` are unrecoverable
  regardless of collector uptime."

**What this subfield does not do**: derive the consequence of the named
mechanism for a causal or predictive estimate. "Selection on the outcome
biases the treatment effect toward X" is an identification claim —
`ds-causal`'s job, consulted once the mechanism is named here. A
`sampling_bias_note` that jumps straight to an identification conclusion
without naming the mechanism that produces it has skipped this subfield's
actual output.
