## Page 1

Module 12 covers the Model Context Protocol, MCP, an open protocol Anthropic published in November 2024 that standardizes how an AI application connects to outside tools and data. The module states the integration problem the protocol removes, defines its host, client, and server roles, describes what a server can offer, builds and tests a server in Python, loads that server's tools into a LangChain agent, and closes with the security cost, the context cost, and the payment protocols through which an agent pays for a call.

## Page 2

This part sets out the integration problem MCP exists to remove and defines the protocol.

## Page 3

Module 11's tools were Python functions marked with the `@tool` decorator and bound to a single LLM client. Each tool's definition, implementation, and calling agent lived in one codebase, so a tool existed only inside the application that defined it.

Reuse was copy and paste. Using the same tool from a second application meant duplicating its code, and using a tool someone else wrote meant importing their code into the process and keeping it current by hand.

## Page 4

The number of integrations grows as the product of applications and systems. An agent needs files, databases, HTTP APIs, and a ticketing system; an IDE assistant and a chat client need the same systems. With no shared protocol, each application carries its own adapter for each system, and every adapter has its own authentication, data shapes, and bugs.

M applications against N systems is M times N adapters, each written and maintained separately. Adding one system means writing M adapters; adding one application means writing N.

## Page 5

MCP replaces per-pair adapters with one protocol that each side implements once. A system is wrapped once as an MCP server. An application implements the client side once. Any application can then use any server with no new code on either side, so the count drops from M times N to M plus N.

The reuse runs both ways. A server written for Claude Desktop works unchanged in an IDE or in a LangChain agent, and an application that speaks MCP gains every existing server without further integration work.

## Page 6

MCP is a published specification with reference implementations. Anthropic released it in November 2024 with the specification at modelcontextprotocol.io and open-source SDKs; during 2025 OpenAI, Google, and Microsoft added MCP support to their agent products, which is what the adoption claim refers to.

Messages use JSON-RPC 2.0, a remote procedure call format in which every message is a JSON object naming a method and its parameters, and each request carries an id that the response repeats so the two can be matched. MCP defines the method names, such as tools/list and tools/call, and the shape of their parameters and results.

The protocol is independent of language because it is only a message format. Official SDKs exist for Python, TypeScript, Java, C#, Kotlin, Swift, and others, and a server in one language works with a client in another.

## Page 7

This part covers the three roles in an MCP deployment, the two transports messages travel over, and the lifecycle of one connection.

## Page 8

MCP splits an integration into three roles. Host: the program the user talks to, which owns the LLM and decides what to do with what servers offer; Claude Desktop, Claude Code, an IDE plugin, or the LangChain agent built in the lab. Client: a component inside the host that holds one connection to one server, carries the JSON-RPC exchange, and hands the server's tools, resources, and prompts to the host. Server: a separate program that exposes those capabilities and runs them on request.

The client-to-server relationship is one to one, so a host that uses three servers runs three clients. Each connection negotiates its own capabilities, the host can grant each server a different permission scope, and disconnecting one server affects no other connection.

## Page 9

The host application is the agent. Inside it sit three MCP clients, one per server. Each client speaks MCP, carried as JSON-RPC, to exactly one server: a filesystem server, the security-tools server from this module's lab, and a database server. Each server in turn talks to the system it wraps, local files, a threat-intelligence API, or a database, using whatever native interface that system has.

The server is where system-specific code and credentials live. The agent holds no API key for the threat-intelligence service and no database driver; it hands tools/call to a client and receives text back. Swapping the threat-intelligence vendor means changing the server, and the agent is untouched.

## Page 10

The host owns every connection. It starts a client for each server it is configured to use, and each client is attached to exactly one server; a host that wants two servers runs two clients.

Where the server runs is the host's choice. Local servers run on the same machine as a child process; remote servers run elsewhere and answer over the network; the client code is the same apart from the transport it opens.

Servers advertise and the host decides. A server lists its tools, resources, and prompts and answers calls; it cannot force a tool to run, insert a resource into the conversation, or trigger a prompt. The host chooses which tools the model sees, whether to ask the user before a call, and which resources to attach.

## Page 11

