## Page 1

Module 10 covers prompt engineering: calling a language model from Python through a vendor SDK or through an abstraction layer that hides the vendor, the request parameters that shape a reply, the practices that make a prompt hold up when code has to parse the answer, chain of thought and meta prompting, classification with a generative model, and querying data in plain English, through PandasAI over a DataFrame and through generated SQL.

## Page 2

This module is Part 2 of the course's four-part sequence on generative AI. Part 1 covered how generative models work. Part 2, prompt engineering, covers getting the most out of a generative model. Part 3 covers the architecture of AI-driven applications, and Part 4 covers red teaming, attacking and defending AI applications.

## Page 3

The module has three threads: strategies for writing prompts, meta prompting, in which one prompt writes the next, and prompting from code rather than from a chat window.

## Page 4

The slide's setup is an Anthropic model called through the anthropic Python package, with the key in .env. Both worksheets instead build their client in the setup cell, which points at the course's serving endpoint, so the model is whatever that cell names and no key of your own is needed. The third bullet names OpenAI; the rest of the slide names Anthropic. The principles carry over to any vendor's model.

The slide keeps the key in a file named .env in the root of the repository, as a single line assigning ANTHROPIC_API_KEY. The bootcamp repository ignores .env in git, so the key stays out of version control. Keep the key out of notebooks and out of code: a notebook is shared and committed, and a key pasted into a cell travels with it.

## Page 5

The python-dotenv package moves the key from the .env file into the process environment. load_dotenv reads the file and sets one environment variable per line. os.environ.get then returns the value, or None if the variable is not set. The anthropic client reads ANTHROPIC_API_KEY from the environment on its own, so the explicit lookup on the last line matters only when the code needs the value itself, such as to confirm the key is present before making a call.

## Page 6

Run the examples in a notebook as you read them. The slide code runs as written once .env holds a valid Anthropic key. In the worksheets the setup cell's client replaces that step: on Databricks it points at the course's serving endpoint, so no key of your own is needed there.

## Page 7

This part defines prompt engineering and separates prompting from a program from prompting in a chat window.

## Page 8

Whether prompt engineering counts as a skill depends on where the prompt is used. In a chat window a weak prompt costs one more turn to rephrase. In a program nobody rephrases, so the prompt has to work the first time on inputs the author does not see.

## Page 9

A program sends the prompt and consumes the reply with no person in between. In a chat a person reads each answer and adjusts the next message. In a program the reply goes to a parser, a database write, or the next stage of a pipeline, so it has to arrive in the shape the code expects. Google Dorking is the nearest parallel: a search query composed from operators such as site: and filetype: so the engine returns exactly the pages wanted, not a page of loosely related hits. In both cases the query is engineered for the result, not for the conversation.

## Page 10

Four things change when a prompt runs from code.

Output format: code has to parse the reply, and JSON is the common choice because json.loads turns it into Python dicts and lists in one step.

Consistency and error checking: the model is not deterministic, so the same prompt can return a reply wrapped in a Markdown code fence, cut off at the token limit, or carrying a label outside the allowed set. The calling code checks that the reply parses and that each field holds an expected value, and decides what to do when it does not. Worksheet 10.1 writes a helper that strips a code fence before parsing.

System and user messages: the prompt splits into a system message, which sets the model's role and rules and goes with every call, and a user message, which carries the input for this call.

Security: the user message often carries text from outside the program, such as a log line, a ticket, or a shell command, and the model reads instructions embedded in that text the same way it reads yours. That is prompt injection. The data also leaves your network for the vendor's API, which matters when it is sensitive.

## Page 11

The openai package wraps the OpenAI HTTP API. The client picks up OPENAI_API_KEY from the environment, so the api_key argument is optional. The call goes through client.responses.create with three arguments: model, the model to run; instructions, the system message; and input, the user message. The reply text is at response.output_text.

One-shot use is a single call with a single input, as here. Chat-like use passes the earlier turns of the conversation along with the new one.

## Page 12

