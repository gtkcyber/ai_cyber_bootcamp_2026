# Synthetic and privacy-preserving generation

Depth for the five generation subfields. SKILL.md carries the protocol;
this file carries worked detail and full citations.

## Synthetic data generation and its validation {#synthetic}

**Literature**: deep generative modeling of tabular data — Xu,
Skoularidou, Cuesta-Infante & Veeramachaneni, "Modeling Tabular Data Using
Conditional GAN" (CTGAN), NeurIPS 2019 —
https://arxiv.org/abs/1907.00503 (fetched, abstract confirmed).

The paper's own motivation: "existing statistical and deep neural network
models fail to properly model" mixed discrete/continuous, multi-modal
tabular columns. Two lessons follow directly:

- **Marginal fidelity ≠ joint fidelity.** A generator validated only on
  per-column distribution match can still fail to preserve correlations
  between columns or rare joint-category structure. "Looks realistic
  column-by-column" and "preserves the properties downstream analysis
  depends on" are different claims — validate both explicitly:
  - **Marginals**: per-column distributional match (e.g., KS-test-style
    comparison per numeric column, category-frequency comparison per
    categorical column).
  - **Correlations**: pairwise (or higher-order) relationship preservation
    — a generator can nail every marginal while destroying the
    correlation structure that made the dataset useful.
  - **Constraint satisfaction**: domain constraints (referential
    integrity, valid ranges, mutually exclusive categories) hold in the
    generated rows — a generator with no constraint awareness can produce
    individually plausible but jointly impossible rows.
- Simpler parametric or copula-based generators remain appropriate for
  lower-stakes needs (e.g., a quick test fixture) — CTGAN-class deep
  generative modeling is the escalation when marginal/simple-parametric
  approaches demonstrably fail to capture the joint structure that
  matters for the task at hand, not a default starting point.

**Edge**: this subfield owns *validation*, regardless of which generator
produced the rows — including generators built by `ds-deep-learning` for
non-tabular modalities (images, audio, text), where architecture and
training mechanics are `ds-deep-learning`'s but property-preservation
validation still routes here when the generated data feeds a downstream
analytical or modeling task.

## Imbalance augmentation mechanics {#imbalance}

**Literature**: SMOTE (Synthetic Minority Over-sampling Technique) —
Chawla, Bowyer, Hall & Kegelmeyer, *Journal of Artificial Intelligence
Research* 16, 2002 — https://www.jair.org/index.php/jair/article/view/10302
(fetched, existence confirmed; open access).

**Mechanic**: for each minority-class point, interpolate new synthetic
points between it and its k-nearest minority-class neighbors in feature
space.

**Key failure mode**: in high-dimensional or noisy feature space,
interpolated points can land inside the majority-class region (class
overlap) — this manufactures label noise rather than signal, the opposite
of the intended effect. SMOTE is a **data-level intervention** and
competes with, rather than automatically beats, algorithm-level
interventions (class weighting, threshold adjustment) — `ds-model` decides
whether/how much to intervene and at which level; this subfield only
executes the chosen data-level mechanic.

**Leakage discipline**: SMOTE-class methods must run **after** the train/
test split, on the train side only. Applying it before the split lets
near-duplicate synthetic neighbors of a single real point land on both
sides of the split — the model then effectively "sees" near-copies of its
own test points during training, inflating apparent performance.

## Privacy-preserving generation {#privacy}

**Literature**: differentially private generative adversarial networks —
Xie, Lin, Wang, Wang & Zhou, "Differentially Private Generative Adversarial
Network," 2018 — https://arxiv.org/abs/1802.06739 (fetched, existence
confirmed).

**Mechanic**: DP-SGD-style noise injection during generator training,
calibrated to a stated privacy budget (ε, δ) under a formal differential-
privacy definition — output indistinguishability bounded by the budget,
regardless of what an adversary knows or does with the released data.

**Key failure mode — composition**: the privacy guarantee is only as
strong as the stated budget *and* holds only if the budget accounting
covers every training step's noise contribution. A system that adds noise
per-step without accounting for the **total** privacy cost across all
steps (composition) silently exceeds its claimed ε — the released
guarantee is then false, not merely weaker than stated. Any entry claiming
"differentially private" without a stated (ε, δ) and an explicit
composition accounting is an unverifiable claim, not a verified one.

**Boundary**: this subfield executes a privacy-protection mechanic already
decided upon (what standard to meet, i.e. a target ε). It does not decide
what must be protected or to what standard — that decision is out of
scope for the entire suite. Masking/anonymization of *real* records
(k-anonymity-style generalization/suppression, hashing) is `ds-clean`'s;
this subfield's mechanics apply only to generating new, synthetic rows.

## Re-identification risk measurement {#reid}

**Literature**: population-uniqueness-based re-identification risk
estimation — Rocher, Hendrickx & de Montjoye, "Estimating the Success of
Re-identifications in Incomplete Datasets Using Generative Models," *Nature
Communications* 10, 3069, 2019 —
https://www.nature.com/articles/s41467-019-10933-3 (fetched, full text
confirmed; open access).

**Central finding**: the paper's model estimates population uniqueness
accurately even from a **1% population sample** — directly rejecting two
common justifications for weak anonymization: that re-identification isn't
a practical risk, and that releasing only a partial/sampled dataset
provides "plausible deniability." "We only released a sample" is not, by
itself, a privacy defense.

**Mechanic**: estimate how uniquely identifiable individuals are within
the released (or generated) data given a set of quasi-identifying
attributes, using a generative model of the population distribution rather
than requiring the true population data itself.

**Edge**: this subfield measures risk; it does not decide what risk level
is acceptable for release — that threshold is a policy decision consumed
by, not made in, this skill.

## Privacy-utility tradeoff measurement {#privacy-utility}

**Literature**: synthetic-data privacy-utility evaluation — Stadler,
Oprisanu & Troncoso, "Synthetic Data — Anonymisation Groundhog Day,"
USENIX Security 2022 — https://arxiv.org/abs/2011.07018 (fetched, abstract
confirmed).

**Headline result**: synthetic data does not, in general, provide a better
privacy-utility tradeoff than traditional anonymization. "It's synthetic,
so it's private" is an unsupported claim on its own — privacy gain must be
quantitatively evaluated against inference/linkage attacks per release.

**Reporting discipline**: report the **privacy-utility curve** — utility
(measured against a named downstream task/metric) at each point along the
privacy-budget spectrum — never a single "utility preserved" number and
never a single privacy-risk number in isolation. A report that states
utility without naming the specific downstream task/metric it was measured
against fails the same discipline `ds-clean`'s utility-loss measurement
enforces for masking transforms on real data (`references/
privacy-transforms.md#utility-loss` in that skill). This subfield does not
decide which point on the curve is acceptable — that is the consumer's
policy decision, informed by the curve this subfield produces.
