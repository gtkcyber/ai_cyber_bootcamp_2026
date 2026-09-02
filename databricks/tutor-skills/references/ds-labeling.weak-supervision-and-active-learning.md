# Weak supervision and active learning

Depth for the two labeling-strategy subfields that decide *what gets
labeled how*, rather than measuring quality after the fact. SKILL.md
carries the protocol; this file carries worked detail and full citations.

## Weak supervision {#weak-supervision}

**Literature**: weak supervision / data programming — Snorkel is the
canonical system. Ratner et al., "Snorkel: Rapid Training Data Creation
with Weak Supervision," VLDB 11(3), 2017 —
https://arxiv.org/pdf/1711.10160 : labeling functions (LFs) — small,
noisy, programmatic heuristics, each voting label/abstain per item — are
combined via a generative model that learns each LF's accuracy and
correlations, denoising the combined vote without any ground truth.

Mechanics that gate (SKILL.md Gates, `attest_id`):

- Each labeling function encodes a claim about what a record's fields
  *mean* — "if `field.X` matches pattern `P`, this item is class `C`."
  That claim is a record-semantic claim in the sense `ds-data-models`'
  Attest register formalizes: it asserts something the record supposedly
  proves. **Every LF cites the `attest_id`** that backs its semantic
  reading of the fields it inspects. An LF built on a field whose meaning
  was never registered (no Attest entry, no semantic-dictionary entry) is
  encoding an unverified guess as a label source.
- The denoising model's core assumption is **conditional independence of
  LFs given the true label** (or explicitly modeled correlation structure,
  where Snorkel's dependency-learning mode is used). LFs that are silently
  correlated — e.g., three LFs all keying off the same underlying signal
  phrased three ways — bias the learned per-LF accuracy weights upward as
  a group. State which LFs share an underlying signal before combining;
  don't rely on the generative model to discover it unassisted at small
  LF counts.
- Coverage and conflict are reportable quantities, not afterthoughts: what
  fraction of items got zero LF votes (abstained on by everything —
  uncovered, needs another route), and what fraction got conflicting votes
  (needs adjudication or a stronger LF, not a coin-flip tiebreak).

Weak supervision produces training labels; it does not, by itself, produce
an evaluation set — a held-out slice with independently-sourced (human or
otherwise higher-trust) labels is required to validate the denoised output
before trusting it, same as any other label-acquisition path.

## Active learning {#active-learning}

**Literature**: query-strategy survey — Settles, "Active Learning
Literature Survey," University of Wisconsin-Madison CS TR 1648 —
https://burrsettles.com/pub/settles.activelearning.pdf. Standard
query-selection families:

- **Uncertainty sampling** — query items the current model is least
  confident about (margin, entropy, or least-confidence scoring).
- **Query-by-committee** — train multiple models, query items where they
  disagree most.
- **Expected model change / expected error reduction** — query items
  predicted to most reduce future loss or most change model parameters if
  labeled — more expensive per query, sometimes worth it under a tight
  label budget.

Two failure modes that gate the strategy choice, not just note it:

- **Query distribution ≠ deployment distribution.** The active-learning loop
  selects *which* items get labeled next based on the current model's
  weaknesses — that selection process itself can bias the resulting training
  set away from the distribution the deployed model will actually see. State
  what population the query strategy is drawing from and whether it matches
  the intended scoring population; if it doesn't, the resulting label set
  inherits a selection mechanism the way any other non-random draw does.
- **Noisy-oracle degradation.** Most query strategies assume the labeler
  answering the query is accurate. Under a noisy oracle (crowd, imperfect
  heuristic, distracted annotator), uncertainty-sampling in particular can
  waste budget repeatedly querying items the oracle will mislabel anyway —
  pair active learning with the annotation-quality subfield
  (`acquisition-and-agreement.md#agreement`), not run it blind to
  annotator reliability.

Active learning decides label *order and priority* under a budget
constraint; it does not change what a label means once collected — quality
measurement and gating (weak-supervision `attest_id` citation, PU-learning
gate) apply identically to actively-selected labels.
