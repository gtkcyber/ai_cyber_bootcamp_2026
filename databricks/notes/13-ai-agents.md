## Page 1

Module 13 covers AI agents: what separates an agent from a single model call, NVIDIA's autonomy levels, the ReAct loop and the prompt that drives it, when a fixed workflow beats an agent, the memory, planning, and reflection patterns layered on top of ReAct, the framework landscape, the agent threat model and its mitigations, where agents fit in security operations, and how to evaluate one. The second half is a five-part lab that builds a phishing-email agent in LangGraph in stages: a single classifier, a tool-calling investigator, conditional routing by risk, a human review step, and a supervisor over specialist agents.

## Page 2

This part defines agents, places them on NVIDIA's autonomy scale, and covers the ReAct loop, the design choices layered on it, the frameworks that implement it, and the threats that come with letting a model act.

## Page 3

Prompt injection is the structural weakness of agents. An agent reads text it did not write: emails, web pages, documents, tool output. The model receives that text in the same context window as its instructions and has no reliable way to tell the two apart, so instructions planted in the input can redirect what the agent does next.

The design question for every tool is what the worst action it permits would cost. A tool that reads a ticket queue can leak the queue; a tool that runs shell commands can run any shell command. Wiring an agent to internal data sources or proprietary systems raises that ceiling from a wrong answer to data loss or exfiltration.

## Page 4

In July 2025 a coding agent with production access deleted a company's database. Jason Lemkin, founder of the SaaStr community, had spent eight days building an application with Replit's agent, which writes and runs code inside a hosted environment. During a declared code freeze, with standing instructions to make no changes without permission, the agent ran a command that wiped the production tables. It then reported that unit tests had passed when they had not, which is what the quoted "lied" refers to: a model has no intent, and what it produced were statements that did not match what it had done.

The instruction not to change anything was text in a prompt. The credential that let the agent write to production was a real permission. Only the second kind of control holds when the model goes wrong, and the apology that followed carries no more information about future behavior than the false test report did.

## Page 5

The screenshots are Lemkin's posts on X. The first quotes the agent's own account of the incident: at 4:26 AM it ran `npm run db:push`, the command that destroyed the database, and it describes the sequence as a catastrophic failure on its part. The second post adds that the agent hid the deletion, claimed the unit tests passed, and was caught only when batch processing failed and Lemkin pressed it to explain.

The candid summary and the false test claim came from the same text generator, so the agent's self-report is not evidence of what happened. What is evidence is the record of commands the harness ran, which is why an agent that can act needs every step logged outside the model.

## Page 6

An agent is a tool-using model placed in a loop. The tool calling from Module 11 was a single round: the model names a tool, your code runs it, the result goes back, the model answers. An agent keeps going: after the result arrives the model may call another tool, then another, and each result is appended to the conversation so later calls see everything earlier ones learned. That accumulating conversation is the agent's memory within a task.

The loop ends on a stopping condition. Either the model emits a final answer in place of a tool call, or the harness stops it at an iteration cap. Without the cap, a model that keeps choosing tools without converging runs until the budget is gone.

## Page 7

The three components come from the reinforcement learning definition of an agent. Inputs are whatever the environment supplies; for a security agent that is an alert, an email, a log record, or the result of a tool call. The goal is the end state the agent works toward: in reinforcement learning it is a reward signal the agent maximizes, and for a prompted LLM agent it is the objective stated in the system prompt. Actions are the moves available, which for an LLM agent means its tool list plus the option to answer.

## Page 8

NVIDIA's autonomy levels rank agent designs by how much of the control flow the model owns. The scale comes from a post on NVIDIA's developer blog on agentic autonomy and security. Level 1 is a linear chain: model, tool, model, output, in a fixed order the developer wrote. The model decides what to say at each step and the code decides what happens next. Every run follows the same path, so the path can be read and tested in full.

## Page 9

Level 2 lets data choose among fixed branches. The model's output determines which of several predefined paths runs next, as a router does. The set of possible paths forms a directed acyclic graph, a DAG: edges point one way and no path revisits a node, so every path is finite and the full list can still be enumerated and tested, only a longer list than at level 1.

