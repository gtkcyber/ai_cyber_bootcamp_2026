---
name: ds-timeseries
description: "Time-series method family: forecasting, decomposition, stationarity, backtesting protocol, temporal cross-validation (performance-estimation method selection), the temporal delta on data leakage, and temporal/contextual anomaly detection. Owns the split/validation scheme whenever composed with another family on…"
---

# ds-timeseries

## Subfields

- **Forecasting** — trigger: "predict/forecast a future value of this
  series". Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*
  (3rd ed) — https://otexts.com/fpp3/ : the standard cross-disciplinary
  method-selection reference. A point forecast without an interval
  understates uncertainty (coverage claim: `ds-uncertainty`); method choice
  must match the series' actual trend/seasonality pattern, not be picked by
  default.
- **Decomposition** — trigger: "separate trend/seasonal/residual" or a
  forecasting method needs seasonal structure characterized first. Hyndman &
  Athanasopoulos, Ch. 3 — https://otexts.com/fpp3/decomposition.html — and
  Cleveland et al., "STL: A Seasonal-Trend Decomposition Procedure Based on
  Loess," *J. Official Statistics* 6(1), 1990 —
  https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/stl-a-seasonal-trend-decomposition-procedure-based-on-loess.pdf
  : components are estimated, not observed; additive vs. multiplicative form
  must match whether seasonal amplitude scales with the level — the wrong
  form biases every downstream forecast built on it.
- **Stationarity** — trigger: a classical model (ARIMA-family) is in play, or
  the series shows drifting level/variance. Hyndman & Athanasopoulos, §9.1 —
  https://otexts.com/fpp3/stationarity.html : stationarity is a property of
  the process, not confirmed by eyeballing one realization; fitting a
  stationarity-assuming model on undifferenced non-stationary input produces
  spurious fit quality.
- **Backtesting protocol** — trigger: any forecast performance number is
  about to be reported. Hyndman & Athanasopoulos, §5.10 "Time series
  cross-validation" — https://otexts.com/fpp3/tscv.html : rolling-origin
  evaluation (a series of expanding/rolling train/test splits) is the
  standard, against a single fixed split. Window cadence must match real
  deployment retraining cadence, not be chosen for evaluation convenience.
- **Temporal CV (performance-estimation method selection)** — trigger:
  choosing *among* forecasting methods, not just reporting one method's
  error. Cerqueira, Torgo, Mozetic, "Evaluating Time Series Forecasting
  Models," arXiv:1905.11744, 2019 — https://arxiv.org/abs/1905.11744 :
  empirically compares out-of-sample vs. CV-style estimators for forecasting
  evaluation; findings are empirical and dataset-dependent, not proof any one
  CV variant is universally safe for serially dependent data.
- **Temporal leakage delta** — trigger: any fold/split touches serially
  dependent data. This family's delta on `doctrine-leakage.md` (link, not
  restated): reuses Hyndman & Athanasopoulos §5.10 and Cerqueira et al.
  (above) — k-fold CV that shuffles across time silently trains on
  information from after a given test point; the delta from the general
  leakage entry is that **temporal order, not row independence, is the
  leakage boundary** here.
- Blázquez-García, Conde, Mori, Lozano, "A Review on Outlier/Anomaly
  Detection in Time Series Data," arXiv:2002.04236, 2020 —
  https://arxiv.org/abs/2002.04236 : point outliers, subsequence outliers,
  and outlier time series require different detector families (that survey's
  own taxonomy). The complementary general framing — contextual anomalies (a
  normal value at an abnormal time) — is Chandola, Banerjee & Kumar 2009's
  taxonomy, not Blázquez-García's; a point-anomaly detector misses both
  contextual and subsequence-level anomalies.

|---|---|---|---|
| Forecasting | quick-answer | yes, re-entrant when horizon changes | `mandatory` |
| Decomposition | quick-answer | no | `conditional-on-data:seasonal-structure-suspected` |
| Stationarity | quick-answer | no | `conditional-on-data:classical-model-in-play` |
| Backtesting protocol | analysis | yes, re-entrant per reported metric | `mandatory` |
| Temporal CV (method selection) | analysis | no | `conditional-on-data:multiple-candidate-methods` |
| Temporal leakage delta | quick-answer | yes, always-composed wherever any fold touches this data | `mandatory` |
| Temporal/contextual anomaly detection | analysis | no | `conditional-on-family:anomaly-intent` |

`mandatory` here means: fires whenever `ds-timeseries` composes at all, same
convention as `ds-gather`'s selection-into-the-dataset row.

## Selection tree

1. **Task intent**: forecast a future value, characterize current structure,
   or flag anomalous behavior?
   - Anomaly intent → **temporal/contextual anomaly detection**: point
     outlier (single observation), subsequence outlier, or an entire outlier
     series (Blázquez-García et al.)? Add the contextual lens (normal value,
     abnormal time — Chandola et al. 2009) before picking a detector family —
     don't reuse a point-anomaly detector for a contextual or subsequence ask.
   - Forecast or structure intent → continue.
