---
name: ds-graph
description: "Graph/network method family: constructing a graph from tabular data, centrality, community detection, link prediction, graph embeddings/GNN framing, and the decision of when graph framing beats a tabular join-then-aggregate representation."
---

# ds-graph

Full depth, worked examples, and citations live in `references/`. This
file is protocol only.

## Subfields

- **When graph framing beats tabular** — trigger: task asks "is this a
  graph problem" or proposes graph framing without a stated reason.
  **LITERATURE-THIN**: no consolidated decision-criterion literature;
  nearest is the motivation section of the graph representation-learning
  survey. Hamilton, Ying, Leskovec, "Representation Learning on Graphs" —
  https://arxiv.org/abs/1709.05584 : graph framing earns its cost only when
  relational structure *between* examples carries signal a
  join-then-aggregate tabular representation would miss. See
  `references/construction-and-structural-metrics.md#framing-decision`.
- **Graph construction from tabular data** — trigger: rows/tables exist,
  no graph object yet. **LITERATURE-THIN**: practitioner-level, not
  surveyed. PyTorch Geometric, "Heterogeneous Graph Learning" —
  https://pytorch-geometric.readthedocs.io/en/latest/notes/heterogeneous.html
  : constructing node/edge tables into a graph object. Edge-construction
  choices are modeling decisions, not a neutral transform — every edge
  type cites its Attest register `attest_id` (Gates). See
  `references/construction-and-structural-metrics.md#construction`.
- **Centrality** — trigger: "which nodes matter / are most important /
  influential." Newman, "The Structure and Function of Complex Networks" —
  https://arxiv.org/abs/cond-mat/0303516 ; Brandes, "A Faster Algorithm for
  Betweenness Centrality" — https://www.uvm.edu/pdodds/files/papers/others/2001/brandes2001a.pdf
  (author-hosted PDF; title/authorship not independently re-extracted).
  Degree, betweenness, closeness, eigenvector each encode a different
  notion of importance — name which one. See
  `references/construction-and-structural-metrics.md#centrality`.
- **Community detection** — trigger: "communities / segments / clusters in
  the network." Fortunato, "Community Detection in Graphs" —
  https://arxiv.org/abs/0906.0612 : "very hard and not yet satisfactorily
  solved." No single ground-truth objective — name the operationalization
  (e.g. modularity maximization). See
  `references/construction-and-structural-metrics.md#community`.
- **Link prediction** — trigger: "predict future/missing edges."
  Liben-Nowell & Kleinberg, "The Link Prediction Problem for Social
  Networks" — https://www.cs.cornell.edu/home/kleinber/link-pred.pdf
  (author-hosted PDF; title/authorship not independently re-extracted).
  Proximity-based predictors assume future links correlate with current
  structural proximity — fails under structural change. See
  `references/prediction-and-representation.md#link-prediction`.
- **Graph embeddings/GNN framing** — trigger: "node classification /
  embedding features / GNN." Hamilton, Ying, Leskovec (as above,
  https://arxiv.org/abs/1709.05584); Kipf & Welling, "Semi-Supervised
  Classification with Graph Convolutional Networks" —
  https://arxiv.org/abs/1609.02907 . This subfield owns the framing choice
  (transductive vs. inductive, which embedding family fits); training
  mechanics are `ds-deep-learning`'s (Edges). See
  `references/prediction-and-representation.md#embeddings`.

|---|---|---|---|
| When graph framing beats tabular | quick-answer | 1 | mandatory |
| Graph construction from tabular data | quick-answer | 2 | mandatory |
| Centrality | quick-answer | 3 | conditional-on-data:importance-ranking-needed |
| Community detection | analysis | 3 | conditional-on-data:cluster-structure-needed |
| Link prediction | analysis | 3 | conditional-on-data:missing-edge-prediction |
| Graph embeddings/GNN framing | analysis | 3 | conditional-on-data:node-embedding-or-classification-needed |

`mandatory`: framing and construction are prerequisite to every other
subfield; the four load-order-3 rows fire only on their own trigger and
may co-occur.

## Selection tree

1. Task lands in the graph family (router dispatch) → **state the
   relational-signal hypothesis** (when-graph-framing-beats-tabular): what
   would a join-then-aggregate tabular representation miss? No stated
   hypothesis → framing gate fails, don't proceed to construction.
