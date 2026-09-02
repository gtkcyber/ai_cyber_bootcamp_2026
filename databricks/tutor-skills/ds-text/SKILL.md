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
  a default. See `references/classic-nlp-methods.md#tokenization`.
- Canonical methods: bag-of-words counts, TF-IDF weighting, cosine
  similarity. Edges: word order is discarded entirely; IDF weights are
  unstable on a small or topically skewed corpus. See
  `references/classic-nlp-methods.md#tfidf-bow`.
- Canonical methods: n-gram counting with smoothing (Laplace, Kneser-Ney).
  Edges: a fixed-order Markov assumption; unsmoothed unseen n-grams zero out
  any sequence containing them. See
  `references/classic-nlp-methods.md#n-grams`.
- Canonical methods: Latent Dirichlet Allocation. Edges: bag-of-words
  exchangeability, topic count *K* fixed a priori, topics assumed
  independent. See `references/classic-nlp-methods.md#topic-modeling`.
- Canonical methods: sequence-labeling NER against a stated
  entity-type/boundary convention. Edges: convention-specific, doesn't
  generalize across domains without re-annotation. See
  `references/entity-similarity-and-escalation.md#ner`.
- Canonical methods: Jaro-Winkler and edit-distance comparator family.
  Edges: not semantic similarity; thresholds are dataset-specific; linkage
  decisions are `ds-entity-resolution`'s. See
  `references/entity-similarity-and-escalation.md#string-similarity`.
- Canonical methods: template-mining and regex-based log parsers. Edges:
  accuracy is format-regularity-dependent, doesn't transfer without
  re-tuning. See
  `references/entity-similarity-and-escalation.md#log-regex-parsing`.
- Canonical methods: word2vec-class embeddings, Transformer encoders,
  BERT-class pretrained representations. Edges: this family frames
  whether/when to escalate; training once escalated is `ds-deep-learning`'s.
  See
  `references/entity-similarity-and-escalation.md#embeddings-transformers`.

## Selection tree

1. **Input shape.** Structured/semi-structured log lines (a stable
   delimiter/template) → log/regex parsing, evaluated on this source's own
   format before any transfer claim. Free prose → tokenize first, always.
2. **Corpus size.** Small/narrowly-scoped corpus → classic methods only,
   small-corpus caveat recorded explicitly (`## Edges`) — never default to
   transformer escalation to compensate for data scarcity.
3. **Task shape.** Similarity/retrieval vector → TF-IDF/BoW. Fixed local
   context (phrase features, simple LM) → n-grams. Latent document themes
   → topic modeling (fix *K* deliberately, state it). Spans/entities → NER
   (state the annotation convention). Approximate string matches feeding
   identity work → string similarity, handed to `ds-entity-resolution` for
   the linkage decision itself.
4. **Escalation gate.** Classic methods underperform *with a stated
   reason* and the corpus supports it → embeddings/transformers, framed
   here; fit and trained in `ds-deep-learning`.
5. **System-level LLM question.** "Would an LLM beat a classical model
   here," a RAG pipeline, or judge/labeler design → out of scope, routes
   to `ds-llm-systems` (pointer, `## Edges`).

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

## Gates

- Tokenization granularity/vocabulary choice recorded, not defaulted
  silently.
- TF-IDF/BoW vocabulary and IDF weights, n-gram counts/smoothing, and any
  topic model's fitted parameters are fit-on-train-only (`ds-features`) —
  cited, not re-checked here.
- Any reported NER metric states the convention it was scored against.
- Any string-similarity threshold states its source corpus; a log/regex
  parser's accuracy claim is scoped to its measured source — reuse
  elsewhere restates the check.
- Transformer/embedding escalation records the specific reason (accuracy
  gain vs. cost); a small-corpus task escalating past classic methods
  records the caveat explicitly (`## Edges`).
- Doctrine gates triggered: leakage, provenance/additivity, scale/cost
  (`references/doctrine-leakage.md`, `doctrine-repro-provenance.md`,
  `doctrine-scale-cost.md`) — linked, not restated.

## Edges

Covered: the eight subfields above (`## Subfields`).

**Small-corpus regimes (edge).** A small/narrowly-scoped corpus caps what
any method here can deliver — augmentation, distant supervision, and
transfer learning bound but don't eliminate the penalty; augmented/
weakly-supervised data can't substitute for real data diversity. This is
why transformer escalation is usually unjustified here — default to
classic methods plus an explicit caveat. Specialized low-resource methods
beyond that (Hedderich, Lange, Adel, Strötgen, Klakow, NAACL 2021 —
https://arxiv.org/abs/2010.12309) are outside coverage: state that,
research externally, verify assumptions against this task's data, report
provenance.

Not covered, pointer only: transformer/multimodal-fusion *training*
(`ds-deep-learning`); when an LLM beats a classical model, RAG,
prompt/pipeline evaluation, LLM-judge design (`ds-llm-systems`); labeling
strategy/quality measurement (`ds-labeling`); linkage decisions built on
string-similarity scores (`ds-entity-resolution`); pretrained-family fit for
non-text modalities (`ds-perception`); generic evaluation scorecard
(`ds-evaluate`); fit-on-train-only mechanics (`ds-features`). No leakage
constraint originates in this family — the partner family or router doctrine
leads split/validation design in every pairing below.
