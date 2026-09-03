# Standards index — `ds-data-models`

Purpose: (1) a starting index of the standards this discipline set runs into
most often, and (2) the *method* for researching a standard this index
doesn't cover. This is not an attempt at completeness — treat every entry as
a seed, not a ceiling, per suite design principle 6.

Every claim below carries: URL, spec/producer version, access date. No
citation, no claim — cut it instead of asserting from memory.

## The method (use this for anything not indexed here)

1. Find the *producer's* spec page, not a third-party summary. Prefer the
   organization that emits the schema (a project's own schema repo/site
   over a blog post about it).
2. Record the version the spec page itself declares (a URL path segment
   like `/1.9.0/` or an on-page "this is the documentation of version X" line
   — not "latest," not the newest GitHub tag if the page shows an older
   pinned version).
3. Fetch, don't recall. Pull the actual page/repo, quote or closely
   paraphrase the defining passage, and record the fetch date.
4. Distinguish the *spec* from what a given *producer* actually emits
   (`references/ds-data-models.disciplines.md#research`) — the spec is the starting point,
   the observed data is the authority once they diverge.
5. Re-run this method on schema/version drift (Production considerations in
   `SKILL.md`) — a standards-index entry is a snapshot, not a permanent fact.

## Event/log schemas

### OCSF (Open Cybersecurity Schema Framework)

- Landing/browse: <https://schema.ocsf.io/> — schema version `1.9.0` (version
  is embedded in the browse URL path, e.g. `/1.9.0/classes/file_activity`).
  Accessed 2026-08-19.
- Repository/structure: <https://github.com/ocsf/ocsf-schema> — repo layout:
  `events/` (event class definitions by category), `objects/` (reusable
  structures), `profiles/`, `extensions/` (e.g. Linux, Windows),
  `metaschema/`, `categories.json`, `dictionary.json` (attribute
  dictionary), `version.json` (current schema version). Accessed 2026-08-19.