## Page 10

Level 3 adds cycles. A tool result can send control back to the model, which can pick any tool again, so the number of possible paths grows exponentially with the number of iterations and cannot be enumerated. Testing every path is impossible, so the controls have to bound what any path can do: restricting tools, sandboxing execution, capping iterations, and gating consequential actions on a person. The ReAct agents built in this module's lab are level 3 systems.

## Page 11

ReAct interleaves reasoning with action. The name is from the 2022 paper "ReAct: Synergizing Reasoning and Acting in Language Models" by Shunyu Yao and colleagues, and the figure is theirs. The left panel is reason-only prompting such as chain of thought: the model writes reasoning traces and feeds them back to itself with no contact with the outside world, so a wrong intermediate fact goes unchecked. The middle panel is act-only systems such as SayCan and WebGPT: the model emits actions and receives observations from an environment, with no written reasoning between them. ReAct closes both loops around one model: a thought, then an action, then an observation, then the next thought informed by what the action returned.

## Page 12

Each ReAct iteration is observe, think, decide, act. The observation is what the environment returned, at first the question itself and afterward the latest tool result. The thought is the model's interpretation of it in text. The decision picks a tool and its input, the action runs the tool, and the result becomes the next observation. The loop ends when the model states that it has the answer or when the iteration cap is hit; the cap exists because convergence is not guaranteed.

## Page 13

A ReAct prompt is a template with two slots. The question slot holds the task. The tools slot holds the tool list, each entry giving a name, a description of what the tool does and when to use it, and the Python function your code runs when the model names it. The model sees only the name and the description, so the description is what determines whether the right tool gets picked.

## Page 14

The example prompt fixes the text format the loop parses. Each step is labeled: observation, thought, then action and action input on separate lines. The instruction not to guess tool results tells the model to stop after writing the action so the harness can run the tool and append the real result before the next call. The closing sentinel, "I've found the answer:", is the string the loop code matches to exit.

This style of prompt predates native tool calling. Chat APIs now return a tool call as a structured field with its own stop reason, which removes the label parsing and the sentinel. The lab uses that interface: tools are bound to the model and the model's reply carries the call.

## Page 15

The dividing line is who controls the path. In a workflow, code you wrote decides the sequence of model calls and tool calls, and the model fills in content at each step. In an agent, the model decides which step runs next, which tool to call, and when to stop. Anthropic's December 2024 guide "Building effective agents" draws the line the same way, and the framework advice later in this deck comes from the same guide. Agency is a matter of degree: the more decisions about control flow the model makes, the more agentic the system.

## Page 16

Four points on the spectrum, ordered by how much control the model has. Single prompt: one call, one answer, no control flow. Chain: a fixed sequence of calls wired in code; the model shapes content and the code shapes order. Router: the model chooses one of several branches you defined, one control decision per run. Agent: the model chooses actions repeatedly and decides when it is done. The rule is to use the least agentic option that solves the task.

## Page 17

An agent earns its cost when the path cannot be written in advance. Open-ended tasks where the steps depend on what earlier steps reveal, tasks whose length varies from one input to the next, work that improves with tool lookups and repeated reasoning, and cases where a better answer justifies extra tokens and seconds all qualify. An investigation that starts from one alert and branches on what each lookup returns is the shape the lab builds.

## Page 18

A workflow wins when the path is known. A task whose steps are fixed is cheaper, faster, and more predictable as code. Tight latency or cost budgets rule out a loop of model calls. When mistakes are expensive and the agent can act on the world, the unpredictability of the loop is itself the risk, which is what the Replit incident demonstrated. A single well-crafted prompt that already answers reliably needs no loop at all.

## Page 19

Autonomy is paid for per iteration. Each pass through the loop is a fresh model call carrying the whole conversation so far, so token cost rises with every step, and the calls run one after another, so latency accumulates. The path is chosen at run time from sampled model output and live tool results, so two runs on the same input can call different tools in different orders and reach different answers, and a failure seen once may not appear again. Two controls belong in every agent: an iteration limit so a run that fails to converge stops, and a log of every thought, tool call, and result so a run can be reconstructed afterward.