The anthropic package does the same job for Anthropic's models. The client reads ANTHROPIC_API_KEY from the environment when api_key is omitted. client.messages.create takes model, max_tokens, and messages, a list of turns each with a role and content. max_tokens is required in this API and caps the length of the reply.

The reply object's content attribute is a list of content blocks rather than a string, so printing message.content prints the list. The text of a plain reply is at message.content[0].text, the form the worksheets use. A system message is not a turn in the messages list; it goes in the separate system argument of the same call.

## Page 13

An image goes into the same call as a content block alongside the text. The request body is JSON, which carries text only, so the file's bytes are base64-encoded first: standard_b64encode returns bytes, and decode turns them into a string. The user turn's content is then a list of two blocks, an image block whose source names the encoding, the media type, and the data, and a text block holding the question. The reply comes back as before, with the answer at resp.content[0].text.

Worksheet 10.1 uses this pattern to pull a license plate, make, model, and other fields out of vehicle photos as a JSON record.

Inlining the bytes suits a one-off script. Each call re-sends the whole file, so for a file used across many calls, or in a production service, Anthropic's Files API is the more robust route: upload the file once, get an id back, and reference the id in each message instead of the bytes.

## Page 14

The transformers package from Hugging Face runs a model on your own hardware instead of calling a hosted API. The calling pattern resembles the vendor SDKs, but the model's weights are downloaded from the Hugging Face hub and run locally, so nothing leaves your machine and the machine needs the memory and, for larger models, the GPU to hold them.

The caution about downloads is about code execution. Weights distributed as PyTorch pickle files run whatever code the file contains when they are loaded. Prefer models published in the safetensors format, which stores tensor data only, and load only models from publishers you trust.

## Page 15

An abstraction layer puts one calling interface in front of many vendors' APIs, so the vendor and model become a configuration value rather than a shape the code is built around. The two named on the slide take different forms. LiteLLM: a Python library that exposes one completion function and translates each call into the target vendor's request format, with the model chosen by a name string. OpenRouter: a hosted service that exposes one OpenAI-style endpoint and forwards each request to the vendor behind the named model, under a single key and a single bill.

The openai and anthropic packages on the earlier slides differ in method names, argument names, and reply structure, so moving a program from one to the other means rewriting every call site. Behind an abstraction layer a model swap is a changed string, which is what the third bullet means by swapping models without rearchitecting the code. The worksheets use the same idea without either product: the setup cell builds one OpenAI-style client and points it at Anthropic's compatible endpoint when run locally and at the course's serving endpoint on Databricks, and the calling code is identical in both cases.

The cost is the lowest common denominator. A feature one vendor offers and the layer has not mapped, such as a new content block type or a request parameter, is unreachable until the layer adds it, and errors arrive translated, one step removed from the vendor's own message.

## Page 16

This part covers the request parameters that shape a reply: temperature, top_p, max tokens, the two repetition penalties, and stop sequences.

## Page 17

At each step the model produces a probability for every token in its vocabulary and samples the next token from that distribution. Temperature rescales the distribution before sampling. Low values sharpen it toward the most likely token, and at 0 the model picks the top token at each step, so repeated runs of the same prompt come back near-identical. Anthropic's documentation states that even at 0 the output is not fully deterministic, so code that depends on an exact repeat still has to check the reply. High values flatten the distribution, so less likely tokens are chosen more often and the wording varies more between runs. Anthropic accepts values from 0 to 1; OpenAI accepts 0 to 2.

top_p, or nucleus sampling, limits which tokens are eligible at all. The tokens are sorted by probability and the smallest set whose probabilities add up to p is kept; the next token is sampled from that set alone. At 1 every token stays eligible. Anthropic's documentation advises changing temperature or top_p, and not both.

## Page 18

max_tokens caps the length of the reply. When the model reaches the cap it stops mid-sentence, and the response reports stop_reason as max_tokens. For a reply that is supposed to be JSON, a cutoff means an unclosed bracket and a parse failure, which is why Worksheet 10.2 sets a large cap for its batch classification and prints a warning when the stop reason shows the cap was hit.

