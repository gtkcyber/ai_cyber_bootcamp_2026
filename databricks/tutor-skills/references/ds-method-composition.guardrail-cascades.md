# Guardrail cascades — model-as-verifier

Worked example and full citation context for `SKILL.md`'s
model-as-verifier / guardrail cascade subfield.

Chen, Zaharia, Zou, "FrugalGPT: How to Use Large Language Models While
Reducing Cost and Improving Performance," 2023 —
https://arxiv.org/abs/2305.05176 . FrugalGPT routes a query across models
of increasing cost: a cheap model answers first, and a scoring/routing
function decides whether to accept that answer or escalate to a more
expensive model. The goal is minimizing spend while preserving accuracy —
the routing function's own reliability is the entire mechanism; a
miscalibrated router defeats the cost savings (by escalating everything)
or the accuracy guarantee (by escalating nothing).

Viola & Jones, "Rapid Object Detection using a Boosted Cascade of Simple
Features," CVPR 2001 —
https://www.cs.cmu.edu/~efros/courses/LBMV07/Papers/viola-cvpr-01.pdf .
The classic-NLP/classic-CV analog: a cascade of increasingly expensive
classifier stages, each rejecting clear negatives early so only ambiguous
cases reach the final, most expensive stage. Applied to LLM outputs, the
"classic" stages are deterministic or lightweight-ML guardrails — regex/
schema validators, toxicity or PII classifiers, retrieval-grounded
fact-verification — gating an expensive generative stage rather than the
reverse: cheap checks run first and either pass, reject, or escalate the
generative output to human review or a more expensive re-generation.

```
[cheap-stage]: fit_on=<train-only rules/classifier fit, described> →
  outputs=accept / escalate decision (+ optional score) →
  escalation_criterion=<explicit calibrated threshold OR named rejection
  class — not a bare confidence number>
[expensive-stage]: fit_on=n/a (pretrained/fixed) or fine-tuned, described →
  outputs=verified/generated answer → visible_to=only cases the
  cheap-stage escalated
```

## Why the escalation criterion is the whole gate

A cheap stage's confidence score is not automatically its calibration.
An overconfident cheap stage can be "usually right" in aggregate and
still silently wrong on exactly the cases that matter — the cases a
calibrated stage would have escalated. Before trusting a confidence score
as an escalation threshold, check calibration (`ds-evaluate`, pointer) or
use a calibrated alternative (conformal prediction, `ds-uncertainty`
pointer) rather than the raw score.

## Classic-NLP guardrails as cheap-stage components

Each guardrail (regex/schema validator, toxicity/PII classifier,
fact-verification against retrieved context) is itself a fit component
with its own leakage boundary — a toxicity classifier fit on a population
that doesn't match the deployment population is a leak into "verified"
outputs just as much as a leaked feature would be. State each guardrail's
own `fit_on` in the composition diagram; do not treat "it's just a
classic-ML filter" as exempting it from the per-component leakage-boundary
gate (`SKILL.md` `## Gates`).