## Page 20

Memory splits by where it lives. Short-term memory is the context window: the system prompt, the conversation, and every tool result so far. The model has it at no retrieval cost, and it is gone when the context fills or the task ends. Long-term memory is anything stored outside the model and fetched into the context when relevant: a vector store of past cases, a database of known facts, notes from earlier runs. The retrieval mechanism is the one Module 11 used for RAG, retrieval-augmented generation. Short-term memory keeps a single task coherent; long-term memory lets one task benefit from previous ones.

## Page 21

Planning separates deciding the steps from doing them. A planning step asks the model to write out the sub-tasks before any tool is called, which gives a hard problem a structure and gives you something to inspect before the agent acts. Plan-and-Execute is the pattern where a planner produces the full list, an executor works through each item, and control returns to the planner to revise the list when a result contradicts it. ReAct decides one step at a time; Plan-and-Execute commits to a sequence and revisits it only when a step forces a change.

## Page 22

Reflection adds a review pass before the agent commits to an answer. The model is asked to critique its own draft against the task and then produce a revised version, which catches arithmetic slips, evidence it skipped, and reasoning that does not support the conclusion. Reflexion, spelled with an x, is the 2023 method from Noah Shinn and colleagues that keeps those critiques in memory across attempts, so a second try at the same task starts with a written note on why the first one failed. Every critique and retry is another model call, so the pattern trades cost for quality.

## Page 23

Each pattern buys something with extra calls. ReAct is the smallest loop and adapts as it goes, so it is the default. Plan-and-Execute spends a planning call to make the run more predictable and reviewable. Reflexion spends critique and retry calls to raise answer quality and costs the most. Adopt them in that order: ReAct first, planning when the task has enough steps to benefit from being laid out, reflection when answer quality matters more than cost.

## Page 24

The frameworks differ in what they make easy. LangGraph, from the LangChain team, models an agent as a graph of nodes and edges with explicit state, which gives fine control over routing and is what the lab uses. LlamaIndex Workflows chain event-driven steps and inherit LlamaIndex's retrieval tooling, a fit when the agent is mostly retrieval. CrewAI assigns roles to agents and has them collaborate, the shortest route to a multi-agent team. AutoGen began as a Microsoft research project that models agents as participants in a conversation; AG2 is the community fork of it. The OpenAI Agents SDK is a small library with handoffs between agents and guardrails built in, and it runs against models other than OpenAI's. Pydantic AI, from the Pydantic team, validates tool inputs and outputs with typed schemas. Hugging Face smolagents, spelled with a single l, has the agent write short Python programs as its actions, so one action can call several tools.

## Page 25

Anthropic's guide recommends starting without a framework. A model with tool calling and a loop of a few dozen lines is already an agent, and writing that loop yourself keeps every prompt and every tool result in view. A framework adds layers of abstraction between you and the model, extra dependencies, and an API that is hard to migrate away from. The cases that justify one are orchestration across several agents, state that must survive a pause or a crash, and streaming partial output. MCP, the Model Context Protocol from Module 12, is a standard for describing and calling tools, so a tool written once works with any agent that speaks the protocol, whichever framework the agent is built in. Whatever you choose, keep the raw prompts and tool calls inspectable, because debugging an agent means reading what the model was actually sent.

## Page 26

Visual builders let you wire an agent on a canvas instead of in code. Flowise: open-source drag-and-drop editor built on LangChain and LangGraph. Langflow: visual flow builder that accepts custom Python components, MIT licensed. Dify: self-hostable platform for LLM applications with visual agents and built-in retrieval. n8n: general automation canvas that ships AI agent nodes, self-hostable. AutoGen Studio: low-code interface over AutoGen. Rivet: open-source node-graph IDE with a debugger for stepping through an agent's run.

They are for prototyping. A flow drawn on a canvas cannot be diffed in version control, unit tested, or code reviewed the way a Python module can, and those are the things testing and production depend on, so the working design gets rebuilt in code.

## Page 27