The two penalties are OpenAI parameters; the Anthropic Messages API does not offer them. Frequency penalty lowers a token's probability in proportion to how many times it has already appeared in the text so far, which discourages repeated phrases. Presence penalty applies one flat reduction to any token that has appeared at least once, which pushes the model toward tokens, and so topics, it has not used yet. Both range from -2.0 to 2.0 in OpenAI's API; the range printed here, 0.0 to 2.0, omits the negative half, where values encourage repetition.

Stop sequences are strings that end generation as soon as the model emits one of them. They hold a reply to one item when the format has a natural terminator, such as a closing tag.

## Page 19

The system message sets how the model behaves: its role, its rules, and the output format. The user message carries the input for one call. The Anthropic Messages API keeps no state between calls, so every request has to carry the system message again, along with any earlier turns the model should see. The system message is written once with the program; the user message changes with each input.

## Page 20

This part covers what makes a prompt fail and seven practices that make it reliable.

## Page 21

Four habits produce unreliable replies.

Vagueness: the model fills every unstated choice with its own, and those choices vary from call to call.

Unspecified output format: the reply arrives in whatever shape the model picks, often prose wrapped around the data, and parsing fails.

No examples: the model guesses where the boundary between categories lies and how each label is spelled, and guesses differently on different inputs.

Facts not on the record: the model answers from its training data, which can be wrong and does not cover your environment. Anything the answer depends on has to be in the prompt.

## Page 22

A prompt opens by telling the model what it is and what the following text is. "Here is a sample of trouble tickets:" labels the data that follows so the model reads it as tickets. "You are a helpful customer service bot" and the longer cybersecurity analyst line set a role, which shapes the vocabulary, the scope, and the tone of the reply.

In the API these opening lines belong in the system message, where they apply to every call without being repeated in each user message.

## Page 23

The model performs best when everything the answer depends on is in the prompt. Summarizing a document and generating output from a given input are the strong use cases because the answer needs nothing beyond the supplied text. What the model recalls from training can be wrong, and a wrong recollection reads as fluently as a right one. Facts not on record are whatever the prompt does not state: your hostnames, your ticket categories, your policies, and events after the model's training cutoff. Relative dates are the everyday case: the model has no clock, so "yesterday" or "last week" in a prompt resolves to nothing unless the prompt also states today's date.

For a program this means the data itself goes into the prompt as text. Worksheet 10.1 turns a table of CPU readings into one line per row before asking the model to find the anomalies in it.

## Page 24

Telling the model the shape of the output is the most direct way to get the same shape every time. "Output the results as a python object" fixes the structure. "Be concise" fixes the length. "Be sure to include docstrings in all functions" fixes what the content must contain.

The worksheets' prompts add "respond with only raw JSON, no markdown, no commentary" because a model asked for JSON can wrap it in a Markdown code fence, and the fence breaks json.loads unless the code strips it first.

## Page 25

Affirmative instructions work better than prohibitions, for two reasons.

"Only include categories C, D" is a closed list: the model has two names to choose from and nothing else is eligible. "Do not include categories A and B" leaves every category other than A and B open, so E and F remain eligible.

A prohibition also puts the unwanted names into the context the model predicts from. Naming A and B in the instruction makes those tokens more available to the model, which works against the intent of the instruction.

## Page 26

The prompt "Generate an image of a room but do not include an elephant" produced two rooms, each with an elephant in it. The prohibition put the word elephant into the prompt the model conditioned on, and the presence of the word outweighed the negation.

The affirmative version describes the room wanted, for example a living room with a sofa, two chairs, and a window, and leaves the elephant unmentioned.

## Page 27

The direct version is an imperative that names the three categories, gives the fallback for uncertain cases, and closes the set with "These are the only possible categories." The polite version buries the same request in a narrative, says "either" without closing the set, and spends its words on courtesy. Courtesy words are tokens the model has to process and pay for, and they constrain nothing about the output.

The direct version also has the three parts a programmatic classification prompt needs: a directive, a closed set of labels, and an instruction for the case that fits none of them. Worksheet 10.2 asks you to write a prompt with the same three parts for a list of shell commands.

