## Page 1

Module 0 covers the bootcamp's agenda and daily schedule, a working definition of artificial intelligence and of machine learning, the security problems machine learning is applied to, the steps of a machine learning project, and the Python libraries the labs use.

## Page 2

The slides, notebooks and anything handed out alongside them are copyright 2026 GTK Cyber LLC and are licensed to registered participants only; reproducing or redistributing them for any other purpose is not permitted. The seal is the FBI Anti-Piracy Warning, which copyright holders in the United States may place on their works under conditions the FBI sets.

## Page 3

Day 1 lays the foundations, and it comes before the modeling days because data that cannot be accessed cannot be analyzed: getting records into memory, inspecting them and shaping them into features is the prerequisite of every model on the later days. Introduction: this module. Getting Security Data and Vectorized Data Structures: the NumPy arrays and pandas DataFrames that hold a dataset in memory, and where security data comes from (Worksheet 1.1). Exploratory Data Analysis: summarizing and inspecting a dataset before modeling it. Data Visualization: plotting with pandas, Matplotlib and Seaborn, and interactive dashboards in Streamlit (Worksheets 2.1 and 2.2). Feature Engineering: turning raw records into the numeric columns a model consumes (Worksheet 3.1).

Day 2 is machine learning proper. Machine learning classifiers: training, tuning and automating a supervised model, with the detection of algorithmically generated domains as the running example (Worksheets 4.1 to 4.3). Building unsupervised clustering models: grouping records without labels (Worksheet 5.1). Anomaly Detection: finding the records that do not fit (Worksheet 6.1). Red Teaming ML Models: attacking a trained model, including an adversarial-example attack on an image classifier (Worksheets 7.1 and 7.2). Exploratory Data Analysis is listed a second time under Day 2; it is the Day 1 topic.

## Page 4

Day 3 moves to language models. Deep Learning and Neural Networks: convolutional and recurrent networks, applied to fingerprint images and to URL strings (Worksheets 8.1 and 8.2). Theory of Large Language Models: embeddings, tokenizers, attention, a first GPT built from scratch, and fine-tuning with its poisoning risk (Worksheets 9.1 to 9.6). Prompt Engineering: calling a language model from code and using it as a classifier (Worksheets 10.1 and 10.2). AI Architecture: RAG, retrieval-augmented generation, in which documents fetched for a query are placed in the model's prompt, applied to CVE records; and MCP, the Model Context Protocol, an open standard for connecting a model to tools and data sources (Worksheets 11.1, 11.2 and 12.1).

Day 4 is agents. AI Automation and Building AI Agents: an email classifier, a tool-calling agent, conditional routing, a human-in-the-loop step and a multi-agent supervisor (Worksheets 13.1 to 13.5). Red Teaming AI: attacks on language models and agents. Final Project: a project of your own that draws on the whole course.

## Page 5

Day 1 starts an hour later than the days that follow. Coffee is served from 09:00, class begins at 10:00, lunch runs from 12:30 to 13:45, a second coffee service falls at 16:00, and class ends at 19:00.

## Page 6

Days 2 through 4 share one schedule. Breakfast runs from 08:00, class starts at 09:00, coffee breaks fall at 10:30 and 16:00, lunch runs from 12:30 to 13:45, and class ends at 18:00.

## Page 7

Ask questions as they come up. Run the examples yourself while they are presented; the labs assume you have. Every exercise's answer is in a slide deck or in the GitHub repository, and the request is that you attempt each exercise before opening it. The course Slack channel is monitored during class, so a question typed there is answered without waiting for a pause, and links and fixes are posted there between sessions.

## Page 8

Everything for the course is in one GitHub repository, at the address on the slide. The Python labs are in the notebooks folder, the decks are in the slides folder, and bonus and optional material is scattered through the rest of the tree.

## Page 9

This part defines artificial intelligence and places large language models within it.

## Page 10

The image macro is a joke about the hype that surrounds large language models, with the caption welcoming it in a villain's voice.

