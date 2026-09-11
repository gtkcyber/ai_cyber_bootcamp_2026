## Page 1

Module 9 opens the artificial intelligence half of the bootcamp with the theory behind large language models: how text becomes tokens and embeddings, how a transformer produces output one token at a time, and why a generative model is non-deterministic and can return confident, wrong answers.

## Page 2

What is new is the subject of this short section: five properties that separate large language models from the classifiers of the earlier modules.

## Page 3

A large language model can be used by anyone through a chat interface or an API call, with no dataset to assemble and no model to train. Each classifier in Modules 4 through 8 required labeled data and a training run before it could make its first prediction. OpenAI is credited with that shift: its hosted API and chat interface put a trained model behind a single call, which made generative AI practical to integrate into an application and to experiment with.

## Page 4

The input to a language model is plain text. Asking it a question does not require building a feature matrix first, which is the work Module 3 spent on feature engineering. The GPT models were among the first multi-purpose models, effective across a range of tasks from the same text input, which is why no per-task feature pipeline precedes the question.

## Page 5

Large language models are one of the first successful examples of transfer learning, which is reusing a model trained for one task on a different task. The model is trained once on a general corpus of text and then applied to summarization, classification, translation and code without being retrained for each. Fine-tuning adapts a pretrained model to a specific task with a small amount of additional training; BERT, later in this module, is the example.

## Page 6

A single large language model serves many tasks. It can classify text, summarize it, translate it, answer questions about it and write new text, with the task chosen by the prompt. Each classifier in the earlier modules did one job and had to be trained separately for any other.

## Page 7

Multimodal means the model handles more than one kind of data. Current large language models accept and produce images, audio and video as well as text.

## Page 8

The Emperor Palpatine meme closes the list. The five properties are real, and the models are easier to use than they were a few years ago; the hype around them rests on the same five properties and exceeds what they justify.

## Page 9

Title card for Part 1, Introduction and Theory, the first of six AI parts in the bootcamp.

## Page 10

The AI portion of the bootcamp has six parts. Part 1, Introduction and Theory: how generative models work. Part 2, Prompt Engineering: how to get the most out of a large language model. Part 3, AI Architecture: the components of an AI application. Part 4, Agentic AI: building AI tools that do work, meaning models that call tools and take actions. Part 5, Red Teaming: how to attack AI applications. Part 6: defending them.

## Page 11

Part 1 covers tokenization, embeddings, attention and the transformer, then the properties of generated text. The diagrams in this part come from Hands-On Large Language Models by Jay Alammar and Maarten Grootendorst, published by O'Reilly in 2024.

## Page 12

Three objectives. Tokenization and embeddings: how text is split into units a model can process, and how those units become vectors of numbers. How a large language model works: the transformer architecture and token-by-token generation. Deterministic and non-deterministic use cases: when the same input is guaranteed to give the same output, when it is not, and why that decides whether a language model is the right tool for a job.

## Page 13

ChatGPT is one product among many. Commercial models: Gemini by Google and Claude by Anthropic. Models with openly downloadable weights: LLaMA by Meta, and the Mistral family from Mistral AI in Paris. OSS on the slide stands for open source software. Hugging Face is a company whose hub hosts models and training datasets from many publishers; models in this module are loaded from it by name. The two links at the foot of the slide are a curated list of open language models and an article on the licenses they ship under, which range from permissive to restricted commercial use.

The slide spells Gemini as Gemeni, and the address is gemini.google.com.

## Page 14

The timeline runs from counting words to generating them. Bag of words: representing a document as the counts of its words; the idea is older than the 2000 on the slide and is credited to Zellig Harris in 1954. Word2Vec, 2013: learned word vectors that capture meaning. Attention Is All You Need, 2017: the paper that introduced the transformer. BERT and GPT, 2018: the first transformer models trained on large corpora, one an encoder for representing text and the other a decoder for generating it. GPT-2 in 2019 and GPT-3 in 2020 scaled the same design up. ChatGPT: the chat interface on top of GPT-3.5 that brought the models to the public. The slide dates it to 2023; OpenAI released it in November 2022. Bag of words and Word2Vec are no longer the state of the art, and they remain worth knowing: a problem that a word-count model solves runs faster and costs less than the same problem put to a large language model.

## Page 15

A language model takes unstructured text as input and can return three kinds of output. Text output: generated text, which is what a chat model returns. Embeddings: a vector of numbers representing the input, used to compare texts with each other. Classification: a label identifying which category the input belongs to.

## Page 16

Language models generalize further than the classifiers of the earlier modules. A classifier from Module 4 was trained on one feature matrix for one task, and asking it a different question meant engineering new features and training again. A language model accepts plain text, and the task is stated in that text, so one model answers many questions with no dataset built for each.

## Page 17

Bag of words begins by splitting text into tokens on whitespace. The two inputs, That is a cute dog and My cat is cute, become nine tokens, five from the first sentence and four from the second. Case is folded, so That becomes that. Word order does not survive the split.

## Page 18

The tokens are reduced to a vocabulary, then each input is counted against it. The nine tokens contain seven distinct words, so the vocabulary has seven entries: that, is, a, cute, dog, my, cat. The vocabulary size is the length of every vector that follows. To represent My cat is cute, the method counts how many times each vocabulary word appears in it: zero for that, one for is, zero for a, one for cute, zero for dog, one for my, one for cat. That row of seven counts is the document's vector, and it is all a downstream model sees.

## Page 19

Bag of words vectors feed three kinds of task. Topic modeling: finding which words tend to appear together across a corpus. Text classification: training a classifier on the count vectors; the slide flags this as the use with security applications, such as sorting phishing email from legitimate email. Text clustering: grouping documents whose count vectors are similar.