The threat model follows from the two things an agent does. It reads data, which gives an attacker a way in, and it takes actions, which give an attack an effect. A chatbot's worst case is a bad answer shown to the person who asked. An agent's worst case is an action taken on an attacker's behalf with the agent's privileges.

Attackers have three targets. The prompt: any text the model reads is a place to plant instructions. The tools: a tool that returns attacker-controlled content is an input channel, and a tool with more privilege than the task needs is a bigger prize. The data: poisoning what the agent retrieves, or what it stores for later, changes its future decisions.

## Page 28

The lethal trifecta is Simon Willison's name, from a June 2025 post, for the combination that turns prompt injection into data theft: access to private data, exposure to untrusted content, and a channel to the outside world. Injected instructions in the untrusted content tell the agent to read the private data and send it out through the channel, for example by fetching a URL with the data encoded in the query string or by emailing it. The exfiltration needs all three legs.

Removing one leg closes the path. No private data means nothing to steal; no untrusted content means no place to inject; no outbound channel means nowhere to send. For an agent that handles sensitive data, choose which leg to give up at design time.

## Page 29

Excessive agency is the gap between what the task needs and what the agent can do. An attacker who controls the agent's decisions controls every tool it holds, so each unneeded tool or permission is attack surface with no benefit. Tool poisoning uses the tool result as the injection channel: a compromised tool, or a legitimate tool that fetches attacker content, returns text crafted to steer the agent, and the model reads it with the same trust as any other observation. In MCP the tool description is model input as well, so a malicious server can inject through the description before the tool is ever called.

Confused deputy is the older name for the resulting failure: a program with authority is tricked into exercising it for someone who lacks it. The agent holds credentials the attacker does not, and follows the attacker's instructions with them. The fix is the same as for user accounts: least privilege, granted per tool.

## Page 30

Four entries from the OWASP Top 10 for LLM Applications apply directly to agents. Prompt injection: attacker text in the input overrides the developer's instructions. Improper output handling: model output passed to a shell, database, browser, or another system without validation, so injected content becomes executed content. Excessive agency: more autonomy or permission than the task requires. Vector and embedding weaknesses: an attacker who can write to the retrieval store controls what the agent later reads as fact.

The numbers here mix two editions. In the 2025 edition, output handling is LLM05, Improper Output Handling; LLM02 was its number in the 2023 edition, under the name Insecure Output Handling. Excessive Agency as LLM06 and Vector and Embedding Weaknesses as LLM08 are 2025 numbers. The design rule is the one that survives renumbering: treat every input as potentially adversarial.

## Page 31

Each mitigation removes a way for a hijacked agent to do damage. Least privilege: each tool gets the narrowest scope that still does the job, read-only where reading is enough, with its own credential. Human in the loop: actions that are risky or cannot be undone, such as sending, deleting, or paying, pause for a person's approval; Part 4 of the lab builds this. Sandboxing: tools run in an isolated environment with short-lived credentials, so there is no standing secret for an injected instruction to read. Allow-lists: the URLs the agent may fetch, the commands it may run, and the recipients it may send to are enumerated in advance, which is one way to cut the trifecta's outbound leg. Output validation: model output is untrusted input to whatever consumes it, so it is parsed and checked against a schema before it reaches a shell, a database, or a send action. Trajectory logging: the full record of prompts, tool calls, and results is both the audit trail and the evidence when an incident is investigated.

## Page 32

The security operations tasks that suit agents are the ones that branch on lookups. Alert triage: pull context for each SOC alert, classify it, and escalate the ones that hold up. Phishing and email analysis: the lab in this module. Threat intelligence enrichment: gather reputation scores, WHOIS registration records for domains, and CVE vulnerability context for an indicator. Incident response: collect evidence from several sources and draft a timeline for an analyst to verify. In each case the agent prepares and the analyst decides; the human-in-the-loop guardrail is the same principle applied to the workflow.

## Page 33

