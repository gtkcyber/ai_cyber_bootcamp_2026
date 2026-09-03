# Caveats and deep-learning interpretability

Worked depth for the mandatory caveats subfield and the deep-learning
interpretability bundle. `SKILL.md` carries the protocol and full
citations; this file carries the mechanics.

## When explanations lie {#when-explanations-lie}

This subfield is not optional and not one failure mode — it is the gate
every other subfield in this skill passes through before its output ships.
Three distinct mechanisms, all traceable to the same root cause (Hooker,
Mentch & Zhou 2019): **permute-and-predict methods break the joint feature
distribution and force the model to extrapolate into regions it was never
fit on**, and the resulting numbers get read as "importance" when they are
actually reflecting the model's arbitrary behavior in a region it has no
real evidence about.

- **Correlated features.** Permutation importance, PDP/ICE, and SHAP's
  independence-assuming approximations all evaluate the model at
  combinations that violate the real joint distribution when the permuted/
  swept feature correlates with another. Check: for any pair of features
  both entering an explanation, was their correlation checked? A
  correlation above a stated threshold (context-dependent — state the
  threshold used, not a universal cutoff) means the resulting attribution
  needs this caveat attached, not silent trust.
- **Interaction masking.** When two features interact (their joint effect
  isn't the sum of their separate effects), attribution methods that
  decompose the prediction into per-feature contributions must choose how
  to allocate the interaction's effect. SHAP's Shapley-value construction
  allocates interaction effects across the interacting features by
  construction (splitting credit by each feature's marginal contribution
  averaged over orderings) rather than surfacing the interaction as its
  own entity — a large SHAP value on one interacting feature can be
  *most* of an interaction effect, misread as that feature's independent
  contribution. Check: does the model's structure (tree depth > 1,
  attention over multiple tokens, an explicit interaction term) suggest
  interactions are present? If so, name which features interact before
  reporting single-feature attributions as if they were independent.
- **Off-manifold evaluation.** The general form of both mechanisms above:
  any method that evaluates the model away from the training data's actual
  support (permuted values, marginalized sweeps, synthetic baselines) is
  measuring model behavior in a region with no real evidence backing it,
  and that behavior can be arbitrary — a tree-based model in particular has
  no basis for extrapolating past its training splits' leaves. Check:
  would the specific feature-value combination the explanation method
  evaluated ever plausibly occur in the real data? If the answer is "no"
  or "unclear," the caveat is required, not optional.

## Deep-learning interpretability {#dl-interpretability}

Four method families, escalating in what they explain:

- **Saliency maps** (Simonyan, Vedaldi & Zisserman 2013/2014): the gradient
  of the output with respect to each input pixel/token, visualized
  directly. Cheapest, noisiest — raw gradients are visually scattered and
  can be manipulated by adversarial input perturbations that leave the
  prediction unchanged but substantially alter the saliency map, so a
  saliency map's *stability* under small input perturbation should be
  checked before it is reported as a reliable attribution, not just its
  face-value appearance.
- **Integrated Gradients** (Sundararajan, Taly & Yan 2017): accumulates the
  gradient along a straight-line path from a chosen baseline input (e.g.
  all-zeros, blurred image, empty-string token embedding) to the actual
  input, satisfying two axioms most gradient/saliency methods violate:
  Sensitivity (a feature that changes the output gets nonzero attribution)
  and Implementation Invariance (functionally equivalent networks yield
  the same attribution). The baseline choice is a modeling decision, not a
  neutral default — attributions on the same input can differ materially
  under a different baseline, so the baseline used is a required part of
  any Integrated Gradients explanation, never left implicit.
- **Attention/probing**: reading attention weights, or training a probe
  classifier on internal activations, as evidence for what the model
  "looked at" or "represents." Attention weights are the model's own
  computed intermediate values, not a validated explanation mechanism —
  report them as a description of internal computation (what the
  architecture did), and only as an explanation of the *prediction* when a
  further check (e.g. does zeroing the high-attention region change the
  output) corroborates it.
- **Concept Activation Vectors / TCAV** (Kim et al. 2018): tests whether a
  human-defined high-level concept (e.g. "stripes," "medical terminology")
  — not a raw input feature — influences the prediction, by fitting a
  linear direction for the concept in an internal activation space and
  measuring the model's sensitivity to moving along it. This escalates
  past raw-feature attribution to a concept the raw features don't
  directly name, at the cost of needing a labeled concept dataset whose
  own construction is a modeling choice worth stating.

**Escalation discipline**: start with the cheapest method that answers the
actual question (a raw saliency map for "does this region matter at all");
escalate to Integrated Gradients when axiomatic grounding matters (a
reported quantitative attribution, not just a visualization); escalate to
TCAV only when the question is about a named concept the raw input
features don't directly express. All four remain attribution, not causal
claims about the underlying phenomenon — the model's sensitivity to a
pixel, token, or concept direction is evidence about the *model*, not
automatically evidence about the real-world mechanism (`ds-causal`, if
that stronger claim is actually being made).
