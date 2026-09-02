---
name: ds-explain
description: "Post-hoc explanation of a fixed, already-trained model and feature set: SHAP, permutation importance, PDP/ICE, global-vs-local framing (LIME), mandatory when-explanations-lie caveats (correlated features, interaction masking, off-manifold evaluation), and the deep-learning interpretability bundle (saliency, integrated…"
---

# ds-explain

+ caveats, not the 12 family skills' framing-note-+-pitfall-checklist. Every
  subfield interprets a *fixed* model on a *fixed* feature set: it never
  changes which features exist (`ds-features`' pruning) and never claims a
  feature *causes* the outcome — attribution and importance are the only
  claims in scope. Full depth and citations live in `references/`; this file
  is protocol only.

## Subfields

- Lundberg & Lee, NeurIPS 2017, https://arxiv.org/abs/1705.07874. Canonical
  methods: TreeSHAP, KernelSHAP, DeepSHAP. Edges: exact computation is
  exponential in feature count; approximations assume feature independence
  and misattribute under correlation — see when-explanations-lie. See
  `references/ds-explain.attribution-methods.md#shap`.
- Fisher, Rudin & Dominici, JMLR 20, 2019, https://arxiv.org/abs/1801.01489
  (Model Class Reliance). See
  `references/ds-explain.attribution-methods.md#permutation-importance`.
- Goldstein, Kapelner, Bleich & Pitkin, JCGS 2015,
  https://arxiv.org/abs/1309.6392; scikit-learn PDP/ICE reference,
  https://scikit-learn.org/stable/modules/partial_dependence.html. Edges:
  marginalizes assuming feature independence — correlated features force
  evaluation at unrealistic combinations, per when-explanations-lie. See
  `references/ds-explain.attribution-methods.md#pdp-ice`.
- Ribeiro, Singh & Guestrin, KDD 2016, https://arxiv.org/abs/1602.04938.
  Edges: local fidelity does not guarantee explanation stability under small
  perturbations. See `references/ds-explain.attribution-methods.md#global-vs-local`.
- **When explanations lie** — trigger: fires whenever this skill composes at
  all, regardless of which other subfield fired. participation: `mandatory`.
  Hooker, Mentch & Zhou, 2019, https://arxiv.org/abs/1905.03151. Covers
  correlated features, interaction masking, off-manifold evaluation. See
  `references/ds-explain.caveats-and-dl-interpretability.md#when-explanations-lie`.
- Simonyan, Vedaldi & Zisserman, 2013/2014, https://arxiv.org/abs/1312.6034
  (saliency); Sundararajan, Taly & Yan, ICML 2017,
  https://arxiv.org/abs/1703.01365 (integrated gradients); Kim et al., ICML
  2018, https://arxiv.org/abs/1711.11279 (TCAV). See
  `references/ds-explain.caveats-and-dl-interpretability.md#dl-interpretability`.

## Selection tree

1. Neural net, question about raw inputs/internal representations/named
   concepts? → **DL interpretability bundle** (saliency cheapest,
   integrated gradients for axiomatic grounding, attention/probing for
   internal computation, TCAV for a named concept).
2. One specific prediction ("why this row")? → **SHAP** local values, or
   **LIME** when no SHAP implementation covers the model class. Model
   overall instead? → **SHAP** aggregated, or **permutation importance**
   for a cheaper global ranking.
3. How the prediction moves as a feature moves? → **PDP** (population
   average) or **ICE** (per-instance — check whenever a subgroup effect is
   plausible; a flat PDP can hide canceling opposite-signed effects).
4. Regardless of path: **when-explanations-lie** fires before the artifact
   is finalized — correlated-feature, interaction-masking, and
   off-manifold checks recorded against this task's actual features.

## Family-specific pitfalls and evaluation

- An attribution/importance number with no stated scope (global vs. local)
  — the reader cannot tell what claim is being made.
- SHAP or PDP/ICE run on correlated features with the independence
  assumption unstated; a LIME explanation reported once with no stability
  note across repeated perturbation sampling; a raw saliency map reported
  without a stability check; an Integrated Gradients attribution with no
  baseline stated.
- Permutation importance's single-fitted-model result generalized to "this
  feature matters for the problem," ignoring the Rashomon-set range
  Fisher, Rudin & Dominici's Model Class Reliance names.
- An "importance" reading on a feature whose semantic-dictionary entry
  (`ds-data-models`) shows derived-post-target or leakage-adjacent
  provenance, shipped as an insight instead of a leakage finding.

**Evaluation delta from `ds-evaluate`'s generic scorecard**: no
performance scorecard here — the artifact is the explanation set and
caveats below. A fidelity/stability claim about an explanation method
itself (e.g. LIME's local fidelity) reports alongside it, never folded
into `ds-evaluate`'s model-performance numbers.