The method has three weaknesses. Common words dominate: a word such as the appears in every document with a high count, so it carries the largest values while saying the least about what the document is about. Meaning is ignored: the vector records that a word occurred, and cat and kitten are as unrelated in it as cat and invoice. Sparsity: the vocabulary of a real corpus is large and each document uses a small part of it, so the count matrix is mostly zeros and has to be stored in a sparse structure to fit in memory.

## Page 20

TF-IDF rescales a word count by how rare the word is across the corpus. Term frequency: how many times the word occurs in the one document being scored. Inverse document frequency: the logarithm of the number of documents in the corpus divided by the number of documents that contain the word. The score is the product of the two.

The logarithm is what removes the common-word problem. A word that appears in every document has a ratio of one, and the logarithm of one is zero, so its score is zero however many times it occurs. A word that appears in one document out of a thousand has a ratio of a thousand, and its count is multiplied by the logarithm of a thousand. The slide's description of inverse document frequency as how many times the word occurs across all documents is loose; the formula counts the documents that contain the word, and the formula is the definition to use. The slide also spells occurrences as occurances.

## Page 21

The scikit-learn pipeline turns TF-IDF into a text classifier in four lines. Five short sentences are the corpus, each labeled Python or Statistics. train_test_split holds out one fifth of them, which with five texts is a single sentence for testing and four for training. make_pipeline chains TfidfVectorizer, which learns the vocabulary and the document frequencies, with MultinomialNB, a naive Bayes classifier that models the per-class distribution of word scores. Calling fit on the pipeline fits the vectorizer on the training texts and then trains the classifier on the resulting matrix. New text passed to predict goes through the same two steps, so the vocabulary and weights learned in training are applied to it unchanged. Other Python implementations of TF-IDF exist; this one is scikit-learn's.

## Page 22

Word2Vec represents each word as a vector whose values are learned from the words around it. Bag of words records only counts, so it has no way to know that cat and kitten are related. Word2Vec, published by Tomas Mikolov and colleagues at Google in 2013 in the arXiv paper linked on the slide, trains a small neural network on a proxy task: given two words, predict whether they appear near each other in the training text. In the diagram, Cat and Cute are looked up as vectors and fed to the network, which outputs 0.74 as its estimate that they are neighbors. The vectors are the parameters the network adjusts during training, so after enough text has passed through, words that occur in similar contexts have ended up with similar vectors. Training one is rarely necessary: pretrained Word2Vec vectors, trained on corpora the size of Wikipedia, are published for download.

Two vectors are compared with cosine similarity, the cosine of the angle between them: one when they point the same way, zero when they are unrelated, and negative when they point in opposite directions. A high cosine similarity between two word vectors means the words are used in similar contexts, which is what the method treats as similar meaning.

## Page 23

Each column is one word's vector and each row is one dimension of it. The dimensions are labeled animal, newborn, human, plural and fruit to make the picture readable; the dimensions a real Word2Vec model learns have no names, and only the pattern of values matters. Read down the columns: cats and puppy both score high on animal, baby scores high on newborn and human, apple alone scores high on fruit, and cats and houses share a high plural value. Read across a row and the words that share a property have similar values, which is what puts their full vectors close together and makes their cosine similarity high. Cosine similarity is the usual measure of that closeness; any distance metric between vectors, Euclidean distance among them, supports the same comparison.

## Page 24

The map projects word vectors onto two axes so that distance on the page stands for similarity. cats, dog and puppy sit together in the upper left, apple and banana in the upper right, building and houses in the lower left, and baby and adult in the lower right. Words from the same domain cluster because their vectors share values on the dimensions that describe that domain. The real vectors have many more than two dimensions, so the flat map is a lossy view; what it shows accurately is which words sit near each other.

## Page 25

An embedding can be produced at any level of text, from a single token up to a whole document. The representation model in the diagram takes three inputs. A passage becomes one document embedding. The sentence My cat is cute becomes one sentence embedding. Her vocalization was melodic is first split into tokens, and vocalization becomes two of them, vocal and ##ization, where the ## prefix marks a piece that continues the word before it. Each token gets a token embedding, and the two pieces of vocalization are combined into one word embedding.

Bag of words works at the document level, since its vector describes a whole document's counts. Word2Vec works at the word level, one vector per vocabulary word. The transformer models that follow produce token embeddings and can pool them into a vector for a sentence or a document, which is the kind the sentence-transformers model in Worksheet 9.1 returns.

## Page 26

An embedding is a list of numbers standing in for a piece of text. No single value in the list means anything on its own; the list is useful only when compared with another list produced by the same model, because the model places texts with similar meaning near each other in its vector space. Embeddings from two different models are not comparable, since each model lays out its space differently. The text embedded can be a word, a phrase, a sentence, a paragraph or a document, and a given model returns a vector of the same length whichever it is.

## Page 27

This section uses an embedding model as a fixed feature extractor. With labeled data, a conventional classifier is trained on the embeddings. Without labels, a text is classified by comparing its embedding with the embeddings of short descriptions of each label.

## Page 28

An embedding model can replace feature engineering. Step one, the feature extractor: the embedding model turns each text into a vector, and that vector is the feature set. Step two, the classifier: any of the supervised models from Module 4, logistic regression in the diagram, is trained on those vectors against the labels.

The embedding model is frozen, meaning its weights are not updated; only the classifier's parameters are fit. Training therefore costs what training the classifier costs, and the labeled set only has to be large enough for the classifier, since the knowledge of language in the embeddings was learned during the embedding model's own pretraining.

## Page 29

