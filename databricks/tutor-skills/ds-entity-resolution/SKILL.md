---
name: ds-entity-resolution
description: "Record-level identity linkage: blocking, fuzzy/probabilistic matching (Fellegi-Sunter), transitive-closure blowup on pairwise-match clustering, identity-graph (cluster-level) evaluation, and identity keys with temporal validity (DHCP/NAT/recycled-account churn — a join key valid at time T is not valid at T+1)."
---

# ds-entity-resolution

**Re-entrancy trigger**: fire whenever a record-level identity-linkage
question appears — a cross-source join on a non-exact key, node resolution
in a graph build, "are these the same entity" — at any tier, mid-pipeline or
not, alongside whichever phase or family raised the question. Full worked
examples and citations live in `references/`; this file is protocol only.

## Subfields

- Papadakis, Skoutas, Thanos, Palpanas, "A Survey of Blocking and Filtering
  Techniques for Entity Resolution," arXiv:1905.06167, 2019 —
  https://arxiv.org/abs/1905.06167 : blocking trades recall for tractability
  — a pair sharing no block key is never compared, so the blocking-key
  choice silently caps achievable recall. Canonical methods:
  standard/sorted-neighborhood/canopy blocking, LSH-based blocking. Edges:
  choosing which fields *can* serve as a block key is `ds-data-models`'
  Interpret; this subfield owns only the blocking scheme and its
  recall-ceiling consequence. See
  `references/ds-entity-resolution.linkage-mechanics.md#blocking`.
- Fellegi & Sunter, "A Theory for Record Linkage," *JASA* 64(328), 1969 —
  http://www2.stat.duke.edu/~rcs46/linkage/presentations/01-baiLi_FelleigSunter1969.pdf
  : link/possible-link/non-link decision rule, optimal only under
  conditional independence of comparison fields — correlated fields (name
  and email corrupted by the same typo source) violate this and bias the
  estimated match probability. Winkler, "String Comparator Metrics and
  Enhanced Decision Rules in the Fellegi-Sunter Model of Record Linkage," US
  Census Bureau RR90/05, 1990 —
  https://www.census.gov/content/dam/Census/library/working-papers/1990/adrm/rr90-05.pdf
  : Jaro-Winkler comparator for approximate strings; thresholds are
  dataset-specific, never universal. Edges: schema/field-level mapping is
  `ds-data-models`' Translate — this subfield owns only the record-level
  match decision once fields are known-comparable. See
  `references/ds-entity-resolution.linkage-mechanics.md#fuzzy-matching`.
- Topic anchored by Getoor & Machanavajjhala, "Entity Resolution: Theory,
  Practice & Open Challenges," VLDB 2012 tutorial —
  https://www.vldb.org/pvldb/vol5/p2018_lisegetoor_vldb2012.pdf (the
  published abstract names ER clustering/canonicalization; the mechanics
  below are standard ER practice, not quoted from it): pairwise match
  decisions aren't automatically transitive (A≈B, B≈C doesn't guarantee A≈C
  under noisy similarity) — naively closing the match graph merges unrelated
  entities whenever one bridging pair is a false positive; the clustering
  algorithm, not just the matcher, bounds how far one bad edge propagates.
  Canonical methods: correlation clustering, connected-
  components-with-threshold, hierarchical merge with a cut criterion. See
  `references/ds-entity-resolution.linkage-mechanics.md#transitive-closure`.
- Same topic anchor as above (standard ER practice, not quoted from the
  tutorial abstract) — cluster (identity-graph) evaluation is distinct from
  pairwise evaluation: a matcher can score well pairwise while still
  producing badly merged or split clusters. Report the metric matching
  what's actually evaluated — see Gates. See
  `references/ds-entity-resolution.linkage-mechanics.md#cluster-evaluation`.
- **LITERATURE-THIN**: no established literature name for this exact
  application; nearest analog is bitemporal/slowly-changing-dimension
  modeling, which solves the same validity-window problem for warehouse
  dimensions, not identity/security keys. Kimball Group, "Slowly Changing
  Dimensions" —
  https://www.kimballgroup.com/2008/08/slowly-changing-dimensions/ : Type 2
  SCD's date-range validity window is the mechanism this subfield adapts — a
  practice protocol, not a directly-on-point citation. Joining on a
  reassignable identifier without a validity window silently attributes
  activity to the wrong entity once recycled; the join must be qualified by
  "at time T," never by the identifier alone. See
  `references/ds-entity-resolution.linkage-mechanics.md#temporal-validity`.

## Selection tree

1. Exact, stable key (never reassigned/reused)? → not this skill's concern;
   schema/field-level mapping is `ds-data-models`' Translate.
2. Exact but reassignable/dynamic (IP, account ID, device ID, token)? →
   **identity keys with temporal validity** — every decision on this key
   carries a validity interval, regardless of tier.
3. Non-exact (fuzzy) key, small candidate space? → **fuzzy/probabilistic
   matching** directly.
4. Non-exact key, large candidate space? → **blocking** first to bound the
   comparison set, then **fuzzy/probabilistic matching** on survivors.
5. Multiple pairwise decisions being merged into entities? →
   **transitive-closure blowup** — bound/audit the merge before it runs.
6. Reporting linkage quality? → **identity-graph evaluation**, at the
   cluster level, not the pairwise level Step 3/4 produced.

## Family-specific pitfalls and evaluation

- Treating a pairwise match decision as automatically transitive — see
  transitive-closure blowup above; audit the merge, don't assume it.
- Applying the Fellegi-Sunter decision rule as if comparison fields were
  independent when they share a corruption source (same OCR pass, same
  typo-prone entry form) — the estimated match probability is biased
  optimistic.
- Reporting pairwise precision/recall where cluster-level (identity-graph)
  precision/recall is what the claim actually needs, or vice versa — state
  which one before reporting either.
- Joining on a reassignable key without a validity interval — silently
  attributes activity to the wrong entity once the identifier is recycled.
  **Adversarial key manipulation**: an adversary who forces or evades
  identity-key reassignment (churn an IP, rotate a device ID) attacks
  linkage validity directly, not just the underlying activity — a general
  threat, not a cyber-specific one (domain framing: `ds-domain-cyber`).
- Choosing a blocking key without stating its recall ceiling — a blocking
  scheme is a recall decision, not just a performance optimization.
- `ds-evaluate` owns the generic scorecard; this family's delta: report at
  the graph/cluster level when the claim is about resolved identities, not
  the pairwise match rate.
