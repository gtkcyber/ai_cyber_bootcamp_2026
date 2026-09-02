---
name: ds-llm-systems
description: "LLM-systems method family: when an LLM beats a classical model (selection economics pointer, not a settled rule), retrieval-augmented systems and their evaluation (RAG, retrieval vs. generation faithfulness), prompt/ pipeline-level evaluation (HELM-class multi-axis), LLM-as-judge design/ calibration/agreement…"
---

# ds-llm-systems

Full depth, worked examples, and citations live in `references/`. This
file is protocol only.

## Subfields

- **When an LLM beats a classical model** — trigger: "should this use an
  LLM or classical NLP/ML," "do we need a foundation model here."
  **LITERATURE-THIN**: no paper gives a direct selection rule. Bommasani et
  al., 2021 — https://arxiv.org/abs/2108.07258 : nearest anchor — the
  capability/homogenization tradeoff of one broadly-capable model over
  task-specific ones; its homogenization warning applies directly — one
  foundation model across many systems concentrates failure into a single
  point of failure. No settled theory; validate empirically per task.
  Feeds `ds-model`'s selection economics, never overrides it. See
  `references/ds-llm-systems.selection-and-rag.md#when-an-llm-beats-a-classical-model`.
- **Retrieval-augmented systems and their evaluation** — trigger: "build/
  evaluate a RAG system," "is the retrieval or the generation wrong."
  Lewis et al., NeurIPS 2020, https://arxiv.org/abs/2005.11401 (RAG
  architecture); Es, James, Espinosa-Anke, Schockaert, "Ragas," 2023 —
  https://arxiv.org/abs/2309.15217 (reference-free metrics). Retrieval
  quality and generation faithfulness must be disentangled — a good answer
  can come from bad retrieval by chance. Reference-free metrics substitute
  an LLM judge for ground truth, risking circularity if the judge shares
  the generator's blind spots (see LLM-as-judge, below). Retrieval/search
  relevance mechanics themselves are `ds-ranking`'s. See
  `references/ds-llm-systems.selection-and-rag.md#retrieval-augmented-systems`.
- **Prompt/pipeline-level evaluation** — trigger: "evaluate this LLM
  pipeline holistically," "compare these prompts/pipelines." Liang et al.,
  "HELM," 2022 — https://arxiv.org/abs/2211.09110 : 7 metrics (accuracy,
  calibration, robustness, fairness, bias, toxicity, efficiency) across 16
  core scenarios; prior norm evaluated models on average across only
  17.9% of them. A single-metric leaderboard number hides real
  multi-metric tradeoffs. See
  `references/ds-llm-systems.pipeline-and-judge-eval.md#prompt-pipeline-level-evaluation`.
- **LLM-as-judge design, calibration, agreement** — trigger: "use an LLM
  to score/judge outputs," "automate this eval with a model." Zheng et
  al., NeurIPS 2023 — https://arxiv.org/abs/2306.05685 : documents
  position, verbosity, and self-enhancement biases, and limited reasoning
  ability. Biases must be actively corrected, not assumed neutral —
  self-enhancement bias favors outputs stylistically similar to the
  judge's own family, silently inflating same-family generator scores.
  See `references/ds-llm-systems.pipeline-and-judge-eval.md#llm-as-judge`.
- **Hallucination/grounding measurement** — trigger: "check for
  hallucination," "measure factual grounding." Ji et al., ACM Comp. Surv.
  2023 — https://arxiv.org/abs/2202.03629; Min et al., "FActScore," EMNLP
  2023 — https://arxiv.org/abs/2305.14251. Intrinsic (contradicts the
  source) and extrinsic (unverifiable/fabricated) hallucination are
  distinct failure modes needing distinct detection — not one taxonomy.
  FActScore's atomic-fact decomposition itself carries parsing/annotation
  subjectivity, reported, not treated as ground truth. See
  `references/ds-llm-systems.hallucination-and-eval-construction.md#hallucination-grounding-measurement`.
- **Generative eval-set construction** — trigger: "need eval data for
  this LLM task," "build a benchmark for this pipeline." Wang et al.,
  "Self-Instruct," ACL 2023 — https://arxiv.org/abs/2212.10560; Kiela et
  al., "Dynabench," NAACL 2021 — https://arxiv.org/abs/2104.14337.
  Self-Instruct bootstraps eval data from the same generative process
  being evaluated — risks amplifying the source model's own blind spots.
  Dynabench's human-and-model-in-the-loop adversarial creation avoids
  saturation but shifts the target distribution each round, complicating
  longitudinal score comparison. See
  `references/ds-llm-systems.hallucination-and-eval-construction.md#generative-eval-set-construction`.

