---
name: ds-perception
description: "Image/audio/video/sensor method family: classical DSP (FFT, filtering, spectrograms, peak detection) on a classical-first ladder through CNN framing; owns modality preprocessing and which-pretrained-family-fits-this-modality (fine-tuning and training: `ds-deep-learning`)."
---

# ds-perception

Composes after `ds-features` writes the feature dictionary and pipeline
object, alongside `ds-model` (baseline-first-ladder procedure) and
`ds-supervised` (classical models fit on DSP-derived features). Full depth,
citations, and failure modes: `references/`; this file is protocol only.

## Subfields

All three: axis `family`, composed-alongside? no.

- Canonical methods (not exhaustive): windowed FFT / spectrograms, FIR/IIR
  filtering, prominence- or matched-filter-based peak detection. Cooley &
  Tukey, "An Algorithm for the Machine Calculation of Complex Fourier
  Series," Mathematics of Computation 19, 1965 —
  https://www.ams.org/journals/mcom/1965-19-090/S0025-5718-1965-0178586-1/S0025-5718-1965-0178586-1.pdf
  : the O(N log N) FFT underlying spectral analysis, spectrograms, and
  filter-bank implementations. Edges: filtering and peak detection are
  practitioner technique clusters, not traceable to one seminal paper each —
  don't cite a single reference as though the whole DSP toolkit derives from
  it. See `references/ds-perception.classical-dsp.md`.
- **LITERATURE-THIN**: practice guidance, not a settled literature — no
  citation invented per this family's brief. Canonical practices (not
  exhaustive): image resize/crop/color-space policy, audio resample-rate and
  frame/hop-size choice for spectrogram/MFCC extraction, video
  frame-sampling rate, sensor calibration and cross-channel sample-rate
  alignment. Edges: every preprocessing statistic (normalization mean/std,
  filter coefficients fit to data) is fit train-only — mechanics owned by
  `ds-features`, cited not re-derived. See
  `references/ds-perception.modality-preprocessing.md`.
- Canonical methods: LeCun, Bottou, Bengio & Haffner, "Gradient-Based
  Learning Applied to Document Recognition," Proc. IEEE 86(11), 1998 —
  http://yann.lecun.com/exdb/publis/pdf/lecun-01a.pdf : the founding CNN
  architecture for grid-structured signals (images, spectrograms-as-images).
  Yosinski, Clune, Bengio & Lipson, "How transferable are features in deep
  neural networks?," NeurIPS 2014 — https://arxiv.org/abs/1411.1792 :
  transferability is layer- and task-distance-dependent, not binary. Edges:
  "which pretrained family fits this modality" is a transferability question
  — a natural-image-pretrained CNN applied to spectrograms or sensor-array
  data is a domain-shift bet, not a neutral default, and that gap is stated,
  never assumed closed by architecture similarity alone.
  Fine-tuning/training mechanics past this framing choice the
  `ds-deep-learning` skill covers this. See
  `references/ds-perception.pretrained-family-selection.md`.

## Selection tree

1. **Name the modality and its preprocessing decision.** Image, audio,
   video, or sensor — each carries a distinct resample/frame/normalize
   choice (`references/ds-perception.modality-preprocessing.md`); an unstated default is
   a hidden bias, not a neutral start.
2. **Classical-first rung.** Do DSP-derived features (FFT/filter-bank/
   spectrogram-derived summary statistics, peak locations/prominences) plus
   a classical model answer the task at acceptable cost/interpretability?
   Yes → stop there; this is the ladder's baseline rung, mirroring the
   suite's baseline-first doctrine (`ds-model` owns the procedure — pointer,
   not re-derived here).
3. **Escalation.** Only with a comparably-tuned classical ceiling on record
   does the task move to CNN framing — residual dissatisfaction with the
   classical rung's performance is not itself the reason.
4. **CNN framing selected → pretrained-family choice.** Natural-image-
   pretrained CNN, a modality-specific pretrained model, or from-scratch —
   state the domain-shift bet (`references/ds-perception.pretrained-family-selection.md`)
   explicitly rather than defaulting on architecture-shape similarity.
5. **Hand off training.** Fine-tuning/training mechanics for the selected
   pretrained family or from-scratch architecture are `ds-deep-learning`'s
   (Edges) — this family's job stops at framing and pretrained-family
   choice.

## Family-specific pitfalls and evaluation

- Spectrogram/FFT output treated as stationarity-free rather than a
  stationarity approximation valid only within each analysis window.
- A fixed window length presented as a neutral default rather than the
  time/frequency-resolution tradeoff it actually is.
- Filtering or peak detection attributed to one seminal citation as though
  the whole DSP toolkit traces to it — both are practitioner clusters.
- Reflexive CNN reach: escalating past the classical-DSP-features +
  classical-model rung with no comparably-tuned classical ceiling on record
  (mirrors `ds-model`'s baseline-first-ladder gate and `ds-deep-learning`'s
  "no stated reason" pitfall).
- Pretrained-family fit assumed neutral — a natural-image-pretrained CNN
  defaulted onto spectrogram or sensor-array data without stating the
  domain-shift bet (Yosinski et al.).
- A modality's preprocessing decision (resample rate, frame/hop size,
  normalization, channel handling) left implicit rather than stated and
  justified per modality.

**Evaluation delta from `ds-evaluate`'s generic scorecard**: which metric
family applies follows the rung actually selected — the classical-DSP +
classical-model rung is scored on `ds-supervised`'s metric family
(accuracy/precision/recall/AUC, RMSE/MAE, per target type); a CNN-rung
report additionally states which pretrained family was used and the
domain-shift note from the Selection tree, not just the resulting score.
