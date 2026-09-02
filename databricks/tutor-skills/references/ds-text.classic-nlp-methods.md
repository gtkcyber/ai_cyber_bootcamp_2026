# Classic NLP methods: tokenization, TF-IDF/BoW, n-grams, topic modeling

Full depth and citations for the four foundational classic-NLP subfields.
`SKILL.md` states triggers and dispatch fields only; this file carries the
method detail.

## Tokenization {#tokenization}

**Literature name**: subword tokenization / open-vocabulary modeling.

**Canonical methods**: word-level splitting (whitespace/punctuation
boundaries), subword/byte-pair-encoding (BPE) segmentation, character-level
tokenization.

**Sources**:
- Sennrich, Haddow, Birch, "Neural Machine Translation of Rare Words with
  Subword Units," ACL 2016 — https://arxiv.org/abs/1508.07909. Introduces
  BPE segmentation for open-vocabulary NMT: greedily merges the most
  frequent adjacent symbol pairs until a target vocabulary size is reached.
- Mielke et al., "Between Words and Characters: A Brief History of
  Open-Vocabulary Modeling and Tokenization in NLP," 2021 —
  https://arxiv.org/abs/2112.10508. Surveys the full word/character
  granularity spectrum and the tradeoffs at each point.

**Failure mode**: BPE is a data-compression heuristic — greedy pair-merge —
not a morphological one. It does not guarantee linguistically meaningful
units, and vocabulary/merge-count is a hyperparameter that materially
changes downstream performance. No universal best granularity exists: it
is task- and language-dependent, and morphologically rich languages fare
worse under naive word-level tokenization specifically because word-level
splitting can't decompose productive morphology the way subword methods
can.

## TF-IDF/BoW {#tfidf-bow}

**Literature name**: vector space model / term weighting.

**Canonical methods**: bag-of-words term counts, TF-IDF weighting (term
frequency times inverse document frequency), cosine similarity between the
resulting document vectors.

**Source**: Manning, Raghavan, Schütze, *Introduction to Information
Retrieval*, Ch. 6 "Scoring, term weighting and the vector space model" —
https://nlp.stanford.edu/IR-book/pdf/06vect.pdf. The canonical, freely
hosted derivation of TF-IDF weighting and cosine similarity in the vector
space model.

**Failure mode**: bag-of-words discards word order entirely — "dog bites
man" and "man bites dog" are the same vector. IDF assumes the corpus is
representative of the term-frequency distribution the model will see at
inference; a small or topically skewed corpus gives unstable,
non-generalizable IDF weights, since a term's rarity in a narrow corpus
doesn't reflect its rarity in the population the model will actually see.

## N-grams {#n-grams}

**Literature name**: n-gram language models.

**Canonical methods**: n-gram frequency counting with a smoothing scheme
(Laplace/add-one, Kneser-Ney) to avoid zero probabilities on unseen
n-grams.

**Source**: Jurafsky & Martin, *Speech and Language Processing*, 3rd ed.
draft, Ch. 3 "N-gram Language Models" — https://web.stanford.edu/~jurafsky/
slp3/3.pdf. The standard treatment of the Markov independence assumption
underlying n-gram models, sparsity, and smoothing.

**Failure mode**: n-grams encode a fixed-order Markov (limited-context)
assumption — they cannot capture dependencies beyond the window size, no
matter how much data is added. Without smoothing, unseen n-grams get zero
probability, which silently zeroes out any sequence containing them
(catastrophic for downstream scoring, not a graceful degradation). The
smoothing scheme is not optional plumbing — it's what keeps the model from
failing on any input it wasn't trained on verbatim.

## Topic modeling {#topic-modeling}

**Literature name**: Latent Dirichlet Allocation (LDA).

**Canonical methods**: LDA — a generative model where each document is a
mixture over a fixed number of latent topics, and each topic is a
distribution over the vocabulary.

**Source**: Blei, Ng, Jordan, "Latent Dirichlet Allocation," JMLR 3, 2003 —
https://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf. The canonical
generative topic model; introduces the plate-notation generative process
and variational inference for fitting it.

**Failure mode**: LDA treats documents as an exchangeable bag-of-words —
word order within a document is irrelevant to the model, same discard as
TF-IDF/BoW — and requires the number of topics *K* to be fixed a priori.
Reporting a fitted *K* as "the" number of topics in the corpus misstates
what happened: *K* was chosen, not discovered. The base model further
assumes topics are independent, so highly correlated topics (e.g. two
topics that co-occur in most documents) are not represented without model
extensions beyond vanilla LDA.
