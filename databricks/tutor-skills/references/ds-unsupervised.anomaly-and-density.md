# Anomaly-as-the-task and density estimation

Full depth and citations for the anomaly-as-the-task and density-estimation
subfields. `SKILL.md` states triggers and dispatch fields only; this file
carries the method detail.

## Anomaly-as-the-task {#anomaly}

**Literature name**: **unsupervised/semi-supervised anomaly detection** —
distinct from `ds-clean`'s outlier-handling-as-cleaning-step framing; here
anomaly detection *is* the deliverable, not a preprocessing step toward
some other model.

**Canonical methods**: distance-based, density-based (LOF), statistical,
classification-based (Chandola et al.'s taxonomy, by the assumption each
makes about "normal"); isolation-based (Isolation Forest) as a distinct
fifth family that skips profiling normality entirely.

**Source**: Chandola, Banerjee & Kumar, "Anomaly Detection: A Survey," ACM
Computing Surveys 41(3), 2009 —
https://conservancy.umn.edu/server/api/core/bitstreams/fbdbe084-f11f-45b1-856e-8c9d58091241/content.
Canonical taxonomy — distance-, density-, statistical-, classification-
based — organized by the underlying assumption about what "normal" looks
like.

**Source**: Liu, Ting & Zhou, "Isolation-Based Anomaly Detection," ACM
TKDD 6(1), 2012 (extended journal version of the 2008 ICDM paper) —
https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/tkdd11.pdf. Isolates
points via random recursive partitioning rather than profiling normality;
anomalies isolate in fewer splits, giving linear-time detection without a
density/distance model.

**Source**: Breunig, Kriegel, Ng & Sander, "LOF: Identifying Density-Based
Local Outliers," SIGMOD 2000 — https://dl.acm.org/doi/10.1145/335191.335388.
**Paywall-corroborated**: ACM DL blocks fetch; existence and mechanism
independently corroborated via the Wikipedia "Local outlier factor"
article plus consistent bibliographic metadata across Scientific Research
Publishing and Semantic Scholar.

**Failure mode**: validating a detector "without labels" still requires
*some* ground-truth surrogate — injected synthetic anomalies, held-out rare
events, or expert audit of the top-scored points. A detector's own score
distribution is never self-validating; "these are the highest- scored 1%" is
a selection rule, not evidence those points are actually anomalous.
Isolation Forest and LOF encode different normality assumptions — global
sparsity (isolation depth) vs. local density (neighborhood comparison) — so
detector disagreement is evidence of a data region where the two assumptions
diverge, not evidence one detector is simply wrong.

## Density estimation {#density}

**Literature name**: **kernel density estimation (KDE)** and nonparametric
density estimation generally.

**Canonical methods**: KDE with a chosen kernel (shape) and bandwidth
(smoothing); bandwidth-selection rules (e.g. Silverman's rule-of-thumb,
cross-validated bandwidth).

**Source**: Silverman, *Density Estimation for Statistics and Data
Analysis*, Chapman & Hall, 1986 —
https://ned.ipac.caltech.edu/level5/March02/Silverman/paper.pdf. Standard
reference on kernel choice, bandwidth selection, and the bias-variance
tradeoff in smoothing.

**Failure mode**: bandwidth selection dominates estimate quality far more
than kernel shape — an unstated or default bandwidth is effectively an
unstated smoothing assumption, not a neutral default; too narrow overfits
to sampling noise, too wide smooths away real structure. Density
estimates in more than 3-4 dimensions degrade sharply (curse of
dimensionality, data sparsity grows faster than sample size can fill it)
and need explicit justification before use — a high-dimensional KDE
presented without that justification, or without first projecting to a
lower-dimensional space, is under-evidenced the same way an unstated
bandwidth is.

**Composition note**: a density estimate is a common building block for a
density-based anomaly score (low estimated density at a point → high
anomaly score) — when used that way, both this subfield's bandwidth gate
and the anomaly subfield's ground-truth-surrogate gate apply to the
combined result, not just one.