## Page 28

Examples fix what an instruction leaves open: the exact spelling and case of each label, where the boundary between labels falls, and the layout of a reply. In the example the ##### lines separate one worked case from the next, ls is labeled safe and rm -rf * is labeled risky, and the model continues the pattern for the command it is given.

In classification this is called few shot learning, where a shot is one labeled example in the prompt. The term is borrowed from machine learning, where it means training on a handful of labeled cases.

## Page 29

A hallucination is a fluent reply with nothing behind it, and a model produces one when the input fits no category it was given, because the generation process still has to emit something. "If you are unable to categorize the response, output unknown" gives the model an output that is legitimate for that case, and the calling code can route unknown to a person.

Telling the model not to hallucinate does nothing because a hallucination is not a decision the model makes and can be told to skip. The same next-token process produces a right answer and a wrong one, and the model has no signal that marks the difference. An escape label works because it makes the truthful reply one of the allowed ones. Worksheet 10.1 applies the same idea to extraction by telling the model to use null for any field it cannot read from the photo.

## Page 30

This part covers the components of a prompt, the order they go in, and what a role, a set of examples, and an output specification each change in the reply.

## Page 31

Five components make up a prompt, as laid out in Learn Prompting's guide to prompt structure.

Directive: the instruction itself, stated so that only one reading is possible.

Examples: worked cases that show the model what a correct reply looks like.

Role or persona: who the model is for this task, which sets the vocabulary and tone of the reply.

Output formatting: the structure, length, and content requirements of the reply.

Additional information: whatever the task needs that the model would not otherwise have, such as the data to work on, definitions, or constraints.

## Page 32

The model predicts each token from everything before it, so the order of the components sets what context is in place when each part is read. Learn Prompting's recommended order is role, directive, additional information, output formatting, examples. The role frames everything after it. The directive comes while the context is still short. The information and the format follow, and the examples sit last, directly before the input the model has to continue, so the pattern to imitate is adjacent to the place where imitation starts.

Position also affects recall. Liu and colleagues' 2023 study Lost in the Middle found that models retrieve information placed at the start or the end of a long context more reliably than information placed in the middle.

## Page 33

The system message sets the model to be a rude customer service bot for a low cost airline, told to refuse every demand, insult the customer, and add fees. The user asks for meal vouchers after an eight hour delay. The reply mocks the customer, refuses the vouchers, and invents a fifteen dollar "Delayed Whiner Assistance Fee." The model is GPT 4.1 at temperature 1.

The model followed the role it was given, including the instruction to add fees, and supplied a fee name on its own. A system message is a policy the model executes, and it executes an abusive policy as readily as a helpful one.

## Page 34

The user message is the same request for meal vouchers, and the model and temperature are unchanged. Only the system message differs: a helpful customer service bot, told to be understanding, permitted to offer meal and hotel vouchers, and told that the airline gives credit for future flights rather than refunds. The reply apologizes, offers meal vouchers, and asks for the booking reference before issuing them.

The reply tracks the permissions in the system message. It offers exactly what the policy allows and nothing the policy forbids, which is the behavior a deployed bot needs. Everything that distinguishes this exchange from the previous one is in the system message.

## Page 35

Zero shot prompting is an instruction with no examples. The model works from the instruction and its training alone. Few shot prompting adds labeled examples to the prompt. The model's weights do not change in either case. In the few shot case the model infers the pattern from the examples at the time of the call, and a handful of examples can move the results from unusable to usable for a classification task.

## Page 36

This prompt has every component in the recommended order. The role is an automated security bot. The directive is to assess whether a command is risky. The output format is a closed set of four labels, very risky, moderately risky, not risky, and unknown, with unknown as the escape label. A ### line separates the instructions from four examples, one command per line with its label.

Three of the four labels have an example; moderately risky has none, so the model has to place that label between the two it has seen from the name alone. The examples are also inconsistent in small ways: the first has a colon between the command and its label and the others do not, and find's option is spelled --name where the real option is -name. The model tolerates both.

## Page 37