## Page 11

The sign is the standard no-bull symbol: the definitions that follow are meant to hold without the hype.

## Page 12

The question is put to the room before any definition is offered. The term is applied to everything from a regular expression that flags a malicious URL to a chat model, and a definition fixes which of those count. Write yours down before reading on.

## Page 13

The working definition is that artificial intelligence is any activity that mimics human behavior. It is deliberately broad: under it a chess program, a spam filter and a chat model all qualify, since each replaces a judgment a person would otherwise make. The definition is taken from a 2017 KDnuggets article by RapidMiner on the distinctions among AI, machine learning and deep learning.

## Page 14

Artificial intelligence and large language models are not the same thing; the operator on the slide is the programmer's not-equal sign. A large language model, LLM for short, is one kind of AI system: a neural network trained on text to predict the next token, used through prompts. The field it belongs to also holds the classifiers, clustering methods, anomaly detectors, and image and sequence networks that fill the first two days of this course.

## Page 15

The greater-than sign is read as written: the field of artificial intelligence is larger than the language models inside it. Classifiers, regression models, clustering and anomaly detectors are all AI methods that involve no language model, and they remain the methods of choice for structured security data such as flow records, log rows and domain strings.

## Page 16

Language models did not retire the older methods. A task-specific model is trained on an organization's own labeled data, scores every event at line rate on ordinary CPUs, and is measured with precision and recall on a held-out set. A language model handles free text and open-ended reasoning that a fixed feature set cannot encode, at a cost per call that rules it out for scoring a firehose of events.

## Page 17

A multiplier scales whatever it is applied to, and zero scaled is still zero. A language model used by someone who understands the task amplifies that understanding: the person can direct the model, judge its output and correct it. Applied to a task the user does not understand, there is nothing to amplify: wrong output cannot be told from right, so the model's errors pass through unchecked.

## Page 18

Both AI in general and machine learning in particular are tools, chosen to fit a task. Two properties of large language models restrict where they fit.

They are non-deterministic. Output is sampled from a probability distribution over the next token, so the same prompt can produce different text on each call, and even at a temperature of zero, differences in how requests are batched on the GPU can change the result. Any task that must return identical output for identical input, such as an audit rule or a parser, is a poor fit.

They are expensive. Producing each output token requires a pass through billions of parameters, so inference runs on GPUs, takes hundreds of milliseconds to seconds per response, and is priced per token. A logistic regression scores a row in microseconds on a CPU for nothing.

## Page 19

A deterministic task has an exact procedure: parsing a timestamp, computing a hash, checking whether an address falls inside a CIDR block, matching a pattern. Code that implements the procedure is right every time and costs nothing per call. Handing the same task to a language model routes it through a GPU, returns the answer inside text that still has to be parsed, and can return a different or wrong answer on a repeat. The better use of a language model on such a task is at development time, helping to write the code that implements the procedure; the code then runs without the model.

## Page 20

This part defines machine learning through three published definitions and sorts its problems into supervised and unsupervised, and into classification, regression, clustering and dimensionality reduction.

## Page 21

The three terms nest. Artificial intelligence is the outer set, any technique that lets a computer mimic human behavior, and it includes hand-written rule systems and search as well as learning. Chess is the example of AI without learning: its rules are fully known and can be programmed directly, so a chess engine is a search over legal moves. Machine learning is the subset for problems whose rules are not known or are hard to define formally; it uses statistical methods so that a program improves with experience, meaning its behavior is fitted to data rather than written out by a programmer. Deep learning is the subset of machine learning built on neural networks with many layers, which became practical once GPUs made the training computation feasible, and a large language model, being a neural network, sits in this innermost set. Every deep learning model is a machine learning model, and every machine learning model is AI; the converse fails at each step.

## Page 22

The first definition is Andrew Ng's, from the description of his Stanford machine learning course on Coursera. The phrase to weigh is "without being explicitly programmed." In ordinary programming the developer writes the rule that maps an input to an output, one case at a time. In machine learning the developer supplies examples and an algorithm that fits a rule to them; the rule that results was derived from the data, and the developer may not be able to state it.