A transport is the channel that carries JSON-RPC messages between client and server; the protocol defines two. stdio: the host launches the server as a child process and writes requests to its standard input, and the server writes responses to its standard output, one JSON message per line. Standard error stays free for logging. The lab notebook's Windows workaround exists because Jupyter's captured stderr has no file descriptor to hand the child process. stdio suits local tools, since the server exits with the host and needs no network port.

Streamable HTTP: the client sends each JSON-RPC message as an HTTP POST to a single endpoint, and the server replies with either one JSON response or an open stream of server-sent events when it has several messages to send. It suits shared or hosted servers, since one server process can serve many clients and can require authentication.

Choosing a transport changes nothing above it. The methods, parameters, and results are identical; only the framing differs, so a server written for stdio can be exposed over HTTP by changing the run call.

## Page 12

A connection passes through four phases. Initialize: the client sends an initialize request carrying the protocol version it speaks, its capabilities, and its name; the server answers with the version it will use and its own capabilities; the client confirms with an initialized notification. A server that does not support the client's version replies with one it does, and the client disconnects if it cannot speak that one.

Capability negotiation happens inside that exchange. The server declares which of tools, resources, and prompts it offers and whether it will send a notification when its lists change; the client declares whether it supports sampling, roots, and elicitation. Neither side may use a feature the other did not declare.

Operate: the client sends tools/list and tools/call, resources/list and resources/read, prompts/list and prompts/get, and the server answers each by id. Shutdown has no protocol message. Over stdio the client closes the server's standard input and waits for the process to exit; over HTTP the client closes the connection.

## Page 13

This part defines the three capability types a server exposes, tools, resources, and prompts, and the requests a server can make of the client in return.

## Page 14

A server exposes up to three kinds of capability, distinguished by who initiates their use. Tools: actions, invoked when the model decides to. Resources: data, attached when the application decides to. Prompts: templates, run when the user decides to.

That distinction sets where the controls go. A tool runs on the model's judgment, so it is the primitive that needs an approval gate; a resource enters the context only when application code or the user asks; a prompt does nothing until a person selects it.

## Page 15

An MCP tool is the Module 11 tool made portable. Each has a name, a natural-language description, and an input schema written in JSON Schema that names the arguments and their types. The host passes all three into the model's context; the model picks a tool and fills its arguments; the host sends tools/call to the server; the server runs the function and returns content, which the host feeds back to the model as the tool result.

The description is the only guidance the model has. It decides both whether the tool is chosen and how its arguments are filled, which is why the lab server's docstrings say when to use each tool and give an example argument. Anything a system can do behind a function is a candidate: query a database, check a URL, send a message.

## Page 16

A resource is read-only data addressed by a URI. The server answers resources/list with each resource's URI, name, and MIME type, and resources/read with the contents. Schemes are the server's to define; file:///logs/today.log and db://users/42 are two examples, and a URI containing a placeholder such as db://users/{id} is a template that covers a family of resources.

The application decides when to read one; the protocol gives the model no method to fetch a resource. The host application or the user attaches it, and its contents enter the context as they are. Claude Desktop lists a server's resources as attachable items in the chat. Examples: file text, a database record, a configuration.

## Page 17

A prompt is a message template the server defines and the user triggers. The server answers prompts/list with each prompt's name, description, and named arguments, and prompts/get with the messages produced for a given set of argument values; the host inserts those messages into the conversation. Claude Code exposes each server prompt as a slash command, and Claude Desktop lists them in its attachment menu.

Prompts standardize repeated work. A server for a ticketing system can ship a "summarize this incident" prompt whose wording was tuned once, and every host that connects to it offers that same wording.

## Page 18

The protocol also runs in the other direction: a server can send requests to the client. Sampling: the server sends sampling/createMessage with a conversation it wants completed; the host runs its own LLM on it and returns the result, and may show the request to the user for approval first. The server gets model access without holding an API key or choosing a model. Roots: the server asks roots/list and the client answers with the file URIs, the directories, the server may work in; the boundary is advisory, and the server is expected to confine itself to it. Elicitation: added to the specification in June 2025; the server sends a JSON schema describing the input it needs, the host renders a form, and the user fills it in, declines, or cancels.