The code runs the two steps in Python. SentenceTransformer loads paraphrase-MiniLM-L6-v2, a small sentence embedding model from the sentence-transformers library: six transformer layers, and a vector of 384 numbers for each input. Applying encode to each row of the query column produces one embedding per record, stored as a list in a new column. The lists are stacked into a NumPy array, which is the feature matrix, and final_label is the target. train_test_split holds out a quarter of the rows. A random forest is fit on the training rows and predicts the held-out ones; from that line on the code is the same as Module 4, since the classifier receives a numeric matrix like any other.

## Page 30

Worksheet 9.1 applies the pipeline to SQL injection detection: embed SQL queries with paraphrase-MiniLM-L6-v2, train a random forest on the embeddings, and score it with a confusion matrix and classification report, first on a synthetic dataset of a thousand queries and then on a larger real one.

## Page 31

This section covers classifying text when no labeled examples exist.

## Page 32

Unlabeled text can be classified from a description of each label. Write a short sentence for each candidate label, here A negative review for 0 and A positive review for 1. Pass the descriptions through the embedding model to get one label embedding each. Pass the document, Best movie ever!, through the same model to get its document embedding. The label whose embedding is most similar to the document's is the prediction. Nothing is trained; the method rests on the embedding model placing a positive review and a sentence describing a positive review near each other. This is zero-shot classification, zero-shot because the model has seen no examples of the classes.

## Page 33

The comparison is geometric. Each embedding is a vector from the origin, and cosine similarity measures the angle between two of them: the smaller the angle, the higher the similarity. In the plot, the angle θ1 between Best movie ever! and A positive movie review is smaller than the angle θ2 between it and A negative movie review, so the document is assigned the positive label. The plot is drawn in two dimensions for legibility; the real vectors have hundreds of dimensions, and the angle is measured across all of them at once.

## Page 34

Three lines do the classification. model.encode on the list of two label descriptions returns two label embeddings. cosine_similarity from scikit-learn takes the matrix of document embeddings and the matrix of label embeddings and returns a matrix with one row per document and one column per label, each cell the cosine similarity between that document and that label. np.argmax along axis one returns, for each row, the index of the column with the highest value. The index refers to the order of the label list: zero is A positive review and one is A negative review, the reverse of the diagram's numbering, so the mapping from index to label has to be read off the list that was encoded. The variable is named sin_matrix although it holds cosine similarities, and the argmax line is missing its closing parenthesis.

## Page 35

Worksheet 9.2 applies embeddings without labels to a shadow IT problem: find the emails in a mailbox that confirm new account sign-ups by their similarity to a description, choose the similarity threshold that works, and extract the unique sender domains to list the unauthorized services.

## Page 36

Section divider. The picture is the film robot; the transformer that follows is a neural network architecture.

## Page 37

The transformer is an encoder-decoder architecture built on attention alone. It was proposed in Attention Is All You Need, published in 2017 by Ashish Vaswani and seven colleagues at Google. It removed the recurrent networks: each layer computes attention between every position and every other position in one matrix operation, so no hidden state is carried from token to token. Every token of a sequence is processed at the same time, which is what makes transformers trainable in parallel across GPUs, and that parallelism is what made training runs of billions of parameters feasible. GPT stands for Generative Pretrained Transformer; every GPT model is this architecture, decoder half only.

## Page 38

The architecture has two stacks. The encoder stack takes the input tokens I love llamas and produces one vector per token that reflects the whole input. The decoder stack takes the encoder's vectors and the tokens generated so far and produces the next output token, building the Dutch Ik hou van lama's one token at a time. Each stack is several identical layers, drawn as the stacked rectangles, with the output of one layer feeding the next. BERT keeps only the encoder stack and GPT keeps only the decoder stack; the original model kept both because it was built for translation, where an input sequence has to be read in full before an output sequence is written.

## Page 39

One encoder layer has two sublayers. Each input token arrives as an embedding, the grey vectors. Self-attention updates every token's vector with a mix of all the tokens' vectors, weighted by how relevant each other token is to this one, and produces the yellow vectors. The self marks the difference from earlier attention, which let a translation decoder weigh the positions of a separate encoder; self-attention relates the positions of one sequence to each other, so each token's representation can draw on the whole input. A feedforward neural network then transforms each position's vector separately, producing the blue vectors that leave the layer. The output is one vector per input token, the same count as went in, and each now depends on the tokens around it: llamas after I love carries different values than llamas alone. The slide title is missing an r in Transformers.

## Page 40

The decoder layer adds a third sublayer and a restriction. Its input is the words generated so far, I and love, as embeddings. Masked self-attention is self-attention in which each position may attend only to positions before it, so the model cannot use tokens it has not yet produced; the mask enforces at training time the condition that holds at generation time. Encoder attention, also called cross-attention, lets each decoder position attend to the encoder's output vectors, the blue column on the left, which is how the source sentence reaches the decoder. The feedforward network transforms the result, and the final vector is turned into the next generated word, llamas.

## Page 41

BERT is an encoder-only transformer that produces representations of text. The name stands for Bidirectional Encoder Representations from Transformers; it was published by Jacob Devlin and colleagues at Google in 2018. Bidirectional means each token attends to the tokens on both sides of it, which the encoder allows and the masked decoder does not, so BERT's vector for a word reflects its whole sentence. The diagram is BERT base: twelve encoder layers, taking the input [CLS] I love llamas and returning a contextualized embedding per token.

[CLS] is a token added at the start of every input. Its output vector is trained to stand for the whole input, so a classifier fine-tuned on BERT reads that one vector. Models of this kind are called representation models: their output is a vector, and something else, a classifier or a similarity comparison, turns the vector into an answer.

