# Grading Rubric

Total: 100 points.

## Challenges solved — 25 points

Scored automatically by `eval/harness.py` against Juice Shop's `/api/Challenges` endpoint.

| Solved | Points |
|---|---|
| 1–4 | 5 |
| 5–9 | 10 |
| 10–14 | 15 |
| 15–24 | 20 |
| 25+ | 25 |

Solving a single trivial challenge earns partial credit — we reward a working end-to-end loop even if the agent is weak.

## Agent architecture & code quality — 20 points

Read `agent/agent.py` and associated modules.

| Criterion | Points |
|---|---|
| Agent loop is coherent and the code matches the architecture claimed in the design doc | 6 |
| Context / state management is deliberate (not just an ever-growing message list) | 4 |
| Error handling on tool calls is reasonable (retries, timeouts, failure reporting back to LLM) | 4 |
| Code is readable, named well, and does not contain obvious AI-generated filler | 6 |

## Novel tools — 15 points

**Quality over quantity.** 3 excellent tools score higher than 10 thin wrappers.

| Criterion | Points |
|---|---|
| At least 3 tools beyond the reference tools, each doing substantive work | 6 |
| Tool interfaces are well-designed (good args, clear return shape, schema aligns with use) | 4 |
| At least one tool demonstrates real pentesting insight (not just "call HTTP with different verb") | 5 |

Examples of substantive tools: parameterized SQL injection tester with error-based + boolean-based detection, JWT decoder + none-alg forger, reflected/stored XSS probe that checks for execution context, business-logic ordering abuse (adding items post-purchase, negative quantities), coupon/code brute-forcer, API discovery through Angular bundle scraping.

## Design document — 20 points

`DESIGN.md`, following `DESIGN_DOC_TEMPLATE.md`.

| Criterion | Points |
|---|---|
| Architecture choice is justified with specific reference to Juice Shop's structure | 5 |
| At least one rejected alternative is discussed with honest tradeoffs | 4 |
| Prompt engineering decisions are explained, not just asserted | 4 |
| Context management strategy is described | 3 |
| Citations: external code, blog posts, AI assistance are all listed honestly | 4 |

Generic writing ("I used ReAct because it is widely used") that doesn't cite specific challenges or observed failures will score low in this section.

## Generated pentest report — 10 points

`reports/final_report.md` — produced by the agent at the end of a run.

| Criterion | Points |
|---|---|
| Findings are grouped by vulnerability class with severity ratings (CVSS or similar) | 3 |
| Each finding includes evidence (requests/responses) captured during the run | 4 |
| Remediation advice is specific, not generic ("sanitize input" is not enough) | 3 |

## Project writeup — 10 points

`WRITEUP.md`, following `WRITEUP_TEMPLATE.md`.

| Criterion | Points |
|---|---|
| Annotated screenshots of a successful end-to-end run (agent terminal output + Juice Shop scoreboard) | 3 |
| Annotated screenshot of a failed run with analysis of why the agent got stuck | 3 |
| One "deep dive" challenge: walk through exactly how the agent solved a specific challenge, step by step, with screenshots | 3 |
| Reflection: what you would do differently, what surprised you | 1 |

Screenshots must show timestamps or other evidence of being real runs. Re-using the same screenshot to claim multiple runs will be treated as academic dishonesty.

---

## Deductions

- **Broken scaffold**: If `eval/harness.py` cannot run against your submission because you modified protected files, −10 points.
- **Pointed the agent at a target other than the local Juice Shop**: automatic fail, disciplinary referral.
- **Uncited LLM-generated code**: −10 points minimum. Cite it; you lose fewer points for honesty.