With the prompt from the previous page as the system message, the user sends passwd and the model replies moderately risky. passwd changes an account's password, and the label had no example in the prompt, so the model placed it between not risky and very risky from the label's name and the examples on either side.

The reply is a single label and nothing else, which is what "You must only output either" asked for. Code can compare the reply against the four allowed strings directly.

## Page 38

ls -lAh gets not risky. The flags differ from the ls -l in the examples: A adds hidden entries and h prints sizes in readable units. The model matched the command to the example by the command name and the fact that a listing reads and changes nothing.

## Page 39

The user message is a request to describe neutron and proton interactions in a nuclear reaction. It is not a command, and the model replies unknown. Without the escape label the model would have had to choose between answering the physics question and forcing a risk label onto text that has none. The constraint held: an off-task input received the label reserved for inputs the prompt does not cover, and the code consuming the reply gets a value it can handle.

## Page 40

sudo -rf / gets very risky. The string is not a valid command, because sudo has no -rf option, and the command it resembles is sudo rm -rf /, which deletes the filesystem as root. The model does not parse or run the input. It classifies the text, and this text carries the -rf / of the rm example plus a request for root privileges, so the top label is the pattern match. That is the strength and the limit of the technique in one reply: it catches intent from surface form, and it has no knowledge of what the shell would do with the string.

## Page 41

A program can only use a reply it can parse, so the prompt has to pin the format down. Even then the model is not deterministic, and any call can return a malformed reply or an invented value. The prompt handles the invented-value case with an escape instruction; the code handles the malformed case with error handling around the parse.

Charles prefers JSON because json.loads turns it into Python objects directly. A JSON reply is still text the model generated, so the parse can fail: the model can add prose before the object, wrap it in a code fence, or truncate at max_tokens. Catch the parse error and decide whether to retry the call, skip the item, or stop. Both Anthropic and OpenAI also offer ways to constrain a reply to a JSON schema, through structured output settings or through tool definitions, which removes most of the format risk.

## Page 42

The prompt asks for JSON and shows the JSON it wants. The numbered rules restrict the categories to a fixed list, route uncertain cases to unknown, name the output format, and ask for a confidence score with two decimal places. The example between the XML tags is the format specification: an object with a product field and a categories list, each entry a name and a confidence. Anthropic's prompting guidance recommends XML tags as delimiters because the model treats the tagged span as a unit and the tag names tell it what the span is.

The example contradicts rule four: it prints confidences with three decimal places, 0.965 and 0.823, where the rule asks for two. The model receives two conflicting signals and either can win on a given call. Make the example obey every rule it illustrates.

## Page 43

Questions on the SDKs, the request parameters, and the seven prompting practices, before the lab.

## Page 44

Worksheet 10.1 has two parts, and both end in a JSON reply parsed into Python. In the first, you format a table of CPU readings as one text line per row, build a prompt from a sample of about fifty normal rows and the first forty unknown rows, ask for the anomalous rows as a JSON list, call the model, and parse the reply with a helper that strips an optional code fence before json.loads. In the second, you base64-encode a vehicle photo, send it with a prompt that lists the fields to extract and asks for raw JSON only, and parse the result into a dict; then you add a field of your own to the prompt and confirm it appears. The helper you write in the first part is reused in the second.

## Page 45

This part covers techniques built for programs and agents: chain of thought, meta prompting, and classification and data analysis with a generative model.

## Page 46

Three techniques follow: chain of thought, which has the model write out intermediate steps; meta prompting and prompt chaining, in which one prompt produces the next; and using a generative model for data analysis and classification.

## Page 47

These techniques are for programs and for AI agents, an agent being a program that calls the model repeatedly and feeds each reply, along with the results of any actions it requested, back into the next call. They are described under several names, and the differences between the named variants are small. Recognize the mechanism and the name matters less.

## Page 48

Chain of thought, abbreviated CoT, is a prompting technique that has the model write out intermediate steps before its answer. It was introduced by Wei and colleagues at Google in 2022, and Learn Prompting's page on it is the source for this section. The model generates the answer token by token, conditioned on everything already written, so when the steps are written out the answer is computed from them; without the steps the answer has to be produced in one jump from the question.

