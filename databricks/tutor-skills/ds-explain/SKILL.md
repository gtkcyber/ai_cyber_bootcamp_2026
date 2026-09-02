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

- **SHAP** — trigger: "SHAP," "Shapley attribution," "feature attribution
  for this prediction." participation:
  `conditional-on-data:attribution-requested`. Lundberg & Lee, NeurIPS
  2017, https://arxiv.org/abs/1705.07874. Canonical methods: TreeSHAP,
  KernelSHAP, DeepSHAP. Edges: exact computation is exponential in feature
  count; approximations assume feature independence and misattribute
  under correlation — see when-explanations-lie. See
  `references/ds-explain.attribution-methods.md#shap`.
- **Permutation importance** — trigger: "permutation importance," "which
  features matter globally," "importance for interpretation" (feature set
  fixed — not a pruning question). participation:
  `conditional-on-data:global-importance-requested`. Fisher, Rudin &
  Dominici, JMLR 20, 2019, https://arxiv.org/abs/1801.01489 (Model Class
  Reliance). See `references/ds-explain.attribution-methods.md#permutation-importance`.
- **PDP/ICE** — trigger: "how does the prediction change with this
  feature," "partial dependence," "individual conditional expectation."
  participation: `conditional-on-data:marginal-relationship-requested`.
  Goldstein, Kapelner, Bleich & Pitkin, JCGS 2015,
  https://arxiv.org/abs/1309.6392; scikit-learn PDP/ICE reference,
  https://scikit-learn.org/stable/modules/partial_dependence.html. Edges:
  marginalizes assuming feature independence — correlated features force
  evaluation at unrealistic combinations, per when-explanations-lie. See
  `references/ds-explain.attribution-methods.md#pdp-ice`.
- **Global vs local (LIME)** — trigger: "explain this one prediction"
  (local) vs. "explain the model overall" (global); "no SHAP support for
  this model class." participation:
  `conditional-on-data:local-explanation-requested`. Ribeiro, Singh &
  Guestrin, KDD 2016, https://arxiv.org/abs/1602.04938. Edges: local
  fidelity does not guarantee explanation stability under small
  perturbations. See `references/ds-explain.attribution-methods.md#global-vs-local`.
- **When explanations lie** — trigger: fires whenever this skill composes
  at all, regardless of which other subfield fired. participation:
  `mandatory`. Hooker, Mentch & Zhou, 2019,
  https://arxiv.org/abs/1905.03151. Covers correlated features, interaction
  masking, off-manifold evaluation. **No explanation ships without this
  subfield's checks recorded** — see `## Gates`. See
  `references/ds-explain.caveats-and-dl-interpretability.md#when-explanations-lie`.
- **Deep-learning interpretability bundle** — trigger: "explain this neural
  net's prediction," "saliency map," "what is the model attending to," "does
  this concept activate the model." participation:
  `conditional-on-data:dl-model-explained`. Simonyan, Vedaldi & Zisserman,
  2013/2014, https://arxiv.org/abs/1312.6034 (saliency); Sundararajan, Taly
  & Yan, ICML 2017, https://arxiv.org/abs/1703.01365 (integrated gradients);
  Kim et al., ICML 2018, https://arxiv.org/abs/1711.11279 (TCAV). See
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

## Gates

- **Core gate**: every `explanation_set` entry states its scope
  (global/local), its method's assumptions, and whether it is attribution
  or importance — a causal-reading entry (e.g. "X causes the outcome to
  change") fails, routing to `ds-causal` as a pointer instead.
- Every `explanation_set` entry pairs with at least one `caveats` entry
  from when-explanations-lie, including a checked-and-absent finding — no
  paired caveat fails the entry.
- Every feature-level explanation cites the feature's `ds-data-models`
  semantic-dictionary entry; leakage-adjacent or derived-post-target
  provenance routes to `ds-evaluate`→`ds-features` as a leakage finding,
  never an "important feature" here.
- The explained model is the exact frozen artifact `ds-model`/`ds-evaluate`
  already produced (`doctrine-repro-provenance.md` delta) — a re-fit
  stand-in explains a different model. Fit-on-train-only compliance for
  any transform the method itself introduces is `ds-features`'
  pipeline-object mandate, applying without restatement.
- Integrated Gradients entries state the baseline used; attention/probing
  entries are labeled internal computation unless an ablation or similar
  check supports reading them as evidence.

## Edges

Covered: post-hoc explanation of a fixed model on a fixed feature set
(SHAP, permutation importance, PDP/ICE, LIME, global-vs-local framing) and
the deep-learning interpretability bundle, with mandatory
correlated-feature/interaction-masking/off-manifold caveats on every
entry.

No leakage constraint originates here — this skill consumes an
already-frozen, already-split model; the off-manifold caveat above is a
*reporting* obligation about the method's own behavior, not a split decision
imposed on anyone else.
