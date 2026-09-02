---
name: ds-ranking
description: "Ranking and recommendation method/goal family: collaborative filtering/matrix factorization, cold start, implicit feedback; learning-to-rank; retrieval/search relevance; ranking evaluation (NDCG/MAP/MRR); position and presentation bias; off-policy/counterfactual evaluation application (identification: `ds-causal`)…"
---

# ds-ranking

Composes after `ds-features` writes the feature dictionary, alongside
`ds-model` (wraps this family's candidates in the cross-family selection
procedure — never itself picks an algorithm class). Full depth and
citations: `references/`; this file is protocol only.

## Subfields

- **Collaborative filtering / MF** — trigger: a user-item interaction
  matrix exists. tier: `analysis`. participation:
  `conditional-on-data:user-item-interaction-matrix`. Methods: latent-
  factor SVD-style MF, regularized MF with bias terms. Edges: sparse
  history is cold start, not an MF fix. See
  `references/ds-ranking.recommendation-methods.md#cf-mf`.
- **Cold start** — trigger: new/near-zero-history user or item. tier:
  `analysis`. participation: `conditional-on-data:cold-start-user-or-item`.
  Methods: content-based fallback, hybrid CF+content, exploration bootstrap
  (policy: `ds-optimize`). Edges: "wait for more data" restates the
  problem. See `references/ds-ranking.recommendation-methods.md#cold-start`.
- **Implicit feedback** — trigger: behavioral signal (clicks, views,
  dwell), not an explicit rating. tier: `analysis`. participation:
  `conditional-on-data:implicit-signal-only`. Methods: confidence-weighted
  implicit MF, all-pairs training. Edges: implicit-feedback trap gate,
  below — absence is not a confirmed negative. See
  `references/ds-ranking.recommendation-methods.md#implicit-feedback`.
- **Learning-to-rank** — trigger: orders a candidate list; a score alone
  is not this subfield. tier: `analysis`. participation:
  `conditional-on-data:ranked-candidate-list`. Methods: pairwise (RankNet),
  gradient-shaped listwise (LambdaRank), boosted-tree (LambdaMART). Edges:
  heuristic approximation — no exact-optimization claim. See
  `references/ds-ranking.ranking-and-retrieval.md#ltr`.
- **Retrieval/search relevance** — trigger: candidate set must be found
  from a corpus against a query, not just reordered. tier: `analysis`.
  participation: `conditional-on-data:query-document-retrieval`. Methods:
  vector-space/probabilistic relevance (classical), dense/embedding
  retrieval (on diagnosed vocabulary mismatch). Edges: an LLM-based
  encoder crosses into `ds-llm-systems` (Pairings). See
  `references/ds-ranking.ranking-and-retrieval.md#retrieval`.
- **Ranking evaluation (NDCG/MAP/MRR)** — trigger: any ranked output needs
  a quality metric. tier: `quick-answer`. participation: `mandatory`.
  Methods: NDCG, MAP, MRR, Precision@k/Recall@k. Edges: metric matches
  relevance-judgment shape (graded vs. binary) — a default pick is a
  silent choice. See `references/ds-ranking.ranking-and-retrieval.md#evaluation`.
- **Position and presentation bias** — trigger: training/eval data is
  logged production clicks/impressions, not neutral judgments. tier:
  `analysis`. participation: `conditional-on-data:logged-click-data`.
  Methods: cascade/examination position-bias models, interleaving. Edges:
  this is a gate, below, not an optional caveat. See
  `references/ds-ranking.bias-and-attribution.md#position-bias`.
- **Off-policy/counterfactual evaluation application** — trigger: would a
  *new* policy outperform the *logged* one, evaluated on its logs. tier:
  `analysis`. participation:
  `conditional-on-data:policy-change-evaluated-on-logs`. Methods:
  replay-based offline evaluation. See
  `references/ds-ranking.bias-and-attribution.md#ope`.
- **Attribution application with `ds-causal`** — trigger: which position/
  touchpoint "caused" a conversion. tier: `analysis`. participation:
  `conditional-on-data:credit-assignment-requested`. Methods:
  causally-motivated attribution reframing (vs. rule-based credit-split).
  Edges: logged impressions aren't randomized — pair with `ds-causal`
  before calling output "causal lift." See
  `references/ds-ranking.bias-and-attribution.md#attribution`.

