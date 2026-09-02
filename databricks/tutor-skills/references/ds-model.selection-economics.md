# Selection economics

**Status**: LITERATURE-THIN. No single established field name covers this
whole. The nearest established concept is cost-sensitive learning (Elkan,
2001), which formalizes *misclassification*-cost tradeoffs (false-positive
vs. false-negative cost) — not the *model-class* cost tradeoff (simple vs.
complex model, given comparable predictive performance) this subfield
addresses. "Pareto-optimal model selection" is a live practitioner framing
for the latter, not a consolidated field. Treat everything below as
practice guidance, not settled theory.

## The rule

At statistically indistinguishable predictive performance, prefer the
cheaper model. "Statistically indistinguishable" is `ds-evaluate`'s
comparison-with-uncertainty call (Demšar's paired significance tests,
never a raw point-estimate difference) — this skill doesn't re-run that
test, it consumes the verdict.

Cost is multi-dimensional. Weigh all of what applies, not just the first
one that comes to mind:

- **Training cost** — compute-hours, cloud spend, human tuning time.
- **Inference latency/throughput** — matters most for anything on a
  request path; a batch-scored nightly job tolerates far more than an
  online endpoint.
- **Hardware** — CPU-only vs. GPU/accelerator requirement; on-device vs.
  server.
- **Retraining cost** — how expensive/frequent a refresh cycle is once the
  model is in production; a model that must retrain weekly on drifting
  data pays its training cost repeatedly.
- **Operational complexity** — how many moving parts (custom preprocessing,
  a bespoke serving stack, exotic dependencies) the model class drags in.
- **Debuggability** — how tractable it is to diagnose a bad prediction;
  a linear model's coefficient is legible in a way a large ensemble's
  contribution isn't (interpretation-for-diagnosis, distinct from
  `ds-explain`'s interpretation-for-stakeholders, feature set fixed).

## Selection inputs, not post-hoc filters

`doctrine-scale-cost.md`: compute/latency are selection *inputs*. Don't
run the full baseline-first ladder to a winner on pure predictive
performance and only then ask "was it worth it?" — the cost profile of
each rung is part of the evidence considered when deciding whether to
climb another rung at all. The escalation threshold that governs how far
the ladder climbs is declared once, in `ds-scoping`'s `kill_check`, and
read from there — this file does not restate a number.

## When the ladder stops

Stop climbing when the marginal predictive gain from the next rung no
longer clears its marginal cost — evaluated in whichever cost dimensions
above are load-bearing for this task (a batch analytics job may only care
about training cost; a fraud-scoring endpoint may be latency-dominated).
"The gain stops paying for itself" is a judgment call made explicit in
`selection_rationale`, not a silent stopping point.

## Worked example

Two candidates score within the CV standard-error band `ds-evaluate`
computed: a random forest (0.842 AUC) and a small neural network (0.847
AUC), flagged statistically indistinguishable. The RF trains in 4 minutes
on CPU with no tuning infrastructure beyond what's already in place; the
NN needs a GPU training job, its own serving container, and a retraining
pipeline the team doesn't yet operate. `selection_rationale` names the RF
as the selected model, citing training cost, hardware requirement, and
operational complexity as the deciding cost inputs — not the 0.005 AUC
gap, which the significance test already ruled out as a distinguishing
factor.

## Referenced delta-only by

`doctrine-scale-cost.md` is the doctrine home for scale/cost escalation
and the threshold mechanism; this file is this skill's delta — the
selection *procedure* that consumes that doctrine at model-choice time.
`ds-mlops` owns ongoing serving/retraining cost once a model is deployed;
this subfield owns the pre-deployment choice, not its production
monitoring.