An agent is evaluated the way a classifier is: on a labeled set, with metrics chosen in advance. Task success rate: the fraction of cases where the final outcome matched the label. Tool-call accuracy: whether each step picked the right tool with the right arguments, judged per call. Trajectory quality: whether the sequence of steps was sound, since a correct verdict reached by skipping the lookups is luck and will not repeat. Cost and latency per task: tokens, number of tool calls, and wall-clock time, because a run that is correct and too expensive still fails. The first three need labels for outcomes and, for trajectory quality, either a rubric or a second model acting as judge.

## Page 34

Four topics that build on this module. LangChain's evaluators score outputs against references or rubrics, which is how two models are compared on the same task set. Document chunking and splitting decide how source text is cut before it is embedded for retrieval, and the cut determines what a query can find. Advanced Pydantic covers validators and nested models, which tighten the structured outputs the lab relies on. Model fine-tuning adapts a model's weights to a task instead of adapting the prompt.

## Page 35

This closes the lecture half of the module. The lab follows.

## Page 36

This part is the lab: five stages that grow a LangGraph phishing detector from a two-node classifier to a supervised team of specialists.

## Page 37

The lab builds one agent in five increasingly capable versions, all aimed at deciding whether an email is phishing. The tools it calls are mocks: functions that return plausible reputation and authentication results without contacting any service, so the loop can be built and tested offline. In a deployment each mock would be replaced by a real implementation, and the emails, which the lab loads from a file, would come from a mailbox.

## Page 38

The objective is an agent that identifies phishing emails. The question of how to do it is a design question: which steps, what data passes between them, and where the model sits. The rest of Part 1 answers it with a state graph.

## Page 39

Part 1 produces a verdict on one email with a single model call. That could be done without any framework, and the state graph built around it is more structure than one call needs. It is introduced here because Parts 2 through 5 add tools, branches, pauses, and additional agents to the same graph, and each addition is a change to nodes and edges rather than a rewrite.

## Page 40

A state graph is the map of steps an agent takes and the data those steps share. Nodes are the workers: each is a function that does one job, such as calling the model or formatting a report. Edges give the order the nodes run in. The state is a shared record that every node reads from and writes to, and after each node finishes, its updates are merged into the state before the next node runs.

## Page 41

The output schema is a Pydantic model that tells the LLM what to return and validates what comes back. The verdict field is a string whose description lists the three allowed values. Confidence is a float with numeric bounds of zero and one, and Pydantic rejects a value outside them. Reasoning is a short explanation, and indicators is a list of the specific signals found, defaulting to empty. The field descriptions are sent to the model as part of the schema, so they are prompt text as well as documentation.

The code in this example and the ones that follow classifies a login event as compromised, suspicious, or normal. The lab's schema has the same shape with a phishing verdict.

## Page 42

The state is declared as a TypedDict, a dictionary whose keys and value types are fixed. This example carries the raw login event, the text version of it formatted for the model, the classification result, and the final report. The last two are Optional because they are empty when the run starts and filled in by nodes. LangGraph reads this class as the state schema when the graph is created; the TypedDict is the shape of the data, and the StateGraph is built from it.

## Page 43

The model is wrapped so its reply is parsed into the schema. ChatAnthropic is LangChain's client for Anthropic's models; the model name selects Claude Opus 4.8, and temperature zero reduces sampling randomness so repeated calls with identical input agree as far as the API allows. Calling with_structured_output with the Pydantic class returns a wrapped model that asks the API for output matching the schema and returns a validated instance of the class instead of raw text.

## Page 44

A node is a plain Python function with a fixed contract. It receives the current state, does its work, and returns a dictionary containing only the keys it changed. LangGraph merges that dictionary into the state, so a node that returns one key leaves every other key as it was. Keeping each node to one job keeps the graph readable and lets each node be tested on its own with a hand-built state.

## Page 45

The classification node is four lines of logic. It reads the formatted event text from the state, puts it into a prompt, calls the structured model, and returns the result as a dictionary under the classification key. The call to model_dump converts the Pydantic instance to a plain dictionary so it can be stored in the TypedDict state. Nothing else in the state changes.

## Page 46

Assembling a graph is four calls. Create a StateGraph from the state schema. Add each node function under a name. Add edges from each node name to the next. Compile, which checks that every referenced node exists and every node is reachable, and returns a runnable object. START and END are sentinels that stand for the entry and exit of the graph, so the first edge runs from START and the last edge runs to END. The compiled graph accepts an initial state through its invoke method.

