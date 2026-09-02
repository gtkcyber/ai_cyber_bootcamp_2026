# Baseline, tuning, CV design

## Baseline {#baseline}

**Claim to avoid**: "the gradient-boosted model beats logistic regression,
so the extra complexity is justified." Lipton & Steinhardt (2018) document
this exact pattern across published ML work — gains credited to a novel
architecture that turn out to be gains from hyperparameter effort the
baseline never received.

**Protocol**:
1. Fit the simplest model that can plausibly represent the target
   relationship (linear/logistic for tabular, a persistence or seasonal-
   naive model for time series) using the *same* feature set the complex
   candidates will use.
2. Give the baseline a comparable tuning budget — not necessarily the same
   search space, but not left at library defaults while the challenger gets
   a random-search sweep.
3. Record the baseline's score under the same CV scheme (below) before any
   complex candidate is scored.
4. A complex candidate's `selection_rationale` entry cites the baseline
   score it beat, by how much, and under what CV scheme — not just its own
   number in isolation.

**Worked example**: churn model. Baseline = logistic regression on the
feature set, L2 strength swept over a small grid (this is the baseline's
"comparable tuning," not zero tuning). Candidate = gradient-boosted trees
with a 50-trial random search. If GBT beats logistic regression by 0.01
AUC, that is not automatically worth the added debuggability/latency cost
— see `references/ds-model.selection-economics.md`.

## Tuning protocol {#tuning}

Bergstra & Bengio (2012): for a fixed budget, random search over the full
hyperparameter space matches or beats grid search over a coarser space,
because typically only a few dimensions matter per dataset and grid search
wastes trials on the unimportant ones.

**Protocol**:
- Default to random (or a Bayesian/bandit-based search when the budget
  supports it) over a full-space grid. Grid search is acceptable only when
  the space is genuinely low-dimensional (1–2 hyperparameters) and the
  budget covers it exhaustively.
- State the search budget (trial count, wall-clock cap, or both) up front,
  not chosen post hoc from whatever happened to run.
- If a model is deployed with library-default hyperparameters, that is a
  tuning decision too — record it as "defaults, justified" plus the reason
  (e.g. dataset too small for a validation-based search to be trustworthy).
- Nested CV (tuning loop inside an outer evaluation loop) when both the
  hyperparameter search *and* the performance estimate need to be
  trustworthy and the dataset can afford the extra folds; otherwise a
  single held-out validation split for tuning, distinct from the final
  test partition, is sufficient — either way, both loops nest inside
  `ds-scoping`'s train partition, never touching the held-out test set.

## CV design choice {#cv-design}

Roberts et al. (2017): standard k-fold CV on data with temporal, spatial,
hierarchical, or phylogenetic structure underestimates generalization
error — folds leak structure to each other even when the leakage isn't
visible as residual autocorrelation. The fix is block/grouped CV, chosen
from the structure, not from whether a leak was observed.

**Decision procedure**:
1. Check `ds-profile`'s `grouping_variables` (patients, users, stores,
   sensors — any unit repeated across rows) and any temporal ordering.
2. Grouping variable present → `GroupKFold` (or a stratified-group
   variant), keyed on that variable — no group's rows span both a training
   and a validation fold.
3. Temporal ordering present and forecast-relevant → `TimeSeriesSplit` or
   an explicit rolling/expanding-window scheme — folds respect time order,
   never shuffle across it.
4. Neither present → record the explicit assertion "rows are independent
   (no group or temporal structure)" before using plain k-fold. This is a
   stated claim, not a default silently assumed.
5. Whatever scheme is chosen here is *refined*, never widened, from
   `ds-scoping`'s `split_design`: the folds partition the train side of
   that split; the held-out test partition is never touched by CV.

**Worked example**: a churn model over per-customer support tickets, one
row per ticket, has a customer-id group; `GroupKFold` on customer id
prevents a customer from having tickets in both train and validation
folds within a CV round, which plain k-fold would allow.
