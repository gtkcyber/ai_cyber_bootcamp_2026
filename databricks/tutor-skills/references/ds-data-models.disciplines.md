# Disciplines — full depth

The nine `ds-data-models` disciplines. Each section: what it does, why it's
separable from its neighbors, and one worked micro-example. Two examples
(Interpret/Leverage's malicious-domain walk, Attest's DC-touch pair) are
load-bearing for the suite and required verbatim in intent — don't drop
their specifics when this file is edited later.

Citations for every standards claim below live in `references/ds-data-models.standards-index.md`; this
file references standard names and points there rather than repeating URLs.

## Identify

Fingerprint the schema/standard a record belongs to from structural tells,
before touching its meaning. OCSF records carry an integer `class_uid` (and
a `category_uid` each class belongs to exactly one of, itself derivable as
`class_uid // 1000` — a mismatch is a Validate finding, not extra
fingerprint evidence); `type_uid` (`class_uid * 100 + activity_id`) is a
stronger fingerprint than `class_uid` alone since it also pins the specific
activity variant. Splunk CIM events
are identified by tag membership (`tag::eventtype`), not field names — the
same field name can appear across multiple CIM data models, so tags, not
schema, disambiguate; ECS records carry `event.category`/`event.type` plus
an `ecs.version` field. Vendor tells (a non-standard field prefix, a
distinctive nesting shape) matter when no formal fingerprint field exists.

An ambiguous fingerprint is a finding, not a guess to paper over — record it
as "unidentified, closest candidates X/Y, distinguishing field absent" and
let Research or Elicit resolve it, rather than silently picking one.

*Micro-example:* a JSON log line has `class_uid: 1001`, `category_uid: 1`,
and an `activity_id` enum. Cross-referencing OCSF's `file_activity` class
definition confirms this is OCSF File System Activity, category "System
Activity" — Identify's job stops there; what `activity_id: 4` *means*
("Delete") and what the record *proves* are Interpret's and Attest's jobs.
`type_uid = 100104` (`class_uid * 100 + activity_id`) confirms the same
fingerprint at finer grain.

## Research

Once the standard is fingerprinted, pin the version the *producer* actually
emits — never "latest published." A producer on OCSF 1.7.0 does not gain
1.9.0's fields by assumption; a producer's CIM 6.0 export does not follow
6.1's tag changes. Vendor extensions and nonconformance (fields the spec
doesn't define, required fields the producer omits) are not noise to filter
out — they're what the data actually is, and every downstream claim about
"what this field means" is scoped to the pinned version plus its observed
deltas from spec.

Mid-stream schema migration is not a special case: if one source's history
crosses a version or dialect boundary, the two eras gate exactly like two
different sources would — a claim spanning the boundary needs a
cross-version reconciliation step, not a silent concat.

*Micro-example:* a vendor's OCSF export declares `metadata.version: 1.7.0`
in every record, but two-thirds of records also carry a `x_vendor_risk_score`
field OCSF 1.7.0 doesn't define. Research pins the base spec at 1.7.0
*and* records the extension field as a producer-specific addition with its
own (separately elicited) semantics — it does not get "OCSF 1.9.0 doesn't
have this either, ignore it" treatment, and it does not inherit meaning from
a same-named field in a different vendor's export.

## Elicit

