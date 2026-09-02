---
name: ds-labeling
description: "Label acquisition and quality intelligence for supervised targets: acquisition strategy, inter-annotator agreement, weak supervision, active learning, label delay/noise, implicit-negative and PU-learning gating, and model-assisted labeling strategy/audit (regardless of which model does the labeling)."
---

# ds-labeling

Runs after `ds-clean` and before `ds-features`, whenever the task's target
requires labels that were not already trustworthy inputs. Full depth, worked
examples, and citations live in `references/`; this file is protocol only.

## Subfields

- **Label acquisition strategy** — trigger: any task needing labels this
  skill hasn't already characterized. Snow, O'Connor, Jurafsky, Ng, "Cheap
  and Fast — But is it Good? Evaluating Non-Expert Annotations for Natural
  Language Tasks," EMNLP 2008 — https://aclanthology.org/D08-1027 :
  redundant non-expert labels, aggregated, can match expert quality — a
  single-annotator pass cannot claim this without redundancy plus an
  aggregation method. See `references/ds-labeling.acquisition-and-agreement.md#acquisition`.
- **Annotation quality and inter-annotator agreement** — trigger: 2+
  annotators (human or model) labeled overlapping items. Cohen, "A
  Coefficient of Agreement for Nominal Scales," 1960 (existence:
  https://journals.sagepub.com/doi/10.1177/001316446002000104 ; content:
  https://www-users.york.ac.uk/~mb55/msc/clinimet/week4/kappa_text.pdf) —
  **Cohen's kappa**, two raters only. Krippendorff, "Computing
  Krippendorff's Alpha-Reliability" —
  https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff's%20Alpha-Reliability.pdf
  — **Krippendorff's alpha**, any rater count/measurement level/missing
  data. See `references/ds-labeling.acquisition-and-agreement.md#agreement`.
- **Weak supervision** — trigger: labels come (in whole or part) from
  programmatic heuristics rather than direct annotation. Ratner et al.,
  "Snorkel: Rapid Training Data Creation with Weak Supervision," VLDB
  11(3), 2017 — https://arxiv.org/pdf/1711.10160 : labeling functions
  combined via a generative model that denoises them without ground truth,
  assuming conditional independence (or explicitly modeled correlation)
  across functions. See `references/ds-labeling.weak-supervision-and-active-learning.md#weak-supervision`.
- **Active learning** — trigger: labeling budget is constrained and items
  can be prioritized before labeling. Settles, "Active Learning Literature
  Survey," UW-Madison CS TR 1648 —
  https://burrsettles.com/pub/settles.activelearning.pdf : query-selection
  strategies (uncertainty sampling, query-by-committee, expected model
  change/error reduction). See
  `references/ds-labeling.weak-supervision-and-active-learning.md#active-learning`.
- **Label delay and noise** — trigger: labels arrive late relative to
  prediction time, or are known/suspected noisy. Song et al., "Learning
  from Noisy Labels with Deep Neural Networks: A Survey," IEEE TNNLS 2022 —
  https://arxiv.org/pdf/2007.08199 : deep nets memorize noisy labels given
  capacity/epochs; noise is usually class-conditional or
  instance-dependent, not uniform. See
  `references/ds-labeling.noise-pu-and-model-assisted.md#noise`.
- **Implicit negatives and PU learning** — trigger: the only observed
  labels are positives and everything else is unlabeled, not confirmed
  negative. Elkan & Noto, "Learning Classifiers from Only Positive and
  Unlabeled Data," KDD 2008 — https://cseweb.ucsd.edu/~elkan/posonly.pdf :
  under SCAR (labeled positives are a random subset of all positives), a PU
  classifier's output rescales into a proper `P(y=1|x)`. Bekker & Davis,
  "Learning from Positive and Unlabeled Data: A Survey," Machine Learning
  109, 2020 — https://arxiv.org/pdf/1811.04820 : the non-SCAR case, where
  calibration breaks. See
  `references/ds-labeling.noise-pu-and-model-assisted.md#pu-learning`.
- **Model-assisted labeling** — trigger: a model suggests or auto-accepts
  labels anywhere in the pipeline. Desmond et al., "Semi-Automated Data
  Labeling," PMLR v133, 2020 —
  http://proceedings.mlr.press/v133/desmond21a/desmond21a.pdf : model
  suggests, human reviews, high-confidence items auto-label, iterating as
  the model improves from corrections. See
  `references/ds-labeling.noise-pu-and-model-assisted.md#model-assisted`.

`mandatory`: every label-bearing dataset was acquired somehow — even
"labels already exist, unchanged" is an acquisition-strategy finding
(assess existing label provenance) — unlike the other six, which fire only
on their own trigger.

## Production considerations

Two deltas: the `production-feedback → labeling` back-edge is this skill's
primary production surface — analyst dispositions and user corrections are
new label acquisition, re-entering acquisition strategy and (if delayed
relative to the original prediction) label-delay characterization, not a
one-off patch to an existing label. Auto-accepted model-assisted labels in
production require the re-audit cadence stated in Gates to run on an
ongoing schedule, not just at initial protocol authorship — model
confidence is not a correctness proxy under distribution shift, and an
unaudited auto-labeling stream can silently compound errors into future
training rounds. Continuous drift monitoring of label distributions in
production is `ds-mlops`', pointer only.