2. **Framing**: forecast the series directly with time-series-native methods,
   or reframe as supervised regression on lagged/rolling features (tabular
   estimator, `ds-supervised` territory)? Neither framing is a default —
   state the choice in the framing note. If reframed as tabular,
   `ds-timeseries` still leads the split (see Pairings/Edges).
3. If forecasting directly: is the series (or the differenced series)
   **stationary**? Non-stationary + a stationarity-assuming model class
   requires differencing first (**stationarity**).
4. Does the series carry seasonal/trend structure that a forecasting method
   needs isolated first? → **decomposition**, additive or multiplicative
   per whether seasonal amplitude scales with level.
5. Reporting one method's performance, or choosing among several? One method
   → **backtesting protocol** (rolling-origin). Choosing among candidates →
   **temporal CV** on top of the same rolling-origin scheme.
6. Every fold/split touched by 3–5 above is governed by the **temporal
   leakage delta** — no exceptions for "just this once."

## Family-specific pitfalls and evaluation

- **Backtest overfitting** (general form; the finance overlay's delta lands
  on this pitfall, not restated here): repeatedly tuning method or
  hyperparameters against the same rolling-origin windows inflates the
  reported metric the same way repeated train-metric peeking does under
  general leakage doctrine — the temporal-specific form is multiple testing
  over a fixed set of origins. Fresh/held-back origins, not just more
  origins, are what recovers a trustworthy estimate.
- **Non-stationarity severity** (general form; finance overlay owns the
  delta): the *degree* of non-stationarity — not just its presence — governs
  which methods stay valid; a mildly drifting mean tolerated by one model
  class can invalidate another. State the severity, not a binary
  stationary/non-stationary flag.
- **Evaluation delta on `ds-evaluate`'s generic scorecard**: forecast
  accuracy is computed per backtest fold and reported as a distribution
  across origins, never a single holdout number — see backtesting protocol.
  Interval-coverage claims are `ds-uncertainty`'s (prediction intervals,
  conformal methods); this family states the point-forecast error only.

## Gates

- Fit-on-train-only (`ds-features` ownership) applies to every
  family-specific transform here: differencing parameters, decomposition
  window/seasonal-period estimates, and any lag/rolling-feature statistic
  are estimated on the train side of the current backtest fold only, never
  on the full series before splitting.
- Every reported forecast metric states its rolling-origin scheme
  (expanding or rolling, window size, step, number of origins) — a metric
  from a single fixed split reported as final performance fails this gate.
- Every fold/split touching this data states how it respects temporal
  order (link `doctrine-leakage.md`, delta per Subfields above) — a
  shuffled or globally-random fold assignment fails this gate outright, not
  just as a caveat.
- When this family leads a multi-family split (see Pairings), the imposed
  scheme is recorded once and every composed family's evaluation cites it —
  a composed family computing its own independent split on the same
  temporally-ordered data fails this gate.
- Doctrine gates this family triggers, linked not restated: leakage
  (`doctrine-leakage.md`), provenance/additivity and scale/cost per router
  doctrine.

## Edges

Covered: forecasting method selection, decomposition, stationarity
diagnosis, backtesting protocol, temporal CV for method selection, the
temporal leakage delta, and temporal/contextual anomaly detection mechanics.

Not covered: sequence-model architecture and training mechanics (LSTM/
Transformer-class forecasters) once a neural framing is chosen — outside
this family's cited coverage; research external sources, verify the found
method's stationarity/seasonality assumptions against the actual data, and
report provenance before adopting one, then hand training mechanics to
`ds-deep-learning`. Finance-specific severity thresholds on backtest
overfitting and non-stationarity are the finance overlay's delta, not
re-derived here.

On temporally-ordered data composed with `ds-supervised` or `ds-graph`,
`ds-timeseries` owns the strongest constraint and imposes: **rolling-origin
evaluation** (expanding or rolling window, per Hyndman & Athanasopoulos
§5.10), with an **embargo/purge gap** between each fold's train and
validation windows sized to the longest look-ahead in any composed feature
or label (lag features, rolling windows, label horizons) — never a shuffled
or globally-random split, regardless of what the composed family would
otherwise default to. Composed with `ds-geospatial` on spatiotemporal data,
the strongest- constraint rule decides per-task by measurement: diagnose
both ranges on the actual data, express each as the fraction of candidate
train rows its block/embargo excludes, the more-excluding constraint leads
and the other nests within each block; near-ties (within ~10%) block on both
jointly. Full procedure (identical wording): `ds-geospatial`'s Edges. The
framing note records both measured ranges, both fractions, and the scheme.
