# Narrative, uncertainty, and chart-type selection

## Narrative

**Literature name**: **narrative visualization** (HCI/InfoVis) / statistical
communication.

**Canonical methods/refs**: Segel & Heer, "Narrative Visualization: Telling
Stories with Data," IEEE InfoVis 2010 —
http://vis.stanford.edu/files/2010-Narrative-InfoVis.pdf — taxonomy of
author-driven structures (e.g. the "martini glass": linear narration then
open exploration) vs. reader-driven ones (interactive slideshow, drill-down).

**Failure modes**: author-driven vs. reader-driven is a real tradeoff
depending on audience and stakes, not a universal ranking — a board memo
wants author-driven; an analyst handoff can afford reader-driven. Narrative
structure exists to structure *interpretation* of findings already on
record, never to introduce a finding the ledger doesn't carry.

**Worked minimum**: a `report`'s narrative opens with the governing finding
(see Executive-summary discipline), then supplies the evidence that
supports it in the order a reader needs to trust it, then the method detail
a specialist reader would check. That three-tier order — finding, then
evidence, then method — is the audience-tiering this skill applies by
default; a reader-driven deliverable (a dashboard, an appendix) may invert
it, but the governing finding is stated before any exploration path is
offered either way.

## Uncertainty

**Literature name**: **uncertainty communication / calibrated confidence
language**. Best cross-domain template, though the source is
domain-specific: IPCC guidance.

**Canonical methods/refs**: Mastrandrea et al., "Guidance Note for Lead
Authors of the IPCC Fifth Assessment Report on Consistent Treatment of
Uncertainties" —
https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf
— separates two non-interchangeable scales: **confidence** (qualitative,
from evidence quality + agreement — "low," "medium," "high," "very high")
and **likelihood** (quantitative, calibrated probability language —
"virtually certain" >99% down to "exceptionally unlikely" <1%).

**Failure modes**: don't blend the two scales — "we're fairly confident
this is a 12% lift" reads as one number when it's actually two different
claims (an effect-size point estimate, and a confidence-quality judgment
about the evidence behind it) that need separate sentences. Don't imply
numeric precision ("we're 73% confident") when only a qualitative
confidence assessment was actually made upstream — that number doesn't
exist in the ledger and this protocol doesn't invent one.

**Worked minimum**: where `ds-uncertainty` or `ds-stats` recorded an
interval or coverage claim, state it beside the point estimate in the same
sentence ("14% lift, 95% CI 9–19%, n=..."), not in a separate uncertainty
appendix. Where no interval exists (a quick-answer one-line recount, or a
descriptive count with no inferential claim), the honest form is simply not
implying one — state the number as a count/rate over its denominator and
stop, rather than dressing a point estimate in confidence language it
didn't earn.

## Charts

No lifecycle-process brief citation exists for this subfield — it wasn't a
named literature concept in that source, and none is fabricated here.

Chart *construction* — mark selection, palette, layout, accessibility,
light/dark rendering — is out of this suite's scope: it belongs to whatever
charting facility the runtime provides. The boundary is stack-agnostic by
design (the report may render into a notebook, a slide deck, a dashboard,
or plain prose with an embedded image).

What stays this skill's own delta is a prior, narrower decision: **chart
type by data relationship**, before any tool question arises —

- trend over time → line/area,
- comparison across categories → bar,
- distribution → histogram/box/violin,
- part-to-whole → stacked bar (rarely a pie — angle judgments are less
  accurate than length judgments),
- correlation/relationship between two measures → scatter.

A finding with no chart-type match to one of these relationships (e.g. a
single number, a short ranked list) doesn't get a chart manufactured for
it — a table or a sentence is the correct choice, and forcing a chart where
the relationship doesn't call for one is itself a failure mode, not a
stylistic option.