## Page 42

BERT is built for transfer learning in two stages. Stage one, pretraining: the model is trained on a large unlabeled corpus, Wikipedia in the diagram, with the objective of masked language modeling, in which some tokens of each input are hidden and the model must predict them from the tokens around them. No labels are needed, because the text supplies its own answers. This stage is the costly one; the BERT paper reports four days on sixteen TPU chips for the base model.

Stage two, fine-tuning: a pretrained checkpoint is downloaded and trained further on a small labeled set for one task, with a task-specific output layer. The author's analogy is a broad college education followed by a specialization: fine-tuning is faster and needs less data and less compute than training from scratch because the pretrained weights already encode the language, and the small labeled set only adjusts them. The downstream tasks named are classification, named entity recognition, which marks which tokens are people, places and organizations, and paraphrase identification, which decides whether two sentences mean the same thing. The BERT paper reports fine-tuning in at most an hour on a single TPU, which is why the shared pretrained checkpoints are the starting point. Worksheet 9.6 repeats the two stages at small scale: pretrain a mini-GPT on general English, then fine-tune it on CVE descriptions.

## Page 43

Generative AI produces content as its output. A classifier from the earlier modules returns a class membership and a regression model returns a number; a generative model returns text, an image, audio or video. Its input is a prompt, the text describing what is wanted. Internally the model still computes probabilities, one distribution over its vocabulary for the next token, and the generated text is the result of picking a token from that distribution and repeating until the response is complete. Multimodal generative models take and produce images, audio and video in addition to text.

## Page 44

Decoder-only transformers, introduced in 2018, are the generative branch. GPT stands for Generative Pretrained Transformer, and GPT-1 was published by Alec Radford and colleagues at OpenAI in June 2018. With no encoder, the prompt itself is fed to the decoder stack, masked self-attention relates each prompt token to the ones before it, and the final vector is decoded into the next word; the diagram shows GPT-1's twelve decoder layers taking I love and producing llamas. GPT-1 had 117 million parameters and was trained on BooksCorpus, about seven thousand unpublished books; Common Crawl, the web scrape named on the slide, entered the series with GPT-3. GPT-2, 2019, had 1.5 billion parameters. GPT-3, 2020, had 175 billion; the 1.75 billion on the slide drops two zeros, and the How Large Are They slide has the right figure.

## Page 45

The sizes and costs are estimates from outside the labs, since OpenAI has not published them. GPT-3, released in 2020: 175 billion parameters, roughly 800 GB of weights, trained on about 500 billion tokens, a run estimated at 34 days on 1024 GPUs and about five million dollars. GPT-4, released in 2023: 1.8 trillion parameters in 120 layers, trained on 13 trillion tokens over about 55 days at a cost of 63 million dollars, figures from a 2023 report by the analyst firm SemiAnalysis that OpenAI has not confirmed. Pretraining at this scale costs tens of millions of dollars, so applications are built on models that are already trained, reached through an API or downloaded as weights. Training is the expensive phase. Inference, one forward pass per generated token, costs a fraction of that per request and is billed by the token, so it is cheap rather than free; the token pricing later in this module is that bill.

## Page 46

The context window is the maximum number of tokens the model can hold at once, and it counts the prompt and the generated output together. The diagram's model has a maximum context length of 512. The prompt Tell me something about llamas. is six tokens; the two tokens already generated, Llamas and are, bring the current length to eight; the model produces one more token, domesticated, from that context. The new token is appended to the input, the length becomes nine, and the next pass begins. Every generated token uses one slot in the window, so a long answer to a long prompt can run out of room, at which point the model stops or the application drops the oldest tokens. The window is a fixed token budget, so techniques that compress what goes into it, summarizing earlier turns of a conversation or trimming retrieved text to the relevant passages, fit more usable memory into the same limit. The limit exists because attention compares every token with every other token, so the work for a pass grows with the square of the context length.

## Page 47

The timeline covers models released from late 2022 to early 2024, split by whether the weights can be downloaded. Proprietary models, available only through their owner's API: ChatGPT and GPT-4 from OpenAI; Bard, PaLM 2 and Gemini from Google; Claude 2 from Anthropic; Grok from xAI. Open models, whose weights are published: Llama and Llama 2 from Meta, MPT from MosaicML, Falcon from the Technology Innovation Institute in Abu Dhabi, Qwen from Alibaba, Mistral and Mixtral from Mistral AI, Yi from 01.AI, DeciLM from Deci, Phi-2 from Microsoft, and Command R from Cohere. The numbers under the open models are parameter counts in billions, and a model released in several sizes lists each. Mixtral's 8 × 7B is a mixture of experts: eight networks of seven billion parameters, of which two are consulted for each token. The chart stops in early 2024 and predates the models on the pricing slide in this module.

## Page 48

A language model reaches an application in one of three ways. API calls to a shared model: one copy of the model serves every customer behind a public API, prompts leave your network, and usage is metered per token; OpenAI's API works this way. API calls to a forked model: a dedicated copy of the model is deployed for one customer, in that customer's cloud account or on the vendor's isolated hardware, so prompts and outputs stay inside the customer's boundary while access is still an API and still metered; enterprise offerings take this form. Self-hosted: open weights run on hardware you control, so nothing leaves your network and there is no per-token bill; the cost is the GPUs and the people to run them.

## Page 49

Worksheets 9.3 through 9.6 build a small language model from parts. 9.3 is a PyTorch primer; 9.4 builds a tokenizer, an embedding table and a first next-token model; 9.5 adds attention and assembles a GPT; 9.6 pretrains it, fine-tunes it and then poisons it. The model that results is tiny and the point is the mechanics: each piece is written by hand so that the diagrams in this deck correspond to code you have run.

