# Imputation decision tree

Routing table, not mechanics. Mechanism hypothesis (Rubin's MCAR/MAR/MNAR,
`ds-clean`'s taxonomy) × downstream use (point prediction vs.
inferential/interval claim) × scale → method class and its owner. Every
row assumes `ds-clean`'s protocol already ran: mechanism hypothesis
classified, operational cause stated, method chosen, rationale logged
(`ds-clean` §Missingness handling).

## Mechanism × downstream use → method class

| Mechanism hypothesis | Downstream use | Method class | Mechanics owner | Failure mode |
|---|---|---|---|---|
| MCAR | Point prediction | Drop (row/column) if the missing fraction is small, or simple imputation (mean/median/mode) | `ds-clean` | Dropping a large fraction still costs sample size/power even though MCAR makes it unbiased — state the tradeoff, don't drop by default |
| MCAR | Inferential/interval claim | Multiple imputation, or complete-case analysis (unbiased under MCAR, but inefficient) | `ds-uncertainty` | State which tradeoff (efficiency vs. simplicity) was chosen — "MCAR so we dropped rows" is not itself a justification |
| MAR | Point prediction, simple structure sufficient | Simple imputation (mean/median/mode) | `ds-clean` | MAR is an assumption about the generating process, argued from operational knowledge — never confirmed from the observed data alone; don't claim "MAR confirmed" |
| MAR | Point prediction, simple imputation judged too crude | Model-based single-point imputation (composed pattern: model-as-imputer) | `ds-method-composition` (escalation from `ds-clean`) | Fit train-only per the composition's leakage delta — a model-as-imputer fit on the full dataset leaks into every downstream split consuming its output |
| MAR | Inferential/interval claim | Multiple imputation — Rubin's rules pooling `m` complete-data analyses | `ds-uncertainty` | The between-imputation variance term only correctly inflates SEs if the imputation model is at least as rich as the analysis model; single-imputation reporting is not multiple imputation |
| MNAR | Point prediction or inferential/interval claim | No default method — naive imputation under an MNAR process is biased regardless of point/inferential use; requires an explicit model of the missingness mechanism itself | `ds-clean` (flag mechanism + operational cause), escalate | Claiming MAR/MCAR to sidestep this is exactly the "ignorability" condition Rubin's framework requires justifying, not assuming away |

## Scale

| Scale concern | Method class affected | Owner | Note |
|---|---|---|---|
| Point-estimate methods (drop, mean/median/mode, single model-based fill) | All MCAR/MAR point-prediction rows above | `ds-clean` | Scales like any single fit/transform — standard fit-on-train-only mechanics (`ds-features`), no `m`-multiplier |
| Multiple imputation | Both inferential/interval rows above | `ds-uncertainty` + `doctrine-scale-cost.md` | Cost scales `m`× the base analysis (`m` complete-data analyses fit and pooled) — state `m` and the compute-cost tradeoff explicitly at production tier |

## Provenance

An imputed value is no longer `observed` (`doctrine-repro-provenance.md`'s
classes): a rule-based fill (drop-and-fill, mean/median/mode) degrades to
`derived`; a model-based fill (single-point or composed model-as-imputer)
degrades to `enriched`. Never left silently as `observed` regardless of
which row produced it.

## Gate

Any imputed column about to feed a confidence interval, hypothesis test,
or other interval/inferential claim routes to `ds-uncertainty`'s multiple
imputation before that claim ships — single-point imputation (any row
above marked "point prediction") understates variance and is not a
substitute, even when the point-prediction fill happens to be model-based.
