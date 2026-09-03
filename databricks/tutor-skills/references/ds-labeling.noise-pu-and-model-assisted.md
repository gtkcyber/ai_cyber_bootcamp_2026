# Noise, PU learning, and model-assisted labeling

Depth for the three subfields concerned with what happens when labels are
imperfect, absent-but-not-negative, or partly produced by a model. SKILL.md
carries the protocol; this file carries worked detail and full citations.

## Label delay and noise {#noise}

**Literature**: learning with noisy labels — Song et al., "Learning from
Noisy Labels with Deep Neural Networks: A Survey," IEEE TNNLS 2022 —
https://arxiv.org/pdf/2007.08199 : surveys 60+ robust-training methods
built on the finding that deep nets, given enough capacity and epochs,
memorize noisy labels rather than generalizing past them.

- **Noise structure matters.** Uniform/random label noise (each label
  flipped independently with fixed probability) is the easy, and least
  realistic, case. Real noise is usually **class-conditional** (some
  classes are confused more than others — visually similar categories,
  adjacent severity tiers) or **instance-dependent** (harder/ambiguous
  items are more likely mislabeled regardless of class). State which
  structure is suspected before picking a noise-robust training method —
  a method designed for uniform noise underperforms on class-conditional
  or instance-dependent noise it wasn't built for.
- **Delay is a distinct, adjacent problem.** A label arriving late relative
  to the prediction it evaluates (fraud confirmed 60 days after the
  transaction; churn confirmed only at contract renewal) is not noise —
  it's a *timing* problem. Static noisy-label methods don't address it.
  Delay means: (a) the training set is systematically missing recent
  outcomes at any snapshot, and (b) evaluation against "current" labels
  undercounts events still in their confirmation window. Both must be
  stated in the protocol, not silently absorbed into "some labels are
  probably still pending."
- Robust-training countermeasures (loss reweighting, label smoothing,
  sample selection) that consume a characterized noise profile are
  `ds-model`'s job — this subfield characterizes and states the noise
  structure and delay window, it does not select or tune the countermeasure.

## Implicit negatives and PU learning {#pu-learning}

**Literature**: positive-unlabeled (PU) learning. Elkan & Noto, "Learning
Classifiers from Only Positive and Unlabeled Data," KDD 2008 —
https://cseweb.ucsd.edu/~elkan/posonly.pdf : under **SCAR** (Selected
Completely At Random — labeled positives are a uniform random subset of
all true positives), a classifier trained to distinguish labeled-positive
from unlabeled data produces scores that rescale into a calibrated
`P(y=1|x)` via a single constant (the labeling frequency `c`). Bekker &
Davis, "Learning from Positive and Unlabeled Data: A Survey," *Machine
Learning* 109, 2020 — https://arxiv.org/pdf/1811.04820 : organizes the
field around cases where SCAR does not hold (labeling propensity varies
with `x` — the common real case: easier-to-detect positives get labeled
more often).

**The gate, restated precisely** (SKILL.md Gates carries the
code-checkable form): a negative class is not "everything not positively
labeled." It is only a valid negative if the label-generating process —
the actual mechanism that would have produced a positive label had the
true outcome been positive — was operating over that item and would have
caught it. That claim is exactly what a **population statement**
(`ds-data-models`, Observe: "contains X, collected by Y, subject to Z")
states for a dataset. So: `labeling_protocol` cites the specific
`population_statement` clause establishing that the label-generating
process covered the item space being treated as negative.

Worked example of what passes and fails the gate:

- **Fails**: "Users who never filed a fraud claim are labeled non-fraud."
  Unless the population statement establishes that *all* fraud, had it
  occurred, would have generated a claim (it doesn't — unreported fraud
  exists) — this is unlabeled treated as negative, not a defensible
  negative class.
- **Passes**: "Transactions that completed a 90-day chargeback window with
  no chargeback filed are labeled non-fraud, citing the population
  statement that the chargeback process captures all disputed transactions
  processed through this gateway within that window." The population
  statement's coverage claim is what makes absence informative.

Where SCAR plausibly holds (the passing case above, if the labeled
positives are also a representative random draw of all positives, not
just "any positive found"), Elkan & Noto's rescaling can be used to
calibrate. Where it doesn't (positives are labeled preferentially because
they're easier to detect, more severe, or self-reported), calibration
breaks and Bekker & Davis's non-SCAR methods are the reference to consult
next — that consultation is out of this subfield's authored scope, it
names the violation and routes it, per SKILL.md Edges.

## Model-assisted labeling {#model-assisted}

`ds-method-composition` points here rather than re-teaching.
LLM-judge/labeler *design mechanics* — prompt/rubric construction,
calibration against a rubric — are `ds-llm-systems`'; this subfield still
owns whether the resulting labels are trustworthy and how they're audited.

**Literature**: human-in-the-loop / semi-automated annotation. Desmond et
al., "Semi-Automated Data Labeling," PMLR v133 (NeurIPS 2020 Competition
track) — http://proceedings.mlr.press/v133/desmond21a/desmond21a.pdf : a
model suggests labels for human review; items above a confidence threshold
auto-label without review; the model retrains/improves from the human
corrections it does receive, iterating.

The load-bearing failure mode, and why the audit requirement is
non-negotiable (SKILL.md Gates, Production considerations): **model
confidence is not a correctness proxy under distribution shift.** A model
that is well-calibrated on the distribution it was validated against can
be confidently wrong on drifted inputs — and because auto-accepted labels
skip human review by construction, a confidently-wrong labeler compounds
its own errors into the next training round with no natural circuit
breaker. Two concrete requirements the protocol must state, not just
imply:

1. **Confidence threshold ≠ correctness threshold** — the threshold above
   which items auto-label is a throughput/cost tradeoff the protocol
   states explicitly, not a claim that items above it are correct.
2. **Periodic re-audit of auto-accepted labels**, on an ongoing cadence
   (not a one-time check at protocol authorship) — pull a sample of
   auto-accepted labels, get an independent (human or higher-trust) read,
   and measure agreement the same way `acquisition-and-agreement.md#agreement`
   measures any inter-annotator agreement. A protocol with an auto-labeling
   threshold and no re-audit cadence has described a labeling mechanism,
   not a quality-controlled one.