## Page 50

A forward pass through a transformer is a sequence of matrix multiplications, and a GPU is built to run them. A CPU has a handful of fast cores; a GPU has thousands of slower cores that execute the same multiply-and-add across a whole matrix at once, which is the shape of the work in attention, the feedforward layers and the embedding lookups. Training and any inference beyond toy scale therefore need one. Frameworks target NVIDIA first because their GPU support is built on CUDA, NVIDIA's programming platform; support for other vendors exists in PyTorch but lags. The second bullet on the slide reads "which GPUs can execute much more effectively on a GPU"; the second "on a GPU" is a leftover.

## Page 51

Section divider for tokens: the units the model reads, writes and bills by.

## Page 52

The model's input is a sequence of token ids. The text you send is converted to a sequence of token ids before the model runs, and the model's output is a sequence of token ids converted back to text. A token is a fragment of text, a whole common word or a piece of a rare one; the four-character average is OpenAI's rule of thumb for English, and other languages come out shorter per token. The conversion is tokenization, and the tokenizer is fixed for a given model, so its vocabulary decides how any input is split. Commercial APIs bill per token in and per token out, so the token count of a prompt is also its price.

## Page 53

OpenAI's tokenizer page splits any pasted text into tokens for a chosen model, colors each token, and reports the count. It is the quickest way to see that a leading space is part of the token that follows it, that a common word is one token, and that an uncommon word or a non-English word becomes several.

## Page 54

The bill has two meters, input tokens and output tokens, and output is the expensive one. In the table, output costs five to six times input for every model listed. Prompt caching lowers the input side: a prefix that repeats across requests, such as a long system prompt, is stored by the provider, and later requests that reuse it pay a reduced rate for those cached tokens, with a separate charge for writing the cache. The table gives prices per million tokens for the OpenAI and Anthropic model lines as of July 2026 and change over time.

Providers retire models. Older, cheaper models are deprecated in favor of larger, costlier ones on a schedule the customer does not control, so an application built against one model has to be retested when that model is replaced.

## Page 55

Three subword tokenization methods cover the models in use. Byte-Pair Encoding, BPE: builds its vocabulary by repeatedly merging the most frequent adjacent pair of tokens; GPT-2, the later GPT models and RoBERTa use it. WordPiece: Google's variant used by BERT, which chooses merges by how much they improve the likelihood of the training text and marks a word-continuing piece with a ## prefix, the notation seen in the vocalization example earlier in this deck. SentencePiece: a Google library that tokenizes raw text without first splitting on spaces, treating the space as a character in its own right, which is what lets one method serve languages that do not use spaces; T5 uses it. The slide title reads Tozenization.

## Page 56

Splitting on spaces is the simplest tokenizer and it leaves punctuation attached to words. Don't you love 🤗 Transformers? We sure do. becomes eight tokens, and among them are Transformers? and do. with their punctuation included. Those are separate vocabulary entries from Transformers and do, so the same word shows up in the vocabulary once for each punctuation mark it has ever been followed by.

## Page 57

Splitting off punctuation removes the duplicate entries and creates a new problem. Don't becomes three tokens, Don, the apostrophe and t, and t on its own carries no meaning. A tokenizer that knows English contractions produces Do and n't, where n't is the negation, and rule-based tokenizers such as spaCy do this. Rules of that kind are what a word-level tokenizer needs for every case in every language, and the vocabulary that results is large: the Hugging Face tokenizer summary the slide draws on gives Transformer-XL's space-and-punctuation vocabulary of 267,735 entries as the example. Every entry needs a row in the embedding table, and the rare ones are seen too seldom in training to get a useful vector. Splitting into single characters is the simpler alternative, with a vocabulary of the characters in the corpus; the same Hugging Face summary gives its costs, sequences several times longer and units that carry no meaning of their own, so the model has to learn every word from its letters.

## Page 58

Subword tokenization splits rare words into pieces that are common. The vocabulary holds whole common words plus fragments, so it stays at a size the model can learn, and a word absent from it, vocalization for instance, is still representable as vocal plus ization, each seen often enough in training to have a good embedding. The output on the slide is from BERT's uncased WordPiece tokenizer: everything is lowercased, and the emoji, which has no entry in the vocabulary, is replaced by the unknown token [UNK]. An unknown token loses the input's information at that position, which is the weakness that byte-level tokenizers fix.

## Page 59

XLNet's tokenizer, a SentencePiece model, keeps the spaces. XLNet is a 2019 model from Google and Carnegie Mellon; its tokenizer replaces each space with ▁, a distinct Unicode block character, and attaches it to the start of the following token, so ▁you records that a space preceded you. The original text can be rebuilt exactly, and a language written without spaces is handled by the same rule. Case is preserved, since the model is cased. Transformers is split into Transform and ers because the whole word is absent from the vocabulary, and the emoji survives as its own token. The ▁ is a separate character from the ASCII underscore; typing an underscore does not produce it.

## Page 60

BPE builds its vocabulary by counting and merging. Byte-Pair Encoding was a data compression method published by Philip Gage in 1994 and was adapted to tokenization for machine translation by Rico Sennrich, Barry Haddow and Alexandra Birch in 2016. Training starts with an initial token set, single characters or single bytes, and tokenizes the corpus with it. It then counts every adjacent pair of tokens, takes the most frequent pair, merges it into one new token, and adds that token to the vocabulary. Repeating the count-and-merge step a chosen number of times grows the vocabulary by one token per step, so the number of merges sets the vocabulary size.

