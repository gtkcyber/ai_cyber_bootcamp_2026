---
name: ds-method-composition
description: "The method-composition hook: any skill consults this before escalating to external research when it hits its own limit (\"imputation too crude,\" \"single detector too weak,\" \"LLM output untrusted\"). Pattern grammar — model-as-imputer, model-as-feature-extractor, residual-as-signal, detector ensembles/voting…"
---

# ds-method-composition

Full depth, worked examples, and citations live in `references/`; this file
is protocol only.

Every method has typed inputs and outputs — labels, scores, residuals,
embeddings, clusters, graph measures, forecasts — and composition wires one
method's output to another's input: pattern grammar, not technique
enumeration. Recognize which pattern applies; the owning family/lifecycle
skill supplies the actual method inside each component. **Central
doctrine**: every component keeps its own leakage boundary — the delta this
skill states on `references/doctrine-leakage.md`'s "generators fit train-only" rule (a
model-as-imputer fit on the full dataset, not just train, leaks into every
downstream split consuming its output).

## Subfields

- **Model-as-imputer** — trigger: "imputation too crude." van Buuren &
  Groothuis-Oudshoorn, "mice," JSS 45(3), 2011 —
  https://www.jstatsoft.org/article/view/v045i03 . Fit train-only,
  provenance degrades to `derived`, uncertainty propagates forward rather
  than collapsing to a point estimate (`ds-uncertainty`, Rubin's rules).
  See `references/ds-method-composition.composition-patterns.md#model-as-imputer`.
- **Model-as-feature-extractor (stacking)** — trigger: "single model too
  weak," a model's own output (graph measure, cluster ID, embedding,
  forecast, base-model prediction) proposed as a feature into another
  model. Wolpert, "Stacked Generalization," 1992 —
  http://machine-learning.martinsewell.com/ensembles/stacking/Wolpert1992.pdf .
  Combiner trains only on out-of-fold level-0 predictions — in-sample
  predictions teach it to trust whichever base model overfit hardest. See
  `references/ds-method-composition.composition-patterns.md#model-as-feature-extractor`.
- **Residual-as-signal** — trigger: an expected-behavior model's forecast
  error, not its output, proposed as an anomaly/drift feature. Vallis,
  Hochenbaum, Kejariwal, "Automatic Anomaly Detection in the Cloud," 2017
  — https://arxiv.org/abs/1704.07706 . The residual is only as meaningful
  as the expected-behavior model's own assumptions — mis-specified
  seasonality/trend biases the "anomaly" flags. See
  `references/ds-method-composition.composition-patterns.md#residual-as-signal`.
- **Detector ensembles / voting** — trigger: "single detector too weak,"
  no ground truth to validate a combination rule. Zimek, Campello, Sander,
  "Ensembles for Unsupervised Outlier Detection," 2014 —
  https://www.kdd.org/exploration_files/V15-01-02-Zimek.pdf . Diversity
  helps only if member errors aren't correlated — not automatic when
  detectors share a feature space. See
  `references/ds-method-composition.composition-patterns.md#detector-ensembles`.
- **Model-as-verifier / guardrail cascade** — trigger: "LLM output
  untrusted" — a cheap classic check gates an expensive generative model's
  output. Chen, Zaharia, Zou, "FrugalGPT," 2023 —
  https://arxiv.org/abs/2305.05176 ; Viola & Jones, "Boosted Cascade of
  Simple Features," 2001 —
  https://www.cs.cmu.edu/~efros/courses/LBMV07/Papers/viola-cvpr-01.pdf .
  See `references/ds-method-composition.guardrail-cascades.md#model-as-verifier`.
- Pointer only.

## Selection tree

What limit did the escalating skill name?

- "point-estimate imputation understates uncertainty" → **model-as-imputer**.
- "a fitted expected-behavior model's deviation, not its output, is the
  signal" → **residual-as-signal**.
- "no single detector/model reliable, no ground truth to pick a winner" →
  **detector ensembles / voting**; check diversity before combining —
  same-feature-space detectors trained the same way aren't diverse.
- "generative/expensive output needs a cheap check before it ships or
  before an expensive escalation" → **guardrail cascade**; needs a
  stated, calibrated escalation criterion.
- "a model should assign or suggest the label itself" → `ds-labeling`.

More than one pattern applies (e.g. an ensemble whose combiner is itself
a stacked model) → compose both, one diagram node per method — patterns
nest, not collapse.

## Family-specific pitfalls and evaluation

Pitfalls specific to composition (generic leakage/provenance doctrine is and
linked, not restated):

- **Uncertainty collapse.** A composed point-estimate output (imputed
  value, residual, ensemble score) is treated downstream as certain as an
  observed value — imputation uncertainty must propagate, not collapse.
- **In-sample stacking leak.** A combiner trained on in-sample level-0
  predictions learns to trust overfitting, not generalization — silent,
  since training accuracy looks fine and only holdout exposes it.
- **Assumed diversity / cascade overconfidence.** Combination rules
  assume member errors are uncorrelated, and a cheap stage's confidence
  score is treated as its calibration, without checking either — a
  shared feature space correlates "different" algorithms, and an
  uncalibrated stage is silently wrong exactly when it matters most.

Evaluation delta from `ds-evaluate`'s generic scorecard: every component
is evaluated **both** stand-alone **and** as wired — the composition's
end-to-end output must improve on its strongest single component, not
merely differ from it, or the composition has failed regardless of how
principled the wiring.
