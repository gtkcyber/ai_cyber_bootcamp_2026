# Framing and proxy statement

## Framing

**Literature name**: no single established academic term. Industry calls it
"problem formulation" or "business-problem-to-ML-task translation."
Framework literature: CRISP-DM, CRISP-ML(Q).

**Canonical methods/refs**:
- "From Business Problems to AI Solutions: Where Does Transformation Support
  Fail?" — https://arxiv.org/html/2604.18770v1 — systematic review defining
  seven required transformation stages (Problem Framing → ML Task
  Formulation → Data Requirements → …); finds most frameworks
  under-specify task-type derivation.
- Studer et al., "Towards CRISP-ML(Q)" —
  https://arxiv.org/pdf/2003.05155 — extends CRISP-DM with quality gates at
  each phase, including business/data understanding.
- Provost & Fawcett, *Data Science for Business* —
  https://fosterprovost.com/wp-content/uploads/2019/06/Data-Science-for-Business.pdf
  — canonical task-type taxonomy (classification, regression, similarity
  matching, clustering, link prediction, causal modeling). Pick the task
  type from this taxonomy before naming a metric — metric selection is a
  downstream decision (`ds-evaluate`), not part of framing.

**Failure modes**: this translation step is "still mostly ad hoc, weakly
supported by methodologies" per the arxiv survey above — don't imply a
settled procedure exists where none does. Don't conflate task-type selection
with metric selection; they are sequential, not the same decision.

**Worked minimum**: a task card's framing fields are complete when `target`
and `unit` name the row-level thing being predicted/measured and its grain
("target: will this account churn; unit: account-month"), and `metric` +
`baseline` name what "better than nothing" looks like before any model is
built (a naive baseline: majority class, last-value, current process).

## Proxy

**Literature name**: **construct validity** (psychometrics, imported into
ML as measurement modeling).

**Canonical methods/refs**: Jacobs & Wallach, "Measurement and Fairness"
(FAccT 2021) — https://arxiv.org/abs/1912.05511 — formalizes construct
reliability/validity for unobservable constructs (e.g. "risk")
operationalized via a measurement model.

**Failure modes**: don't treat the label/proxy as identical to the
construct — construct/operationalization mismatch is a direct mechanism for
downstream failure (the model optimizes the proxy, the business cares about
the construct), not a footnote caveat.

**Worked examples** (the required form for `proxy_statement`): "churn" (the
construct: a customer relationship ending) is operationalized as "30-day
inactivity" (the proxy) — the gap: a customer on a documented seasonal
schedule reads as churned but isn't. "Fraud" (the construct: an
illegitimate transaction) is operationalized as "chargeback filed" (the
proxy) — the gap: fraud that isn't disputed, and disputes that aren't
fraud, both slip the label. A `proxy_statement` that only restates the
label ("churn = customer churned") fails the Gates check in `SKILL.md`
because it names no gap.