Applying a trained BPE tokenizer to new text replays the same merges in the same order. Starting from bytes means any input is representable, including an emoji or a script absent from the training data, so a byte-level tokenizer has no unknown token. The GPT models use byte-level BPE; Worksheet 9.4 trains a BPE tokenizer from scratch.

## Page 61

tiktoken is OpenAI's open-source library for the tokenizers its models use. encoding_for_model returns the tokenizer matched to a model name, gpt-4o here. encode turns the sentence into eleven token ids, and decode_single_token_bytes turns each id back into the bytes it stands for. Three things are visible in the result. Don't is a single token, because it is common enough to have been merged whole. The leading space belongs to the token that follows it, so you and space-you are different tokens. The emoji, four bytes in UTF-8, is split across two tokens, three bytes then one, and is printed as escaped bytes because neither piece is a complete character on its own. Forty-two characters became eleven tokens, close to four characters per token.

## Page 62

Two references for counting tokens. The tiktoken repository on GitHub holds the library, its encodings and the list of which encoding each OpenAI model uses. The OpenAI cookbook notebook How to count tokens with tiktoken walks through counting tokens for plain strings and for whole chat message lists, including the per-message overhead the chat API adds, which is the count that matches the bill.

## Page 63

Section divider for denial of wallet, the attack that turns per-token billing against the application's owner.

## Page 64

A denial of wallet attack runs up the victim's bill. A denial of service attack exhausts a service's capacity so that legitimate users are refused. Denial of wallet exploits usage-based pricing: the attacker sends requests the service handles normally, the service scales to meet them, and the metered charges accumulate to the owner. The service stays up throughout, and the damage is the bill.

Applications built on a language model API are exposed on every count. Each request is expensive to serve, the provider scales without limit, the endpoint is reachable by anyone the application accepts input from, and the price is a function of both the input tokens and the output tokens of every request. The attacker controls the input directly and can steer the length of the output through what the input asks for.

## Page 65

The scenario is an application that answers product reviews with a language model: a negative review gets an apology and an offer to fix things, a positive one gets thanks. The review on the slide is positive, so it gets thanks, and it also asks for shoe recommendations and for the reply to reach family members who speak French, Dutch, Italian, German, Hebrew, Arabic, Farsi and Chinese. Posting a review costs the reviewer nothing, and the reply is billed to the application's owner by the token.

## Page 66

The application's instruction to the model is the system message shown: act as an agent that answers Amazon product reviews, thank the customer for a positive review, apologize and give the support address for a negative one. The review is passed as the user message. Nothing in the system message limits the length or the language of the reply, and that gap is what the review exploits.

## Page 67

The model did what the review asked. The reply thanks the customer in English and then repeats the thanks in French, Dutch, Italian, German, Hebrew, Arabic, Farsi and Chinese, for a total of 634 output tokens. The review as posted here ends with an explicit request to include responses in those languages. The languages were chosen to inflate the count: Hebrew, Arabic, Farsi and Chinese each take more tokens per word than English in GPT tokenizers. At the output prices on the token pricing slide one such reply costs between about four tenths of a cent and three cents, and a script posting reviews at volume bills every reply to the application's owner.

## Page 68

UNRESOLVED

## Page 69

Log the token count of every input and output. The code tokenizes a prompt with the model's own tokenizer and prints its length, which is the number the provider will bill for input. The API response also reports the input and output tokens it charged, and that is the figure to log for the output side. With both counts recorded per request, an alert can fire on a jump in output tokens per request, on a single user whose totals stand out, or on a daily total above budget. Denial of wallet is invisible in availability metrics because the service keeps working; it shows only in the token log and the bill.

## Page 70

Cap the output. Every model API takes a parameter that limits the number of tokens generated for one response, max_tokens in Anthropic's API and max_completion_tokens in OpenAI's, and the model stops when it reaches the cap. Set it to the largest response the use case needs, a few hundred tokens for a review reply, and the eight-language answer is cut off at that length. The cap bounds the cost of any one response; the number of requests an attacker can make is bounded separately by rate limiting and authentication.

## Page 71

The whole path from text to text. Input text is tokenized into token ids. Each id is looked up in the embedding table to give a token embedding. The transformer processes the embeddings and produces output token ids, one per pass. The output ids are decoded back into text. The tokenizer and the embedding table belong to the model and are fixed, so the same text produces the same ids each time; billing counts the ids at the two ends of the diagram.

## Page 72

Worksheet 9.4 builds the first two boxes of the workflow by hand: a BPE tokenizer trained on a text corpus, an embedding table that turns token ids into learnable vectors, and a bigram model that predicts the next token from the one before it, trained with cross-entropy loss. Worksheet 9.3 is a twenty-minute PyTorch primer, tensors, automatic differentiation and a training loop, for anyone who has not used the library; 9.4 assumes it.

## Page 73

A language model produces one token per pass. The prompt goes in, the model outputs a single token, that token is appended to the prompt, and the extended prompt goes in again for the next one. In the diagram the prompt asks for an apology email to Sarah, and the first four passes yield Dear, Sarah, a comma and a newline; punctuation and line breaks are tokens like any other. A response of a few hundred tokens is a few hundred passes, which is why output length drives both latency and cost, and why the output-token price is the higher one. Every token it emits is an entry in the tokenizer's vocabulary table, the same table that split the prompt, so each word in the output is assembled from the pieces that table holds.

## Page 74

Each pass ends with a probability for every token in the vocabulary. The model's last layer produces a score per token, and a softmax turns the scores into probabilities that sum to one; in the diagram, Dear has forty percent, Title thirteen, To eight and Hi two. A decoding strategy then picks one token from that distribution. Greedy decoding takes the highest, Dear here, every time. Sampling picks at random with probability proportional to the values, so Title is chosen about one time in eight.