All three are declared as client capabilities during initialization, and a server must check for them before use. Their purpose is to let a server use the host's model and the host's user, so a server needs neither a model nor an interface of its own.

## Page 19

This part builds a server in Python with FastMCP, checks it with the MCP Inspector, and runs it as a stdio process.

## Page 20

Lab marker. Students work through Worksheet 12.1, Building an MCP Server, the MCP lab the slide links to.

## Page 21

FastMCP is the server class in the official mcp Python package, importable from mcp.server.fastmcp. It reads a decorated function's signature and docstring to produce the tool, resource, or prompt definition, converts type hints into the JSON Schema the protocol requires, and answers every JSON-RPC method itself. The author writes the function body and nothing about the wire format.

The name has two owners. FastMCP began as an independent open-source project by Jeremiah Lowin; its first version was merged into the official SDK in early 2025, and a separate FastMCP 2 package continues on its own. The lab and this deck use the one inside the official package. Install it with the cli extra, `pip install "mcp[cli]"`, to get the mcp command used for testing.

## Page 22

Four lines register a server and one tool. `FastMCP("security-tools")` creates the server and sets the name it reports during initialization. The `@mcp.tool()` decorator registers the function beneath it: the function name becomes the tool name, the `url: str` annotation becomes an input schema with one required string field, and the docstring becomes the description the model reads. The return value, a string here, is sent back as the tool result.

The body is where real work would go. The example returns a fixed verdict; the lab server, `notebooks/mcp_server.py`, uses the same pattern for three tools and looks the domain up in a small in-memory reputation table. Calling a real reputation service from the body would leave the tool's name, schema, and description as they are.

## Page 23

A resource is registered by decorating a function with the URI that names it. `ioc://blocklist` uses a scheme the server made up; any scheme is valid as long as the host treats the URI as an opaque identifier. The function takes no arguments, so this is a single fixed resource; a URI with a `{placeholder}` would turn it into a template and the placeholder into a function parameter. The docstring is the description in resources/list, and the returned string is the content of resources/read.

The blocklist reaches the model only when the application or the user reads it in; the server cannot push it, and the model sees the list as ordinary text once it arrives. `load_known_bad_domains` stands for whatever code fetches the list.

## Page 24

A prompt is a function whose parameters become the template's arguments. `@mcp.prompt()` registers `phishing_report` with one argument, `sender`, listed by name in prompts/list along with the docstring as its description. When the user picks the prompt and supplies a sender, the host calls prompts/get, the function runs, and the returned string becomes a user message in the conversation. A function can also return a list of messages when the template needs several turns.

## Page 25

`mcp.run()` starts the server loop and, with no argument, chooses the stdio transport: the process reads requests from standard input and writes responses to standard output until the client closes the input. Passing `transport="streamable-http"` starts an HTTP server on a port instead, and the tool definitions are unaffected.

The `__main__` guard matters more here than in an ordinary script. The mcp dev command and other tooling import the file to find the `mcp` object, and without the guard the import itself would start a server that then waits on standard input. Run directly from a terminal, the server sits waiting for a client and prints nothing; Ctrl-C stops it.

## Page 26

The MCP Inspector is a browser application maintained alongside the protocol that connects to a server as a client with no model involved. The `mcp dev <file>` command from the Python SDK launches it: it starts the server as a stdio subprocess, opens the Inspector page on localhost, and connects the two. The Inspector is a Node package, so the command needs npx on the path.

Inside it, the Tools, Resources, and Prompts tabs show what the server returned to the corresponding list request, each tool has a form built from its input schema, and every request and its raw JSON-RPC response appear in a history pane.

Inspecting first separates a broken server from a model that chose badly. A tool that fails to appear, a schema missing an argument, or a description that omits when the tool applies is visible here in seconds; with an agent in the loop the same fault shows up only as odd model behavior with no obvious cause.

## Page 27

The Inspector connected to the lab's security-tools server. On the left, the transport is STDIO and the launch command is the one mcp dev generated, uv running mcp with the server file; the status is connected, and the server reports its name and a version, the installed mcp package's version, since the server declared none of its own. The Tools tab lists the three tools with the first line of each docstring.