## Page 23

Tom Mitchell's definition, from his 1997 textbook Machine Learning, is the one used when a claim of learning has to be tested, because it names three things that must be specified. The task T is what the program does, for instance labeling a domain name as generated by malware or registered by a person. The performance measure P is a number computed on the task, for instance the fraction of a set of domains labeled correctly. The experience E is the data the program is given, for instance a file of domains with known labels. The program learns if P on T rises as E grows. A program that scores the same after seeing more data has not learned anything, whatever its architecture.

## Page 24

The Wikipedia definition names the artifact: a model, built from example inputs, that makes predictions or decisions on new data. The contrast it draws, in bold on the slide, is with static program instructions. An intrusion detection signature is a static instruction: it matches the bytes it was written to match and nothing else. A model built from examples of malicious and benign traffic produces a prediction for traffic that matches no example exactly, which is the property the security applications in this module depend on.

## Page 25

The photograph is a can of SPAM, the Hormel canned pork product whose name became the word for unsolicited bulk email by way of a Monty Python sketch in which the word is chanted until it drowns out everything else. Email spam is the case followed here, and it starts with rules: the first defense email providers built was a list of keywords, and a message containing one was blocked.

## Page 26

The three flavors stand for what happened next: spammers adapted, producing new varieties of message that the keyword lists did not match, and each new variety forced a change in the defense.

## Page 31

Email spam filtering is the textbook case of the shift from rules to learning, and the four items are its history in order. Blacklists: a list of sender addresses, domains or relays known to send spam, which blocks exactly the senders already on the list and nothing that arrives from a new one. Simple keyword matching: hand-written rules that flag messages containing words associated with spam, which senders defeat by misspelling the words or embedding them in images. Naive Bayesian classifiers: a learned model, popularized for spam by Paul Graham's 2002 essay A Plan for Spam, that estimates the probability a message is spam from how often each of its words appeared in known spam and known legitimate mail, treating the words as independent evidence; it is trained on the recipient's own mail and adapts as senders change their vocabulary. Deep learning: neural networks over the message text and headers that learn their own representation of what spam looks like.

Machine learning has largely defeated spam as a nuisance. Unsolicited mail remains one of the main attack vectors, now as the carrier of phishing and malware.

## Page 32

Supervised learning fits a model to records that already carry the answer. Each training record is a set of features paired with a label, such as a domain name paired with the verdict malicious or benign, and the model is fitted so that its output on the features reproduces the labels. The labels are what make the problem supervised, and they are also its cost: someone or something, an analyst, a sandbox or a threat feed, had to produce a verdict for every training record.

Unsupervised learning fits a model to records with no labels at all. There is no answer to reproduce, so the model describes structure in the features themselves: which records resemble one another, which are far from all the rest, which features move together. What that structure means is decided afterward by a person looking at the output.

Most security problems fall on the supervised side. The question asked of an observed event is whether it is malicious, and a verdict with two possible values is a classification problem, so the applications surveyed later in this module are mostly classifiers.

## Page 33

The four problem types differ in what the model outputs, and the slide's colors sort them by whether labels are needed, blue for supervised and green for unsupervised. Classification: the output is one of a fixed set of classes, such as malicious or benign, or one of a dozen malware families. Regression: the output is a number on a continuous scale, such as the bytes a host is expected to transfer in the next hour. Clustering: the output is a grouping of the records, with no names for the groups. Dimensionality reduction: the output is a smaller set of variables chosen so that the larger set can be reconstructed from them with small error, used to plot a dataset with hundreds of features in two dimensions or to strip redundant features before modeling.

## Page 34