- Fingerprint mechanics (worked, `classes/file_activity`, class `1001`,
  category `System Activity`): every event class carries a required integer
  `category_uid` ("the category unique identifier of the event... each event
  class belongs to exactly one category") and the class itself is identified
  by `class_uid`; enum attributes (`activity_id`, `category_uid`) pair with a
  string sibling (`activity_name`, `category_name`) that must match the
  enum's defined caption unless the enum value is `99` ("Other"), in which
  case the string sibling carries the source-specific label instead.
  <https://schema.ocsf.io/1.9.0/classes/file_activity>, accessed 2026-08-19.
- Time semantics: OCSF's `time` attribute is explicitly "the primary
  timestamp... when the activity actually occurred at the source," distinct
  from `metadata.logged_time` / `metadata.processed_time` for pipeline
  lifecycle timestamps — directly relevant to the Interpret discipline's
  "When" sub-check. Same source, accessed 2026-08-19.

### Splunk Common Information Model (CIM)

- Current documented version: `6.1`. "Use the CIM to normalize data at
  search time": <https://help.splunk.com/en/splunk-cloud-platform/common-information-model/6.1/using-the-common-information-model/use-the-cim-to-normalize-data-at-search-time>,
  accessed 2026-08-19.
- Fingerprint mechanics: CIM identifies events not by field name but by
  **tags** applied through **event types** — "many of the CIM data models
  have the same field names, so the tags act as constraints to filter the
  data to just the relevant events for that model." A dataset qualifies for
  a CIM data model by matching its tag set, verified via the
  `tag::eventtype` field. Same source, accessed 2026-08-19.
- Both `docs.splunk.com` and `help.splunk.com` block automated fetch (HTTP
  403) as of 2026-08-19. This entry relies on the verbatim passage quoted
  above (recorded via non-automated access) plus the `splunk/cim` add-on's
  own repository docs for cross-verification. Re-verify via a non-automated
  fetch method before citing a CIM version newer than `6.1`.

### Elastic Common Schema (ECS)

- Reference: <https://www.elastic.co/guide/en/ecs/current/ecs-reference.html>
  — "This is the documentation of ECS version `9.5.0`." Accessed 2026-08-19.
- Categorization fields: <https://www.elastic.co/guide/en/ecs/current/ecs-category-field-values-reference.html>
  — ECS splits classification into "where it's from" (`event.module`,
  `event.dataset`, `agent.type`, `observer.type`) vs. "what it is," the
  latter carried by four `event.*` fields: `event.kind`, `event.category`,
  `event.type`, `event.outcome`. Accessed 2026-08-19.

## Cross-model mapping (Translate discipline)

- Splunk's own OCSF→CIM mapping: "OCSF-CIM Add-On for Splunk," mapping
  overview at <https://splunk.github.io/ocsf_cim_addon_for_splunk/mappings/>
  — ships search-time knowledge objects that map OCSF-shaped events onto CIM
  tags/fields per data model. Accessed 2026-08-19.
- Independent field-level crosswalk of six schemas (Splunk CIM 6.0, Google
  Chronicle UDM, Microsoft Sentinel ASIM, Elastic ECS 9.4.0, OpenTelemetry,
  Zeek) into OCSF 1.8.0, validated against the public OCSF schema and mapper
  fixtures: "Six schemas into OCSF: the mapping is the hard part,"
  <https://securitydataworks.com/writing/ocsf/six-schemas-into-ocsf/>,
  accessed 2026-08-19. Worked row: OCSF Network Activity (`class_uid 4001`)
  against all six sources shows `category_uid`/`class_uid` are always
  constants set by the mapper (never read from the source), while
  `activity_id` derives from a different source field per schema (CIM
  `action`, UDM `security_result.action`, ASIM `DvcAction`+`EventSubType`,
  ECS `event.type`, Zeek a constructed value from `conn.log`) — the concrete
  evidence for "map by semantics, never by field-name similarity."
- Mapping-notes principle from both sources: cross-model mapping is a
  many-to-one *semantic* projection, not a schema diff. A source field with
  no reachable OCSF attribute is recorded as a mapping gap (`—`), not
  papered over; a low-confidence/inferred mapping is flagged, not silently
  accepted.

## Composite field structure

### User-Agent

- RFC 9110, "HTTP Semantics," IETF Standards Track, June 2022, obsoletes RFC
  2818/7230/7231/7232/7233/7235/7538/7615/7694 and updates RFC 3864.
  <https://www.rfc-editor.org/rfc/rfc9110.html>, accessed 2026-08-19.
- Grammar (Appendix A, Collected ABNF): `User-Agent = product *( RWS
  ( product / comment ) )` — a required leading `product` token
  (name and optional `/version`) followed by zero or more further products
  or free-text `comment`s. This is why User-Agent decomposition (product /
  OS / engine / device) is inherently a parse-and-tolerate problem, not a
  fixed-field split: the grammar only guarantees the leading product token,
  everything after it is producer-chosen free text.
- The User-Agent string is entirely client-asserted — nothing server-side
  verifies it matches the requesting software. Modern browsers are actively
  freezing/reducing the string's information content and migrating toward
  UA Client Hints (structured, opt-in headers) rather than a richer
  free-text UA. Either way, any OS/device/engine field decomposed from
  User-Agent carries provenance class `asserted`, not `observed`
  (`disciplines.md#interpret`) — the analytic consequence is sharpest for
  bot-heavy or adversarial populations, where the UA string is the easiest
  field in the record to spoof; treat UA-derived fields as evidence of what
  the client claimed to be, not what it was.

### Domain names / PSL / eTLD+1

- Public Suffix List: <https://publicsuffix.org/>, accessed 2026-08-19. "A
  'public suffix' is one under which Internet users can (or historically
  could) directly register names" (e.g. `com`, `co.uk`, `pvt.k12.ma.us`).
  Mozilla-initiated, community-maintained; consumed by browsers and other
  software to avoid treating a public suffix as if it were a registrable
  domain (their stated example: preventing supercookies scoped to an entire
  public suffix).
- eTLD+1 ("effective TLD plus one label") is the registrable domain: the
  public suffix from the PSL plus exactly one label to its left. Decomposing
  a hostname without consulting the PSL (e.g. naively splitting on the last
  two labels) misclassifies any hostname under a multi-label public suffix
  (`co.uk`, `k12.ma.us`, and many others) — this is the concrete reason PSL
  consultation, not a fixed dot-count rule, is the Interpret-discipline
  method for domain decomposition.
- The PSL is split into an **ICANN section** (delegated TLDs) and a
  **PRIVATE section** (community-submitted entries like `github.io` or
  `herokuapp.com`, where the operator wants each subdomain treated as its
  own registrable domain). Which section(s) a given eTLD+1 computation
  consults (ICANN-only, or ICANN+PRIVATE) is a declared analysis decision —
  some libraries default to ICANN-only — not a fixed default, and it must be
  recorded alongside the pin. The PSL itself isn't versioned by its
  maintainers the way OCSF/CIM/ECS are: treat the fetched snapshot as the
  pinned artifact, record the fetch date as the pin in the semantic
  dictionary's `pinned_version` field, and re-pin (re-fetch, re-diff,
  re-run affected eTLD+1 decompositions) on any Production-considerations-
  triggered re-check — the same version-pinning discipline Research imposes
  on producer specs.

## Sentinel value conventions

- General definition and taxonomy (magic numbers, null-pointer/null-option
  patterns, the semipredicate problem): "Sentinel value,"
  <https://en.wikipedia.org/wiki/Sentinel_value>, accessed 2026-08-19.
- Field-specific conventions this suite runs into most (not from the article
  above — pattern-match against the actual producer, never assume): `0` or
  `-1` standing in for "unset"/"unknown" in an integer field that also has
  legitimate `0`/positive values (ambiguous without a companion flag or
  documented convention); epoch `1970-01-01T00:00:00Z` standing in for
  "never happened"/"not set" in a timestamp field (collides with a
  genuinely epoch-time event without a range check); empty string vs. null
  vs. a literal `"NULL"`/`"N/A"` string used interchangeably by the same
  producer. Elicit-discipline check: does the producer's sentinel collide
  with a legitimate value, and is there a distinguishing signal
  (companion field, out-of-range check, documented convention)?
