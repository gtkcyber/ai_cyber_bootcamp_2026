---
name: ds-deep-learning
description: "Neural-network method family: when a neural approach beats classical (Grinsztajn tabular result), architecture selection by data shape (geometric deep learning), representation learning (embeddings, autoencoders, self-supervised, transfer/fine-tuning), training mechanics (regularization, schedules, early stopping…"
---

# ds-deep-learning

Full depth, worked examples, and citations live in `references/`. This
file is protocol only.

## Subfields

- **When neural approaches beat classical** — trigger: "neural net or
  classical/tree model," "would deep learning help here." No canonical
  method — a decision node. Grinsztajn, Oyallon & Varoquaux, NeurIPS 2022,
  https://arxiv.org/abs/2207.08815 : across 45 medium tabular benchmarks
  GBMs remain state-of-the-art — a current empirical finding on medium
  tabular data specifically, never extrapolated to image/audio/text/graph,
  where the opposite holds. Feeds `ds-model`'s selection economics, never
  overrides it. See
  `references/ds-deep-learning.architecture-selection.md#when-neural-beats-classical`.
- **Architecture selection by data shape** — trigger: neural approach
  selected/framed on image/audio/video/sensor/sequence/set/graph-shaped
  data. Canonical methods: CNN (grid), Transformer (sequence/set), GNN
  (graph) — one symmetry-equivariance framework (Bronstein, Bruna, Cohen &
  Veličković, 2021, https://arxiv.org/abs/2104.13478) unifying LeCun et
  al. 1998's grid case and Vaswani et al., NeurIPS 2017's sequence/set
  case. A prior, not a guarantee — a CNN's translation-equivariance can be
  wrong for non-grid-aligned sensors. Pretrained-family fit for a
  perception modality is `ds-perception`'s framing call. See
  `references/ds-deep-learning.architecture-selection.md#architecture-selection-by-data-shape`.
- **Representation learning** — trigger: "need an embedding/pretrained
  representation," "should we self-supervise," "does this transfer."
  Canonical methods: autoencoders, self-supervised contrastive
  pretraining, transfer/fine-tuning. Bengio, Courville & Vincent, IEEE
  TPAMI 35, 2013; Chen et al. (SimCLR), ICML 2020; Yosinski et al.,
  NeurIPS 2014 — https://arxiv.org/abs/1411.1792 (transferability is
  layer- and task-distance-dependent, not binary — validate per use case,
  never assume). Consuming an embedding downstream as a feature is
  `ds-method-composition`'s. See
  `references/ds-deep-learning.representation-and-training.md#representation-learning`.
- **Training mechanics** — trigger: "not converging/overfitting," "what
  regularization/schedule/early-stopping," "compress this model," "update
  online." Canonical methods: dropout, cyclical LR schedules, early
  stopping, distillation (Srivastava et al. 2014; Smith 2017; Prechelt
  1998; Hinton, Vinyals & Dean 2015, https://arxiv.org/abs/1503.02531).
  Not interchangeable — each addresses a distinct failure mode
  (co-adaptation / landscape traversal / overfitting / compression); the
  wrong one is a wrong-mechanism error, not a tuning error. Co-owned with
  `ds-supervised` for online/incremental mechanics; when/why to compress
  is `ds-mlops`'s. See
  `references/ds-deep-learning.representation-and-training.md#training-mechanics`.
- **Generative modeling (non-text)** — trigger: "generate new
  images/audio/samples," "build a GAN/diffusion/VAE," "evaluate generated
  quality." Canonical methods: GANs, VAEs, diffusion; FID-class evaluation
  (Goodfellow et al. 2014; Kingma & Welling 2013; Ho, Jain & Abbeel 2020;
  Heusel et al., https://arxiv.org/abs/1706.08500 — compares feature-space
  statistics, not perceptual quality; mode collapse can hide behind a low
  score — report mode-coverage separately, never a bare FID). Text-
  generative evaluation is `ds-llm-systems`'s. See
  `references/ds-deep-learning.generative-and-rl.md#generative-modeling`.
- **Deep-RL training mechanics** — trigger: "train/stabilize this deep-RL
  policy" — reward framing already done in `ds-optimize`. Canonical
  methods: DQN (experience replay + target network), PPO (clipped
  surrogate objective) — Mnih et al. 2013, https://arxiv.org/abs/1312.5602;
  Schulman et al. 2017, https://arxiv.org/abs/1707.06347. Training-
  mechanics results, not problem-framing results — a well-converged run
  against a misspecified reward is a stable failure, not a success. See
  `references/ds-deep-learning.generative-and-rl.md#deep-rl-training-mechanics`.

`mandatory`: every composition answers the neural-vs-classical question
first. The load-order-3 rows fire only on their own trigger and may
co-occur (e.g. representation learning feeding a generative model).

## Selection tree

1. Tabular, medium-sized (the Grinsztajn et al. regime)? **Yes** → GBMs
   are the benchmarked-strong default (`ds-supervised`) — a neural net
   needs a stated reason (multimodal reuse, online updates, out-of-regime
   scale) before `ds-model`'s ladder costs it out.
2. **No** (image/audio/video/sensor/text/graph/sequence/set): which
   symmetry does the data carry? Grid → CNN. Sequence/set → Transformer
   (positional encoding if order matters). Graph → GNN (framing:
   `ds-graph`). → Architecture selection by data shape.
3. Needs a reusable representation, not a one-off prediction? →
   Representation learning; else train the framed architecture directly.
4. Deliverable is new samples, not a prediction? → Generative modeling
   (mode-coverage reported alongside any FID-class number).
5. Framed problem is a sequential-decision/policy one (framed upstream in
   `ds-optimize`)? → Deep-RL training mechanics.

Every path converges on Training mechanics once an architecture is chosen
and data exists to fit it.

## Family-specific pitfalls and evaluation

- Neural architecture on medium tabular data with no stated reason the
  Grinsztajn et al. GBM edge doesn't apply.
- Architecture-to-shape matching treated as a guarantee, not a prior.
- "Pretrained = transferable" treated as binary, not validated per use
  case (Yosinski et al.).
- Wrong-mechanism diagnosis in training — dropout/schedule/early-stopping/
  distillation applied interchangeably rather than to the failure mode
  each addresses.
- A single FID number reported with no mode-coverage stated.
- A well-converged deep-RL run treated as a good-policy claim when the
  reward/framing was never validated.

**Evaluation delta from `ds-evaluate`'s generic scorecard**: the metric is
architecture-dependent (FID-class for generative work, standard
discriminative metrics otherwise); a reported metric states which
pitfalls above were checked against this task's actual data, not just
the number.
