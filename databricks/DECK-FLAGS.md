# Deck flags from the notes pass

Things the note writers found on the slides themselves while writing the read-alone
notes. The notes teach the correct reading; the slide images are untouched. For whoever
edits the Keynote sources. Page numbers are PDF pages.

## 05-unsupervised-learning
- p46: arrow labeled "Best number of clusters" points at K=6, the silhouette minimum; by the deck's own definition (p44) the best value is the maximum, K=2.
- p32: code reads `labels_f`, meant `labels_`.
- p47: figure title says MiniBatchKMeans, code passes `KMeans()`; `poof()` is `show()` in current Yellowbrick.
- p51: "dimensionality reduction loses no information" is stated unconditionally; the note scopes it.
- p49: worksheet slide; Worksheet 5.1 also covers agglomerative clustering and DBSCAN, which the deck does not.

## 08-deep-learning
- p11: perceptron attributed to "Minksy & Papert, 1969" and "McCulloh-Pitts"; Rosenblatt 1958 introduced it, Minsky and Papert 1969 analyzed its limits. Two misspellings.
- p12: weights "(1,-0,75,0.25)" for (1, -0.75, 0.25).
- p22: "gets their faster". p49: "utilize for gates" for "four gates".
- p42: library list (Theano, Torch, Lasagne, Caffe, Pylearn2, Chainer) is dated; the labs use Keras and PyTorch.
- p41, p50: notes describe the current worksheets; re-check if the notebooks change.

## 12-model-context-protocol
- p3: "we will built".
- p23: code string literal wraps mid-string on the slide.
- p20: bare pointer to https://ai.gtkcyber.com/mcp-lab with no description in the deck (UNRESOLVED note).
- Worksheet 12.1 markdown says "Module 12" and "Module 13" where it means Module 11 (notebook, not deck).

## 02-data-visualization
- p14: URL plus one frame of an animated port-by-country chart, axes unreadable; talking point not inferable (UNRESOLVED note).
- p6, p7: joke slides (pie photo, Pac-Man pie); short descriptive notes written.
- p4: radial bar chart with URL only; note explains the arc-length distortion from the geometry.
- p19, p20: bar and pie charts drawn from different data than the Series on p18 (3,5,7,3,4,8 vs 3,4,6,7,5,8,2); notes avoid quoting their values.
- p20: pie renders as an ellipse; current Matplotlib forces an equal aspect.
- p26: `distplot` is deprecated since Seaborn 0.11; note gives `histplot(kde=True)`.
- p37: link is to Matplotlib 3.1.0 docs; note points at the stable URL. p50: `bokeh_chart` moved out of Streamlit core.

## 03-feature-engineering
- p16: "the are often written as X".
- p22: "State of Authority (SOA)" for Start of Authority; "BlueGtaor" garbled registrar name.
- p27: "First seen with the Conficker worm" is contestable (Kraken and Srizbi used DGAs earlier in 2008); note says "made widely known by".
- p31: CountVectorizer example with a dotted vocabulary ('.com', '.de', '.uk') returns all zeros under the default token pattern, which strips the dot (documented behavior, not executed).
- p32: "tild/zoom" for tilt.
- p38: outdated Feature-engine import; `feature_engine.encoding.OneHotEncoder` is current.
- p41: second sentence truncated ("...you will").
- p55: caption "Selects all features above a given threshold" misdescribes SelectPercentile, which keeps a percentile by rank.
- p61: stray bullet character under the code block.

## 06-anomaly-detection
- p24: "167 outside 1 deviation" matches a one-tail count under the shown normal fit (about 159 of 1000); two-sided would be about 317. The 44 beyond 2 deviations is consistent.
- p27: title "Mean Absolution Deviation"; pseudocode omits the absolute value; `Series.mad()` was removed in pandas 2.0.
- p60: `behavior='new'` fails on every scikit-learn version (spelled `behaviour`, removed in 0.24).
- p66: MAC address shown with five hex pairs; a MAC has six.
- p67: `tokenize_data(d)` substitutes on `mac`, not `d`; `template_token` never defined; pandas and `good_macs` unused.
- p69: the homoglyph is the Cyrillic letter er, not a "Russian Rho" (rho is Greek).
- p15: "algorithms include" for "including". p65: Jaro "from each file" for "each string".

## 10-prompt-engineering
- p4: says an OpenAI API key is needed; the module and both worksheets use Anthropic (and, on Databricks, the workspace endpoint).
- p41, p62: JSON rule asks for confidence to two decimal places; the worked example prints three (0.965, 0.823).
- p17: frequency and presence penalty range shown as 0.0 to 2.0; OpenAI's range is -2.0 to 2.0, and the Anthropic Messages API has neither parameter.
- p9, p56: "Programatically". p28: "doesn't'".