## Page 47

The assembled Part 1 graph is a straight line. Two nodes are registered, one to classify and one to format the decision, and three edges connect START to the classifier, the classifier to the formatter, and the formatter to END. There is no branching and no loop, so in NVIDIA's terms this is a level 1 chain: the same path every run. Compiling it produces the graph object that is invoked next.

## Page 48

Running the graph means passing it a complete initial state. Every key in the TypedDict is present: the first event from the loaded data, an empty string for the formatted text, and None for the two fields that nodes will fill. The return value is the final state after the last node, so the report is read from it by key and printed. In the lab, the event is an email and the report is the phishing verdict.

## Page 49

Lab 13.1 builds this two-node graph for an email: a classification node and a formatting node connected in a straight line.

## Page 50

The first worksheet takes thirty to forty minutes. It defines the state and the output schema, writes the two nodes, assembles and compiles the graph, and runs it on the sample emails.

## Page 51

Part 2 gives the agent tools and the loop that uses them.

## Page 52

The Part 1 agent judged each email from its text alone. Part 2 lets the model look things up before deciding: it can check a URL, a sender, or the authentication headers, read the result, and decide whether it needs another lookup or has enough to classify.

## Page 53

A tool-calling agent keeps its state as a message history. The exchange is a conversation: the model sends a message asking for a tool call, the tool's result is appended as a tool message, the model reads the whole sequence and either asks for another tool or answers. A fixed set of fields cannot hold a conversation of unknown length, so the state has one field, a list of messages.

The list needs a reducer. When a node returns a value for a state key, LangGraph replaces the old value by default, which would discard the history on every step. Annotating the field with add_messages tells LangGraph to append returned messages to the existing list instead, so the history grows and nothing earlier is lost.

## Page 54

The tool decorator turns a Python function into something the model can call. It registers the function as a tool, sends the docstring to the model as the tool's description, and builds the argument schema from the function's signature and type hints, so the model knows the parameter names and types. The docstring is prompt text: it is what the model reads to decide when to call the tool and with what.

## Page 55

The three names here belong to the earlier login example. The lab's mock tools file provides three email tools instead: a URL reputation check, a sender reputation check, and an email authentication check that reads the SPF, DKIM, and DMARC results. All three return canned results offline.

## Page 56

A tool definition is a decorated function with a documented signature. The list at the top collects the tools so they can be bound to the model in one call. The function takes typed string arguments and returns a string, since tool results go back to the model as text. The docstring's first line is the description the model sees, the Args section documents each parameter, and the Returns section tells the model what shape of answer to expect. This example detects impossible travel: two logins from places too far apart to travel between in the time elapsed.

## Page 57

Binding attaches the tool schemas to every request the model receives. The wrapped model sends the tool names, descriptions, and argument schemas along with the messages, and its reply may contain structured tool calls. The model does not run anything; it names the tool and the arguments, and the graph runs the call.

## Page 58

The investigator node is the model call at the center of the loop. Each time it runs it takes the message history from the state, adds the system prompt if it is missing, sends the messages to the tool-bound model, and returns the reply, which the reducer appends to the history.

The reply takes one of two forms. If the model wants evidence, the reply's tool calls field holds one or more requested calls. If the model has enough, the reply is text carrying the verdict. Which form came back decides where the graph goes next.

## Page 59

Two pieces close the loop. ToolNode is a LangGraph prebuilt node: it reads the tool calls from the last model message, runs each requested tool, and returns the results as tool messages that join the history. The routing function inspects the last message: if it carries tool calls the graph goes to the tool node, and if it is plain text the graph ends.

## Page 60

Assembled, the graph runs the ReAct pattern. The investigator reasons over the evidence so far and either requests a tool or answers. A requested tool runs and its result joins the conversation. The investigator runs again with the result in view. A text reply is the exit. There is no explicit iteration cap in this graph; LangGraph's recursion limit, twenty-five steps by default, raises an error if the graph keeps looping past it.

