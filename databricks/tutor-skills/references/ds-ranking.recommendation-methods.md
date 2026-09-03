# Recommendation methods

Full depth and citations for collaborative filtering/matrix factorization,
cold start, and implicit feedback. `SKILL.md` states triggers and dispatch
fields only; this file carries the method detail.

## Collaborative filtering / matrix factorization {#cf-mf}

**Literature name**: matches spec — latent-factor collaborative filtering.

**Canonical methods**: SVD-style latent-factor models, regularized MF with
user/item bias terms, temporal-dynamics extensions, ALS-style solvers for
implicit-signal variants (see `#implicit-feedback`).

**Source**: Koren, Bell & Volinsky, "Matrix Factorization Techniques for
Recommender Systems," IEEE Computer 42(8), 2009 —
https://datajobs.com/data-science-repo/Recommender-Systems-%5BNetflix%5D.pdf.
Latent-factor MF was the Netflix Prize's dominant approach; the paper
covers regularization, bias terms, and temporal dynamics as the standard
extensions to plain SVD.

**Failure mode**: latent-factor MF assumes the rating matrix's structure is
well-approximated by a low-rank decomposition. Sparse, low-interaction-
history users/items violate this by having too few observations to
estimate stable factors — this is the cold-start case (`#cold-start`), and
the source paper itself names it as an open MF limitation, not something a
regularization tweak fixes.

## Cold start {#cold-start}

**Status**: literature-thin for an independently fetchable canonical
citation. The field's named paper — Schein, Popescu, Ungar & Pennock,
"Methods and Metrics for Cold-Start Recommendations," SIGIR 2002 (ACM DOI
10.1145/564376.564421) — could not be fetched (ACM DL 403; three mirror
URLs 404'd) and is excluded per cite-or-cut rather than cited from memory.
Folded into Koren, Bell & Volinsky 2009 (`#cf-mf`), which names cold start
explicitly as a structural MF limitation.

**Canonical methods**: content-based fallback (item/user metadata features
in place of interaction history), hybrid CF+content models, exploration-
based bootstrap policies (allocation policy itself: `ds-optimize`).

**Failure mode**: don't present cold-start mitigation as "more data solves
it." The defining property of the cold-start case is that the needed
interaction data doesn't exist yet for this user/item — the fix is a
different information source (content, metadata, an exploration policy),
never more of the same collaborative signal. "Wait for more interactions"
is not a mitigation; it's a restatement of the problem.

## Implicit feedback {#implicit-feedback}

**Literature name**: matches spec.

**Canonical methods**: confidence-weighted implicit matrix factorization —
all (user, item) pairs trained, not just observed ones, with confidence
weights derived from interaction frequency/recency rather than treating
interaction as a binary rating.

**Source**: Hu, Koren & Volinsky, "Collaborative Filtering for Implicit
Feedback Datasets," ICDM 2008 — http://yifanhu.net/PUB/cf.pdf. Reframes
implicit signals (views, purchases, dwell time) as confidence-weighted
binary preference rather than missing explicit ratings.

**The implicit-feedback trap, restated precisely** (`SKILL.md` Gates
carries the code-checkable form): absence of an interaction is not a
negative preference. It conflates true disinterest with simple
non-exposure — a user who never saw an item cannot have declined it. This
is the ranking-specific instance of the suite's PU-gate doctrine
(`ds-labeling` § implicit negatives and PU learning,
`references/ds-labeling.noise-pu-and-model-assisted.md#pu-learning`): a claimed
negative is only valid if the label-generating process — here, the
*exposure* mechanism (was the item ever shown/reachable to this user?) —
covered the item being treated as a non-interaction. That exposure claim is
exactly what a `population_statement` (`ds-data-models`, Observe; doctrine
home `references/doctrine-repro-provenance.md` § Population statements are composable
artifacts) states for the logged-interaction dataset. Confidence-weighting
(Hu, Koren & Volinsky's scheme) is a modeling choice about this ambiguity —
it makes the uncertainty gradual instead of binary — it does not resolve
it. This trap compounds with position bias (`SKILL.md` § position and
presentation bias): a never-shown item and a shown-but-ignored item are
different label-generating processes, and both are different again from a
seen-and-declined item.

**Worked example**: "Items a user never clicked are labeled not-preferred."
Fails unless the population statement establishes the user was exposed to
(shown, reachable, in the served candidate set for) every item being
treated as a non-preference — for most production recommenders it does
not, because ranking/retrieval itself determines what a user could see.