The flowchart routes a problem to a method by two questions. The first is whether the data carries labels. With labels, the second is whether the label is a category or a quantity: a quantity calls for regression, which yields a prediction and also inference, since a fitted regression reports how much each feature moves the target; a category calls for classification, which yields a prediction. Without labels, the second question is whether labels could be produced. If they can, at whatever cost in analyst time or sandbox runs, the problem becomes a supervised one and rejoins the upper path. If they cannot, what remains is clustering and pattern finding: recommenders, similarity search and anomaly scoring.

One way to produce labels is to have people produce them as a side effect of something else. reCAPTCHA is the standing example: the distorted words its early versions asked a website's visitors to type were words that optical character recognition had failed to read in scanned books, and each transcription became a label for that image; later versions asked which photograph tiles contain a storefront or a traffic light, and the answers labeled the photographs.

"Nothing proven" is the caution on the last path. A cluster or an anomaly score has no ground truth to be checked against, so there is no correct answer to compare it with; the output is a lead for a person to examine, and a claim that it detects attacks has to be established some other way.

## Page 35

This part surveys where machine learning is used in security, with network intrusion detection and malware classification as the worked cases. Whether a host may join the network, whether a message is spam and whether a flow is allowed through are the shape of the applications, each a yes or no, and the first task in any of them is to check that the problem fits a data science method at all.

## Page 36

Clustering serves anomaly detection because it defines what normal looks like. The sketch is the one-dimensional case: a value tracked over time, a threshold drawn above its usual range, and a spike that crosses the threshold marked as the anomaly. With one measurement a fixed threshold suffices. With many measurements per record, bytes, packets, duration, port and time of day at once, no single line separates normal from abnormal; clustering finds the dense regions where records concentrate, and a record far from every region is the multidimensional equivalent of the spike. The slide's "anything really" is accurate: the method applies to any stream of records with numeric features, traffic, server load, logins or process launches.

Clustering is chosen here because the two kinds of record are unequally available: normal records are plentiful and labeled anomalies are scarce, too few to train a classifier on. K-means, which partitions the records into a chosen number of groups around their centers, is a common choice for the job.

## Page 37

Network intrusion detection starts from captured traffic. The raw material is either full packet capture, pcap, which holds every byte of every packet, or NetFlow, which summarizes each connection as a record of endpoints, ports, protocol, byte counts and timing. Tools named on the slide are tshark and tcpdump for packet capture and Bro, since renamed Zeek, which turns raw traffic into connection logs.

The example features are the connection features of the 1999 KDD Cup intrusion dataset, itself derived from the DARPA 1998 evaluation: each connection is summarized over a two-second window into its duration, protocol, service, and bytes sent by source and destination. The slide's "dat bytes" is destination bytes. The image on the right is a node-link graph of hosts and their connections, with a dense hub of activity at the center.

Public traffic datasets named on the slide come from Netresec's list of pcap files, the Mid-Atlantic Collegiate Cyber Defense Competition, West Point's Cyber Research Center and the Canadian Institute for Cybersecurity at the University of New Brunswick.

## Page 38

Malware classification works from the file's contents. Features come from the binary's content and from metadata extracted by a disassembler such as IDA: the functions it calls, the strings it contains, the segments it is laid out in. The example features are counts and sequences over that material: opcode n-grams, sequences of n consecutive instructions counted across the disassembly; byte n-grams, the same idea over raw bytes; segment counts; function names; and pixel intensity, which treats the bytes of the file as a grayscale image and uses the image's statistics as features.

The featureless alternative trains a deep network directly on the byte or opcode sequence, with word2vec, the 2013 technique for learning a vector for each token from the tokens around it, supplying the representation instead of a hand-built feature list.

Sample sources named on the slide are VX Heaven, VirusShare, Maltrieve, a tool that downloads samples from public feeds, and Open Malware.

## Page 39

Each application on the list is a problem type from the earlier taxonomy applied to one kind of security record, and the parenthetical says which. Where a labeled corpus exists the problem is classification; where the interest is in structure or in records unlike the rest, clustering is listed alongside.