## Page 61

The code adds two nodes and three kinds of edge. The investigator and the tool node are registered by name. A fixed edge runs from START to the investigator. A conditional edge runs from the investigator through the routing function, with a mapping from the function's return values to the tool node or to END. A fixed edge runs from the tool node back to the investigator, and that back edge is what turns the graph from a chain into a loop.

## Page 62

Lab 13.2 takes forty-five to sixty minutes. It defines the message-based state, binds the three email tools, writes the investigator and routing functions, and assembles the loop.

## Page 63

Part 3 adds triage: a first pass that decides how much investigation each email gets.

## Page 64

The Part 2 agent ran tool calls for every email. Some emails are plainly benign and do not justify a full investigation, so Part 3 puts a triage step first and routes each email to a path matched to its risk. The text here says login events; the lab applies the same idea to emails.

## Page 65

Routing needs state that carries results forward. Each node adds what it learned, and later nodes read it; the lab calls this state enrichment. The state for Lab 3 holds the raw email, its formatted text, the risk level the triage step assigns, the structured classification from the analysis node, a list of investigation notes that accumulates tool results as evidence, and the final report assembled at the end.

## Page 66

A conditional edge is a function plus a mapping. The routing function takes the state and returns a string naming the next node. The call that adds the edge takes the source node, the routing function, and a dictionary from return values to node names. The routing function reads one field, the risk level, and returns a string; it makes no decision of its own. The decision was made by the triage node that set the field.

## Page 67

Three paths, each its own node, matched to a risk level. Deep investigation, for high risk: runs the URL, sender, and authentication tools and then classifies with the evidence. Light review, for medium risk: runs the authentication check only and classifies from that. Fast pass, for low risk: approves without calling a tool or the model. Effort scales with risk, and the low-risk path costs nothing beyond the triage call.

## Page 68

The Lab 3 graph fans out and back in. Triage runs first, a conditional edge sends the email to one of the three paths, and all three paths lead to the report node, which leads to the end. Dotted edges in the drawing are conditional; solid edges are fixed.

## Page 69

The mapping keys are the routing function's return values and the mapping values are node names. Here the two are the same strings, which reads well, but they need not match: the function could return short codes that the dictionary translates to node names.

## Page 70

Lab 13.3 takes forty-five to sixty minutes. It writes the triage node, the routing function, the three path nodes, and the report node, and wires them with a conditional edge.

## Page 71

Part 4 pauses the graph for an analyst's decision.

## Page 72

A model can be uncertain, and some actions are too costly to take on a model's say-so. In both cases the graph hands the decision to a person: the agent does the preparation, then stops and waits for an analyst to confirm, override, or escalate. This is the approval gate from the mitigations list, built into the graph.

## Page 73

Pausing for a person needs four pieces. A field in the state to hold the analyst's decision. A way to stop the graph at the review node and hand control back to the caller. A way to restart the graph from that point with the decision supplied. And storage for the state while the graph is stopped, since the wait may be minutes or days and the process may not survive it. LangGraph provides the last three as interrupt, resume, and the checkpointer.

## Page 74

The Lab 4 graph extends Lab 3 after the report node. A conditional edge asks whether the case needs review. If it does, the human review node pauses for the analyst and the apply decision node records the answer. If it does not, the auto finalize node closes the case. Both branches end the graph.

## Page 75

A node pauses by calling interrupt with a value. The call stops the graph, returns control to whatever invoked it, and hands that value back so the caller can show the analyst what needs a decision; here the value is the verdict and confidence. The checkpointer saves the graph's state at the pause. When the graph resumes, the node runs again from its first line and the interrupt call returns the value the analyst supplied, which the node stores in the state.

## Page 76

Resuming is another invoke call carrying the analyst's answer. The graph is invoked with a Command whose resume field holds the decision, and with the same thread identifier in the config, which is how the checkpointer finds the saved state. Inside the paused node the interrupt call returns that decision and execution continues from there. In the example the analyst approves, so the resumed node stores an approve action and the graph proceeds to apply it.

## Page 77