## 00-introduction
- p31: photo of SPAM varieties with no caption; point not stated anywhere in the deck (UNRESOLVED note).
- p7: title says "Aug 2-4, 2025"; the course is Aug 2-4, 2026 (p6 says 2026).
- p4: "Exploratory Data Analysis" listed under both Day 1 and Day 2.
- p19: "Aritificial". p34: "a observation's". p78: "the the". p14: trailing empty bullet.
- p38: "src and dat bytes" for dst bytes; "bro" is now Zeek.
- p79, p81: terminal examples from a prior year (env "gtk-bh-ai", directory "ads_blackhat_2025").
- p83: screenshot's worksheet numbering (7.1 CNN, 8.1 Attacking AI) predates the current README.
- p2: extracted text carries an email and Slack invitation not visible in the render (hidden behind the Miniconda banner).

## 14-red-teaming-ai
- p15, p16: "Can you spot the prompt injection?" image slides (neon banner, "AI MUSIC MALWARE" thumbnail); the hidden injection is not inferable (UNRESOLVED notes).
- p42: "Prompt-Injection Dogo" for Dojo; the lab is ai_labs/prompt_injection_lab/workbench.py (Streamlit, OpenAI or Ollama). The other three ai_labs apps are not referenced by any deck.
- p51: "consulting form McKinsey". p60: injection text starts "ops," (dropped the O).
- p21, p66, p74: absolute titles ("always", "never"); notes teach the scoped reading.

## 13-ai-agents
- p6: "Agents will loop ... until it runs out" (subject/verb mismatch); "a stopping criteria" should be "criterion".
- p9, p10: "Level 2 the output ..." and "Level 3 the number ..." lack a colon or "At" after the level name.
- p11: figure is reproduced from the Yao et al. 2022 ReAct paper with no attribution on the slide.
- p24: "Microsoft AutoGen (AG2)" conflates Microsoft's AutoGen with AG2, the community fork.
- p30: OWASP numbers mix editions: "LLM02 Insecure Output Handling" is the 2023 list; in the 2025 list it is LLM05 Improper Output Handling, while LLM06 and LLM08 are 2025 numbers. The note explains the renumbering.
- p37, p38, p39, p49: describe a phishing-email lab, but the code and prose on p41, p42, p43, p45, p47, p48, p53, p55, p56, p57, p64, p83, p85 use a suspicious-login / account-takeover example (LoginState, classify_login, ATO_TOOLS, check_geo_velocity, identity_analyst) that matches none of the five notebooks. The notes follow the notebooks (phishing emails) and say so on the affected pages; if the source is reconciled to one domain, trim those sentences on p41, p55, p64, p83 and p85.
- p54 says the three tools are "already implemented in utils/mock_tools.py", but p55 names check_geo_velocity, check_device_reputation, check_login_velocity; that file contains check_url_reputation, check_sender_reputation, check_email_authentication.
- p42: "State Graphs are defined as TypedDicts" is imprecise; the state schema is the TypedDict and the StateGraph is built from it.
- p49 and p50: two consecutive lab-prompt slides for the same lab; p49 uses the old title "Phishing Lab Part 1".
- p53: says Lab 1's state had "login, classification, and confidence" fields; Lab 1 has no confidence field and uses email fields.
- p66: raw markdown asterisks are visible ("**routing function**", "**mapping dict**", "*sets*").
- p80: "react agents" should be "ReAct agents".
- p82: names create_react_agent with a prompt parameter; Worksheet 13.5 uses create_agent from langchain.agents with system_prompt.
- Unsure pages p36, p51, p63 ruled own slides (section dividers).

## 11-ai-components
- p11: the cloth photograph overlaps the title; "Rescue!" is clipped.
- p18: says Chroma is used for the labs; Worksheet 11.1 and ai_examples/rag_demo.py use LangChain's InMemoryVectorStore.
- p19: `import chroma` should be `import chromadb`.
- p22: the template is an f-string with placeholders meant to be filled later; the f prefix should go.
- p30: the figure overlaps and cuts off the bullet text; "contraction of sequences" should be "construction".
- p33: `os` is used without being imported; ChatOpenAI/gpt-3.5-turbo and `langchain.schema` are dated, and the repository's ascii_art_generator.py uses ChatAnthropic and langchain_core.messages.
- p35: "one token at a a time" has a doubled "a".
- p36: `SystemMessageTemplate` should be `SystemMessagePromptTemplate`; `from_template(template)` should pass `system_template`; the invoke key `{ai_name: "Jill"}` needs quotes; the comment names risky_sql_queries.py but the file is risky_sql_query_generator.py.
- p42: ChatOpenAI import; the repository's output_parsers.ipynb uses ChatAnthropic.
- p44: the chain uses `json_output_formatter` but the parser was created as `json_output_parser`.
- p49: `get_relevant_documents` is deprecated (retriever.invoke); ChatOpenAI gpt-4o while the repository example uses Claude.
- p51: `llm.predict` is deprecated; the listing is a loop body with the `while` line omitted and inconsistent indentation.
- p76: `init_chat_model(..., model_provider="openai")`; the repository uses ChatAnthropic.
- p77: "a client have" should be "a client has".
- p81: imports `Tool` from langchain.tools but uses the `@tool` decorator, which is not imported; the function has no docstring, which the decorator requires.
- p82: `tools=[phone_tool]` is undefined on the slide; `my_tool` is rebound to the Tool wrapper, discarding the decorated tool; `initialize_agent`/`AgentType` are deprecated; ChatOpenAI gpt-4 while tool_example.py uses ChatAnthropic and create_react_agent.
- p83: `agent.run` is deprecated.
- p85: title says "Lab 11.2: Tool Usage"; the notebook is "Worksheet 11.2: Building & Using an Agent Tool".
- Unsure page p11 ruled own slide.
- Port note (not a slide defect): the notes for the code slides say the worksheets target Claude through langchain_anthropic, which is the unported notebooks; the Databricks worksheets call the course endpoint through the seam cell. Same in decks 10, 12, 13, 14; a provider pass over those notes is pending.

