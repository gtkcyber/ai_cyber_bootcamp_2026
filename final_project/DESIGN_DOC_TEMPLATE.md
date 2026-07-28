# Design Document

> Rename this file to `DESIGN.md` and fill in every section. If a section does not apply, explain why rather than deleting it.
>
> This document is graded heavily. Generic answers will score low. Tie every decision to something specific you observed about Juice Shop, the LLM you chose, or a failure mode you hit.

---

## 1. LLM Choice

**Model:** `{{provider/model}}`

**Why this model:** Justify with reference to cost, context window, tool-calling reliability, or observed behavior during development. If you tried another model first, say so.

## 2. Agent Architecture

**Pattern chosen:** (ReAct / Plan-and-Execute / Multi-agent / Hierarchical / your own)

**Diagram:**

```
(Replace with an ASCII or mermaid diagram showing the flow of control between
 planner, executor, tools, and any memory/state components.)
```

**Why this architecture:** Explain why it is a good fit for Juice Shop specifically. "It is popular" or "it works well" are not answers — tie it to challenges like `scoreBoard`, `loginAdmin`, or business-logic challenges.

### Rejected alternatives

Describe at least one architecture you considered and rejected. What would have been worse about it for this problem?

## 3. Prompting Strategy

**System prompt structure:** Briefly describe the sections of your system prompt and the reasoning behind each section.

**Task decomposition:** Does the agent plan, then execute, or react step-by-step? How did you arrive at that choice?

**What did you try and discard?** Honest documentation of failed prompt experiments scores better than a too-clean story.

## 4. Tool Design

| Tool | Purpose | Why you built it |
|---|---|---|
| example | example | example |

For each custom tool you built, answer:
- What decisions did you make about the tool's parameters? Why did you expose X but not Y?
- What does the tool do in code vs. what is left to the LLM to reason about? (This split is a key design choice.)

## 5. Context / Memory Management

A 100-step run generates a lot of tokens. How do you prevent the context window from blowing up?

- Do you summarize old turns? Drop them? Keep a scratchpad?
- How does the agent remember which challenges it has attempted?
- If the LLM returns to a dead end, what prevents it from looping?

## 6. Attack Strategy

How does the agent decide what to attack next? Does it enumerate the scoreboard, pick targets by category, or respond opportunistically to what it finds during recon?

Describe the coverage/exploration tradeoff in your agent.

## 7. Observed Failures

List at least three specific failures you observed during development and what you changed in response. (Without this, it is very hard to believe you actually ran your agent.)

1. **Failure:** What broke?
   **Diagnosis:** Why did it break?
   **Fix:** What you changed.

2. ...

3. ...

## 8. Limitations

What categories of challenges is your agent structurally unable to solve? (DOM XSS without a browser? Challenges requiring multi-page reasoning? Blind SQLi?) Be honest — acknowledging limits scores better than pretending they don't exist.

## 9. Citations

List every external source you consulted:

- **External code/libraries** (beyond what's in `requirements.txt`): URL, what you used from it
- **Blog posts / write-ups**: URL, what idea you borrowed
- **AI assistance**: which tool (ChatGPT, Claude, Copilot, etc.), and for what (e.g., "asked Claude to draft the initial XSS payload list; reviewed and modified 6 of 12 payloads")

Uncited code is academic dishonesty. Cited code is fine; the point of this course is not to teach you to write from scratch.
