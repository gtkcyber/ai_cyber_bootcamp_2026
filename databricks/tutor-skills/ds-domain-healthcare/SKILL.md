---
name: ds-domain-healthcare
description: "Domain overlay for clinical/EHR/claims tasks (readmission and deterioration risk, comparative-effectiveness and treatment-effect analysis, survival/ time-to-event outcomes, diagnostic/screening classification): states only the healthcare-specific deltas on censoring conventions, treatment-effect identification…"
---

# ds-domain-healthcare

## Subfields

- **Readmission/deterioration risk prediction** — trigger: "will this
  patient be readmitted/deteriorate," EHR/claims-derived encounter data.
- **Comparative-effectiveness / treatment-effect analysis** — trigger:
  "does treatment X improve outcome Y," EHR-derived cohort comparison with
  no randomization.
- **Survival/time-to-event modeling** — trigger: "time to event," "hazard,"
  mortality/relapse-free survival with censoring.
- **Diagnostic/screening classification under clinical cost asymmetry** —
  trigger: an alerting or screening detector where missing a case and a
  false alarm carry clinically different costs (sepsis/deterioration
  alerting, cancer-screening triage).

## Deltas

- **Censoring conventions** — general treatment: time-to-event outcomes with
  censoring, product-limit (Kaplan–Meier) estimation, non-informative-
  censoring assumption · domain delta: clinical outcomes are pervasively
  right-censored — loss to follow-up, competing mortality, and
  administrative censoring at study/observation-window end are the default,
  not the exception — and the censoring mechanism is routinely
  *informative*: sicker patients are differentially more likely to drop out
  or die before the event of interest is observed, which violates ds-stats'
  non-informative-censoring assumption outright rather than as an edge case.
  ds-stats' survival-analysis gate ("any survival-analysis claim states the
  censoring-mechanism assumption, non-informative or the alternative with
  its operational cause") is the load-bearing check here — a readmission or
  mortality outcome defined without naming which patients were censored and
  why is not a defined outcome.
- **Treatment-effect practice** — general treatment: observational/
  quasi-experimental identification and uplift · domain delta: EHR-derived
  treatment comparisons are near-never randomized, and confounding by
  indication is the baseline condition, not a special case — sicker patients
  get more aggressive treatment, which is exactly the confound ds-causal's
  DAGs-and-confounding subfield exists to classify before any adjustment.
  ds-causal's mandatory "Identification without randomization" subfield and
  its `identification_statement` gate (naming the untestable assumption —
  unconfoundedness, most often) are not optional rigor here; a treatment-
  effect claim with a survival outcome composes this delta with the
  censoring delta above — the identification strategy and the
  censoring-aware outcome definition are separate obligations, neither one
  substitutes for the other.
- **Cost-asymmetric errors** — general treatment: single-threshold
  operating-point selection under a stated cost function/(C(FP)+C(FN))`) ·
  domain delta: false-negative and false-positive costs are typically wildly
  asymmetric and clinically defined, not economically estimated — a missed
  sepsis flag costs a life, a false alarm costs a clinician's time on a
  workup — so ds-evaluate's gate against a default 0.5-symmetric threshold
  is the binding constraint, not a formality: the cost matrix must be
  clinician-elicited per outcome and setting, never assumed or back-fit from
  convenience, and re-elicited when the clinical context changes (screening
  population vs. ICU deterioration alerting carry different matrices even
  for the same underlying model).
- **Small-n rigor** — general treatment: effect-size reporting and its
  small-sample bias; hierarchical/mixed-effects partial pooling," Laird &
  Ware 1982) · domain delta: rare-disease cohorts, single-site trials, and
  per-site or per-provider subgroups routinely run at an n too small for
  standard asymptotics to hold — biased η² (already flagged at ds-stats'
  Effect sizes subfield) overstates effect magnitude at these sample sizes
  before any healthcare-specific correction is even applied, and per-site/
  per-provider point estimates need partial-pooling shrinkage
  (ds-uncertainty's Hierarchical/mixed-effects subfield) rather than
  unpooled estimates a small n makes unstable — an unpooled per-site
  readmission rate on a dozen patients is noise reported as a finding.

## Standards catalog

Seeds for `ds-data-models` Research, not ceilings — confirm producer
version/dialect against the actual feed before relying on any entry.

- **HL7 FHIR** — resource-based standard for exchanging healthcare data.
  Producer: hl7.org/fhir; current published version Release 5 (R5), with
  R4B/R4/R3/R2 in active parallel use — confirm the actual release a source
  system emits before assuming R5.
- **ICD** — WHO's disease/health-condition classification, legally mandated
  under the WHO Constitution. Producer: who.int/standards/classifications.
  Current revision ICD-11 (in effect since 2022-01-01); ICD-10 remains in
  active parallel use — confirm which revision (and which national
  clinical-modification variant, e.g. ICD-10-CM) a given source actually
  codes to.
- **SNOMED CT** — clinical healthcare terminology for electronic health
  records. Producer: snomed.org, SNOMED International. The terminology
  alone specifies no data-quality guarantee without an implementing
  application — confirm how the source system actually populates SNOMED
  fields (coded at the point of care vs. mapped after the fact) before
  trusting a code's provenance.

### Readmission-risk model

1. `ds-scoping` — task card; population and `split_design` name the patient
   as the unit that must not leak across train/eval.
2. `ds-data-models` — Identify/Research fingerprints the source schema
   against the catalog above; Interpret's grain contract declares
   one-row-per-encounter vs. one-row-per-patient before "readmission" is
   even defined, `data-models.population_statement`.
3. `ds-profile` — `grouping_variables` identifies patient (and site/
   provider) as the non-iid keys this overlay's small-n and CV-design delta
   depend on.
4. `ds-labeling` — defines the censoring-aware readmission-window outcome
   under this overlay's censoring delta (a patient who dies or is lost to
   follow-up inside the window is not a verified negative).
6. `ds-evaluate` — cost-asymmetric operating point under this overlay's
   clinician-elicited cost-matrix delta.

### Treatment-effect analysis from EHR

2. `ds-data-models` — Attest register distinguishes what a treatment record
   actually proves (order placed vs. medication administered vs. patient
   adherence are three distinct attestations, none substituting for the
   others).
3. `ds-causal` — confounding-by-indication classification and an
   identification strategy under this overlay's treatment-effect delta;
   mandatory `identification_statement` names the untestable assumption.
4. `ds-stats` — states the censoring-mechanism assumption for the survival
   outcome under this overlay's censoring delta.
5. `ds-uncertainty` — interval/coverage claim around the treatment-effect
   estimate, per `ds-causal`'s Pairings (identification here, interval
   discipline there).

## Gates

- No delta bullet restates owner content beyond naming it — re-deriving
  owner content fails overlay scope.

## Edges

Covered: the four deltas above and the two worked compositions. FDA
group-sequential boundaries) — already an `ds-stats` research- escalation
trigger, not re-derived here.
