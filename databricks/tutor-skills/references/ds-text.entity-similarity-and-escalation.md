# NER, string similarity, log/regex parsing, and transformer escalation

Full depth and citations for the extraction/matching subfields and the
classic-to-transformer escalation decision. `SKILL.md` states triggers and
dispatch fields only; this file carries the method detail.

## NER {#ner}

**Literature name**: named entity recognition (NER).

**Canonical methods**: sequence-labeling NER (span/boundary detection plus
type classification) against a stated annotation convention.

**Source**: Tjong Kim Sang & De Meulder, "Introduction to the CoNLL-2003
Shared Task: Language-Independent Named Entity Recognition," CoNLL 2003 —
https://aclanthology.org/W03-0419.pdf. Defines the standard NER benchmark
task and the entity-type/boundary annotation conventions still used as the
reference standard for evaluation.

**Failure mode**: entity boundary and type definitions are
annotation-convention-specific — CoNLL's conventions were built for
newswire text. A model trained on that convention does not automatically
generalize to other domains (social media, biomedical, legal text) with
different entity taxonomies or boundary rules; a reported F1 is only
meaningful alongside the convention it was scored against.

## String similarity {#string-similarity}

**Literature name**: string comparator metrics for record linkage
(Jaro-Winkler family).

**Source**: Winkler, "The State of Record Linkage and Current Research
Problems," U.S. Census Bureau Research Report RR99-04 —
https://www.census.gov/content/dam/Census/library/working-papers/1999/
adrm/rr99-04.pdf. Surveys string-comparator metrics used to score
approximate field matches in probabilistic record linkage — Jaro-Winkler
and the wider edit-distance-based comparator family.

**Failure mode**: string similarity is not semantic similarity — a high
edit-distance or Jaro-Winkler score does not imply the same real-world
entity (nor does a low score rule it out; abbreviations, transliterations,
and legal-name variants can score low while referring to the same entity).
Similarity thresholds are dataset-specific, with no universal cutoff that
transfers across corpora — a threshold tuned on one dataset's name
distribution is not evidence it holds on another's. Turning a similarity
score into a linkage decision (which pairs are the same entity) is
`ds-entity-resolution`'s call, not this subfield's; this subfield only
produces the score.

## Log/regex parsing {#log-regex-parsing}

**Literature name**: automated log parsing.

**Canonical methods**: template-mining parsers that infer a log's static
template plus variable fields, and hand-written or generated regex
parsers for known formats.

**Source**: Zhu et al., "Tools and Benchmarks for Automated Log Parsing,"
ICSE-SEIP 2019 — https://arxiv.org/abs/1811.03509. Benchmarks parser
accuracy across log formats and datasets, showing substantial
accuracy variance by format.

**Failure mode**: parsing accuracy is highly dependent on log-format
regularity. An off-the-shelf parser's accuracy on one log source does not
transfer to a differently-formatted log source without re-tuning or
re-templating — a reported accuracy number is scoped to the source it was
measured on, and reuse on a new source is a new claim, not an inherited
one. This applies whether the log source is application, infrastructure,
or security-event text; the general form holds regardless of the specific
log domain.

## Embeddings/transformers (escalation from classic NLP) {#embeddings-transformers}

**Literature name**: word embeddings and the Transformer architecture.

**Canonical methods**: dense word/document embeddings (word2vec-class),
the Transformer encoder-decoder architecture, BERT-class pretrained
bidirectional representations fine-tuned for a downstream task.

**Sources**:
- Mikolov, Chen, Corrado, Dean, "Efficient Estimation of Word
  Representations in Vector Space," 2013 — https://arxiv.org/abs/1301.3781.
  word2vec: dense embeddings from local context prediction, the first
  widely-adopted alternative to sparse TF-IDF/BoW vectors.
- Vaswani et al., "Attention Is All You Need," NeurIPS 2017 —
  https://arxiv.org/abs/1706.03762. The Transformer architecture:
  self-attention replaces recurrence for sequence modeling.
- Devlin, Chang, Lee, Toutanova, "BERT: Pre-training of Deep Bidirectional
  Transformers for Language Understanding," NAACL 2019 —
  https://arxiv.org/abs/1810.04805. Bidirectional pretraining plus
  task-specific fine-tuning as the standard transfer pattern for text.

**Failure mode**: embeddings and transformer models need substantially
more data and compute than classic methods (TF-IDF, n-grams) to earn their
keep. The escalation from classic NLP must be justified per-task — a
stated accuracy gain weighed against the added data/compute cost — never
defaulted to because it's the more sophisticated-sounding option. This
family owns the escalation decision (framing: is the gain worth the cost
on this task's data); `ds-deep-learning` owns fitting and fine-tuning the
model once that decision is made.

**Interaction with the small-corpus edge**: a small corpus is exactly the
regime where this escalation is hardest to justify — see `SKILL.md`
`## Edges`. Low-resource NLP methods (augmentation, distant supervision,
transfer learning) bound but don't eliminate the small-corpus penalty, and
that bound is often below what transformer escalation would need to pay
for itself.
