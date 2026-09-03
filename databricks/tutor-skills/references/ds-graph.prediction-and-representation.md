# Link prediction and graph representation learning

## Link prediction

**Literature name**: the link prediction problem.

**Canonical methods/refs**: Liben-Nowell & Kleinberg, "The Link Prediction
Problem for Social Networks," CIKM 2003 —
https://www.cs.cornell.edu/home/kleinber/link-pred.pdf : formalizes
predicting future/missing edges from network structure alone and
benchmarks proximity-based predictors; fetched successfully as a binary
PDF directly from the author's own hosted copy (title/authorship not
independently re-extracted from text, but existence and hosting
confirmed).

**Failure modes**: proximity-based predictors assume future links
correlate with current structural proximity — this fails under structural
change (new communities forming). Evaluation requires a held-out edge set
that respects the graph's actual leakage boundary, not an arbitrary random
split.

**Leakage delta — the graph-specific boundary**: link-prediction splits
leak through **shared neighborhoods** and, on a temporal graph, through
**temporal edge order** — not merely through row/edge independence the way
a tabular k-fold split does. Two structurally adjacent edges removed into
different folds still let information flow between them via their shared
neighbors, so a naive random edge-holdout overstates achievable
performance.

**Static-graph holdout (this skill's own leakage constraint, no temporal
pairing)**: state the scheme explicitly rather than leaving "random edge
removal" unstated. Two admissible patterns:
- **Structurally distant holdout**: held-out edges are chosen to connect
  nodes with low structural overlap with the training edge set (e.g. no
  shared neighbor within k hops), so the predictor is scored on genuine
  generalization rather than short-range proximity leakage.
- **Stratified random removal**: edges removed at random but stratified
  to preserve node degree distribution and avoid disconnecting
  components, with the stratification scheme and its rationale stated in
  the framing note.
Either pattern is acceptable; a scheme description that says only "held
out 20% of edges" with no stratification/distance rationale fails the
static-graph split gate (`SKILL.md` Gates).

**Temporal graph handoff**: when the graph carries a time dimension and
`ds-timeseries` is paired in (`SKILL.md` Pairings), that skill's rolling-
origin / temporal-CV protocol governs the split — this skill does not
re-derive a competing scheme (multi-family rule: the family owning the
strongest leakage constraint leads). The echo from `ds-timeseries`'s own
temporal leakage entry: "evaluation requires a held-out edge set that
respects temporal order (train-time/test-time edge split)."

## Embeddings

**Literature name**: graph representation learning; graph neural
networks.

**Canonical methods/refs**:
- Hamilton, Ying, Leskovec, "Representation Learning on Graphs: Methods
  and Applications," *IEEE Data Engineering Bulletin*, 2017
  (arXiv:1709.05584) — https://arxiv.org/abs/1709.05584 : conceptual
  review of matrix-factorization, random-walk, and GNN-based embedding
  methods.
- Kipf & Welling, "Semi-Supervised Classification with Graph Convolutional
  Networks," ICLR 2017 (arXiv:1609.02907) —
  https://arxiv.org/abs/1609.02907 : canonical GCN architecture, a
  localized first-order spectral-convolution approximation.

**Failure modes**: embedding methods assume the graph structure at
training time is representative of structure at inference time.
Inductive (GCN-style, generalizes to unseen nodes) vs. transductive
(matrix-factorization-style, fixed node set) methods are not
interchangeable — using a transductive method on a graph that grows in
production silently breaks at serving time, because the method has no way
to place a node it never saw during fitting.

**This skill's boundary**: `ds-graph` owns the framing choice — which family
fits (transductive vs. inductive) and why, given whether unseen nodes will
appear at serving time. This skill does not re-derive GNN training
mechanics; it hands off the framing decision and the fit-on-train-only graph
boundary.

**Worked minimum**: the framing note states the serving-time question
first — "will nodes unseen at fit time need embeddings at serving time?"
— then names the method family it implies (yes → inductive/GNN-style;
no → transductive is admissible), before any embedding is fit. An
embedding chosen for training convenience with no answer to that question
on record fails the framing gate the same way an unstated
when-graph-beats-tabular hypothesis does.
