---
name: ds-unsupervised
description: "Unsupervised method/goal family: clustering (k-choice, label-free validation), dimensionality reduction for structure discovery, anomaly-as-the-task (detector families, validation without labels), density estimation."
---

# ds-unsupervised

Composes after `ds-features` writes the feature dictionary and pipeline
object, alongside `ds-model` (wraps this family's candidates in the
cross-family selection procedure — never itself picks an algorithm class).
No subfield here has a target — every validation claim below stands
without one. Full depth, citations, and failure modes: `references/`;
this file is protocol only.

## Subfields

- **Clustering (k-choice, label-free validation)** — trigger: "group these
  into segments," "find natural clusters," "how many clusters." participation:
  `mandatory` when the deliverable is a partition of instances with no
  known labels. Canonical methods (not exhaustive): k-means, hierarchical
  agglomerative, DBSCAN, Gaussian mixture models. Edges: an internal
  index's optimum is not label-free ground truth — it encodes a geometric
  assumption about cluster shape (see Gates). See
  `references/ds-unsupervised.clustering-and-validation.md#clustering`.
- Canonical methods: t-SNE, UMAP (nonlinear/manifold); PCA (linear,
  `ds-features`' province when used purely for feature decorrelation — this
  subfield owns DR as the deliverable itself). Edges: a learned
  representation destined for a downstream model, not for human/structure
  inspection, is `ds-deep-learning`'s representation-learning subfield — the
  boundary is *who consumes the output*, not the algorithm. See
  `references/ds-unsupervised.dimensionality-reduction.md#dr`.
- **Anomaly-as-the-task (detector families, validation without labels)** —
  trigger: "find the unusual/rare instances" as the deliverable itself — not
  a data-cleaning step, not a temporal-context question, not production
  monitoring. Canonical methods: distance-based, density-based (LOF),
  statistical, isolation- based (Isolation Forest), classification-based
  (Chandola et al.'s taxonomy). Edges: a detector's own score distribution
  is never self-validating (see Gates); disagreement between detector
  families reflects different normality assumptions, not one detector being
  wrong. See `references/ds-unsupervised.anomaly-and-density.md#anomaly`.
- Canonical methods: kernel density estimation (KDE), bandwidth-selection
  rules. Edges: bandwidth choice dominates estimate quality more than kernel
  shape;
  >3-4 dimensions degrades sharply and needs explicit justification, not a
  default. See `references/ds-unsupervised.anomaly-and-density.md#density`.

## Selection tree

1. **Deliverable shape first — this determines the subfield, not library
   familiarity.**
2. Deliverable is a partition of instances into groups, no known labels? →
   **Clustering**. *k* stated up front by the ask? Fit directly. *k* must
   be chosen from the data? → internal-index selection (state the index's
   geometric bias) plus a stability check across resamples/parameter
   perturbations (`references/ds-unsupervised.clustering-and-validation.md#stability`) —
   neither alone is label-free ground truth.
3. Deliverable is a low-dimensional map for a human to inspect, not an input
   to another model? → **Dimensionality reduction**.
4. Deliverable is "which instances are unusual" under this task's own
   definition of normal — not cleaning (`ds-clean`), not temporal/seasonal
   context (`ds-timeseries`), not production monitoring (`ds-mlops`)? →
   **Anomaly-as-the-task**. One detector validatable against a named
   ground-truth surrogate → fit and validate directly.
5. Deliverable is the density itself, or a density-based score needed by
   step 4? → **Density estimation**, bandwidth selection stated explicitly.
6. Deliverable references temporal or spatial structure? The corresponding
   family leads the split/validation scheme when it owns the stronger
   leakage constraint — this family still supplies the candidate method.

## Family-specific pitfalls and evaluation

**Label-free validation is this family's centerpiece pitfall** — every
subfield above lacks a target, so "how do we know this is right" has no
generic answer; two label-free tools exist and neither is self-sufficient:

- **Internal validation indices** (silhouette, Dunn, Davies-Bouldin)
  encode a geometric assumption — typically convex, similarly-sized
  clusters. A high silhouette score on non-convex or highly unequal-
  density clusters is not evidence of a good partition; report the index's
  known geometric bias alongside its value, never the value alone.
- **Stability** (agreement across resamples/parameter perturbation,
  Halkidi et al.'s relative-validation category) complements internal
  indices, never replaces them — a clustering can be perfectly stable and
  still geometrically wrong, since instability and geometric mismatch are
  different failure modes.
- **Detector validation without labels** still needs *some* ground-truth
  surrogate — injected synthetic anomalies, held-out rare events, expert
  audit of top-scored points. A detector's own score distribution is never
  self-validating.
- **Neighbor/manifold DR plots are not distance plots** — t-SNE/UMAP
  preserve local neighbor structure, not global inter-cluster distance;
  axis positions and gaps are not meaningful, and both are sensitive to
  their neighborhood/perplexity hyperparameter, which shifts the apparent
  cluster count.
- **Density estimates decay silently past 3-4 dimensions** — an
  unjustified high-dimensional KDE is a hidden smoothing assumption, not a
  neutral default.

**Evaluation delta.** `ds-evaluate` owns the generic scorecard; this
family's delta *is* the label-free discipline above — every reported
result states which internal index, stability check, or ground-truth
surrogate backs it, not a bare metric number.
