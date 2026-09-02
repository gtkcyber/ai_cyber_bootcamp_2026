# Clustering and label-free validation

Full depth and citations for the clustering subfield and the stability
half of this family's label-free validation discipline. `SKILL.md` states
triggers and dispatch fields only; this file carries the method detail.

## Clustering {#clustering}

**Literature name**: cluster analysis; the validation half is **cluster
internal validation indices** (silhouette, Dunn, Davies-Bouldin family).

**Canonical methods**: k-means (centroid-based, assumes roughly convex/
similarly-sized clusters), hierarchical agglomerative (dendrogram, no *k*
required up front), DBSCAN (density-based, arbitrary shape, no *k*
required, sensitive to its eps/min-points pair), Gaussian mixture models
(soft assignment, elliptical clusters via covariance structure).

**Source**: Rousseeuw, "Silhouettes: A Graphical Aid to the Interpretation
and Validation of Cluster Analysis," J. Computational and Applied
Mathematics 20, 1987 —
https://wis.kuleuven.be/stat/robust/papers/publications-1987/rousseeuw-silhouettes-jcam-sciencedirectopenarchiv.pdf.
Per-point tightness-vs-separation score, averaged into a whole-clustering
quality measure usable to pick *k*.

**Source**: Halkidi, Batistakis & Vazirgiannis, "On Clustering Validation
Techniques," J. Intelligent Information Systems 17, 2001 —
https://web.itu.edu.tr/sgunduz/courses/verimaden/paper/validity_survey.pdf.
Taxonomizes internal, external, and relative validation criteria and
surveys the index families within each.

**Failure mode**: internal indices — silhouette included — encode a
geometric assumption, typically convex, similarly-sized clusters. A high
silhouette score on non-convex or highly unequal-density clusters is not
evidence of a good partition. Never present one index's optimum as
label-free ground truth without stating its geometric bias; a k-means run
scored by silhouette on data with elongated or nested clusters will report
a confidently wrong *k*.

## Stability as a complementary check {#stability}

**Status**: grounded in Halkidi et al.'s **relative validation** category
— criteria that compare clusterings against each other (across parameter
values or resampled subsets) rather than against an absolute internal
score or an external label. Resampling/parameter-stability comparison
(does the same *k* and roughly the same partition recur across bootstrap
resamples or small parameter perturbations) sits in this category.

**Failure mode**: stability is not a substitute for stating an internal
index's geometric bias, and the reverse also holds. A clustering can be
highly stable — the same wrong partition recurs on every resample — and
still be geometrically wrong for the data's actual shape, because
instability (sensitivity to sampling noise) and geometric mismatch
(wrong assumed cluster shape) are different failure modes that happen to
both hide behind "the index looks good." Report both when *k* is chosen
from the data rather than stated by the ask; reporting either alone is
under-evidenced.

**Escalation**: k-means/GMM assume roughly convex/elliptical clusters by
construction — persistent instability *and* a low silhouette together are
evidence the assumed shape doesn't fit; DBSCAN or a density-based
reframing (`references/ds-unsupervised.anomaly-and-density.md#density`) is the next
rung, not a different *k* on the same method.
