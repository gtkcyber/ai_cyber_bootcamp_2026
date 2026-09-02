---
name: ds-domain-cyber
description: "Domain overlay for security-telemetry tasks (intrusion/malware detection, alert triage, identity/access disambiguation, threat-graph analysis): states only the cyber-specific deltas on imbalance, adversarial drift, label scarcity, base-rate-driven alert cost, adversary-influenced identity keys, and graph-heavy framing…"
---

# ds-domain-cyber

## Subfields

- **Malicious-domain/URL/host classification** — trigger: "is this
  domain/IP/host malicious," DNS/proxy/threat-intel telemetry.
- **Identity/access disambiguation** — trigger: "did user X access system
  Y," Kerberos/AD/session logs, "count DC accesses."
- **Alert-triage / base-rate-aware detection** — trigger: an
  analyst-facing detector at production alert volume, "reduce false
  positives," SOC queue sizing.
- **Adversarial-drift-aware monitoring** — trigger: a deployed detector
  facing an adaptive adversary, not a passive population shift.
- **Threat-graph analysis** — trigger: lateral movement, C2 infrastructure
  clustering, provenance-graph investigation.

## Deltas

- **Imbalance extremes** — general treatment: whether/how much to intervene;
  generation mechanics; metric selection under imbalance · domain delta:
  attack prevalence in production security telemetry runs 1e-4–1e-6 of total
  events (practitioner estimate, not a measured population figure), two to
  four orders below even the extreme end of commonly benchmarked imbalance
  (~1e-2–1e-3) that class-imbalance literature validates against (Buczak &
  Guven 2016; Krawczyk, already cited at `ds-model`'s Imbalance intervention
  decision) — techniques proven at benchmark ratios don't automatically
  transfer to this regime, and unconstrained SMOTE-class oversampling risks
  manufacturing attack patterns that are statistically plausible but
  semantically impossible. Buczak & Guven 2016 is bibliographically
  confirmed (title/venue/year verified); full text not independently fetched
  in this pass — same access-caveat disclosure pattern `standards-index.md`
  uses for its CIM entry, re-verify before citing a specific figure from it.
- **Labels scarce, delayed, analyst-costed; negatives usually implicit** —
  general treatment: label acquisition strategy and implicit-negative/PU
  gating · domain delta: SOC analysts dismiss the overwhelming majority of
  alerts without full investigation under sustained time pressure (Alahmadi,
  Axon, Martinovic, USENIX Security 2022 — 99% false-positive rate reported
  by working analysts) — an alert never escalated is missing ground truth,
  not a verified negative; no population statement can assert the SOC's
  label process would have recorded a positive had one occurred, so "no
  analyst escalation" as a negative class fails ds-labeling's PU-learning
  gate outright. It also breaks SCAR (Elkan & Noto 2008; non-SCAR survey:
  Bekker & Davis 2020) — labeled positives are whatever subset analysts had
  time/priority to confirm — which ds-labeling's Edges require be named
  here, not resolved.
- **Alert-triage cost function and base rates** — general treatment:
  single-threshold operating-point selection under a stated cost function ·
  domain delta: at realistic base rates (attack prevalence rare relative to
  total events) even a detector with high sensitivity and specificity
  produces a false-positive flood that swamps true positives (Axelsson 2000,
  "The Base-Rate Fallacy and the Difficulty of Intrusion Detection") — never
  report sensitivity/ specificity in isolation without stating the assumed
  base rate; the same classifier's positive predictive value swings from
  useless to excellent purely as a function of base rate, independent of
  model quality (Alahmadi et al. 2022 confirms the fallacy's practical
  consequence remains unresolved 22 years later). Axelsson 2000 is
  bibliographically confirmed (title/venue/year verified); full text not
  independently fetched in this pass — same access-caveat disclosure pattern
  `standards-index.md` uses for its CIM entry, re-verify before citing a
  specific figure from it.
