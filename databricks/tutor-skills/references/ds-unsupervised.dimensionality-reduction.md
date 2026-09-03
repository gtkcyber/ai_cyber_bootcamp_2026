# Dimensionality reduction for structure discovery

Full depth and citations for the DR subfield. `SKILL.md` states triggers
and dispatch fields only; this file carries the method detail.

## Dimensionality reduction {#dr}

**Literature name**: nonlinear **manifold learning / embedding**, as
distinct from linear methods (PCA) used for feature decorrelation
(`ds-features`' province, not this subfield's — the boundary is *why* the
reduction is being done: decorrelating inputs for a downstream fit vs.
discovering/visualizing structure as the deliverable itself).

**Canonical methods**: t-SNE (neighbor-probability matching between
high- and low-dimensional space via a heavy-tailed low-D kernel, reducing
crowding), UMAP (Riemannian-geometry/algebraic-topology framework;
competitive visualization quality with better global-structure
preservation and runtime than t-SNE).

**Source**: van der Maaten & Hinton, "Visualizing Data using t-SNE," JMLR
9, 2008 — https://jmlr.org/papers/v9/vandermaaten08a.html.

**Source**: McInnes, Healy & Melville, "UMAP: Uniform Manifold
Approximation and Projection for Dimension Reduction," 2018 —
https://arxiv.org/abs/1802.03426.

**Failure mode**: neither method preserves global inter-cluster distances
by design. Axis positions and inter-cluster gaps in a t-SNE/UMAP plot are
not meaningful distances and must not be read as such — two clusters
drawn far apart are not necessarily more different than two drawn close
together; only local neighbor relationships are (approximately)
preserved. Both are sensitive to their neighborhood/perplexity
hyperparameter, which changes the apparent cluster count — a different
perplexity on the same data can show a different number of visual
clusters without the underlying data changing. Every plot presented
states the parameter used and disclaims the distance-reading pitfall
explicitly (`SKILL.md` Gates), not as a footnote elsewhere.

## Representation-learning boundary {#representation-boundary}

The discriminating question is who consumes the output, not which algorithm
produced it: PCA/t-SNE/UMAP can all appear on either side of that line
depending on what happens to their output next.