CoT raises performance on multi-step tasks without fine tuning, which is retraining the model's weights on additional data. It differs from ordinary few shot prompting in what the examples contain: a few shot example pairs an input with its answer, while a CoT example pairs an input with the reasoning that leads to its answer.

## Page 49

A CoT exemplar is a triple: the question, the worked reasoning, and the answer. When the prompt holds a few of these, the model reproduces the shape for the new question and writes reasoning before answering. The accuracy gain comes from the written steps, which each later token conditions on, so errors that a single-jump answer would make become visible steps that the model can build on or correct.

## Page 50

CoT works through two moves. Decomposition: the prompt leads the model to split a complex question into sub-questions, each of which it can answer in a single step, so no step requires more than the model can do at once. Exemplars: worked examples show what a step looks like and how fine the steps should be, so the model knows the granularity to reproduce.

## Page 51

The written steps are generated text, produced by the same next-token process as everything else the model emits. They are not a trace of an internal computation. Turpin and colleagues showed in 2023 that a model's stated reasoning can omit the factors that determined its answer, so a chain that reads well is not evidence that the answer was reached that way.

How far models "think" is an open debate, and the effectiveness of CoT varies with the task and the model. The practical reading is that the steps are output. Check them like any other output, and treat a wrong step as grounds to distrust the conclusion.

## Page 52

The slide is a few shot chain of thought exemplar in a security setting. The worked case takes an alert, an obfuscated PowerShell script on a workstation, and lays out eight triage steps, from reading the intent of obfuscated PowerShell, through retrieving and de-obfuscating the script, checking the parent process, matching the behavior to MITRE ATT&CK technique T1059.001, isolating the host, hunting for persistence, sweeping for the same script elsewhere, and capturing forensics, ending in a stated conclusion. MITRE ATT&CK is a public catalog of attacker techniques, and T1059.001 is its identifier for command execution through PowerShell.

The steps are the point. They fix the grain of the reasoning the model should reproduce, so that when the second scenario, unexpected outbound traffic to a Tor exit node from a development server, is handed to the model with the same "Think step by step" cue and no answer, the model continues the demonstrated pattern and writes its own eight-step chain before concluding.

## Page 53

Zero shot chain of thought adds a trigger phrase and no worked example. The prompt states a distributed-query-engine problem, whether to push an operation down to the source system or split the query and run the parts in parallel, and ends with "Let's think this through." Kojima and colleagues showed in 2022 that appending a phrase of this kind, their version was "Let's think step by step," makes a model produce intermediate steps on its own, which raises accuracy on reasoning tasks without any exemplars in the prompt.

This is the contrast with the previous slide. The few shot version supplies worked chains for the model to imitate. The zero shot version supplies only the instruction to reason, and the model generates the steps unaided. The trigger costs almost nothing to add, which is why it is often the first thing to try on a task the model gets wrong in one jump.

## Page 54

An LLM can pull structured artifacts out of unstructured text, which is the task called entity recognition or extraction. The case for it over a regular expression is variability: a regular expression matches a fixed pattern, so it works for something with rigid form and fails when the same information appears in prose, in different orders, or in wordings the pattern did not anticipate. The model reads the text for meaning and returns the artifacts regardless of how they are phrased. Worksheet 10.1 does this with an image rather than text, extracting a vehicle's plate, make, and model into a JSON record, but the principle is the same: describe the fields, ask for structured output, and parse the reply.

## Page 55

This part covers meta prompting: using the model to write the prompts that drive a longer task.

## Page 56

Meta prompting is using one prompt to generate further prompts. It suits a task too large for a single call, one that takes many steps and produces more output than one reply can hold. The examples given are working through a collection of files or through sequential data, where each item needs its own prompt and the number of items is not known when the code is written. Rather than write every prompt by hand, one prompt produces the next.

## Page 57

