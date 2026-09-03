# Generative modeling and deep-RL training mechanics

## Generative modeling (non-text modalities)

Three architecture families, one shared evaluation pitfall.

- Goodfellow et al., "Generative Adversarial Networks," 2014 —
  https://arxiv.org/abs/1406.2661. An adversarial minimax game: a
  generator produces samples, a discriminator tries to tell them from real
  data, and the generator is trained to fool it. No explicit likelihood —
  sample quality is only as good as the adversarial equilibrium reached,
  which is notoriously unstable to train (mode collapse: the generator
  finds a narrow set of outputs that reliably fool the discriminator and
  stops exploring the rest of the data distribution).
- Kingma & Welling, "Auto-Encoding Variational Bayes," 2013 —
  https://arxiv.org/abs/1312.6114. The VAE: amortized variational
  inference reframed as a reparameterized, gradient-trainable autoencoder
  objective. Has an explicit (approximate) likelihood, at the cost of
  typically blurrier samples than GANs/diffusion — a direct consequence of
  optimizing a lower bound on likelihood rather than an adversarial
  objective.
- Ho, Jain & Abbeel, "Denoising Diffusion Probabilistic Models," 2020 —
  https://arxiv.org/abs/2006.11239. Generation via learned reversal of a
  fixed noising Markov chain: train a network to iteratively denoise, then
  run the chain backward from pure noise to generate. Currently the
  strongest sample-quality results of the three families, at higher
  inference-time compute cost (many denoising steps per sample).

**Evaluation — the pitfall this file exists to prevent.** Heusel et al.,
"GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash
Equilibrium" (introduces FID), 2017 —
https://arxiv.org/abs/1706.08500. The Fréchet Inception Distance: the
Fréchet distance between Inception-feature statistics (mean/covariance of
a pretrained classifier's penultimate-layer activations) computed over a
real-sample set and a generated-sample set.

Two failure modes to check explicitly before reporting an FID number:

1. **Domain mismatch in the feature extractor.** FID's Inception features
   are trained on ImageNet (natural photographs). Applying the same
   extractor to a non-photographic domain (medical imaging, satellite
   imagery, synthetic sensor data, spectrograms) measures similarity in a
   feature space that was never trained to represent that domain's
   meaningful variation — a low FID in this setting is a weaker signal
   than the same number would be on natural images.
2. **Mode collapse hiding behind a low score.** FID compares aggregate
   feature-space *statistics*, not per-sample perceptual quality. A
   generator that collapses onto a narrow subset of realistic-looking
   modes can still produce a low FID, because the statistics of that
   narrow subset can resemble the statistics of the full real
   distribution closely enough in the summarized (mean/covariance) sense.
   **Report mode-coverage separately** (e.g. recall-focused metrics,
   qualitative diversity checks, or a precision/recall decomposition) — a
   bare single-number FID is not a complete evaluation and must not be
   presented as one.

Also sensitive to sample count: FID estimates are biased at small sample
sizes and only stabilize with a large enough generated/real sample pool —
an FID computed on too few samples understates the true distance.

**Boundary with `ds-llm-systems`.** This subfield covers non-text
generative modalities (image, audio, video, other signal types) only.
Text-generative evaluation — reference-free scoring, LLM-as-judge design,
hallucination/grounding measurement — is `ds-llm-systems`'s scope
entirely; don't apply FID-class reasoning to text generation, the
literatures don't transfer.

## Deep-RL training mechanics

A well-converged training run says nothing about whether the reward was the
right one to optimize; conflating "the algorithm converged stably" with "the
policy is good" is the single most common category error this subfield
exists to prevent.

- Mnih et al., "Playing Atari with Deep Reinforcement Learning," 2013 —
  https://arxiv.org/abs/1312.5602 (the original DQN preprint; the
  peer-reviewed follow-up is Mnih et al., *Nature* 521, 2015, not
  independently fetchable here). Two training-mechanics innovations
  stabilize Q-learning with a neural function approximator, which is
  otherwise prone to divergence: **experience replay** (train on a buffer
  of past transitions sampled i.i.d.-ish, rather than the highly
  correlated sequence the agent just experienced) and a **target
  network** (a slowly-updated copy of the Q-network used to compute
  bootstrapped targets, preventing the network from chasing a target that
  moves every gradient step).
- Schulman et al., "Proximal Policy Optimization Algorithms," 2017 —
  https://arxiv.org/abs/1707.06347. A clipped surrogate objective bounds
  the size of each policy update, giving most of TRPO's stability
  (preventing destructively large policy updates) without TRPO's
  second-order (natural-gradient) machinery. The dominant practical
  choice for policy-gradient training mechanics because of that
  stability-per-implementation-complexity tradeoff.

**What this subfield checks before calling a training run successful:**
the loss/return curve shows the stabilization mechanisms are doing their
job (replay buffer diversity, target-network lag behaving as designed for
DQN; clipped-objective updates staying within bound for PPO) — that's a
training-mechanics claim. Whether the reward signal being optimized
against actually corresponds to the intended objective is explicitly out
of scope here and must be stated as such, not silently implied solved by
a smooth convergence curve.

## Referenced delta-only by

`ds-optimize` hands this subfield an already-framed reward/objective and
consumes back a trained, converged policy; it does not re-derive the
training-stabilization mechanics documented here. `ds-llm-systems` owns
the entire text-generative evaluation literature independently of the
FID-class metrics documented above for non-text modalities.