- **Adversary-influenced, log-source-specific identity keys** — general
  treatment: record/identity-level linkage · domain delta: identity keys
  here churn on timescales from minutes upward under DHCP lease policy (Xie
  et al. 2007), and NAT collapses many hosts behind one address
  simultaneously. `ds-entity-resolution`'s adversarial-key- manipulation
  pitfall (its Family-specific pitfalls, naming ds-domain-cyber as the
  domain instance), in its cyber instance: client- asserted fields
  (User-Agent is self-reported by the client, not observed by the log source
  — `asserted` provenance, not `observed`, per `ds-data-models`' Attest
  provenance classes) are as manipulable as the network-layer keys the
  pitfall already names; different log sources (firewall 5-tuple vs. Windows
  Event Log SID vs. DNS query log) expose non-interchangeable identity keys
  for what may be the same entity — every cross-log join needs its own
  `validity_interval`-qualified linkage decision, never a shared-field-name
  assumption.
- **Graph-heavy analysis** — general treatment: graph construction,
  centrality, community detection, link prediction, embeddings/GNN framing")
  · domain delta: entity-resolution errors propagate directly into spurious
  or missing edges before any anomaly-detection algorithm runs (Akoglu,
  Tong, Koutra 2015's survey assumes graph construction isn't adversarially
  targeted — the identity- key delta above breaks that assumption here);
  provenance-graph detection (UNICORN, Han et al. 2020 NDSS) targets attacks
  designed to be invisible at the single-event level and detectable only via
  multi-hop structure — graph framing is a direct response to adversary
  behavior, not incidental to the data's shape.

## Standards catalog

Seeds for `ds-data-models` Research, not ceilings — confirm producer
version/dialect against the actual feed before relying on any entry.
OCSF, Splunk CIM, ECS, the Public Suffix List, and User-Agent/RFC 9110 are
already researched, fetched, and pinned in
`ds-data-models/references/standards-index.md` — cited there, not re-fetched.

- **STIX** — OASIS threat-intelligence exchange language/serialization
  (current: 2.1). Producer: oasis-open.github.io/cti-documentation.
- **MITRE ATT&CK** — adversary tactics/techniques/procedures knowledge
  base. Producer: attack.mitre.org.
- **Per-protocol RFCs** — DNS (RFC 1034/1035), TLS (RFC 8446), HTTP (RFC
  9110, indexed above), Kerberos (RFC 4120).
- **IANA registries** — authoritative protocol parameter codes/numbers.
  Producer: iana.org/protocols.

### Malicious-domain classifier

2. `ds-data-models` — Identify fingerprints the domain-field schema against
   the catalog above; Interpret decomposes hostname fields via PSL/eTLD+1;
   Attest registers what a DNS/proxy record actually proves,
   `data-models.attest_register`.
3. `ds-gather` — join gate at every site combining passive DNS, proxy logs,
   and threat-intel feeds.
4. `ds-entity-resolution` — links domain/IP identity across log sources
   under this overlay's identity-keys delta.
5. `ds-labeling` — PU-learning gate on "not confirmed malicious" domains.
6. `ds-features` — feature dictionary cites the semantic-dictionary/Attest
   claims each feature derives from.
7. `ds-model` — imbalance intervention decision under this overlay's
   extreme-prevalence delta, `model.selection_rationale`.
8. `ds-evaluate` — base-rate-aware operating-point selection under this
   overlay's alert-triage delta.

### DC-access disambiguation

Quick-answer tier.

1. `ds-data-models` — Attest-register walk on the DC-touching records:
   Kerberos ticket issuance vs. an admin interactive session, citing that
   skill's own required worked example (both "touch the DC," neither attests
   the other); counting discipline (Attest, "disaggregate unlike events
   before counting") — every distinct record-type discriminator value
   (ticket-issuance `EventID` vs. session-logon `EventID`) counts under its
   own Attest entry, never pooled into one "DC access" figure.
2. `ds-communicate` — reports the disaggregated counts against their
   respective population statements (`data-models.population_statement`) —
   never a single pooled "N DC accesses" claim.

## Gates

- No delta bullet restates owner content beyond naming it — re-deriving
  owner content fails overlay scope.

## Edges

Covered: the six deltas above and the two worked compositions.