The diagram traces a chain where one model's output becomes another step's input. An initial command, write a children's book, goes to GPT-4 and yields story text. A second command, create image generation prompts, goes to GPT-4 and yields image prompts. Those prompts go to an image model, MidJourney, which returns images. The story text and the images combine into the final output, an illustrated book.

The point is the link between stages: the image prompts are not written by a person, they are generated by the first model and consumed by the second. Output at one step is input at the next, and separate chains merge into one product. This is meta prompting seen as a pipeline, and it is also called prompt chaining.

## Page 58

The system message makes the model produce the next instruction rather than answer directly. It casts the model as a penetration-testing assistant whose input is the output of the previous command and whose job is to write the prompt for the next step, closing with "Only output the prompt." The reply is therefore not an action or an answer but a prompt, ready to be sent as the next call.

That is the mechanism of meta prompting in one message. Each command's result feeds back in, the model emits the following prompt, and a program can run the loop, using the model to plan the sequence one step at a time. "Only output the prompt" keeps the reply clean enough to pass straight to the next call without editing.

## Page 59

This part covers using a generative model to classify data, and the ways it differs from a purpose-built classifier.

## Page 60

A generative model can classify, filling the role a trained classifier usually fills. The reasons to reach for it are limited data and text-based inputs. A conventional classifier has to be trained on many labeled examples before it works. A generative model can classify from an instruction and a few examples in the prompt, with no training run. That makes it a fit when labeled data is scarce or when the input is language, which conventional classifiers handle only after heavy feature engineering.

## Page 61

Four properties separate a generative classifier from a trained one. Not deterministic: the same input can return different labels on different calls, so a fixed test set does not pin the behavior down the way it does for a conventional model. Not auditable: there is no set of learned weights or decision rule to inspect, so you cannot explain why a label was chosen. Slower and more compute-heavy: each classification is a full model generation, which costs more time and more hardware than scoring one row through a small trained model. No probabilities: a trained classifier reports a score for each class, and a generative model returns a label with no calibrated probability behind it.

## Page 62

The trade the previous slide describes is worth making in specific conditions. Little training data, or subjective categories: when there is not enough labeled data to train a classifier, or when the boundary between classes is a judgment rather than a rule, the generative model's ability to work from a description and a few examples is an advantage. Less human effort: writing a prompt is cheaper than labeling a training set and training a model. The slide also notes scoring: a generative model can put a number on an artifact, but that number is arbitrary. It is not anchored to a measured quantity, so it orders items loosely and should not be read as a precise value. Worksheet 10.2 makes the same point about the confidence field its classifier returns.

## Page 63

The prompt is the product-categorization example again, now as a classification task, with a fifth rule added: sort the categories by confidence, highest first. The other four rules are unchanged, restricting the output to a fixed category list, routing uncertain products to unknown, naming JSON as the format, and asking for a two-decimal confidence, with the format shown by an example inside XML tags.

The same inconsistency remains. Rule four asks for two decimal places, and the example prints three, 0.965 and 0.823. A prompt that shows one thing and says another gives the model conflicting instructions. Correct the example to match the rule.

## Page 64

The aspiration behind LLM-driven analysis is to ask a question of your data in plain language and get the answer back, with no query and no plotting code written by hand. The heading names it the holy grail of data analytics.

## Page 65

The follow-up question flags that the ideal has catches. The slides that come next name them.

## Page 66

There are two ways to put an LLM between you and your data. Generate intermediate code: give the model a description of your data and have it write code, such as SQL, which you then run against the data yourself. Analyze directly: hand the data to the model and have it answer from the data itself. The difference decides what leaves your machine and where the answer comes from. In the first, only a description goes to the model and the computation runs on your data locally; in the second, the data goes to the model and the model produces the result.

## Page 67

Sending data to a hosted model for analysis is a security and privacy exposure. In the direct approach the data itself leaves your network for the vendor's API, which matters when it is regulated, personal, or sensitive. In the code-generating approach the data stays local, but the model writes code that then runs against it, and running model-written code carries its own risk: the generated query can read or change more than intended, so it needs review before execution rather than blind running.

## Page 68