The string classifiers take a piece of text as the record. Domain generation algorithm detection: malware that computes rendezvous domains from a seed produces names unlike those people register, and a classifier on the characters of a domain separates the two (Worksheet 4.1). Malicious URL and phishing detection: the same approach applied to URLs and to messages. SQL injection and cross-site scripting detection: classifying a request's parameters by whether they carry an attack payload.

The traffic problems take a connection or a window of connections as the record. Beaconing detection: an implant that calls its controller on a schedule leaves a regular timing pattern, found by classifying or clustering inter-arrival times. General anomaly detection and denial-of-service detection: the volume and shape of traffic against its usual range. New malware classes: clustering samples so that a group matching no known family stands out. Log anomaly detection: the same over log records. Authentication: classifying a login as the account's owner or someone else from its time, source and behavior.

The working difficulty across the list is false positives. A detector that fires on benign events buries the real ones in alerts, and an analyst who works a queue of false alarms stops trusting the queue; that is alert fatigue, and it decides whether a deployed model is used. The aim is not to replace the analyst but to extend what one analyst can cover.

## Page 40

The funnel is Austin Taylor's 2017 picture of where machine learning sits in threat hunting. Everything at the top is network traffic, produced naturally and all of it in scope. Machine learning makes the first cut, separating the anomalous fraction from the normal bulk; the figure puts that fraction at ten percent. Domain knowledge, meaning an analyst who knows the environment, makes the second cut to what is interesting, one to five percent, and the third to what is potentially bad, a thousandth of a percent. At the bottom is the malicious traffic.

Taylor's examples for the machine learning cut are finding periodic communication, the regular timing of an infected host calling its command and control server; scoring user agent strings with a Markov model, which rates a string by how likely each character is given the one before it, and keeping the least likely; and flagging DNS requests for domains with high entropy or flagged as algorithmically generated. The examples for the domain knowledge cut are the questions an analyst asks of what remains: whether the domain is in the Umbrella, Majestic or Alexa top one million, whether the IP address is a known Tor node, whether either carries a blacklist or threat intelligence association, who owns the IP space, and how recently the domain was registered.

The ordering is the lesson. A model does the coarse, high-volume reduction that no analyst could do by hand, and a person does the fine reduction that needs context the model does not have. Neither stage replaces the other.

## Page 41

Every application in the survey reduces to the same act: deciding, for each event, whether it is bad, and doing so at the rate events arrive. Classification decides it directly; anomaly scoring decides it relative to normal; clustering groups events so that the decision can be made once per group. "Rapidly" is the constraint that separates a detection from a forensic finding: an event that is scored after the attacker has moved on is a record, not a detection.

## Page 42

A static rule matches the pattern it was written for. When an attacker learns the rule, changing a byte in the payload, a word in the lure or the interval of a beacon takes the traffic outside the pattern, and the rule sees nothing. A model fitted to examples has learned a boundary rather than a pattern, so a variation that stays on the malicious side of the boundary is still caught, and retraining on newly labeled examples moves the boundary without anyone rewriting rules. The adaptation has a condition: a model that is not retrained misses new tactics just as a rule does.

## Page 43

This part walks through the stages of building a model, from the analytic question through data, features, model and evaluation.

## Page 44

The supervised process runs in a loop. Getting and cleaning data, in pandas, produces a table of records. Preprocessing and feature engineering, in pandas and scikit-learn, turns the raw columns into numeric features. Advanced feature selection, in scikit-learn, drops the features that carry no signal. The result is the dataset.

The dataset is then split. The training data is what the model is fitted to. The testing data is withheld from fitting and used only to evaluate the model; scoring a model on the records it was fitted to measures how well it memorized them, and only records it has not seen measure how well it generalizes. Building and evaluating alternate, and the long arrow from evaluation back to the top of the diagram is the ordinary case: an evaluation that disappoints sends the work back to the data and the features, not only to the model.

## Page 45

The unsupervised process has the same front half and a different back half. Data is gathered, cleaned, engineered into features and selected exactly as before. There is no split, because there are no labels to score against; the whole dataset goes into building the model. Evaluation is done another way: with internal measures of cluster quality, such as how tightly each group holds together and how far apart the groups are, and with a person inspecting what the groups contain. The loop back to the data is the same.

