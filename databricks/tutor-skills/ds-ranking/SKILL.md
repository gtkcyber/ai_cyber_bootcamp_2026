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

- Methods: latent- factor SVD-style MF, regularized MF with bias terms.
  Edges: sparse history is cold start, not an MF fix. See
  `references/ds-ranking.recommendation-methods.md#cf-mf`.
- Methods: content-based fallback, hybrid CF+content, exploration bootstrap
  (policy: `ds-optimize`). Edges: "wait for more data" restates the problem.
  See `references/ds-ranking.recommendation-methods.md#cold-start`.
- Methods: confidence-weighted implicit MF, all-pairs training. Edges:
  implicit-feedback trap gate, below — absence is not a confirmed negative.
  See `references/ds-ranking.recommendation-methods.md#implicit-feedback`.
- Methods: pairwise (RankNet), gradient-shaped listwise (LambdaRank),
  boosted-tree (LambdaMART). Edges: heuristic approximation — no
  exact-optimization claim. See `references/ds-ranking.ranking-and-retrieval.md#ltr`.
- Methods: vector-space/probabilistic relevance (classical), dense/embedding
  retrieval (on diagnosed vocabulary mismatch). Edges: an LLM-based encoder
  crosses into `ds-llm-systems` (Pairings). See
  `references/ds-ranking.ranking-and-retrieval.md#retrieval`.
- **Ranking evaluation (NDCG/MAP/MRR)** — trigger: any ranked output needs
  a quality metric. tier: `quick-answer`. participation: `mandatory`.
  Methods: NDCG, MAP, MRR, Precision@k/Recall@k. Edges: metric matches
  relevance-judgment shape (graded vs. binary) — a default pick is a
  silent choice. See `references/ds-ranking.ranking-and-retrieval.md#evaluation`.
- Methods: cascade/examination position-bias models, interleaving. Edges:
  this is a gate, below, not an optional caveat. See
  `references/ds-ranking.bias-and-attribution.md#position-bias`.
- Methods: replay-based offline evaluation. See
  `references/ds-ranking.bias-and-attribution.md#ope`.
- Methods: causally-motivated attribution reframing (vs. rule-based
  credit-split). Edges: logged impressions aren't randomized — pair with
  `ds-causal` before calling output "causal lift." See
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

**Evaluation delta.** `ds-evaluate` owns the generic scorecard; this
family's delta is NDCG/MAP/MRR by relevance-judgment shape, position-bias
correction or interleaving before any logged-click metric is reported
unbiased, and off-policy estimates reported alongside the logging policy's
exploration structure.