For data with no findable spec (internal tables, ad-hoc CSV exports):
semantics come from observed behavior, not documentation, because there is
none. Full scripts-first order (value boundaries, update cadence,
referential integrity, null patterns, distribution breaks at policy
changes) lives in `references/ds-data-models.elicitation-protocol.md` — this section states the
discipline's contract, not its procedure. Every semantic derived this way
that can't be independently confirmed is a **declared assumption**: field,
inferred meaning, evidence, confidence, downstream impact if wrong.
Unresolvable ambiguity (evidence points two ways, or evidence doesn't exist)
routes to the human — it is not resolved by picking the more convenient
reading.

*Micro-example:* a column `status` in an internal accounts table takes
values `{0, 1, 2, 9}` with no data dictionary. A written script shows `9` is
rare, always co-occurs with a non-null `closed_at`, and its first appearance
coincides with a schema-migration date found in a separate deploy log —
declared assumption: "`9` = closed/terminated, introduced at migration date
D; confidence high (co-occurrence + introduction date); if wrong, any
active-account count computed before validating this undercounts terminated
accounts as active." That declaration, not a guess baked silently into a
filter, is what ships.

## Observe

What exists in a dataset is a function of collector configuration — audit
policy, verbosity level, sampling rate, filters, truncation, retention
window, and any outages — not of what actually happened. Every dataset
carries a population statement before its first aggregate claim: "contains
X, collected by Y, subject to Z." Absence of a record type in the data is
never itself evidence the underlying activity didn't occur; it may just be
outside what the collector was configured to keep. Population statements
compose through every downstream transform (join, filter, aggregate, dedup)
per the doctrine references — each rewrites or reaffirms the statement it
inherited.

*Micro-example:* a Windows security-event feed shows zero 4625 (failed
logon) events for a three-week window. Before that becomes "no failed
logons occurred," Observe checks the audit-policy config and finds logon
failure auditing was disabled org-wide for that exact window during a
troubleshooting change — the population statement becomes "contains
successful-logon events only for [window], failure auditing disabled by
change ticket #N," and any downstream brute-force-detection claim over that
window is scoped or excluded accordingly.

## Interpret

Field-level semantics, six sub-checks:

- **Composite decomposition** — a field that packs multiple facts into one
  string (User-Agent → product/OS/engine/device) needs a real parser
  against the field's actual grammar, not a split-and-hope. Domain names
  need PSL/eTLD+1 consultation, not a fixed dot-count rule (worked in
  Leverage below).
- **Constrained values** — enums, units, and their allowed ranges; a value
  outside the declared enum is a Validate-discipline finding, not silently
  coerced.
- **Sentinel encodings** — `0`, `-1`, `1970-01-01` and similar standing in
  for "unset"/"unknown"/"never" collide with legitimate values unless a
  companion signal disambiguates (see `references/ds-data-models.standards-index.md`).
- **Nested/array fields** — a field holding zero-or-more values (an array of
  file hashes, a nested list of process ancestors) needs its cardinality
  semantics declared explicitly: is zero meaningful, is order meaningful, is
  the field append-only. State whether downstream analysis flattens (one row
  per element), aggregates (count/any/all), or picks one (first/last/
  primary) — flattening rewrites the table's grain contract (below) and
  therefore the population statement (Observe) inherited into the flattened
  output.
- **Canonicalization** — any field used for comparison, join, or
  agreement-counting declares its canonical form before use: hostname
  case-folding/trailing-dot/IDN-punycode normalization, IPv4-mapped vs.
  zero-compressed IPv6 literal forms, epoch seconds vs. milliseconds vs.
  microseconds, timezone-naive local timestamps. Comparing two fields
  without a shared canonical form manufactures disagreement that isn't real
  (Leverage's hostname-agreement example, below, depends on this).
- **Provenance class** (observed/derived/enriched/defaulted/asserted/
  privacy-transformed) — a composite or derived field inherits its weakest
  input's class; privacy-transformed inputs change variance, granularity,
  and joinability and the analysis must account for it. Fields produced by
  third-party enrichment — PSL-based domain decomposition, User-Agent
  parsing, GeoIP, ASN lookup — carry class `enriched` and inherit the
  suite-wide unvalidated-external-output restriction
  (`references/doctrine-repro-provenance.md`) before feeding any claim; pointer only,
  not restated here. **When** (event vs. ingest vs. decision time, clock
  skew, as-of discipline) and the **grain contract** (declared grain + key
  uniqueness for the table) round out this discipline — both gate every join
  per SKILL.md's Gates section.

*Micro-example* (continues into Leverage below): a hostname field
`login.accounts-secure.example.co.uk` decomposes, via PSL consultation, to
public suffix `co.uk`, eTLD+1 `example.co.uk`, subdomain labels
`login.accounts-secure`. A naive last-two-labels split would have produced
`co.uk` as if it were the registrable domain — wrong, because `co.uk` is
itself a two-label public suffix. Which PSL section(s) this decomposition
consults (ICANN-only, or ICANN+PRIVATE) is a declared analysis decision, and
the PSL snapshot's fetch date is pinned in the semantic dictionary's
`pinned_version` field exactly like a producer spec version
(`references/ds-data-models.standards-index.md`).

## Attest

What a record *proves* happened — not what its column names suggest.
Decompose every record-type into **actor (and role) / action / mechanism /
target**, and disaggregate unlike events before counting them together
(measurement vs. meaning: two rows with the same "event type" label can
attest structurally different claims). Every claim also names its
**asserter and incentive** — who asserted this value, and what could make
it false or motivated to shade it — plus its **falsifier**: the concrete
mechanism that would produce this record without the claim being true. The
"unlike events" a dataset disaggregates before counting are exactly the
distinct values of its declared record-type discriminator field(s)
(`class_uid`, `EventID`, a CIM tag set, or the literal `single-type` for an
undifferentiated table), registered once in the semantic dictionary — the
Attest-coverage gate (SKILL.md) joins those discriminator values against
Attest register entries.

*Required worked example: Kerberos ticket issuance vs. admin session.* Both
event types can be summarized loosely as "touched the domain controller,"
and a naive count of "DC touches" would merge them. They don't attest the
same claim:

| | Kerberos ticket issuance (TGT/TGS) | Interactive admin session |
|---|---|---|
| Actor | The requesting principal (user or service account) | The same principal, but now *as an interactively authenticated session* |
| Action | Cryptographic credential exchange — prove identity, receive a ticket | Establish an interactive logon context (console = Logon Type 2, RDP = Logon Type 10, or Logon Type 11 cached credential) |
| Mechanism | Kerberos AS-REQ/AS-REP or TGS-REQ/TGS-REP, evaluated by the KDC | Logon session creation — Windows Security 4624 filtered to Logon Type ∈ {2 Interactive, 10 RemoteInteractive, 11 CachedInteractive} — evaluated by the local/domain logon subsystem |
| Target | The KDC's ticket-granting function on the DC | The DC's OS itself, as a session host |
| Asserter | The KDC, incentivized to issue tickets to any principal presenting valid credentials — routine and high-volume | The logon subsystem, gated by interactive-logon rights on that host — rare and privileged by design |
| Falsifier | Pass-the-ticket, golden/silver ticket forgery, or a stolen keytab — any of these produce a valid-looking ticket-issuance record without the named principal ever presenting their own credentials | Token theft (pass-the-hash into a logon), a stolen NTLM hash, or a hijacked session — any of these produce a valid-looking interactive-logon record without the named principal being the human at the keyboard |

A count of "who touched the DC" that merges these two treats routine,
high-volume, low-privilege ticket issuance as equivalent to a rare,
high-privilege interactive session on the DC itself — the exact kind of
count that produces a badly miscalibrated anomaly baseline. The Attest
register entry for each is separate, naming its own actor/action/mechanism/
target, so any later count cites one or the other explicitly, never "DC
activity" undifferentiated.

Filtering 4624 to Logon Type ∈ {2, 10, 11} matters because 4624 alone
merges interactive and non-interactive logons (e.g. Logon Type 3, Network —
the type PSRemoting uses) into one event ID; treating raw 4624 volume as
"interactive sessions" is the same measurement-vs-meaning error one level
down from merging Kerberos issuance with logon-session creation. Sharpest
form of the ticket-issuance claim: a TGS request (Windows Security 4769)
attests that a service ticket was *requested* for a given SPN — not that
the ticket was ever presented to the service, or that access succeeded. The
KDC's record ends at issuance; reaching the service is a separate,
unattested step unless the target system's own access log corroborates it.
Both rows' Asserter claims are narrower than they look, too: the KDC
attests valid credentials were presented, not that the named human acted;
the logon subsystem attests a logon session was created, not that the named
human is physically present — the Falsifier row above is what makes that
gap explicit rather than assumed away.

## Leverage

Specs are feature-mines, and the standard itself is not the only spec worth
mining: cross-source disagreement is a signal in its own right. Independent
sources that *should* report the same fact, and don't, are informative
precisely because they disagree — this is a general principle for any
multi-source dataset, not a cyber-specific trick.

*Micro-example (continues the Interpret hostname example, and is the
required malicious-domain classifier walk):* a session log carries three
independently-produced hostname signals for the same connection — the DNS
query name, the TLS SNI extension value, and the HTTP `Host` header. Each
is decomposed to eTLD+1 via the PSL (Interpret discipline's canonicalization
sub-check). In benign traffic these three eTLD+1 values agree almost always
(browser resolves `example.co.uk`, connects via TLS SNI `example.co.uk`,
sends `Host: example.co.uk`). Classic domain-fronting diverges Host from
DNS/SNI while keeping DNS and SNI themselves in agreement — **DNS ≈ SNI ≠
Host**, not a three-way divergence: the DNS query name and the TLS SNI both
present the same allow-listed CDN front, while the decrypted HTTP `Host`
header requests the actual, different target. SNI ≠ DNS alone has benign
base-rate causes — connection reuse, HTTP/2 connection coalescing,
forward/transparent proxies — that a fronting feature has to beat before
DNS/SNI disagreement is treated as suspicious on its own; the Host-header
divergence against an *agreeing* DNS/SNI pair is the actual signal. The
feature isn't any single hostname field; it's the **disagreement rate** and
**which pair diverges** across DNS/SNI/Host, computed after eTLD+1
normalization (Interpret's canonicalization sub-check) so that harmless
multi-CDN or multi-region hostname variation (same eTLD+1, different
subdomain) doesn't get miscounted as disagreement. This generalizes
directly: any dataset with two independently-asserted facts about the same
entity (inventory system A's hostname vs. system B's, two vendors'
geolocation for the same IP) can mine agreement/disagreement the same way.

This feature carries a collection precondition Observe must state before
Leverage computes it: the HTTP `Host` header is inside the TLS-encrypted
payload, observable only where TLS interception (a forward proxy performing
MITM decryption) is deployed, and SNI itself is disappearing under
Encrypted Client Hello (ECH) rollout — a joined DNS/SNI/Host feed's
population statement must name both constraints ("contains Host-header
values only where TLS interception was active for [population/window]; SNI
values only where ECH was not in use") before any disagreement-rate claim
is computed over it. The DNS↔TLS join itself is also inferential, not a
guaranteed record-level link: pairing a DNS query to the TLS connection it
presumably preceded typically keys on client IP plus a bounded time window,
and DNS caching (a resolved name reused with no fresh query), shared
resolvers, and NAT/CGNAT (many clients behind one IP) all defeat it. State
this join as a declared assumption with its failure modes, the same as any
Elicit assumption; record-level identity linkage beyond this join is
`ds-entity-resolution`'s job, not this one's.

## Translate

Cross-model mapping (OCSF ↔ CIM ↔ ECS, or any two schemas) by semantics,
never by field-name similarity. Two fields with the same or similar name
across schemas frequently encode different actor/action/target semantics
(Attest discipline) or different units/grain (Interpret discipline) — the
mapping walks through those decompositions, not a string match on field
names. Splunk's own OCSF-CIM add-on and the independent six-schema
crosswalk (`references/ds-data-models.standards-index.md`) both demonstrate the pattern: the
classification fields (`category_uid`/`class_uid` in OCSF) are set as
mapper constants, never read from the source, while behavioral fields like
"what activity happened" derive from a different source field per schema
because each schema's own action vocabulary differs. Record-level identity
linkage (the same real-world entity showing up in two sources) is a
different problem, owned by `ds-entity-resolution` — Translate is about
schema/field mapping, not row-to-row identity.

## Validate

Conformance as a data-quality signal, checked continuously, not just at
onboarding: extension fields the pinned spec version doesn't define,
deprecated values still in use, and version skew across the record set (one
subset of records on an older/newer schema dialect than the rest) are all
findings even when every record still parses without error. A record that
"parses" is not the same as a record that conforms — Validate is what
catches that gap, and it feeds directly into Research's version-pinning
(a Validate finding of widespread version skew is itself grounds to
re-run Research on the affected subset).

OCSF's derived-identifier arithmetic is one concrete, scriptable
conformance check: `type_uid = class_uid * 100 + activity_id` and
`category_uid = class_uid // 1000` are both derivable, so a record whose
stated `category_uid` or `type_uid` disagrees with the arithmetic identity
is a Validate finding — not additional Identify fingerprint evidence, and
not silently recomputed and passed through.
