# Doctrine: leakage

Stated once, here. Every skill states only its delta from this and links
back — never restates the principle.

## Principle

Leakage includes **point-in-time correctness** — this is generic physics,
not a domain peculiarity. No transform, feature, split, or evaluation may
use information that would not have been available at decision time in the
population it is applied to.

## Split-timing rules

- The **initial split is a `ds-scoping` output** — split design is decided
  before profiling or modeling begins, not derived from what's convenient
  once the data is in hand.
- **Full-data profiling is limited to structure, typing, and missingness.**
  Nothing about the target or target-correlated behavior may be examined
  across the full dataset.
- **Target-relationship exploration is train-only.** Any analysis that
  relates features to the target (correlation, distribution-by-class,
  target-encoding statistics) runs on the train split only.

- **Generators fit train-only.** Any generator whose output a model will
  train on (synthetic data, SMOTE-class augmentation, model-as-imputer) is
  fit and run on the train split only — otherwise synthetic rows carry
  held-out information into training (`ds-simulation`,
  `ds-method-composition` state the mechanics).

## Ownership of split mechanics