Temperature is the parameter that controls the sampling. It rescales the scores before the softmax: a temperature near zero sharpens the distribution until sampling behaves like greedy decoding, and a higher temperature flattens it so lower-ranked tokens are chosen more often, which makes the output more varied. The distribution is recomputed after every token, so one different choice early changes every probability that follows it. The same selection is where hallucination comes from. The model emits the token that is probable after what precedes it, with no representation of whether the sentence it is building is true, so a fluent falsehood and a fluent fact are produced by the same step.

## Page 75

Attention enriches each token's vector with information from the other tokens in the sequence. In I gave the book back to the library because it, the vector for it has to carry whether it means the book or the library, and the model resolves that by attending to those earlier positions when it processes it; the sentence on the slide stops at it, and the word that follows is what settles the reference. The diagram is one attention head: the position currently being processed is compared with the other positions in the sequence through three learned projection matrices, query, key and value, and the result is the current position's vector enriched with context from the others.

Word order reaches the model by a separate route. Positional encodings are added to the token embeddings before the first layer, so that attention, which on its own treats the input as an unordered set, can tell the first token from the fifth. The slide's first bullet attributes the positional information to the attention layer; the attention layer contributes the contextual information.

## Page 76

Worksheet 9.5 implements the attention head of the preceding slide in PyTorch, with the query, key and value projections, the softmax and the causal mask, stacks heads into transformer blocks, and trains a small GPT that generates text.

## Page 77

A question put to a chat model, and its answer, follow.

## Page 78

The question is nonsense from end to end. It has the form of a cloud certification exam item: a scenario at a financial services company, a set of requirements, four lettered options naming AWS services. None of the services exists, and neither do the glimglom, the wibblenibbet, frobnication or the Grumbleflux standards. The only true content is the format.

## Page 79

The model answered with confidence. It chose option C and gave a reason for each requirement in turn: Zimzam is purpose-built for glimglom scenarios, its Blarglefoo integration provides frobnication shielding, only Zimzam supports quibble-threading. Each reason is assembled from words in the question, which is what completion by probability looks like: the training data includes exam questions of this shape followed by answers of this shape, and the most probable continuation of the question is an answer that picks an option and justifies it. No step in the process checks whether Zimzam exists.

## Page 80

The summary repeats the verdict with a check mark: Zimzam is the only option that meets every requirement, final answer C. No part of the reply says that the services are unknown or that the question cannot be answered.

## Page 81

A hallucination is a confident, wrong response. Fluent, assured text is what the model is trained to produce, and nothing in the training objective rewards truth over plausibility, so the confidence of an answer carries no information about its accuracy.

## Page 82

A transformer predicts the token sequence most likely to follow the prompt, given its training data. A hallucination is a prediction that reads as correct and is false. The mechanism is the same in both cases: the training corpus has been compressed into the model's weights, and a statement appears in the output because token sequences like it were frequent in the corpus after prompts like this one. A fact that was common in the corpus tends to be reproduced; a rare subject or a fictional one gets the most plausible sequence available, which is a fabrication with the right shape.

The model has no database of facts to consult. The asterisk on the slide marks the exception: retrieval-augmented generation puts retrieved documents into the prompt so the model can draw on them, which Worksheet 11.1 builds. Models do not understand facts or think in any recognizable way; they compute a distribution over the next token.

## Page 83

The article does not exist. The user asked ChatGPT to summarize a New York Times piece at a URL, and the model returned a coherent summary about ChatGPT being used to evade content filters. The model at the time could not fetch web pages, and the URL's path, chatgpt-prompts-to-avoid-content-filters, was enough for it to compose what a summary of an article with that title would say. It did not report that it had no access to the page. The example comes from the Wikipedia article on hallucination in artificial intelligence, linked at the foot of the slide.

## Page 84

The case is Mata v. Avianca, decided in the Southern District of New York in June 2023. Two lawyers filed a brief whose case citations and quotations had been produced by ChatGPT, and six of the cited decisions did not exist. Judge P. Kevin Castel fined the lawyers and their firm five thousand dollars; the slide spells the judge's name Casten. Attorney Steven Schwartz told the court he had not known that ChatGPT could produce false information. He had also asked ChatGPT whether the cases were real, and it had answered that they were: the same failure a second time, since the most plausible reply to a question about whether a citation is real is yes.

## Page 85

The sanctions continued through 2025. In July 2025 two attorneys representing the MyPillow chief executive in a Colorado defamation case were each ordered to pay three thousand dollars after filing a brief with about thirty defective citations. In California, attorneys from Ellis George LLP and K&L Gates LLP filed a brief with invented citations in a case against State Farm; the motion was denied, the briefs were struck from the record, and the attorneys paid thirty-one thousand dollars of the other side's legal fees. In Chicago, attorneys for the Chicago Housing Authority were found to have cited nonexistent cases in an appeal.

Citations are the worst case for a language model. A citation has a rigid form, party names, a reporter volume, a page number and a year, and the model produces that form whether or not a case behind it exists, so a fabricated citation is indistinguishable from a real one until someone looks it up.

## Page 86

Damien Charlotin, a legal researcher in Paris, maintains a public database of court decisions in which a party or a lawyer relied on hallucinated content. It records the court, the tool if known, the nature of the fabrication and the sanction, and it covers courts worldwide. At the time the slide was written it held over 1,785 cases, and the count rises as decisions are published.

## Page 87

The slide embeds a web video: a recording of a court hearing, published on the YouTube channel Audit the Court in May 2026, in which the judge questions a lawyer about having used AI. The database on the preceding slide is built from written decisions; the hearing is where one of them starts. The video is at https://www.youtube.com/watch?v=T_0MjD-UGaE.