2. Graph object exists already? No → **construct** from tabular
   node/edge sources; each edge type cites an `attest_id`. Node identity
   already resolved? No → pointer to `ds-entity-resolution`, inherit its
   `linkage_decisions`, don't re-resolve here.
3. What does the task ask of the graph structure?
   - "Which nodes matter" → **centrality** — pick the measure (degree /
     betweenness / closeness / eigenvector) that matches the stated
     notion of importance (local connectivity vs. brokerage vs.
     influence-by-association).
   - "What substructure exists" → **community detection** — pick an
     algorithm, name its objective; no universal ground truth.
   - "Will an edge exist" → **link prediction** — is the graph temporal?
     Yes → `ds-timeseries` owns the split (Edges/Pairings). No → state
     the static-graph leakage-safe holdout scheme (Gates).
   - "Represent nodes for downstream modeling" → **embeddings/GNN
     framing** — will unseen nodes appear at serving time? Yes → inductive
     method family (GNN-style); No → transductive method family
     (matrix-factorization-style) is admissible. Either way, training
     mechanics hand off to `ds-deep-learning`.

## Family-specific pitfalls and evaluation

- **Edge-definition risk concentration**: an edge asserts a relationship —
  the analytic risk in a graph task concentrates at construction, not at
  the algorithm run on top of it. See Gates.
- **Unqualified "importance"**: reporting a centrality score without
  naming the measure states a different claim depending on which measure
  was actually computed.
- **Community structure presented as ground truth**: no algorithm's
  partition is objectively correct; the objective (e.g. modularity) is a
  modeling choice.
- **Static-graph link-prediction leakage**: held-out edges leak through
  shared neighborhoods, not just row independence — see Gates.
- **Transductive/inductive mismatch**: a transductive embedding method
  (fixed node set) silently breaks in production once the graph grows;
  don't treat the two families as interchangeable.
- **Reflexive graph framing**: reaching for graph representation without
  a stated relational-signal hypothesis (subfield 1) adds representation
  and training cost with no corresponding gain.

**Evaluation delta from `ds-evaluate`'s generic scorecard**: graph outputs
rarely have one "accuracy." Centrality/community outputs are evaluated
against the stated question — community detection against modularity or
(if labels exist) ARI/NMI, never presented as settling "the" correct
partition. Link prediction is evaluated on a held-out edge set
(precision@k / AUC) from the leakage-safe split in Gates — a split that
shuffles edges without respecting neighborhood/time structure invalidates
the score. Embedding/GNN quality is evaluated through the downstream task
it feeds, not embedding geometry in isolation.

## Gates

- **Node-identity gate**: where node identity is ambiguous across
  sources, construction cites `ds-entity-resolution`'s `linkage_decisions`
  — an ungated merge of unresolved identities into one node fails this
  gate.
- **Centrality-naming gate**: every centrality output names its measure —
  an unqualified "importance score" fails.
- **Community-operationalization gate**: the algorithm and its objective
  are named alongside any partition reported.
- **Static-graph link-prediction split gate**: absent a `ds-timeseries`
  pairing, this skill states its own edge-holdout scheme explicitly (e.g.
  structurally distant held-out edges, or removal stratified to avoid
  disconnecting components) — unstated "random edge removal" fails. On a
  temporal graph, `ds-timeseries`'s split scheme governs (multi-family
  rule, Edges); this gate defers rather than re-deriving one.
- **Framing gate**: the when-graph-beats-tabular subfield states an
  explicit relational-signal hypothesis before construction proceeds.

## Edges

Covered: graph-framing decision, construction from tabular sources,
centrality, community detection, link prediction, embedding/GNN framing
choice, static-graph leakage-safe split statement.

Not covered, pointer only: node/identity-level resolution
(`ds-entity-resolution` — construction inherits `linkage_decisions`, never
re-derives them); GNN/embedding training mechanics — architecture,
regularization, schedules (`ds-deep-learning` — this skill owns framing
only); the split scheme on a temporal graph (`ds-timeseries` owns it per
the multi-family rule — the static holdout gate applies only absent that
pairing); generic leakage/provenance principle (router
`doctrine-leakage.md`; this skill's delta is the neighborhood/temporal-edge
boundary, not the principle); production graph-serving and monitoring
(`ds-mlops`, pointer only).