## Page 46

The analytic question comes before the data and before the model. It fixes the unit of observation, the thing each record describes; the target, the thing to be predicted or found; and the measure by which the answer will be judged. Without it the choice between the problem types on the flowchart cannot be made, and a model built anyway answers a question nobody asked.

## Page 47

Stating what you are trying to do means naming the action the model's output will drive. Block a domain, page an analyst, rank the morning's alerts, or add a field to a report: each of these implies a different tolerance for false positives, a different required latency, and a different form of output, a label, a score or a ranking.

## Page 48

Success has to be defined as a measurement, chosen before the model is built. The choice matters because security data is imbalanced: if one event in a thousand is malicious, a model that labels every event benign is right nine hundred ninety-nine times in a thousand and detects nothing. Accuracy therefore says little; precision, the share of alerts that are real, and recall, the share of real events that are alerted, say what the model does for the analyst who receives its output, and the acceptable trade between them depends on how many alerts that analyst can work.

## Page 49

Choosing data sources is four questions. What is available: which logs and captures the organization already collects and retains, and for how long. Is it enough: whether the records include enough examples of the thing to be detected, since a classifier for an event that appears three times in the archive has three examples to learn from. Is it reliable, clean and consistent: whether timestamps agree across sources, whether fields are populated the same way throughout, and whether the collection changed partway through the period. What other data could you use: enrichment such as asset inventory, WHOIS records or threat intelligence that adds a column to every record.

## Page 50

Five constraints sit outside the data itself and can stop a project that the data would support. Policies: the organization's own rules on who may access a source, how long it is retained and what it may be combined with. Legal constraints: privacy and monitoring law, and contract terms, that limit what may be collected from employees, customers or partners and where it may be processed. Biases in data: a training set gathered under one set of conditions, one network, one month, one attacker, teaches the model those conditions, and its output on any other is unsupported. Latency: the time between an event and the decision the model must make about it, which decides whether the model runs inline on each event or in a nightly batch. Data size: the volume, which decides whether the work fits in memory on one machine with pandas or needs a cluster.

## Page 51

Exploring the data before modeling it answers the four questions on the right. The figure is a pair plot of the iris dataset, Ronald Fisher's 1936 set of 150 flowers from three species, with four measurements each. Each off-diagonal panel plots one measurement against another with a point per flower colored by species; each diagonal panel is the histogram of one measurement. The plot shows that setosa, in blue, separates from the other two species on petal length and petal width alone, while versicolor and virginica overlap on every pair. That is an answer to "is the data good enough": good enough to separate one class cleanly, and a warning that the other two will be confused. The same plot on a security dataset shows which features carry signal, which are redundant with one another, and whether the classes are balanced, before any model is fitted. Exploration is not a step done once and left behind. It continues through the project, since every change to the data or the features raises the same four questions again, and most of a project's effort goes here rather than into fitting the model.

## Page 52

Feature engineering fixes the shape of the table a model will consume. The observations are the rows: one per unit being measured, which the analytic question determines. The features are the columns: the numeric representation of each observation, since a model computes on numbers and on nothing else. For a domain name classifier the observation is one domain and the features are quantities computed from its characters, such as length, the share of vowels, and character entropy. Choosing what a row is and what its columns are is done before any modeling, and it is where the domain knowledge enters.

## Page 53

Fitting the model is the easy step because it is a library call. Scikit-learn, Spark's MLlib, TensorFlow, Keras and R's caret each expose an algorithm as an object with a fit method and a predict method; the algorithms themselves are implemented, tested and documented already. Tuning, the search over an algorithm's settings for the combination that scores best, is automated by the same libraries, and packages that search over algorithms as well as settings automate the whole step (Worksheet 4.3). Splunk and Elasticsearch ship model fitting inside the log platform, so that a model can be trained and applied to the indexed data without exporting it.