An LLM's analytic answer is a black box: it arrives without a derivation you can check. A conventional analysis leaves a query or a script that shows exactly how the number was produced. A model that answers from the data directly shows only the answer, and because the model is not deterministic and exposes no probabilities, there is nothing to audit and no way to confirm the figure other than recomputing it another way. A wrong number reads as confidently as a right one.

## Page 69

The model reads the data as tokens in the prompt, and the prompt has a maximum size, the context window, so a dataset past that size cannot be sent whole. The direct approach then forces a workaround, sampling or aggregating the data down to what fits, which changes what the model sees. This is where the code-generating approach has the edge: only a description of the data goes into the prompt, while the generated code runs over the full dataset locally, so the data's size is bounded by your machine rather than by the context window.

## Page 70

PandasAI wraps a pandas DataFrame so it can be queried in natural language, generating and running pandas code behind each question. The setup shown imports pandas and PandasAI, creates an OpenAI language-model client from an API key, passes it to PandasAI, loads a DataFrame from dailybots.csv, a table of daily botnet-infection counts by family, and converts the date column to datetime so questions about days and ranges can use it. The library drives whichever model it is given; here that is OpenAI rather than the Anthropic models on the earlier slides.

This is the code-generating approach from the two-approaches slide, packaged as a library: the model sees the frame's column names and a few sample rows, not the full data, and writes code that runs locally over the whole frame. The API shown, constructing PandasAI with the model and later calling the object with a question, is the library's earlier interface.

## Page 71

Asking the DataFrame "What botfams had the most infections?" returns the top families by total infection count: ConfickerAB with 321,373, then Ramnit, PushDo, Sality, and Bedep. The values are exact because PandasAI does not have the model read the numbers and total them. It has the model translate the question into pandas code, groups the botfam column and sums, then runs that code against the DataFrame and returns the computed result. The exactness comes from executed code, not from the model, which is the reason a generated-code path is trustworthy for arithmetic where a direct read would not be.

## Page 72

The question "Make a line chart of infections per day, broken down by botfam" produces a matplotlib line chart, one line per family across June to August 2016. The same mechanism is at work as on the previous slide: the model turns the request into plotting code and PandasAI runs it. The chart shows ConfickerAB far above the rest, its line running between about 3,000 and 5,600 infections a day, while every other family stays under about 2,000.

## Page 73

PandasAI exposes named helpers for routine data-preparation steps in addition to free-form questions: clean_data for tidying a frame, impute_missing_values for filling gaps, generate_features for deriving new columns, and plot_histogram for a quick distribution of one column. Each wraps the same generate-and-run pattern behind a fixed method name. These method names belong to the library version shown; later releases of PandasAI changed the interface.

## Page 74

The slide marks a live demonstration, not reproduced in the deck, of SQL query generation in Apache Drill, the SQL engine introduced in Module 0: the model is given a table's schema and a question in plain language and writes the query that answers it, and the engine runs the query. This is the code-generating approach from the two-approaches slide with SQL as the generated code instead of pandas. The prompt carries the schema and the question, not the rows, so the data stays where it is and its size is bounded by the engine rather than the context window. The query is text you can read before it runs, which answers the black-box objection, and the engine computes the result, so the numbers are exact. What the model can still get wrong is the query itself, a join on the wrong key or a filter that reads the question differently than you meant, which is why the query is reviewed before it runs.

## Page 75

Questions on the advanced techniques, before the second lab.

## Page 76

Worksheet 10.2 builds a text classifier from a prompt. You load a list of shell commands, then send the whole list in one batch call rather than one call per command, trading the risk that a single malformed reply loses the batch for a large saving in cost and time. The prompt asks for a JSON array, one object per command in order, each carrying the command, an is_risky flag, a confidence from zero to one, a risk category from a fixed set, and a one-sentence reason. You call the model with a large token cap so a long reply is not cut off mid-object, parse the array with the fence-stripping helper, and load it into a DataFrame to show the risky commands, most confident first. The worksheet closes on the confidence field: it is the model's own guess at its certainty, not a calibrated probability, so it is fit for sorting what to review first and unfit as a gate for any automated action.
