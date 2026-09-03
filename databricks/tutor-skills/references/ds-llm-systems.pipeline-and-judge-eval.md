# Pipeline evaluation and LLM-as-judge

## Prompt/pipeline-level evaluation

**Holistic Evaluation of Language Models (HELM)**: Liang et al., 2022 —
https://arxiv.org/abs/2211.09110. Before HELM, the field's norm was
evaluating a model on whichever narrow scenario/metric combination a paper
chose to report — the authors measured that prior published work covered,
on average, only 17.9% of the 16 core scenarios HELM defines, meaning most
comparisons were implicitly cherry-picked or simply incomplete relative to
the full evaluation surface.

**The seven metrics HELM taxonomizes** (not a closed list — the framework's
contribution is the discipline of stating which axes a number covers, not
these seven specifically): accuracy, calibration, robustness, fairness,
bias, toxicity, efficiency.

**What this means for a pipeline/prompt comparison**: "prompt A scores
0.82, prompt B scores 0.79" is under-specified unless the report states
which axis 0.82/0.79 measures and whether the two prompts were also
compared on the axes not shown. A prompt that improves accuracy while
degrading calibration or increasing toxicity is not an unambiguous win —
it's a tradeoff that needs to be seen, not averaged away.

**Common wrong pattern**: single-metric (almost always accuracy-only)
leaderboard-style comparison presented as a complete evaluation. State
explicitly which axes were measured and which were not — an omitted axis
is a scope statement, not evidence the pipeline is fine on it.

## LLM-as-judge

**Documented biases**: Zheng et al., "Judging LLM-as-a-Judge with MT-Bench
and Chatbot Arena," NeurIPS 2023 — https://arxiv.org/abs/2306.05685.

- **Position bias** — a judge's preference shifts based on which response
  is shown first/second in a pairwise comparison, independent of quality.
  Mitigation: score both orderings and check for order-dependent flips,
  not a single-pass judgment.
- **Verbosity bias** — longer responses score higher independent of
  actual quality gain. A judge prompt/rubric that doesn't explicitly
  penalize unnecessary length will reward padding.
- **Self-enhancement bias** — a judge model rates outputs from its own
  model family (or stylistically similar models) higher than outputs of
  equal or better quality from a different family. This is the most
  dangerous for same-vendor generator/judge pairs specifically, since it's
  invisible without a cross-family control.
- **Limited reasoning ability** — judges can fail at tasks requiring
  multi-step reasoning to actually verify correctness (math, logic),
  producing confident but wrong verdicts on exactly the outputs hardest to
  spot-check by eye.

**The provenance discipline this requires**: a judge's output is not an
observed label. Per `references/doctrine-repro-provenance.md`'s provenance classes
(observed / derived / enriched / defaulted / asserted /
privacy-transformed), an LLM-judge score is **`asserted`** — a claim made
by a named party (the specific judge model/version) with a specific
incentive (the objective it was itself trained/prompted toward, which may
not be "score accurately"). State the asserter and the incentive
explicitly in the artifact; do not record a judge score as if it carried
the same epistemic weight as a human-verified label or a ground-truth
value.

**Calibration and agreement**: before trusting a judge at scale, measure
its agreement with a human-labeled sample on the same items (treat this as
an inter-annotator-agreement problem — Cohen's kappa/Krippendorff's alpha
mechanics are `ds-labeling`'s) and report the position/verbosity/self-
enhancement checks above as part of that calibration, not as a one-time
disclaimer.

**Common wrong pattern**: using a single judge, single ordering, no
human-agreement sample, and reporting the resulting score as ground truth
rather than as one calibrated-or-uncalibrated assertion.
