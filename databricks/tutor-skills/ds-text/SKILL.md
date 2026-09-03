---
name: ds-text
description: "Text method/goal family: classic NLP first — tokenization, TF-IDF/BoW, n-grams, topic modeling, NER, string similarity, log/regex parsing — escalating to embeddings/ transformers only when justified; small-corpus regimes a declared edge."
---

# ds-text

Composes after `ds-features` writes the feature dictionary, alongside
`ds-model` (cross-family selection; never itself picks a method class).
Full depth, citations, failure modes: `references/`; protocol only here.

## Subfields

- Canonical methods: word-level splitting, subword/BPE segmentation,
  character-level. Edges: granularity is task- and language-dependent, never
  a default. See `references/ds-text.classic-nlp-methods.md#tokenization`.
- Canonical methods: bag-of-words counts, TF-IDF weighting, cosine
  similarity. Edges: word order is discarded entirely; IDF weights are
  unstable on a small or topically skewed corpus. See
  `references/ds-text.classic-nlp-methods.md#tfidf-bow`.
- Canonical methods: n-gram counting with smoothing (Laplace, Kneser-Ney).
  Edges: a fixed-order Markov assumption; unsmoothed unseen n-grams zero out
  any sequence containing them. See
  `references/ds-text.classic-nlp-methods.md#n-grams`.
- Canonical methods: Latent Dirichlet Allocation. Edges: bag-of-words
  exchangeability, topic count *K* fixed a priori, topics assumed
  independent. See `references/ds-text.classic-nlp-methods.md#topic-modeling`.
- Canonical methods: sequence-labeling NER against a stated
  entity-type/boundary convention. Edges: convention-specific, doesn't
  generalize across domains without re-annotation. See
  `references/ds-text.entity-similarity-and-escalation.md#ner`.
- Canonical methods: Jaro-Winkler and edit-distance comparator family.
  Edges: not semantic similarity; thresholds are dataset-specific; linkage
  decisions are `ds-entity-resolution`'s. See
  `references/ds-text.entity-similarity-and-escalation.md#string-similarity`.
- Canonical methods: template-mining and regex-based log parsers. Edges:
  accuracy is format-regularity-dependent, doesn't transfer without
  re-tuning. See
  `references/ds-text.entity-similarity-and-escalation.md#log-regex-parsing`.
- Canonical methods: word2vec-class embeddings, Transformer encoders,
  BERT-class pretrained representations. Edges: this family frames
  whether/when to escalate; training once escalated is `ds-deep-learning`'s.
  See
  `references/ds-text.entity-similarity-and-escalation.md#embeddings-transformers`.

## Selection tree

1. **Input shape.** Structured/semi-structured log lines (a stable
   delimiter/template) → log/regex parsing, evaluated on this source's own
   format before any transfer claim. Free prose → tokenize first, always.
3. **Task shape.** Similarity/retrieval vector → TF-IDF/BoW. Fixed local
   context (phrase features, simple LM) → n-grams. Latent document themes
   → topic modeling (fix *K* deliberately, state it). Spans/entities → NER
   (state the annotation convention). Approximate string matches feeding
   identity work → string similarity, handed to `ds-entity-resolution` for
   the linkage decision itself.
4. **Escalation gate.** Classic methods underperform *with a stated
   reason* and the corpus supports it → embeddings/transformers, framed
   here; fit and trained in `ds-deep-learning`.

## Family-specific pitfalls and evaluation

Pitfalls (full detail, citations: `references/`):

- BPE/subword granularity is a compression heuristic, not a morphological
  one — no universal best granularity; task- and language-dependent.
- TF-IDF's IDF weights assume corpus representativeness; small/skewed
  corpora give unstable, non-generalizable weights.
- Unsmoothed n-grams silently zero out any sequence with an unseen n-gram.
- LDA's *K* is fixed a priori, topics assumed independent — a fitted *K*
  is not "the" topic count, it's what was assumed going in.
- NER's taxonomy/boundary rules are convention-specific; a reported F1 is
  meaningless without stating which convention.
- String-similarity thresholds don't transfer across corpora.
- Log parser accuracy is format-specific, re-validated not assumed on a
  new source.
- Transformer escalation defaulted to (not justified per-task against
  data/compute cost) is a selection-economics failure, not a modeling one.

**Evaluation delta.** `ds-evaluate` owns the generic scorecard; this
family's delta is task-specific and convention-bound — NER (F1 against
its stated convention, never bare), topic modeling (coherence and
*K*-sensitivity alongside any perplexity number), string similarity
(threshold's source corpus stated), log parsing (accuracy per source, not
inherited), TF-IDF/n-gram retrieval (evaluated on this corpus's own
statistics, not borrowed).