## Page 88

Three Google AI Overview results from May 2024, the week the feature launched in the United States. Asked how many rocks to eat, it advised at least one small rock per day, citing geologists at UC Berkeley; the source was a satirical article in The Onion. Asked about cheese sliding off pizza, it suggested adding an eighth of a cup of non-toxic glue to the sauce; the source was a joke comment on Reddit. Asked how to pass kidney stones quickly, it advised drinking two quarts of urine every twenty-four hours, a garbling of medical advice to produce that much. The overview system retrieves pages and summarizes them, and the summarizer cannot tell satire from advice or notice that a sentence it rewrote now says the opposite of its source.

## Page 89

The query 1000 km to tomatoes is nonsense, and the overview answered it anyway: one thousand tomatoes equal one kilotomato. The cited source is a Reddit post about a mnemonic, five tomatoes for the 5,280 feet in a mile, which the model combined with the kilo prefix into a fluent sentence. This is the Zimzam question again in a search box: a well-formed query gets a well-formed answer regardless of whether one exists.

## Page 90

The examples are jokes until the outputs are used as reference answers. Search overviews and chat assistants are consulted for medical, legal and technical facts, and the lawyers on the preceding slides filed the results in court.

## Page 91

A person rejects eat one rock a day on sight. A model has no such check: it scores a sentence by how probable it is given its context, and a sentence copied from a satirical article that ranked highly in retrieval is probable. Sense is not a quantity the model computes.

## Page 92

A deterministic system returns the same result every time it is given the same input; a non-deterministic system is not guaranteed to. A vending machine is the slide's example: the same button returns the same product, and the machine on the right returned an onion. Code that parses a log line, a database query, a hash function and a fitted classifier are deterministic. A system that draws from a probability distribution is not, and a language model draws once per token. The slide's second bullet reads systems is; the subject and verb disagree.

## Page 93

If a rule can compute the answer, code should compute it. Parsing a timestamp, looking up an IP address, matching a signature or computing a hash runs in microseconds, costs nothing per call and gives the same answer every time. A language model call for the same task takes seconds, is billed per token and can answer differently on the next call, so for a deterministic workflow it is the slowest and most expensive option available.

A non-deterministic workflow has to be tested across many runs and many inputs. One passing run says nothing about the next, so evaluation means a held-out set of inputs with known correct outputs, scored over repeated runs, and re-scored whenever the prompt or the model changes.

## Page 94

Language models are non-deterministic by construction. Each token is drawn from a distribution, and a temperature of zero narrows the draw without making the output fixed: providers do not guarantee identical output for identical input, because batching and floating-point arithmetic on the GPU can change which of two near-equal tokens ranks first, and the model behind a name is updated over time. Some describe the variation as a feature rather than a defect, since it is what produces a different draft on each request; an application that needs the same answer twice has to be designed around it either way.

## Page 95

A generative model can classify by prompting. A prompt that presents the text and asks for one of a fixed set of labels returns a label, and Worksheet 10.2 does this. The cost is the non-determinism just described: the same input can get a different label on a rerun, the model can return a label outside the set or add an explanation that the calling code has to parse away, and every call takes seconds and tokens. The embedding-plus-classifier approach of Worksheet 9.1 is deterministic, free per call after training, and gives a probability that can be thresholded, so prompting is the choice when there is no labeled data and no time to build one.

## Page 96

The demo is an AI-enabled calculator that gets sums wrong on purpose. Its settings panel sets an error frequency, thirty percent by default, and an error magnitude from off by one or two up to off by ten to fifty, and the page states that it intentionally produces subtly incorrect results to demonstrate the risks of trusting AI outputs without verification. Arithmetic is the deterministic workflow of the preceding slides. A calculator that is right seven times in ten and wrong by a little the rest of the time is worse than a plain one, because every result now has to be checked, and checking a sum costs as much as computing it.

## Page 97

There is no single model to choose. Hugging Face hosts models by the hundred thousand, and the slide's figure of nearly a hundred thousand is dated; the hub passed one million in 2024. Some are general, trained to handle any text task; some are task-specific, trained or fine-tuned for one job such as sentiment or named entity recognition. The options are to use a task-specific model as is, to prompt a foundation model, or to fine-tune an existing model on your own data. The considerations: cost, per token for an API or per GPU hour for a self-hosted model; speed, the latency of a call, which grows with model size; size, which decides what hardware can run it; and license, which decides whether commercial use, modification and redistribution are allowed.

## Page 98

A model file is code, and code can be malicious. The formats in which models are shared can execute instructions when loaded: PyTorch's default save format is a Python pickle, and unpickling runs whatever Python the file contains, so a model file can carry a payload that executes the moment it is loaded. Researchers have demonstrated this by uploading working malicious models to Hugging Face, and malicious models placed by others have been found there; JFrog's security team reported about a hundred of them in February 2024, including one that opened a reverse shell to a remote host on load. Treat a downloaded model as a downloaded executable: take it from a publisher you trust, prefer the safetensors format, which stores only tensors and cannot execute code, and load pickle files with the weights-only option. Worksheet 9.6 covers the other route to a malicious model, poisoning its training data.

## Page 99

Close of Part 1.

## Page 100

Worksheet 9.6 finishes the build-your-own-LLM sequence in two halves. First, fine-tuning: the mini-GPT from 9.5 is pretrained on general English and then fine-tuned on real CVE descriptions until it produces vulnerability text. Second, poisoning: the same training step is fed tampered data, and the model's output changes to match, which is the lesson of the worksheet: whoever controls the training data controls the model.