The right panel is the selected tool, `check_url_reputation`: the full description, the documented url argument, a form field to call it with, and an output schema that FastMCP derived from the `-> str` return annotation. The four flags above the form are the tool annotations, hints a server may attach so a host knows whether a tool is read-only, destructive, idempotent, or open-world. This server sets none, so the Inspector displays the specification's defaults: read-only false, destructive true, idempotent false, open-world true. A host that respects annotations therefore treats an unannotated lookup as if it could cause damage.

The bottom panes are the protocol in motion. History holds the requests sent since connecting, resources/list, resources/templates/list, and tools/list, each expandable to its JSON. Server Notifications holds notifications/message entries, the server's log lines delivered as JSON-RPC notifications.

## Page 28

Run the Inspector against the lab server before the notebook uses it: `mcp dev notebooks/mcp_server.py` from the repository root. The command requires the cli extra of the mcp package and a Node.js installation for npx. In the browser, connect, list the tools, and call `check_url_reputation` with http://paypa1-secure.com/login; the server answers with a malicious verdict and a risk score of ninety. github.com scores five, and any domain missing from both tables scores forty with a caution note, since the server's reputation data is two small dictionaries. Call `check_email_authentication` with fail, none, and fail to see the spoofing summary. Resources and Prompts both list nothing because this server defines neither, and the history pane shows the exact JSON each call produced.

## Page 29

This part shows how a host is told which servers to launch and how a LangChain agent loads a server's tools.

## Page 30

A host learns about servers from configuration, and each entry describes how to reach one. For a stdio server the entry is the command to run and its arguments; for a remote server it is a URL. At startup the host spawns each command, opens a client on the child's standard input and output, runs the initialize exchange, and calls tools/list to learn what it can offer the model.

The shape is shared across hosts. Claude Desktop reads a file named claude_desktop_config.json, Claude Code reads .mcp.json in the project, and both use a top-level mcpServers object; the LangChain client in the lab takes the same structure as a Python dictionary.

## Page 31

The entry names a server and tells the host how to start it. The key, security-tools, is the label the host uses for the connection and for prefixing tool names when it needs to keep servers apart; it need not match the name the server reports. `command` and `args` are the process to spawn, so the host runs python with mcp_server.py as its argument and speaks stdio to it. No transport field is needed; a command implies stdio, and an HTTP server would give a url instead.

Two details matter in practice. Relative paths resolve against the host's working directory, which is why the lab notebook computes an absolute path to the server file. An env object alongside command passes environment variables such as an API key to the server process, so a credential the server needs stays out of the agent's own code.

## Page 32

The langchain-mcp-adapters package makes MCP tools indistinguishable from LangChain tools. Its client connects to each configured server, calls tools/list, and wraps every entry as a LangChain tool object carrying the same name, description, and argument schema. When the agent calls one, the adapter issues tools/call to the server and hands the returned text back as the tool result.

The agent code stays as it was in Module 11. The wrapped tools go into create_agent in the same list as any locally decorated function, and the model sees one set of callable tools with no marker of which are local and which are served over MCP.

## Page 33

The listing connects to one server and builds an agent from its tools. `MultiServerMCPClient` takes a dictionary keyed by server name; each value gives the command, its arguments, and a transport, which the adapter requires explicitly, stdio here and streamable_http with a url for a remote server. `get_tools()` connects, lists, and wraps, and it is awaited because the connection is asynchronous; a Jupyter cell can await at top level since the notebook already runs an event loop. The remaining two lines are Module 11's: a chat model and create_agent with the tool list.

The adapter opens a session per call by default. Each tool invocation starts the server, initializes, calls the tool, and shuts down, which is simple and correct for a stdio server that starts in well under a second. The lab notebook uses the same code with two changes: the command is the notebook's own Python interpreter and the argument is the absolute server path, so the launch does not depend on what python means on the student's machine or where the kernel started.

## Page 34

This part covers what connecting a server exposes an agent to, the four main risks, the defenses against them, and the context cost that every connected tool adds to each request.

## Page 35

Connecting a server moves the trust boundary to include that server's code. A stdio server is a process on the machine running with the user's privileges; its tool results enter the model's context; its tools act with whatever access the agent has. A server that is malicious, or that was benign and then compromised, can read every argument the agent passes it, return text that steers the model, and perform actions in the agent's name.

