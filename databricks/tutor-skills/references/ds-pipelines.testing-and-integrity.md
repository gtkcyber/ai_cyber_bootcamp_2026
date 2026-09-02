# Analysis-code correctness and training-data integrity

Depth for the two artifact-bearing subfields: property/golden-row testing
of transforms, and the training-data poisoning surface. SKILL.md carries
the protocol; this file carries worked detail and full citations.

## Analysis-code correctness (property tests, golden-row regression, idempotency tests) {#analysis-code-correctness}

**Literature**: property-based testing (QuickCheck) and golden master /
approval testing — two distinct, complementary techniques.

- Claessen & Hughes, "QuickCheck: A Lightweight Tool for Random Testing of
  Haskell Programs," ICFP 2000 —
  https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf :
  generates random inputs and checks a stated, universally-quantified
  property holds for all of them (e.g. "row count is conserved across this
  join" or "this transform is idempotent under a second application").
- Falco, "Approval Tests" —
  http://llewellynfalco.blogspot.com/2008/10/approval-tests.html : runs the
  transform against a fixed input, compares the output byte-for-byte
  against a stored "approved" reference file, and fails on any diff until a
  human deliberately re-approves it.

**Three test kinds, all feeding `transform_test_suite`**:
1. **Property tests** — an invariant that must hold for any valid input,
   not just the examples on hand: row-count conservation across a
   non-filtering join, schema stability, referential integrity between fact
   and dimension keys, monotonicity of a cumulative aggregate.
2. **Golden-row regression fixtures** — a small, hand-picked set of input
   rows (chosen to cover known edge cases: nulls, boundary values, each
   enumeration value) with their expected output, checked byte-for-byte on
   every run.
3. **Idempotency tests** — run the same transform twice over the same
   input/partition and assert byte-identical output; this is the automated
   check for the idempotency design `orchestration-and-refresh.md#backfills-idempotency`
   calls for.

**Key failure modes**: a property test is only as good as the invariant
someone actually stated — "we ran QuickCheck" with no named property checks
nothing. A golden fixture that gets re-approved every time it diffs,
without anyone checking *why* the output changed, has been converted from a
regression test into a no-op that always passes — the gate (SKILL.md
Gates) requires a stated invariant or a recorded reason for re-approval,
not merely the presence of a test file.

## Training-data integrity checks (poisoning surface) {#training-data-integrity}

**Literature**: adversarial machine learning — poisoning attacks. Biggio &
Roli, "Wild Patterns: Ten Years After the Rise of Adversarial Machine
Learning," Pattern Recognition 84, 2018 —
https://arxiv.org/abs/1712.03141 : surveys training-time (poisoning) and
test-time (evasion) attacks against learning systems as two distinct attack
surfaces with distinct defenses.

**Key failure mode**: poisoning and evasion are not interchangeable —
a defense built for one (e.g. adversarial-example robustness at inference
time) does not address the other (a corrupted training set baked into the
model before it ever serves a request).

**Scope of this subfield**: this skill flags the poisoning *surface* at the
pipeline-delivery stage — whether the training data's provenance includes a
channel an adversary could influence (user-submitted content, crowd-sourced
labels, scraped web text, any feed where the data-generating actor has
incentive to shape the training distribution). It does not design the
labeling-quality response to that surface; that ownership sits with
`ds-labeling` (strategy and quality measurement, regardless of labeler),
consulted once this subfield has named the channel and its exposure.

**Worked example**: a fraud-detection training set built from user-
submitted transaction disputes has a poisoning surface — a coordinated ring
could submit disputes engineered to teach the model their pattern looks
legitimate. A training set built from an internal, access-controlled
audit log has a much narrower one (still non-zero: an insider with write
access). State which channel(s) a training set's rows came through and
whether each is externally influenceable *before* the data feeds model
training, not as a post-hoc explanation once a poisoning incident is
suspected.
