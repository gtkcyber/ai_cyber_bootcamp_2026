## Page 1

The final project asks each student to build an autonomous agent that runs a penetration test, an authorized attack on a system to find and exploit its security weaknesses, against a deliberately vulnerable web application. The slides ahead cover the target, the learning objectives, and the required deliverables.

## Page 2

The assignment is a design problem. What gets built and graded is the control logic that drives a language model. An agent is a program that runs a language model in a loop: the model proposes an action, a tool executes it, the output returns to the model, and the cycle repeats until the goal is met or a step budget is spent. A lone prompt exercises none of that structure. The grade rests on the design of the loop, meaning how the task is broken into steps, which tools the model can call, and how its choices become executed actions.

## Page 3

The target is OWASP Juice Shop, a web application built by the Open Worldwide Application Security Project to be broken into on purpose. It ships with a catalog of planted vulnerabilities spanning the common classes of web flaw, which gives the agent real bugs to find and a fixed answer key to score against. Students run it one of two ways: locally as a Docker container, or on an instance the instructors host during class. Setup steps for the local container are in the final project `README`.

## Page 4

The project has four aims.

- Agent construction: implement an autonomous loop that calls tools and acts on what they return.
- Methodology translation: express the stages of a penetration test, reconnaissance to map the target, vulnerability discovery to find weaknesses, exploitation to prove them, and reporting to write them up, as logic a program runs on its own.
- Design sensitivity: measure how prompt wording and tool choice change what the agent manages to accomplish.
- Practical limits: experience where language-model automation struggles on adversarial security tasks, where a plausible-sounding answer is not a working exploit.

## Page 5

Four things must be turned in.

- The agent loop, in `agent/agent.py`: a stub fixes the interface, and the architecture is the student's call. Named options include ReAct, which interleaves one reasoning step with one action each turn; Plan-and-Execute, which drafts a full plan first and then works through it; a multi-agent design that splits the work across cooperating agents; and a hierarchical design where a controller directs sub-agents.
- The prompts, in `agent/prompts/`: the system prompt and any prompts that break the task into parts, filled into the empty templates provided.
- At least three new tools in `agent/tools/`, on top of the two reference tools that ship with the scaffold. Each must do real work; a tool that only forwards to another tool does not count. Workable examples are a SQL injection tester, a JSON Web Token decoder and forger, a cross-site scripting payload generator, a directory brute-forcer, an API fuzzer, and a business-logic probe.
- The report, at `reports/final_report.md`, written by the agent when a run ends. It states each finding, its severity, the evidence that proves it, and how to fix it.

Three files stay untouched so every submission is judged on equal terms. The scorer and harness, `eval/score.py` and `eval/harness.py`, run the evaluation. The abstraction in `agent/llm.py` pins every agent to one fixed language-model interface, so a result reflects the design and not a more capable model. The protocol in `agent/tools/base.py` sets how a tool is declared and invoked.

## Page 6

Questions about the assignment go to the course instructors, whose contacts are in the course `README`.

## Page 7

This closes the final project briefing. From here the work is done independently, and the evaluation harness scores each run against the challenges Juice Shop tracks.
