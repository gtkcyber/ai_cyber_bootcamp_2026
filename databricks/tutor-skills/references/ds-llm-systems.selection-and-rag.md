# Selection and retrieval-augmented systems

## When an LLM beats a classical model

**No settled selection theory — this is empirical, per task, not a
literature-derived rule.** The nearest anchor is Bommasani et al., "On the
Opportunities and Risks of Foundation Models," 2021 —
https://arxiv.org/abs/2108.07258 — which studies the tradeoff of adopting
one broadly-capable foundation model in place of many task-specific ones,
without prescribing a selection threshold. Two things transfer directly
from that paper into a selection decision:

- **Capability breadth vs. specialization cost.** A foundation model
  amortizes development effort across tasks a classical pipeline would
  need separate models for — the paper's "capabilities" side. This is a
  development-cost argument, not automatically a quality or latency one;
  a classical model tuned for one narrow task can still out-perform a
  general LLM on that task, at lower serving cost.
- **Homogenization risk.** Bommasani et al.'s central risk claim:
  standardizing many downstream systems on one foundation model
  concentrates their failure modes into a single point of failure — a bug,
  bias, or capability gap in the shared model now propagates everywhere
  it's used, simultaneously. This is directly relevant to a selection
  decision at production tier — it is a cost of adoption, not just a
  caveat, and belongs in the same accounting as latency/compute cost.

**What actually decides it, since the literature doesn't**: cost per
inference, latency budget, and achieved quality on the specific task,
measured, not assumed — the selection-economics *method* (baseline-first
ladder, cost-per-experiment accounting) is `ds-model`'s and
`references/doctrine-scale-cost.md`'s; this subfield only supplies the LLM-specific
framing question and the homogenization line item that a classical-only
selection economics pass would otherwise omit.

**Common wrong pattern**: reaching for an LLM because it's available and
general, without pricing the classical alternative first — this inverts
the scale playbook's "escalate only as far as the data forces"
(`references/doctrine-scale-cost.md`). A stated reason (need for open-ended
generation, need to handle unbounded input variety a rule-based/classical
pipeline can't enumerate, multimodal reuse of an existing LLM investment)
is required before the LLM is even costed against the classical baseline.

## Retrieval-augmented systems

**Architecture**: Lewis et al., "Retrieval-Augmented Generation for
Knowledge-Intensive NLP Tasks," NeurIPS 2020 —
https://arxiv.org/abs/2005.11401. A retriever fetches supporting documents
from an external index; a generator conditions on both the query and the
retrieved documents. Two independently-failing components, not one.

**Evaluation must disentangle the two components**:

- **Retrieval quality** — did the retriever fetch the documents that
  actually support a correct answer? Standard retrieval metrics
  (precision/recall@k, MRR) apply; the *mechanics* of retrieval/search
  relevance ranking are `ds-ranking`'s, not re-taught here.
- **Generation faithfulness** — given what was retrieved, did the
  generator's answer actually rely on it, versus fabricating from
  parametric memory despite good retrieval, or despite bad retrieval
  producing a right answer by chance? A correct final answer with bad
  retrieval is not evidence the RAG system works — it is evidence the
  eval didn't separate the two failure surfaces.

**Reference-free metrics**: Es, James, Espinosa-Anke, Schockaert, "Ragas:
Automated Evaluation of Retrieval Augmented Generation," 2023 —
https://arxiv.org/abs/2309.15217. Scores faithfulness, answer relevance,
and context relevance without needing hand-labeled references, by using an
LLM to judge each. This is a substitution, not an elimination, of ground
truth: **the LLM judge becomes the reference**. If the judge shares
architectural lineage, training data, or blind spots with the generator
being scored, the metric risks circularity — the judge validating errors
it would itself make. See LLM-as-judge design mechanics
(`pipeline-and-judge-eval.md#llm-as-judge`) for the bias-correction
discipline this circularity risk requires before trusting a Ragas-class
score.

**Common wrong pattern**: reporting one blended "RAG quality" number.
Report retrieval quality and generation faithfulness as two figures, both
against the failure mode each actually measures — a high blended score can
hide a retriever that's failing half the time, compensated by a generator
that happens to know the answer anyway (which won't generalize past the
training distribution the generator memorized).