## 07-attacking-machine-learning-models
- p5: Model Inversion row defines it as recovering trained weights and Membership Inference as recovering training data; in the literature inversion reconstructs class inputs (which p19 to p21 demonstrate) and membership inference tests whether a record was in the training set.
- p7: paper title shown with no citation (Nguyen, Yosinski and Clune, CVPR 2015).
- p8: only the Gizmodo URL is cited; the patch is Brown et al., "Adversarial Patch" (2017).
- p12: the figure is Figure 1 of Kurakin, Goodfellow and Bengio, "Adversarial Examples in the Physical World" (2016); caption cites Goodfellow et al. 2014.
- p16: embedded image caption misspells "Prairie" as "Prarie" (in the source image).
- p33: Evtimov title reads "Machine Learning Models" while p9 and p10 read "Deep Learning Models"; both are arXiv revision titles of the same paper, published as Eykholt et al., CVPR 2018.
- p45, p46, p47: acronym written "FSGM" in titles and body; the method is FGSM. (Worksheet 7.2's filename has the same misspelling.)
- p49: exact duplicate of p48.
- p51: "PGD is MUCH SLOWER that FSGM" should read "than FGSM".
- p53: steps 4 and 5 are the two goals of step 3 but are numbered as separate steps.
- p76: title "Boundary Attack: How it Works" on a pros and cons slide.
- p84: x_adv from FGSM is overwritten by the PGD line before it is evaluated, so the printed "adv" row is PGD only.
- p85: same pattern; HopSkipJump's x_adv is overwritten by BoundaryAttack before anything reads it.
- p87: "Counterfeit" should be "Counterfit"; "Cleverhans is built by Google and part of Tensorflow" is inaccurate (created by Goodfellow and Papernot, hosted under the tensorflow GitHub org as a separate library, v4 supports JAX, PyTorch and TF2).
- p26 to p31: six stages of one Chio and Freeman poisoning figure classified as separate slides; each has its own note, but they could be grouped as builds.
- Unsure pages p16, p18, p20, p38, p55, p68 ruled own slides.
- Notebook, not deck: Worksheet_7.1_Attacking_AI.ipynb's title cell reads "Worksheet 8.1 Attacking AI - Answers" and cites HopSkipJump as "Jianbo et al. (2019)" (the author is Jianbo Chen).

## 09-artificial-intelligence-introduction-and-theory
- p13: "Gemeni" misspelled twice; the link should be gemini.google.com.
- p14: ChatGPT dated 2023; OpenAI released it November 2022. "2000: Bag of Words" is not an origin date (Harris, 1954).
- p20: "occurances" typo; "documents_containing-term" has a hyphen for an underscore; the IDF bullet describes occurrences, the formula counts documents containing the term.
- p31: "labelled" (UK spelling) alongside "Unlabeled" on p32.
- p32, p33: "for the those descriptions".
- p34: variable named sin_matrix holds cosine similarities; the np.argmax line is missing its closing parenthesis.
- p37: credits 2014 attention with improving word2vec; it improved RNN encoder-decoder translation (Bahdanau, Cho, Bengio).
- p42: title "Transfomers".
- p43: encoder output reads "I am a student" while the decoder generates "I love llamas" (inherited from the source figure).
- p47: "Tranformers" typo; GPT-3 "1.75 billion" should be 175 billion (p48 has it right); GPT-1 was trained on BooksCorpus, Common Crawl entered with GPT-3.
- p53: "which GPUs can execute much more effectively on a GPU" is redundant.
- p58: title "Tozenization".
- p77: attributes positional information to the attention layer; positional encodings are added before the attention layers, attention adds context.
- p88: Judge "Kevin Casten" should be P. Kevin Castel.
- p95: "Non-Deterministic systems is not guaranteed" (subject-verb).
- p99: bare URL; the note was written from calculator.gtkcyber.com itself, which states it returns wrong results at a configurable frequency and magnitude.
- p100: "nearly 100k models on HuggingFace" is dated; the hub passed one million models in 2024.
- Unsure pages p9 (module title card) and p59 (Method 1 of the tokenization sequence) ruled own slides.
- Spot-check: p57 note restates the slide's July 2026 price table as an input-to-output ratio; p72 note names max_tokens (Anthropic) and max_completion_tokens (OpenAI); p101 note cites JFrog's February 2024 report of about a hundred malicious models on Hugging Face.
