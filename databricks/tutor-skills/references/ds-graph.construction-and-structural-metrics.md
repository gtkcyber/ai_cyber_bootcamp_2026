# Graph framing, construction, and structural metrics

## Framing decision

**Literature name**: no consolidated decision-criterion literature exists.
Nearest: the motivation section of the graph representation-learning
survey.

**Canonical methods/refs**: Hamilton, Ying, Leskovec, "Representation
Learning on Graphs: Methods and Applications," *IEEE Data Engineering
Bulletin*, 2017 (arXiv:1709.05584) — https://arxiv.org/abs/1709.05584 :
motivates graph framing specifically when relational structure *between*
examples — not just per-example features — carries predictive signal.

**Failure modes**: don't reflexively reach for graph framing. If
relationships between rows don't carry signal beyond what a
join-then-aggregate tabular feature set would already capture, graph
framing adds representation and training cost without a corresponding
gain. The decision needs a stated hypothesis about what relational signal
tabular features miss — not a preference for graph tooling.

**Worked minimum**: the framing note (`SKILL.md` Artifact) states the
hypothesis in one sentence naming the specific relational structure
believed to carry signal: "a customer's fraud risk correlates with the
fraud status of accounts sharing a device fingerprint" (relational —
worth a graph) vs. "a customer's fraud risk correlates with their own
transaction velocity" (per-example — no graph framing needed; this is a
`ds-features` window aggregate).

## Construction

**Literature name**: no established academic name. Practitioner concept,
documented at the tooling level.

**Canonical methods/refs**: PyTorch Geometric, "Heterogeneous Graph
Learning" —
https://pytorch-geometric.readthedocs.io/en/latest/notes/heterogeneous.html
: documents constructing a heterogeneous graph object from multiple
node/edge tables — the standard practitioner pattern for turning
relational/tabular data into a graph.

**Failure modes**: edge-construction choices (which columns become edges,
what threshold turns a relationship into an edge) are modeling decisions
that determine what the graph can express — not a neutral transformation
of the underlying data. A co-occurrence threshold picked for graph density
rather than domain meaning silently encodes an unstated assumption into
every downstream centrality/community/link-prediction result.

Node identity: construction assumes node identity is already resolved.

## Centrality

**Literature name**: centrality measures (degree, betweenness, closeness,
eigenvector).

**Canonical methods/refs**:
- Newman, "The Structure and Function of Complex Networks," *SIAM Review*
  45(2), 2003 (arXiv:cond-mat/0303516) —
  https://arxiv.org/abs/cond-mat/0303516 : broad survey covering degree
  distributions and the structural metrics centrality measures build on.
- Brandes, "A Faster Algorithm for Betweenness Centrality," *Journal of
  Mathematical Sociology* 25(2), 2001 —
  https://www.uvm.edu/pdodds/files/papers/others/2001/brandes2001a.pdf :
  canonical exact betweenness-centrality algorithm; fetched successfully
  as a binary PDF directly from an author-hosted mirror (title/authorship
  not independently re-extracted from text, but existence and hosting
  confirmed) — this is the algorithm every major graph library's
  betweenness implementation cites.

**Failure modes**: different centrality measures encode different notions
of "importance" — degree measures local connectivity, betweenness measures
brokerage/bottleneck position, eigenvector measures influence-by-
association. Reporting a single centrality score as *the* importance
metric without naming which one, and why it fits the question, states a
claim the number doesn't support.

**Worked minimum**: "most connected node" (degree) answers a different
question than "node whose removal fragments the network" (betweenness) or
"node closest to influential neighbors" (eigenvector) — pick the measure
from the question actually being asked, state it in the framing note.

## Community

**Literature name**: community detection / graph clustering.

**Canonical methods/refs**: Fortunato, "Community Detection in Graphs,"
*Physics Reports* 486(3-5), 2010 (arXiv:0906.0612) —
https://arxiv.org/abs/0906.0612 : comprehensive survey; states the problem
is "very hard and not yet satisfactorily solved" despite large research
effort.

**Failure modes**: community detection has no single ground-truth
objective — modularity maximization is one operationalization, not the
definition of "community." Algorithm choice encodes an assumption about
what "community" means; presenting one algorithm's output as objectively
correct overstates what the method delivers.

**Worked minimum**: report the algorithm and its objective alongside any
partition ("Louvain, modularity-maximizing, resolution=1.0 → 14
communities") — never a bare community count or membership list with no
stated objective. If external labels exist for validation, name the
comparison metric (ARI/NMI) and treat modularity-optimal ≠
label-matching as an expected, not anomalous, outcome.
