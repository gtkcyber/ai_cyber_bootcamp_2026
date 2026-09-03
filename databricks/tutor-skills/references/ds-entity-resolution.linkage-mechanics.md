# Linkage mechanics

`SKILL.md` carries the protocol and full citations; this file carries the
mechanics.

## Blocking {#blocking}

Blocking exists because all-pairs comparison is O(n²) and most pairs are
obviously not matches. A blocking key partitions records into buckets;
comparison only runs within a bucket.

- **Standard blocking**: exact match on a derived key (e.g. soundex of
  last name, first 3 digits of zip). Cheap, but a single-typo error in the
  key field drops a true match into a different bucket permanently.
- **Sorted-neighborhood**: sort by a key, slide a fixed-size window,
  compare within the window. Tolerant of small key-value errors near the
  sort boundary; still bounded by the window width.
- **Canopy / LSH-based blocking**: cheap similarity metric (TF-IDF cosine,
  MinHash) groups near-duplicates into overlapping canopies before the
  expensive comparator runs. Scales to large candidate spaces; canopy
  overlap trades extra comparisons for better recall.

**State the recall ceiling explicitly.** A blocking scheme is a recall
decision made before any matcher runs — two true-match records that share
no block key are never compared, no matter how good the downstream
comparator is. "We used soundex blocking" without naming which
match-classes it structurally excludes (e.g. transposed given/family
names in some naming conventions) is an incomplete blocking statement.

## Fuzzy/probabilistic matching {#fuzzy-matching}

Fellegi-Sunter frames the decision as a likelihood ratio: for each
candidate pair, compare *k* fields, estimate `m` (probability of
agreement given a true match) and `u` (probability of agreement given a
non-match) per field, and combine into a match weight. Thresholds split
the weight into link / possible-link (route to review) / non-link.

- **Conditional-independence assumption**: the combination step multiplies
  per-field likelihood ratios, which is only valid if fields don't share an
  error source. In practice, name and address entered by the same
  data-entry process often share exactly that — a systematic bias, not
  noise that averages out.
- **String comparators**: exact-match indicator functions are too brittle
  for names/addresses; Jaro-Winkler (boosts agreement on shared prefixes)
  is the standard replacement, but its threshold is fit per dataset, never
  imported as a universal constant from another linkage project.
- **possible-link handling**: a threshold band that routes ambiguous pairs
  to human review (or a secondary, more expensive comparator) is part of
  the protocol, not an edge case to collapse into a binary decision.

## Transitive-closure blowup {#transitive-closure}

Worked example: records A, B, C. Pairwise matcher finds A≈B (weight 0.9)
and B≈C (weight 0.85), but A and C were never directly compared (different
blocks, or simply not evaluated). Naive transitive closure merges {A, B, C}
into one entity. If B≈C was a false positive — B and C share a common
address by coincidence, not identity — the merge silently pulls A's
history into C's entity, and vice versa. One bad edge determines how far
the contamination spreads; the more densely a cluster is cross-matched,
the more one false edge can corrupt.

Bounding strategies:

- **Correlation clustering**: optimize a clustering that penalizes both
  false merges and false splits jointly, rather than growing connected
  components unconditionally.
- **Threshold-cut clustering**: build the full weighted match graph, then
  cut at a global or per-cluster weight threshold before taking connected
  components — a bridging edge below threshold cannot merge two otherwise
  weakly-connected sub-clusters.
- **Audit before merge**: for any cluster above a size or density
  threshold, spot-check whether every within-cluster pair would still
  match under direct comparison (not just transitively) before the merge
  is used downstream.

## Identity-graph evaluation {#cluster-evaluation}

Pairwise precision/recall (evaluated per candidate pair, before
clustering) and cluster-level precision/recall (evaluated per resulting
entity, after clustering) measure different things and can disagree
sharply:

- A matcher with high pairwise precision can still produce low
  cluster-level precision if a small number of high-confidence false
  positives happen to bridge otherwise-correct clusters (the
  transitive-closure failure mode above, seen from the evaluation side).
- Cluster-level metrics (e.g. pairwise-F1 computed *over the induced pairs
  of the final clustering*, B-cubed precision/recall, or variation of
  information against a gold clustering) score the actual deliverable —
  the entity clusters — rather than an intermediate artifact.

State which level a reported number is at before citing it. "92% match
accuracy" with no level stated is not an evaluable claim.

## Identity keys with temporal validity {#temporal-validity}

Worked example: a DHCP lease assigns IP `10.0.4.17` to host `laptop-42`
from `09:00`–`13:00`. At `14:10`, the same IP is reassigned to
`laptop-91`. A join that maps "activity from `10.0.4.17`" to
`laptop-42` without checking the timestamp against the lease's validity
window attributes `laptop-91`'s `14:10` activity to `laptop-42` — a wrong
entity, not a wrong value.

The same pattern recurs for recycled account IDs (a deactivated account's
numeric ID reissued to a new user), reassigned device IDs (device
returned/refurbished/reissued), and rotating session tokens. In every
case, the identifier's *meaning* — which entity it denotes — has a
validity interval, and a linkage decision that omits the interval is
implicitly claiming permanent validity it cannot support.

**Adapting Type-2 SCD**: Kimball's Type 2 slowly-changing-dimension pattern
(new row per change, each row carrying a `valid_from`/`valid_to` pair) is
the closest established mechanism, built for warehouse dimension changes
rather than identity/security keys — the adaptation here is: every
`linkage_decisions` entry keyed on a reassignable identifier carries its
own `validity_interval`, and a join qualifies the identifier by "at time
T" (checked against that interval), not by the identifier value alone.

**Adversarial delta (general form)**: an adversary who can force or evade
identifier reassignment — churn a DHCP lease early, rotate a device ID,
recycle an account faster than normal — is directly attacking linkage
validity, not merely generating noisy activity. Treat identifier churn
rate itself as a signal worth monitoring wherever adversarial control over
reassignment is plausible; domain-specific framing of *when* that's the
operating assumption is `ds-domain-cyber`'s delta, not this skill's.