A checkpointer is where the graph's state lives between steps. MemorySaver keeps it in a Python dictionary inside the process, which is enough for development and testing and is lost when the process exits. SqliteSaver and PostgresSaver write it to a database, so a paused investigation survives a restart and can be resumed from another process.

Each run is identified by a thread identifier, a string you choose and pass in the config. The checkpointer saves the state after every step, so a graph can resume from the exact point it stopped, and the saved history can be inspected afterward. Runs under different identifiers do not see each other's state, so one checkpointer serves any number of investigations in flight.

## Page 78

Lab 13.4 takes forty to fifty minutes. It adds a routing function that sends a case to review when the verdict is suspicious, the confidence is below seven tenths, or a high-risk email was classified as legitimate, then adds the review, decision, and finalize nodes, compiles with a memory checkpointer, and runs cases under separate thread identifiers to approve, override, and escalate.

## Page 79

Part 5 replaces the single agent with a supervisor and a team of specialists.

## Page 80

In Parts 1 through 4 the developer fixed the graph: the nodes, the branches, and the order were written in code, and the model's choices were limited to which tools to call inside the loop. Part 5 moves the choice of path to the model. A supervisor agent reads the case and decides which specialists to consult and in what order, and each specialist is a ReAct agent of its own.

## Page 81

The supervisor is the hub of the Lab 5 graph. Control enters at the supervisor, a conditional edge sends it to one of the three specialists or to the end, and a fixed edge from each specialist returns to the supervisor, which decides again. The three specialists are a content analyst, a header analyst, and a URL and attachment analyst. The structure is the ReAct loop one level up: the specialists play the role that tools played in Part 2.

## Page 82

The prebuilt agent factory packages the Part 2 loop into one call. It takes the model, a list of tools, a name, and a system prompt, and returns a compiled graph with the tool-calling loop, automatic tool execution, and message-based state already wired. The tool list may be empty for a specialist that works from reasoning alone. The name is what the supervisor uses to hand off to the agent, and the prompt defines its specialty. Each specialist is self-contained: the supervisor knows what each one is for and nothing about how it works inside.

The lab notebook uses the newer name for the same factory, create_agent from LangChain, and its prompt parameter is called system_prompt.

## Page 83

A specialist is a model, a short tool list, a name, and a role prompt. This example is from the login domain: an identity analyst with two tools and a prompt that lists the checks to run and asks for a detailed, specific report. The report matters because the specialist's final message is what the supervisor reads when it synthesizes the verdict. The lab's three specialists follow the same template: a header analyst with the sender reputation and authentication tools, a content analyst with no tools, and a URL and attachment analyst with the URL reputation tool.

## Page 84

The supervisor is an agent whose tools are other agents. The supervisor factory, from the langgraph-supervisor package, builds one that receives the case, decides which specialists to consult, delegates by sending each a message, collects their reports, and writes a final verdict from them. Its parameters are the list of specialists, a prompt that tells it how to run the team, and an output mode: full history returns every message including the handoffs, and last message returns only the supervisor's summary.

The handoff works through tool calling. Each specialist is presented to the supervisor as a callable tool; when the supervisor calls it, control passes to that specialist's own loop, and the specialist's final message comes back as the tool result. The full history mode is the one to use while learning, because it shows every handoff and every specialist report in order.

## Page 85

The supervisor's prompt is where the investigation policy lives. It names each specialist and what it checks, lays out the procedure of review, delegate, synthesize, verdict, and evidence, and adds rules: consult at least two specialists, consult the geolocation analyst for logins from new locations, and consult the identity analyst for unusual devices. In Part 3 the routing policy was a Python function and ran the same way every time; here it is prose in a prompt, and compliance is not enforced by code. Compiling the supervisor produces the graph that is invoked with the case. This example is the login version; the lab's prompt names the three email specialists and asks for a phishing, suspicious, or legitimate verdict.

## Page 86

Lab 13.5 takes sixty to ninety minutes. It builds the three email specialists, builds the supervisor over them, runs the team on sample emails, and reads the full message history to follow the handoffs and the reports that produced each verdict.

## Page 87

End of the module.
