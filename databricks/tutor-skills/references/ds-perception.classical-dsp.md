# Classical DSP — FFT, filtering, spectrograms, peak detection

## FFT and spectrograms

Cooley & Tukey, "An Algorithm for the Machine Calculation of Complex
Fourier Series," Mathematics of Computation 19, 1965 —
https://www.ams.org/journals/mcom/1965-19-090/S0025-5718-1965-0178586-1/S0025-5718-1965-0178586-1.pdf
: the O(N log N) FFT algorithm. A spectrogram is a windowed FFT applied
over successive frames — the standard route from raw signal to a
time-frequency representation for filtering, feature extraction, or
CNN-as-image framing (spectrogram treated as a 2-D grid).

**Stationarity is a window-scoped approximation, not a property of the
whole signal.** FFT-based spectral analysis assumes the signal is
stationary *within* each analysis window. A spectrogram does not remove
this assumption — it just narrows its scope to each window. Treating a
spectrogram as a stationarity-free representation of a non-stationary
signal misstates what the transform did.

**Window length is a resolution tradeoff, not a free parameter.** A longer
window gives finer frequency resolution and coarser time resolution; a
shorter window the reverse — an uncertainty-principle-style tradeoff, not
a tuning knob with one correct default. State the window length and which
side of the tradeoff the task needs (localizing a transient event vs.
resolving close frequencies) before reporting spectral output.

The standard DSP textbook name for this material is Oppenheim & Schafer;
its full text could not be independently fetched (publisher catalog pages
did not confirm content), so it is named here for context but not cited
as a link — only the Cooley-Tukey primary source above is cited.

## Filtering

Low-pass, high-pass, band-pass, and notch filters (FIR or IIR
implementations) remove or isolate frequency bands before downstream
analysis or feature extraction. **This is a practitioner technique
cluster, not a field traceable to one seminal paper** — there is no single
"filtering" citation the way FFT traces to Cooley-Tukey. State the design
choice explicitly instead of citing a source for the choice:

- cutoff frequency/frequencies and the reason they were placed there
  (known noise band, known signal band, a stated frequency of interest)
- filter order (steepness of the rolloff) and its cost in phase distortion
  or group delay
- causal (real-time-safe, introduces phase delay) vs. zero-phase
  (filtfilt-style, non-causal, only valid in offline/batch analysis)

An unstated cutoff, order, or causality choice is a hidden analytic
decision, not a neutral default.

## Peak detection

Local-maxima thresholding, prominence-based detection, and matched-filter
detection are the common approaches — again a **practitioner cluster**,
not one canonical method. State which was used and its threshold/
prominence criterion; a peak count or location reported without the
detection criterion is not reproducible from the artifact alone.

## Gate mapping

These three failure modes map directly to `SKILL.md`'s Gates: window
length + resolution tradeoff stated (spectrogram/FFT gate); filter/peak
method not attributed to a fabricated single citation (citation-cluster
gate); cutoff/order/causality or detection criterion stated explicitly
(design-choice gate).
