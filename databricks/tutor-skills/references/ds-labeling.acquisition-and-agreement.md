# Acquisition and agreement

Depth for label acquisition strategy and inter-annotator agreement.
SKILL.md carries the protocol; this file carries worked detail and full
citations.

## Label acquisition strategy {#acquisition}

**Literature**: crowdsourced/non-expert annotation. Snow, O'Connor,
Jurafsky, Ng, "Cheap and Fast — But is it Good? Evaluating Non-Expert
Annotations for Natural Language Tasks," EMNLP 2008 —
https://aclanthology.org/D08-1027 : aggregated non-expert (Mechanical Turk)
labels can match expert-level quality **when redundantly collected and
aggregated** — the finding is about the redundancy+aggregation combination,
not about non-expert labeling in general.

Every acquisition path is one of, or a mix of:

- **Existing labels, unchanged** — the dataset already carries a target.
  This is still an acquisition-strategy finding: characterize *who/what*
  produced the existing labels (asserter, per Gates), whether they were
  redundant, and whether the population that produced them matches the
  intended scoring population — an existing label set collected under a
  different population is a scope mismatch, not a free pass.
- **New human annotation** — state annotator count, redundancy (items per
  annotator, annotators per item), and the aggregation method (majority
  vote, weighted vote by annotator reliability, adjudication). A
  single-pass, non-redundant human label carries no quality claim beyond
  "one asserter said so" — see Gates.
- **Weak supervision** — see `references/ds-labeling.weak-supervision-and-active-learning.md`.
- **Model-assisted** — see `references/ds-labeling.noise-pu-and-model-assisted.md`.

A protocol that names a source but not a redundancy/aggregation scheme has
described where labels came from, not whether they can be trusted — the two
are separate claims and the `labeling_protocol` artifact carries both.

## Annotation quality and inter-annotator agreement {#agreement}

**Literature**: Cohen, "A Coefficient of Agreement for Nominal Scales,"
*Educational and Psychological Measurement* 20, 1960 (bibliographic
existence: https://journals.sagepub.com/doi/10.1177/001316446002000104 ;
formula/content: https://www-users.york.ac.uk/~mb55/msc/clinimet/week4/kappa_text.pdf)
— **Cohen's kappa**: chance-corrected agreement, exactly two raters,
categorical labels. Krippendorff, "Computing Krippendorff's
Alpha-Reliability" —
https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff's%20Alpha-Reliability.pdf
— **Krippendorff's alpha**: generalizes to any number of coders, any
measurement level (nominal/ordinal/interval/ratio), and missing data.

Statistic selection is not a style choice:

- **Exactly two raters, nominal labels** → Cohen's kappa is appropriate.
- **Three or more raters, or non-nominal measurement, or missing
  ratings** → Cohen's kappa does not apply; use Krippendorff's alpha.
  Reporting a pairwise-averaged kappa across 3+ raters as if it were a
  single agreement statistic is a common but incorrect substitute — it is
  not the same quantity Krippendorff's alpha estimates.

**The kappa paradox**: high raw percent-agreement can coexist with a low
kappa/alpha when the label distribution is skewed (most items share one
class) — the chance-correction term shrinks the statistic as prevalence
moves away from balanced. Two consequences, both gated (SKILL.md Gates):

1. Report prevalence/base rate alongside any kappa/alpha value — the bare
   number is not interpretable without it.
2. Do not compare kappa/alpha values across datasets or label sets with
   different base rates and conclude one annotation effort was "better" —
   the paradox can produce the opposite of the intuitive read.

This subfield measures agreement; it does not resolve disagreement (that's
adjudication, part of acquisition strategy above) or diagnose *why*
annotators disagree (definitional ambiguity in the labeling guideline vs.
genuine item difficulty vs. annotator error) — a low agreement score is a
finding to route back into the acquisition strategy and guideline, not a
number to report and move past.
