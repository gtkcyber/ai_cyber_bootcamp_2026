# CNN framing and pretrained-family selection

## CNN framing

LeCun, Bottou, Bengio & Haffner, "Gradient-Based Learning Applied to
Document Recognition," Proc. IEEE 86(11), 1998 —
http://yann.lecun.com/exdb/publis/pdf/lecun-01a.pdf : the founding CNN
architecture — local receptive fields, weight sharing, pooling — for 2-D
grid-structured signals. This is the default framing this family owns for
grid-shaped perception input (images, and spectrograms treated as images)
before handing training/fine-tuning to `ds-deep-learning`.

## Pretrained-family selection is a transferability question

Yosinski, Clune, Bengio & Lipson, "How transferable are features in deep
neural networks?," NeurIPS 2014 — https://arxiv.org/abs/1411.1792 :
quantifies the transferability-vs-specificity gradient across network
layers. Early layers transfer more readily than late layers; co-adapted
layers transfer worse than expected even after fine-tuning. The result is
layer- and task-distance-dependent, not a binary "pretrained = transfers."

**Domain distance is the governing variable, and it must be stated as a
bet, not assumed closed by architecture similarity.** Three candidate
choices, in order of decreasing domain distance from natural-image
pretraining:

- **Natural-image-pretrained CNN** (e.g. ImageNet-family weights) — closest
  fit for photographic image input; a stated bet, not a neutral default,
  when applied to anything else.
- **Modality-specific pretrained model** (audio-pretrained, sensor-domain-
  pretrained, or a spectrogram-domain-pretrained model where one exists) —
  closer domain match than a natural-image model for non-photographic
  input; still requires stating what the pretraining domain actually was
  and how far this task's data sits from it.
- **From-scratch architecture** — no transfer bet at all, at the cost of
  needing enough task data to train the representation from nothing;
  the right default when neither pretrained option's domain is
  defensibly close.

A natural-image-pretrained CNN applied to spectrograms or sensor-array
data is a domain-shift bet — spectrograms share a 2-D grid structure with
photographs but not the same low-level statistics (edges, textures,
color) the pretraining learned to detect. Applying it anyway can still
work, but the gap between pretraining domain and task domain must be
stated in the framing note, not silently assumed closed because both are
"images" in tensor shape.

## Handoff

This subfield's output is the selection and its stated domain-shift
rationale, not a trained model.

## Gate mapping

Pretrained-family selection states the domain-distance bet explicitly
(`SKILL.md` Gates) — an unstated assumption that architecture-shape
similarity implies transferability fails this gate.
