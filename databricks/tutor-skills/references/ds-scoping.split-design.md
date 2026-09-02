# Split design

`ds-model` refines the scheme (CV design choice) but never widens what this
skill withheld. `ds-features` owns fit-on-train-only mechanics;
`ds-evaluate` owns using the chosen scheme for trustworthy comparisons. Each
of those is a distinct concept with its own owner — this skill owns only the
initial decision of what gets held out and when.

## Doctrine pointer

This skill's only delta from that doctrine is **timing**: the split is
decided as a `ds-scoping` output, before `ds-data-models`'s
Observe/Interpret disciplines or any profiling touches the data, not derived
from what's convenient once the data is already in hand. Everything else —
full-data profiling limited to structure/typing/missingness,
target-relationship exploration confined to the train split — is the
doctrine file's content, not restated here.

## Literature

**Literature name**: **data leakage** (data mining) + **pre-registration
for predictive modeling**.

**Canonical methods/refs**:
- Kaufman, Rosset & Perlich, "Leakage in Data Mining: Formulation,
  Detection, and Avoidance" (KDD 2011 / ACM TKDD 2012) —
  https://www.cs.umb.edu/~ding/history/470_670_fall_2011/papers/cs670_Tran_PreferredPaper_LeakingInDataMining.pdf
  — formal taxonomy of illegitimate target-information exposure.
- "Exploring pre-registration for predictive modeling" —
  https://statmodeling.stat.columbia.edu/2023/12/06/exploring-pre-registration-for-predictive-modeling/
  (links https://arxiv.org/abs/2311.18807) — adapts pre-registration from
  explanatory to predictive modeling to curb adaptive/forking-paths
  overfitting to test data.

**Failure modes**: pre-registration cannot prevent leakage by itself, only
make forking-path decisions auditable — don't oversell `split_design` as a
clinical-trial-style guarantee. It's a recorded commitment, not an
enforcement mechanism; `ds-verify` is what checks the commitment held.

## Worked minimum

`split_design` names: the split unit (must match, or be coarser than,
`unit` from framing — splitting rows when the real unit is accounts leaks
across the split), the split mechanism (time-based, group-based, random —
and why), and the point at which the split is drawn relative to any
time-varying feature. A split_design that doesn't name a unit is
incomplete: it can't be checked against the framing subfield's `unit`
field, which is exactly the join `ds-features`'s post-join cardinality gate
and `ds-model`'s group-key CV gate both depend on downstream.