|---|---|---|---|
| When an LLM beats a classical model | quick-answer | 1 | mandatory |
| Retrieval-augmented systems and their evaluation | analysis | 2 | conditional-on-data:retrieval-augmented-system |
| Prompt/pipeline-level evaluation | analysis | 2 | conditional-on-data:pipeline-comparison-requested |
| Generative eval-set construction | analysis | 2 | conditional-on-data:eval-set-construction-needed |
| LLM-as-judge design, calibration, agreement | analysis | 3 | conditional-on-data:llm-judge-proposed |
| Hallucination/grounding measurement | analysis | 3 | conditional-on-data:grounding-check-required |

`mandatory`: every composition answers the LLM-vs-classical question
first. Load-order-2 rows may co-occur (an eval set built to feed a
pipeline comparison); load-order-3 rows consume their output.

## Selection tree

1. Is the open question itself "LLM or classical here"? → When an LLM
   beats a classical model — states the cost/latency/quality reason
   before anything else composes.
2. LLM chosen, retrieves from an external corpus before generating? →
   Retrieval-augmented systems (retrieval and faithfulness scored
   separately).
3. No existing eval data for this task? → Generative eval-set
   construction, before the evaluation subfields below can run against it.
4. Comparing prompts/pipelines/configurations, not a single run? →
   Prompt/pipeline-level evaluation (state which axes are covered).
5. No reference/ground truth available for scoring? → LLM-as-judge
   (bias-corrected, provenance-tagged).
6. Deliverable makes factual claims that must trace to a source? →
   Hallucination/grounding measurement (intrinsic vs. extrinsic, stated
   separately).

Paths compose: a RAG pipeline commonly needs eval-set construction, then
pipeline evaluation, then judge-mediated scoring, then grounding checks —
each subfield's output feeds the next, not a single terminal branch.

## Family-specific pitfalls and evaluation

- LLM adoption's homogenization/single-point-of-failure risk (Bommasani et
  al.) treated as a footnote instead of weighed against the choice.
- RAG scored on final-answer quality alone, without disentangling
  retrieval quality from generation faithfulness; a reference-free
  metric (Ragas-class) trusted as ground truth with no check for
  judge/generator blind-spot overlap.
- A single pipeline-level accuracy number reported with no statement of
  which HELM-class axes (calibration, robustness, fairness, bias,
  toxicity, efficiency) were checked.
- An LLM judge treated as a neutral oracle: position/verbosity/self-
  enhancement bias uncorrected, its score used as an observed label
  rather than a named assertion.
- Intrinsic and extrinsic hallucination conflated under one detection
  method.
- An eval set built by the same model family being evaluated, with no
  check for amplified bias/blind-spot overlap between builder and target.

**Evaluation delta from `ds-evaluate`'s generic scorecard**: LLM-system
evaluation is multi-axis (HELM-class) and frequently judge-mediated rather
than single-ground-truth-metric; a reported score states which axes and
which judge/bias corrections were applied, not just the number.

## Gates

- The LLM-vs-classical decision states the specific cost/latency/quality
  reason — feeds `ds-model`'s selection economics
  (`doctrine-scale-cost.md`), never overrides it.
- Any RAG evaluation reports retrieval quality and generation faithfulness
  as separate figures — a single blended score fails.
- Any pipeline-level evaluation states which axes it covers (Liang et
  al.'s taxonomy or an equivalent stated set) — a bare single number
  fails.
- Any LLM-as-judge score is tagged `asserted` provenance
  (`doctrine-repro-provenance.md`) with the judge model and its incentive
  named — used as `observed` fails. Position/verbosity/self-enhancement
  bias correction is recorded, or explicitly stated as unchecked.
- Any hallucination/grounding claim states intrinsic-vs-extrinsic
  classification and the detection method used per class.
- Any generative eval-set construction states whether it draws on the
  same model family under evaluation, and names the bias-amplification
  risk if so — silent reuse fails.

## Edges

Covered: the six subfields above.

No leakage constraint originates in this family — the partner family or
router doctrine leads split/validation design in every pairing below.
