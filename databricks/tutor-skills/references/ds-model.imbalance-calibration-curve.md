# Imbalance, calibration, learning curve

## Imbalance intervention decision {#imbalance}

Krawczyk (2016) surveys three competing intervention families — resampling
(over/undersampling the training set), algorithm-level (cost-sensitive
loss, class weights), and threshold/output adjustment (leave training
alone, move the decision threshold) — and notes threshold adjustment can
outperform resampling, contrary to the reflex to resample first.

**Decision procedure**:
1. Quantify the imbalance ratio and confirm it's the label distribution,
   not just a training-set artifact of `ds-clean` filtering.
2. Ask whether the model's raw scores are usable as scores (ranking task,
   threshold set downstream by `ds-evaluate`) — if so, threshold/output
   adjustment alone may be sufficient and avoids distorting the training
   distribution the model calibrates against.
3. If the algorithm supports class weighting natively (most linear models,
   trees, and boosting libraries), prefer algorithm-level weighting over
   resampling — it doesn't discard or duplicate rows.
4. Resampling (SMOTE-family oversampling, undersampling) only when neither
   of the above is available or sufficient. Generation mechanics for any
   synthetic oversampling method are `ds-simulation`'s, not this skill's.
5. Never justify the choice, or its absence, by accuracy — accuracy is
   misleading under imbalance regardless of which intervention is picked.
   Which metric to judge the intervention by is `ds-evaluate`'s call.
6. Record the decision and reasoning in `selection_rationale` even when
   the decision is "no intervention" — a default that goes unrecorded
   reads as an oversight, not a judgment call.

## Calibration {#calibration}

Accuracy and calibration are orthogonal properties: a model can rank
examples correctly (good accuracy/AUC) while its probability outputs are
systematically over- or under-confident. Guo et al. (2017) show modern
neural networks are typically overconfident by default, and temperature
scaling — a single learned scalar — corrects it cheaply.

**When calibration is required**: whenever a downstream consumer treats
model output as a probability rather than a rank — a cost-sensitive
threshold/(C(FP)+C(FN))` requires calibrated probabilities), a probability
reported to a human, or an ensemble that averages scores across models.

**Method choice**:
- **Platt scaling** (Platt, 1999) — sigmoid fit on held-out scores; binary
  classification only; works well when the miscalibration is roughly
  sigmoidal (common for SVM-style margins).
- **Isotonic regression** — non-parametric, more flexible, needs more
  held-out data to avoid overfitting the calibration map itself.
- **Zadrozny & Elkan (2002)** extension for multiclass — Platt/isotonic as
  stated are binary-only; multiclass needs this extension or an
  equivalent, not a naive one-vs-rest patch assumed to work.
- **Temperature scaling** (Guo et al., 2017) — single-parameter, standard
  for neural network logits.

**Non-negotiable**: fit the calibration map on a held-out split, never the
training data the base model fit on — calibrating on train measures how
well the model fits its own training distribution, not miscalibration.

**Verification**: reliability curve (predicted probability vs. observed
frequency, binned), Brier score, or expected calibration error (ECE),
computed on a further held-out slice from the calibration data itself.

## Learning-curve / data-sufficiency method {#learning-curve}

Mohr & van Rijn (2022) survey learning curves as a decision tool: train on
increasing subsample sizes, plot the validation metric against N, and use
the curve's shape (still rising steeply vs. flattening) as evidence for
whether more data would help.

**When this subfield fires**: `ds-scoping`'s kill-check flagged sample
size as borderline-sufficient rather than clearly adequate or clearly
inadequate — this skill computes the curve `ds-scoping` only judged
whether to attempt.

**Method**:
1. Train the candidate (or the baseline, if the complex candidate is too
   expensive to refit repeatedly) at several subsample sizes (e.g. 10%,
   25%, 50%, 75%, 100% of the available train partition), each under the
   same CV scheme chosen above.
2. Plot metric vs. N. A curve still rising steeply at 100% is evidence more
   data would help; a flattened curve is evidence it likely wouldn't.
3. Do not over-read a noisy or non-monotonic curve at small N as a real
   trend — small-N points are high-variance, not a reliable slope estimate.
4. Extrapolation past the measured range (e.g. fitting a power-law curve
   to project performance at 2x current N) is explicitly a modeling
   assumption, not a measurement — `model_card` states the assumed
   parametric form when extrapolation is reported, and never presents an
   extrapolated number as if it were measured.
