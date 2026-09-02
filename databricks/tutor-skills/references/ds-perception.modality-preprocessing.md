# Modality preprocessing

**LITERATURE-THIN.** No settled academic literature names "modality
preprocessing" as one field the way FFT or CNN architecture selection have
canonical papers — this is practice guidance distilled from how each
modality is conventionally prepared before extraction or modeling, not a
citation-backed method claim. Mark it as such rather than inventing a
source.

## Per-modality decisions

- **Image** — resize/crop policy (aspect-ratio preservation vs. forced
  resize changes what the model sees as "the same object at different
  scale"), color space (RGB vs. grayscale vs. domain-specific spaces),
  per-channel normalization statistics.
- **Audio** — sample-rate choice (resampling to a fixed rate before any
  spectral feature extraction — mismatched source rates are not
  comparable), frame length and hop size for spectrogram/MFCC extraction
  (the same time/frequency-resolution tradeoff as `classical-dsp.md`
  applies here), loudness/amplitude normalization.
- **Video** — frame-sampling rate (uniform vs. keyframe-based — changes
  which temporal information survives into the model), per-frame image
  preprocessing (inherits the image practices above), temporal window
  length for any windowed model input.
- **Sensor** — calibration and unit conversion to a common scale before
  fusion across channels, cross-channel sample-rate alignment (sensors on
  one rig frequently sample at different native rates), and explicit
  handling of missing samples — the *framing-level* resampling/alignment
  choice belongs here; per-record defect handling (bad readings, dropped
  packets) is `ds-clean`'s, not re-derived here.

## Fit-on-train-only

Every preprocessing statistic that is *learned from data* — normalization
mean/std, filter coefficients fit to an empirical noise profile, any
per-channel calibration constant estimated from the corpus rather than fixed
by hardware spec — is fit on the train split only.

Fixed, hardware-specified constants (a known sensor's calibration curve,
a codec's fixed sample rate) are not data-derived and are not subject to
this rule — the distinction is whether the number was *estimated from the
corpus* or *specified independent of it*. State which applies for each
preprocessing statistic in the framing note.

## Gate mapping

Every modality's resample/frame/normalize/channel-handling decision is
stated explicitly (`SKILL.md` Gates) before extraction or modeling
proceeds — an unstated default (e.g. "resampled the audio," with no rate
given) is a hidden analytic choice, not a neutral preprocessing step.
