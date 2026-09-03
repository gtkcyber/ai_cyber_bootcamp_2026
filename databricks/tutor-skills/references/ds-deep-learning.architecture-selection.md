# Architecture selection

## When neural beats classical

**The live empirical debate, not a settled decision rule.** Grinsztajn,
Oyallon & Varoquaux, "Why do tree-based models still outperform deep
learning on tabular data?," NeurIPS 2022 (Datasets & Benchmarks) —
https://arxiv.org/abs/2207.08815. Across 45 benchmark datasets, tree-based
models (GBMs) remain state-of-the-art on medium-sized tabular data. The
paper identifies *why*, not just *that*:

- **Uninformative features.** Neural nets are less robust to
  uninformative/noisy columns than tree ensembles, which split around them
  for free.
- **Orientation sensitivity.** Rotating the feature space (a
  no-op for a tree split) degrades an MLP's fit — trees are invariant to
  feature-axis rotation, dense nets are not.
- **Irregular target functions.** Tabular targets are often locally
  irregular in ways a smooth neural function approximator fits less
  naturally than a piecewise-constant tree ensemble.

**Scope of the claim.** This is a *current empirical finding on
medium-sized tabular data specifically* — the paper does not claim a
general theorem, and the authors are explicit that the result may not hold
as dataset size or feature-engineering sophistication changes. Do not
extrapolate the tree-beats-NN conclusion to image, audio, text, or graph
data, where the opposite is well established (see architecture-by-shape,
below) — the tabular regime is the one place classical wins by default.

**What would justify trying a neural net anyway, even on medium tabular
data:**
- The task needs a *reusable representation* shared across a multimodal
  pipeline (an embedding that also feeds a perception or text model) —
  route to Representation learning.
- The deployment needs *online/incremental updates* a tree ensemble
  doesn't support as naturally.
- Entity embeddings are wanted specifically for high-cardinality
  categorical encoding — that's `ds-features`' Encodings subfield's call,
  not this family's, but it does route back here for the actual embedding
  training mechanics once selected.
- The benchmarked regime doesn't apply (data is much larger than the
  paper's medium-sized benchmarks, or heavily unstructured columns are
  mixed into an otherwise-tabular table).

None of these are automatic — each is a stated reason recorded in the
framing note, not a default. The actual escalate-or-not decision and its
cost accounting is `ds-model`'s baseline-first ladder + selection
economics (`references/doctrine-scale-cost.md`); this subfield only supplies the
justification for treating "neural" as a candidate worth costing out.

## Architecture selection by data shape

**Geometric deep learning**: architecture choice as encoding a data
domain's symmetry group, not a stylistic preference.

- Bronstein, Bruna, Cohen & Veličković, "Geometric Deep Learning: Grids,
  Groups, Graphs, Geodesics, and Gauges," 2021 —
  https://arxiv.org/abs/2104.13478. Unifies CNNs, GNNs, and Transformers as
  instances of one symmetry-group-equivariance framework: a CNN encodes
  translation equivariance for grid data, a GNN encodes permutation
  equivariance for graph-structured data, a Transformer (via self-
  attention) encodes permutation equivariance for set/sequence data absent
  an explicit positional signal. Architecture choice should follow the
  data's geometric structure, not familiarity or library convenience.
- LeCun, Bottou, Bengio & Haffner, "Gradient-Based Learning Applied to
  Document Recognition," Proc. IEEE 86(11), 1998 —
  http://yann.lecun.com/exdb/publis/pdf/lecun-01a.pdf. The founding case
  for grid-structured (image) data: local receptive fields and weight
  sharing exploit spatial locality and translation invariance.
- Vaswani et al., "Attention Is All You Need," NeurIPS 2017 —
  https://arxiv.org/abs/1706.03762. The founding case for sequence/set-
  structured data: self-attention dispenses with recurrence and
  convolution, at the cost of needing an explicit positional encoding to
  recover order when order is semantically load-bearing.

**Decision table** (illustrative, not exhaustive — canonical methods per
the Subfields section, not a closed list):

| Data shape | Symmetry encoded | Architecture class |
|---|---|---|
| Grid (image, spectrogram-as-image) | Translation | CNN |
| Sequence/set (text tokens, event streams, unordered bags) | Permutation (+ positional encoding if order matters) | Transformer |
| Graph (relational structure) | Permutation over nodes/edges | GNN |
| Tabular, medium-sized | — | Not this row — see "When neural beats classical" above |

**Failure mode, stated plainly.** Matching architecture to data shape is a
*prior*, not a guarantee of fit. A CNN's translation-equivariance
assumption is wrong for non-grid-aligned sensor data (e.g. an irregularly
sampled sensor array reshaped into a pseudo-grid); a Transformer's
permutation handling still needs an explicit positional encoding to
recover order when order matters, and omitting one silently discards
sequence information the architecture was chosen specifically to exploit.
State the symmetry assumption explicitly in the framing note — don't let
"CNN because it's an image" stand in for verifying the grid structure is
real and aligned.

**Boundary with `ds-perception` and `ds-graph`.** "Which pretrained family
fits this modality" for perception data (images, audio, sensor signals)
is `ds-perception`'s framing call — it owns modality preprocessing and the
transfer-distance judgment for that specific domain; this subfield owns
the architecture-class decision and everything after that framing choice
(training, fine-tuning mechanics). Graph *construction* from tabular data
and when graph framing beats tabular framing is `ds-graph`'s; this
subfield owns the GNN training mechanics once a graph is framed and an
architecture selected.

## Referenced delta-only by

`ds-model`'s baseline-first ladder and selection economics consume this
subfield's "neural is a candidate" verdict — they don't re-derive it.
`ds-perception` and `ds-graph` own the upstream framing calls this
subfield's architecture decision depends on; this file states only the
architecture-class decision itself, not their framing logic.