## Page 54

Evaluation is done with a scoring function, and the score is chosen to match the cost of being wrong. Libraries supply the standard ones, among them F1, the harmonic mean of precision and recall, and the area under the receiver operating characteristic curve, which summarizes the trade between true positives and false positives across every threshold. When the costs are asymmetric, a missed fraud costing more than a false alarm, a custom scorer that weights each error by its cost is a few lines of code and a better guide than any standard metric.

The second bullet is the loop. A disappointing score returns the work to the first step, the analytic question, and from there to the data and the features. The Monopoly reference means that there is no shortcut past those steps to the model.

## Page 55

The exercise applies the process to credit card fraud detection, which shares the shape of a security detection problem: a stream of transactions, a small fraction of them bad, and a decision required on each one. The six questions follow the steps in order. Features and data sets are the feature engineering and data source steps. Legal and policy challenges are the constraints on cardholder data. Other challenges are the biases, latency and volume questions. Defining success is the choice of a scoring measure. Articulating the value to stakeholders is the translation of that measure into money saved and customers not inconvenienced.

## Page 56

This part lists the Python libraries the course draws on, grouped by the step of the process they serve, and the books recommended for going further.

## Page 57

The libraries are grouped by process step. Data gathering: pandas reads CSV, JSON, Excel and SQL results into a DataFrame; Apache Drill runs SQL queries directly over files, NoSQL stores and cloud storage without loading them into a database; BeautifulSoup parses HTML; PyDBAPI refers to Python's standard database interface, which every SQL driver implements; PyDAL is a database abstraction layer; Boto3 is the AWS SDK for Python. Feature extraction: pandas and NumPy for column arithmetic, and Featuretools for generating features automatically from related tables.

Machine learning splits in two. The libraries labeled regular are for models fitted on tabular features: scikit-learn, the reference implementation used throughout this course; H2O; and MLlib, Spark's library, reached from Python through PySpark for datasets too large for one machine. The deep learning libraries are for neural networks: TensorFlow, Keras, which is a high-level interface over TensorFlow, PyTorch, Caffe, and Theano, whose development ended in 2017.

Visualization: Matplotlib is the base plotting library and Seaborn a statistical layer over it; Yellowbrick draws diagnostic plots for scikit-learn models; LIME explains an individual prediction by fitting a simple local model around it; ggplot is a port of R's grammar of graphics; and plot.ly produces interactive charts.

## Page 58

Aurélien Géron's Hands-On Machine Learning with Scikit-Learn and TensorFlow, from O'Reilly, works through the process taught in this module with code: an end-to-end project in scikit-learn first, then neural networks in TensorFlow. The instructor who recommends it calls it the best book on machine learning in Python they have read.

## Page 59

Deep Learning, by Ian Goodfellow, Yoshua Bengio and Aaron Courville, published by MIT Press in 2016, is the standard textbook on neural networks, from the linear algebra and probability they rest on through convolutional and recurrent architectures, and the full text is free to read at the address on the slide.

## Page 60

Machine Learning and Security, by Clarence Chio and David Freeman, from O'Reilly, covers the application of machine learning to intrusion and malware detection, fraud and abuse, and the ways a deployed model can itself be attacked. The instructors' reason for recommending it is its worked examples and use cases of machine learning in security.

## Page 61

Feature Engineering for Machine Learning, by Alice Zheng and Amanda Casari, from O'Reilly, is a book-length treatment of the step this module gave a single slide to: encoding numbers, categories, text and images as features a model can use. The instructors single it out because the topic is often passed over in treatments of machine learning.

## Page 62

Learning Apache Drill, by Charles Givre and Paul Rogers, from O'Reilly, is the guide to the SQL engine listed under data gathering, written by one of this course's instructors.

## Page 63

Questions on the agenda, the material or the environment setup are taken here.

## Page 64

The introduction ends here. The first lab, Worksheet 1.1 on vectorized data structures, needs the environment installed and selected in PyCharm.
