# Ranking and retrieval

Full depth and citations for learning-to-rank, retrieval/search relevance,
and ranking evaluation. `SKILL.md` states triggers and dispatch fields
only; this file carries the method detail.

## Learning-to-rank {#ltr}

**Literature name**: matches spec — pairwise/listwise ranking objectives,
the RankNet/LambdaRank/LambdaMART family.

**Canonical methods**: pairwise cross-entropy (RankNet), gradient-shaping
toward a target ranking metric (LambdaRank), boosted-tree implementation
(LambdaMART); listwise losses as the alternative to pure pairwise framing
when list-level context matters.

**Source**: Burges, "From RankNet to LambdaRank to LambdaMART: An
Overview," Microsoft Research Technical Report MSR-TR-2010-82 —
https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/MSR-TR-2010-82.pdf.
Traces the lineage from pairwise cross-entropy through gradient-shaping for
a target metric to a boosted-tree implementation.

**Failure mode**: LambdaRank-style gradients are a heuristic approximation
that empirically optimizes NDCG-like metrics — there is no proven direct
connection to them for all metric/loss pairs. Don't claim exact metric
optimization from a LambdaRank-family fit; state it as an empirically
effective heuristic. Pairwise objectives alone ignore list-level context
that a listwise loss captures — that's a scope choice to state, not an
oversight to silently accept.

## Retrieval / search relevance {#retrieval}

**Literature name**: information retrieval — classical relevance ranking,
distinct from recommender collaborative filtering (`#cf-mf` in
`references/ds-ranking.recommendation-methods.md` assumes a user-item interaction matrix;
retrieval assumes a query against a document/item corpus).

**Canonical methods**: vector-space and probabilistic relevance models,
inverted-index retrieval, as the classical baseline; dense/embedding
retrieval as the escalation once vocabulary mismatch is diagnosed.

**Source**: Manning, Raghavan & Schütze, *Introduction to Information
Retrieval*, Cambridge University Press, 2008 —
https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf. Standard
reference for the vector-space/probabilistic relevance models, indexing,
and evaluation underlying modern search relevance.

**Failure mode**: classical relevance models assume query-document term
overlap *is* the relevance signal. This breaks down for vocabulary-mismatch
queries (synonyms, paraphrase, cross-lingual) — exactly the regime dense/
embedding retrieval was built to address. Don't present the classical model
as sufficient once vocabulary mismatch is diagnosed in the query
population; escalating to dense retrieval crosses into embedding-model
territory (`ds-llm-systems` when the retriever/encoder is LLM-based — see
`SKILL.md` Pairings).

## Ranking evaluation (NDCG/MAP/MRR) {#evaluation}

**Literature name**: matches spec.

**Canonical methods**: (Normalized) Discounted Cumulative Gain — graded
relevance with a logarithmic position discount; Mean Average Precision and
Mean Reciprocal Rank — binary-relevance metrics.

**Source**: Järvelin & Kekäläinen, "Cumulated Gain-Based Evaluation of IR
Techniques," ACM TOIS 20(4), 2002 —
https://www.cc.gatech.edu/~zha/CS8803WST/dcg.pdf. Defines (N)DCG as an
alternative to binary-relevance metrics that can't express "somewhat
relevant."

**Failure mode**: NDCG's log-position discount is a modeling choice about
user attention decay, not a derived fact — different discount functions
produce different system rankings on the same data, so the discount choice
is stated, not defaulted silently. MAP/MRR assume binary relevance and
silently discard graded-relevance information when applied to graded
judgments — applying them to a graded-judgment set is a metric/data
mismatch, not a neutral simplification.