## Selection tree

1. **Task shape.** Engagement over a catalog for known users, no
   per-request query → recommendation branch. A query exists per request
   → retrieval branch.
2. **(Recommendation) density + signal.** Dense history both sides,
   explicit ratings → collaborative filtering/MF. New/near-zero-history
   side → cold start (a different information source, not more CF
   signal). Behavioral-only signal → implicit-feedback confidence-weighted
   MF, gated by the implicit-feedback trap before any unobserved
   interaction is treated as negative.
3. **(Retrieval) candidate set state.** Already fixed, order is the ask →
   learning-to-rank. Must be found from a corpus → retrieval/search
   relevance; classical term-overlap first, escalate to dense/embedding
   only once vocabulary mismatch is diagnosed.
4. **(Either) judgment shape + data source.** Graded relevance → NDCG
   (state the discount function); binary only → MAP/MRR — never apply
   either to graded judgments without acknowledging discarded grade
   information. Logged clicks/impressions → position-bias correction or
   interleaving fires first; "would a new policy have done better" →
   off-policy/counterfactual evaluation, not a raw re-score.
5. **(Either) credit-assignment ask.** "Which touchpoint caused the
   conversion" → attribution application paired with `ds-causal` for
   identification — never resolved by ranking-side association alone.

## Family-specific pitfalls and evaluation

Pitfalls (full detail, citations: `references/`):

- Absence of interaction is not a negative preference — conflates
  disinterest with non-exposure. Ranking-specific form of the suite's
  PU-gate doctrine (`ds-labeling` § implicit negatives and PU learning);
  see Gates.
- Cold start's fix is a different information source, never "more of the
  same" collaborative signal. LambdaRank-family gradients empirically
  optimize NDCG-like metrics without a proven exact connection for all
  metric/loss pairs; classical term-overlap retrieval breaks on
  vocabulary-mismatch queries without flagging the gap dense retrieval
  closes.
- NDCG's discount is a modeling choice, not a derived fact; MAP/MRR
  silently discard graded-relevance information if misapplied.
- Raw CTR without position-bias correction favors already-top-ranked
  results — a training-data confound, not just an evaluation caveat.
- Off-policy replay is unbiased only if the logging policy's
  action-selection is known and has full support over evaluated actions.
  Attribution credit on unrandomized logged impressions is association,
  not causal lift, until paired with a `ds-causal` identification strategy.

## Gates

- **Implicit-feedback trap gate**: an unobserved (user, item) pair is a
  negative only if the `population_statement` (`ds-data-models`, Observe;
  doctrine home `doctrine-repro-provenance.md` § Population statements are
  composable artifacts) establishes exposure covered that item — absence
  alone fails. Ranking-specific form of `ds-labeling`'s PU-gate.
- **Position-bias gate**: logged click/impression data requires a stated
  position-bias correction or interleaving design before any CTR-derived
  quantity is reported as relevance — uncorrected raw CTR fails.
- **Cold-start gate**: records which alternate information source is used
  — "wait for more data" fails. **Evaluation-metric gate**: states graded
  vs. binary judgment shape explicitly. **LTR gate**: no claim of
  exact-metric optimization for a LambdaRank-family fit.
- **Off-policy gate**: states the logging policy's action-selection
  structure — an estimate without it fails.
- **Attribution gate**: output is labeled credit-assignment (association),
  never "causal lift," unless a `ds-causal` identification strategy is
  attached. Fit-on-train-only compliance (`ds-features`) — cited, not
  re-checked. Doctrine gates: leakage, provenance/additivity, scale/cost
  (`doctrine-leakage.md`, `doctrine-repro-provenance.md`,
  `doctrine-scale-cost.md`) — linked, not restated.

## Edges

Covered: collaborative filtering/MF, cold start, implicit feedback,
learning-to-rank, retrieval/search relevance, ranking evaluation, position/
presentation bias, off-policy/counterfactual evaluation application,
attribution application.

Not covered, pointer only: off-policy/counterfactual identification and
attribution causal identification (`ds-causal`); LLM-based retriever/judge
design and RAG-pipeline evaluation (`ds-llm-systems`); generic evaluation
scorecard (`ds-evaluate`); randomized experiment design (`ds-stats`);
cold-start bootstrap exploration policy (`ds-optimize`); fit-on-train-only
mechanics (`ds-features`).