The Module 11 example is the July 2025 incident in which Replit's coding agent deleted a production database during a declared code freeze. That agent acted through tools it had been given; a connected MCP server is the same kind of capability handed over with one line of configuration.

## Page 36

Four risks, each with its mechanism. Untrusted servers: a server is a program you run, and a stdio server launched from a package registry executes arbitrary code at first start with your filesystem and network; it can exfiltrate what it is sent, alter what it returns, or do anything else a process can. Tool poisoning: the model reads a tool's description as instructions, so a description containing hidden directives, for example an instruction to read a private key file and pass its contents in a spare argument, gets followed while the host's interface shows the user only the tool's name; Invariant Labs documented this against MCP in April 2025.

Prompt injection: a tool result is text placed in the model's context, so when a tool fetches a web page, an email, or a ticket that contains instructions, the model may follow them. The attacker controls the retrieved data, and the server itself can be honest. Over-permissioning: a server holding a broad credential, a database administrator account or a repository token with write scope, turns a model mistake or an injection into damage at that credential's full scope. The remedy is least privilege, the rule applied to any other service account: each server gets the access its job needs and no more, and several tools each holding narrow access are preferable to one tool holding broad access.

## Page 37

Each defense answers one of the risks. Vetting and pinning: read the server's source, pin a package version or a commit so an update cannot substitute new code, and prefer servers in the official repository or published by the vendor of the system they wrap. Pinning also defeats the variant of tool poisoning in which a server ships a clean description, is approved, and changes it in a later release.

Least access: run each server with a credential scoped to its job, a read-only database user, a token limited to one repository, a filesystem root limited to the directories it needs. Human in the loop: the host asks before a destructive call; Claude Desktop and Claude Code prompt on tool calls by default, and a LangChain agent gets the same gate through an interrupt before the tool runs. Secrets: a credential passed to a server you do not control is in that server's hands from then on, so secrets go only to servers you run yourself, through the environment of the server process.

## Page 38

Tool definitions are sent on every request, and that is the MCP tax. LLM APIs hold no state between calls, so each request carries the full conversation plus every tool the host has enabled, serialized as name, description, and JSON Schema. A host serializes every tool from every connected server into every call, whether or not the model uses any of them.

The cost has three parts. Tokens: each definition is billed as input on every request, and prompt caching lowers the price of re-sending an unchanged prefix while the definitions still occupy the context window. Latency: the model processes those tokens before it produces anything. Selection quality: tools with overlapping names or descriptions from different servers become harder to tell apart as the list grows, and the model picks the wrong one or calls several. The cost scales with the count of tools and the length of their descriptions.

## Page 39

Five ways to cut the tax. Per-task connection: configure servers per agent or per workflow instead of attaching every available server to every agent; the lab agent connects one server with three tools. Fewer, broader tools: a server that wraps an API one endpoint per tool ships dozens of definitions, while one that offers a few task-level tools ships a handful.

On-demand loading: Anthropic's API offers a tool search feature that keeps definitions out of the prompt until the model searches for them, and in a LangChain agent the equivalent is passing create_agent only the subset of tools a task needs. Short descriptions: every word travels with every request, and the description is also what the model chooses by, so cut the padding and keep the sentence that says when to use the tool. Accounting: each tool added is a cost on every turn for the life of the conversation.

## Page 40

Hand-rolled tools are the right default when one application owns them. A decorated function in the agent's own process has no subprocess, no protocol layer, no adapter, and a stack trace that ends in your code. MCP earns its overhead when the same tools are needed in several hosts, when a team shares tools across projects, or when a third party's server does what you would otherwise write.

The model cannot tell the two apart. Either way it receives a name, a description, and a schema, and either way the result comes back as text. The signal to move is the second application that wants a tool, or the first external server you want to connect.

## Page 41

Existing servers cover the common systems. The official repository, github.com/modelcontextprotocol/servers, holds reference servers for the filesystem, git, HTTP fetch, and memory, and links to servers maintained by vendors; GitHub maintains its own server for its API, and Google publishes servers for its threat intelligence and security operations products. An official registry at registry.modelcontextprotocol.io opened in preview in September 2025 as a searchable index.

