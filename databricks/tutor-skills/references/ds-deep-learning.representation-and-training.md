# Representation learning and training mechanics

## Representation learning

Embeddings, autoencoders, self-supervised pretraining, and transfer/
fine-tuning — the question is whether the deliverable is a *reusable
representation*, not a one-off prediction.

- Bengio, Courville & Vincent, "Representation Learning: A Review and New
  Perspectives," IEEE TPAMI 35, 2013 — https://arxiv.org/abs/1206.5538.
  Surveys probabilistic models, autoencoders, and manifold learning under
  the thesis that representation *quality* — not just model capacity —
  drives downstream performance. Sets the frame: a representation is
  evaluated by how well it transfers to tasks it wasn't trained on, not
  only by its training-objective loss.
- Chen, Kornblith, Norouzi & Hinton, "A Simple Framework for Contrastive
  Learning of Visual Representations (SimCLR)," ICML 2020 —
  https://arxiv.org/abs/2002.05709. Self-supervised representation
  learning via an augmented-view contrastive loss — no labels required for
  pretraining. The template for "pretrain without labels, fine-tune with
  few."
- Yosinski, Clune, Bengio & Lipson, "How transferable are features in deep
  neural networks?," NeurIPS 2014 — https://arxiv.org/abs/1411.1792.
  Quantifies the transferability-vs-specificity gradient across network
  layers: early layers transfer broadly (edge/texture detectors), late
  layers specialize to the source task. Co-adapted layers transfer worse
  than naively expected even when fine-tuned — the paper's central
  empirical surprise is that fine-tuning does not always fully recover the
  performance a from-scratch model would reach, when source and target
  tasks are sufficiently dissimilar.

**The failure mode to name explicitly**: transferability is layer- and
task-distance-dependent, not a binary "pretrained = transferable." Every
transfer/fine-tuning claim in the framing note states the source domain,
the target domain, and the distance between them (same modality/different
label space vs. different modality entirely) — a claim that only says
"we used a pretrained model" without that distance statement has not
validated transfer, it has assumed it.

**Boundary with `ds-method-composition`.** Once an embedding is trained,
*consuming* it as a feature in a downstream (possibly non-neural) model is
model-as-feature-extractor composition — `ds-method-composition`'s scope,
cited not restated. This subfield's job ends at "the representation is
trained and its transferability is stated," not at how another model
later ingests it.

## Training mechanics

Four named literatures, each addressing a *different* failure mode.
Treating them as interchangeable "regularization knobs" is the pitfall
this section exists to prevent.

| Mechanism | Addresses | Citation |
|---|---|---|
| Dropout | Unit co-adaptation (overfitting via correlated hidden units) | Srivastava et al., "Dropout," JMLR 15, 2014 — https://jmlr.org/papers/v15/srivastava14a.html |
| LR schedule (cyclical) | Optimization-landscape traversal (getting stuck, needing manual tuning) | Smith, "Cyclical Learning Rates," 2017 — https://arxiv.org/abs/1506.01186 |
| Early stopping | Validation-curve overfitting (training continuing past the point of generalization) | Prechelt, "Early Stopping — but when?," 1998 — https://page.mi.fu-berlin.de/prechelt/Biblio/stop_tricks1997.pdf |
| Distillation | Deployment-size compression (a large "teacher" trained normally, a small "student" trained against its soft outputs) | Hinton, Vinyals & Dean, "Distilling the Knowledge in a Neural Network," 2015 — https://arxiv.org/abs/1503.02531 |

**Dropout** — Srivastava et al.: random unit-masking at training time
approximates training and ensembling exponentially many thinned
sub-networks, then averaging their predictions at test time. Fixes
co-adaptation specifically; does not by itself fix an optimization
that's stuck or a model that's simply underfit.

**Cyclical learning rates** — Smith: oscillating the learning rate within
a bounded range across training removes most of the need for manual
LR-schedule tuning by letting the optimizer periodically escape shallow
local minima/saddle regions. Addresses *how* the loss landscape is
traversed, not whether the model has enough capacity or is overfit.

**Early stopping** — Prechelt: formalizes stopping criteria against the
validation-error generalization-loss curve versus training progress,
rather than a fixed epoch budget. A precondition, not a fix: the model
must already be capable of fitting the data — early-stopping an
*underfit* model (one that hasn't yet reached its achievable training
performance) treats an optimization-time problem as though it were an
overfitting problem, and stops before the model has learned what it
could.

**Distillation** — Hinton, Vinyals & Dean: trains a small "student" network
against a large "teacher" network's soft output distribution (the full
probability vector, not just the hard argmax label), which carries more
information about the teacher's learned decision boundary than a one-hot
label does.

**Wrong-mechanism diagnosis, worked example.** A model's validation loss
plateaus while training loss keeps falling — the textbook overfitting
signature, so early stopping is applied. But if the real cause was an
LR schedule stuck oscillating around a poor local minimum (a landscape
problem, not a generalization-gap problem), early stopping locks in a
suboptimal model instead of fixing the actual optimization issue. The
diagnosis — which curve pattern, which mechanism — is what the framing
note records, not just "we regularized it."

## Online/incremental training mechanics (co-owned with `ds-supervised`)

Training-time mechanics for a model updated incrementally as new data
arrives, as distinct from the *serving* wrapper that routes production
traffic to it. `ds-supervised`'s citation base covers the classical (SGD,
linear/GLM-family) online-learning case; this subfield covers the
neural-network case specifically — the training mechanics above
(regularization, schedule, early stopping, distillation) all still apply,
but must be re-evaluated under a non-stationary data stream rather than
assumed to hold at their offline-tuned settings. Concept drift in the stream
is monitoring's job (`ds-mlops`), not resolved by online training mechanics
alone — this subfield must not imply that failure mode is solved just
because the model updates continuously.

## Referenced delta-only by

`ds-mlops` reads this subfield's distillation mechanics once it has
decided *when/why* to compress; it does not re-derive the training
method. `ds-method-composition` reads a trained representation's
transferability statement as an input to its own composition; it does not
re-run the representation-learning training. `ds-supervised` co-owns the
online/incremental training-mechanics row and defers the neural-specific
case to this file.