Connecting an existing server is still running its code, so the vetting on the defenses slide applies in full. The check before writing a server is whether one already exists; the check before connecting one is who wrote it and what it can reach.

## Page 42

This part covers two new protocols that allow an agent to pay for a tool or API call on its own, and what a wallet does to the agent's risk.

## Page 43

Agents that call paid APIs need a way to pay per call with no account and no human at checkout. x402, published by Coinbase in 2025 and since handed to Linux Foundation governance, uses the HTTP status code 402 Payment Required, defined in the original HTTP specification and left unused. The flow: the client requests a resource; the server answers 402 with the price, the asset, the network, and the address to pay; the client signs a stablecoin transfer authorization and repeats the request with the signed payment attached; the server verifies it, settles it on chain, and returns the resource.

MPP, the Machine Payments Protocol from Stripe and Tempo, the payments-focused blockchain Stripe announced with Paradigm in 2025, replaces per-call settlement with a session. The agent authorizes a spending limit once, then streams many small payments against it, so each call avoids a fresh on-chain settlement and the latency and fees that come with one. MPP is backward compatible with x402, so a server that speaks x402 can be paid by an MPP client.

A remote MCP server over Streamable HTTP is an HTTP endpoint, so the same flow applies to a tools/call request: the server answers 402 with a price, the client pays, and the call proceeds. That is how a server or a single tool charges per call.

## Page 44

A wallet turns prompt injection into spending. Every injection path from the security section now ends in money leaving, and an on-chain settlement is final, so payment belongs in the same class as a destructive action.

x402 adds a trusted third party. A facilitator is an off-chain service the resource server calls to verify a signed payment and submit it on chain, so the server needs no chain access of its own; the protocol defines the facilitator's interface and says nothing about its correctness. A faulty or dishonest facilitator can report an unsettled payment as settled or settle one wrongly, and every service relying on it is affected at once.

Published research has demonstrated three attacks. Replay: one signed authorization accepted more than once when nonces are not tracked. Interception: an attacker in the path relays the authorization, collects the charge, and delivers nothing. Fake discovery: a malicious endpoint listed in a discovery index, which an agent then selects and pays. The defenses follow from them: spending limits enforced in the signing layer where the model cannot override them, human approval above a threshold, single-use nonces and idempotent charge handling, delivery only after settlement is confirmed on chain, and an allowlist of payees. Both protocols are months old and changing, so an agent that pays unattended is a pilot with a capped wallet.

## Page 45

The module's six claims. MCP is one protocol implemented once per side, so M applications and N systems cost M plus N integrations. A host runs one client per server; a server offers tools chosen by the model, resources attached by the application, and prompts triggered by the user. A FastMCP server is decorated functions plus a run call, and the adapter client brings it into a LangChain agent in four lines.

The costs are as fixed as the benefits. Every tool definition on every connected server is sent with every request, so tool count is a per-turn expense. Every server is code trusted with the agent's context and actions, so servers are vetted, pinned, scoped to least access, and gated by a person for destructive calls. A payment protocol makes spending one more action an injection can trigger, so a wallet comes with hard limits set outside the model.

## Page 46

Questions on MCP before the lab.

## Page 47

Lab 12.1 is the client side of this module. The server, `notebooks/mcp_server.py`, is given and complete: a FastMCP server named security-tools with three simulated tools for URL reputation, sender reputation, and SPF, DKIM, and DMARC analysis. The worksheet, `Worksheet_12.1_Building_an_MCP_Server.ipynb`, has you configure a MultiServerMCPClient with the stdio transport, await get_tools and confirm three come back, build an agent with create_agent and a SOC phishing-triage system prompt, and send it two emails.

The first email claims to be PayPal billing from paypa1-secure.com with failing authentication and a login link; the agent should call the tools and return a phishing verdict. The second is a GitHub sign-in notice with passing authentication; the agent should return legitimate. Needed beforehand: the mcp and langchain-mcp-adapters packages; the chat model comes from the setup cell, which builds it against the course's serving endpoint, so the model is whatever that cell names.

## Page 48

Title card for Lab 12.1, in which an agent is connected to the security-tools server and made to triage two emails.
