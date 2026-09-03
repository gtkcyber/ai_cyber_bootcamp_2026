## Page 1

Module 3 covers feature engineering: turning raw records such as a URL into numeric columns a model can learn from, preparing those columns by imputation, encoding, scaling and resampling, and choosing which of them to keep. The worked example throughout is detecting domain names produced by a domain generation algorithm.

## Page 2

The machine learning module has four parts: feature selection and engineering, an overview of classification models without the mathematics, evaluating model performance, and improving it. This deck is the first part. Features come first because a model is fitted to its features, so what the features encode bounds what any model built on them can learn.

## Page 3

The question is whether large language models have made classical machine learning unnecessary. Classical machine learning here means models such as logistic regression, decision trees and random forests, fitted to a table of numeric features and a column of labels. A language model can be asked to analyze a dataset or to write the code that fits such a model, which is where the question comes from.

## Page 4

The first form of the question is whether the analysis itself can be handed to a language model: put the data in the prompt and ask for the finding. Analysis here means the exploratory work of Module 1 and the classification work of this module, summarizing a dataset, finding structure in it, and deciding which records are malicious.

## Page 5

The second form is whether a language model can be given the data and asked to deliver a trained classifier, so that nobody on the team writes or fits the model. Delivering a classifier means writing the training code, running it against the data, and adjusting it until its predictions are good enough to act on.

## Page 6

The answer to both questions is no. The reasons are properties of how large language models work.

## Page 7

A deterministic function returns the same output every time it is given the same input; a non-deterministic function does not. A fitted classifier is deterministic. Its prediction is a fixed calculation over the fitted parameters and the feature values, so the same row always gets the same score.

Large language models are non-deterministic. They produce text by sampling each next token from a probability distribution, and even with sampling switched off, providers do not guarantee identical output for identical input. Two runs of the same prompt over the same data can return different findings, and nothing in the model records which run was right.

## Page 8

A requirement of guaranteed consistency rules out a non-deterministic component. Consistency means the same verdict for the same input on every run, and any output that is acted on automatically or compared against an earlier run needs it. A non-deterministic function cannot meet the requirement, and prompt wording does not change the property, because the randomness enters at the decoding step, after the prompt has been read.

## Page 9

An audit requires that a result can be reproduced and its cause traced. A trained model supports both. The training data, the code, the fitted parameters and the feature values behind each prediction are all stored, so a prediction can be recomputed exactly and the features that drove it inspected. A language model supports neither. Its output cannot be rerun to the same answer, the weights that produced the answer are not interpretable, and an explanation it writes for its own answer is itself generated text with no link to the computation that produced the answer.

## Page 10

The better approach is to ask the language model for code. The model drafts the code that computes a feature, fits a model or draws a chart; a person reads the draft, runs it, and keeps it. The result then comes from deterministic code running over the data, which can be rerun, tested and audited. The model's non-determinism is confined to the drafting step, where a reviewer can reject a bad draft before it runs.

## Page 11

A language model can write the code that fits a model, and it cannot tune one. Tuning is the loop of fitting, measuring on held-out data, records kept out of the fit, changing a setting, and fitting again: which features to keep, how complex the model may be, where to put the decision threshold. Each change is chosen from the numbers the last fit produced and from which kind of error the use case can tolerate, and a model that only writes the code sees neither.

## Page 12

A language model is expensive and slow per prediction compared with a trained classifier. Each call runs the input through billions of parameters, takes seconds, and is billed per token. A fitted logistic regression scores a row with one weighted sum passed through the logistic function, and a random forest with one pass down each of its trees; both run locally with no cost per call. The difference is multiplied by the number of records scored, and network telemetry is scored one record at a time.

## Page 13

The cartoon's subject is tool fit. A chainsaw will spread butter, and a butter knife does the job with none of the cost or risk. A large language model applied to a classification problem is the chainsaw: it can produce a verdict for a domain or a URL, at a cost in money and time that a classifier fitted to a handful of numeric columns does not carry, and without the reproducibility the classifier gives.

## Page 14

This part lays out the stages of a supervised machine learning project and defines the terms for its inputs and outputs.

## Page 15

A supervised machine learning project runs through the stages in the diagram. Getting and cleaning data: loading the records and fixing missing or malformed values, done in pandas, the Python library for tabular data. Preprocessing and feature engineering: computing numeric columns from the raw records and putting them on a usable scale, done in pandas and in scikit-learn, the Python machine learning library, pronounced sy-kit learn and imported as sklearn. Advanced feature selection: dropping columns that carry no information about the target, done in scikit-learn. The output of these three stages is the dataset that the modeling stages consume.

The dataset is split into training data and test data. The model is built from the training data alone and evaluated on the test data, so the evaluation measures how the model behaves on records it was not fitted on. The arrows running back from evaluation to model building and to the preparation stages show that the process iterates: a poor evaluation sends the analyst back to change the model, the features or the cleaning.

## Page 16

Three terms name the parts of a dataset. Features: the numeric representation of the original data, one column each; the set of features is a matrix, written X, with a row per record and a column per feature. Observations: the rows of X; in the lab each observation is one domain name. Target: the variable being predicted, written y, a vector with one entry per observation; in the lab it is the isDGA column, which labels each domain as algorithmically generated or legitimate.

The model is fitted to X and y together and applied to X alone. The target exists for the training records and is what the model produces for new ones.

## Page 17

The choice of method follows from the data. Labeled data, meaning every record carries the value to be predicted, leads to supervised learning, and the type of that value picks the method. A quantity leads to regression, which predicts a number and supports inference about which inputs move it. A category leads to classification, which predicts a class. Without labels, the question is whether labels can be obtained, by hand labeling or from an existing source such as a blocklist; if they can, the supervised methods apply. If they cannot, what remains is clustering and pattern finding: recommenders, similarity search and anomaly detection. The chart marks this branch nothing proven because no label exists to check the output against, so the result is a structure found in the data, with no way to score it as right or wrong.

Detecting generated domains sits on the classification branch. Each domain is labeled legitimate or generated, and the label is a category.

## Page 18

A URL string is not usable input for a model. A classifier computes with numbers: it multiplies feature values by weights or compares them against thresholds, and a string of characters supports neither operation. The string has to be turned into numeric columns before any model can be fitted to it, and choosing which columns is the work of feature engineering.

## Page 19

Three features are computed from the domain part of the URL. domain_length: the number of characters in google, six. vowel_count: the number of vowels in it, three. digit_count: the number of digits in it, zero. Each is a whole number a model can compute with, and together they form one row of the feature matrix for this URL.

The features are measured on google alone. The protocol and the www prefix say nothing about the site behind them, so counting their characters would add a constant to every row and separate nothing. Which part of a URL to measure is itself a feature engineering decision.

## Page 20

Features are the representation of the problem that the model receives, and the representation has to be rich enough to describe the problem. The model receives no rules. It receives the columns and finds the pattern that links them to the target, so what it can find is bounded by what the columns encode, and a feature set that leaves out the property separating the classes leaves the model nothing to learn.

A good feature varies with the thing being predicted. The slide's example is a feature that is high when it rains and low when it is sunny; the feature carries information because its value moves with the outcome. A column that takes the same value for malicious and benign records carries none. High variance about the problem means that the feature's value differs between the outcomes.

## Page 21

A URL is made of parts, and each part is measured separately. Protocol: the scheme before the double slash, https here. Subdomain: the label in front of the registered domain, www. Zone apex: the registered domain together with its top-level domain, google.com, which is the name at which the owner's DNS zone begins. Domain: the registered name on its own, google. Top-level domain: the suffix administered by a registry, .com. Path: everything after the host, here /search followed by a query string of parameter and value pairs.

The parts carry different information. The domain is chosen and paid for by the registrant, so its characters reflect who registered it; the path and query string are produced by the server and can be any length and any content. Lexical features are therefore computed per part, and computing them starts with splitting the string correctly. A top-level domain can itself contain a dot, as in co.uk, so the split cannot be done by counting dots; tldextract, a Python library that splits a hostname into subdomain, domain and suffix using the public suffix list, does it correctly.

## Page 22

DNS resolves a domain name to an IP address, and the terms on the slide are the parts of that system. Registrar: the company, GoDaddy for example, accredited to register a unique name on the owner's behalf. Start of Authority record, abbreviated SOA: the record at the top of a zone that names its primary name server and its administrator and sets its timers, including the default time to live, which is how long a resolver may cache a record before asking again, and how long a secondary server waits before checking the primary for updates. The slide's State of Authority is a mislabel; the record's name is Start of Authority. Root zone: the top of the name hierarchy, managed by the Internet Assigned Numbers Authority. NS record: names the servers that hold the authoritative records for a zone, which is how a top-level domain server hands a query on to the zone's own name servers. A record: maps a name to an IPv4 address. CNAME record: maps one name to another name, which is then resolved in turn. Autonomous system number and Border Gateway Protocol data: identify which network announces the address and how traffic reaches it.

These records are the source of host-based features. Registration date and registrant come from WHOIS, the registries' ownership database; time to live and name servers come from DNS; the autonomous system number comes from routing data. The Python libraries on the slide fetch them: python-whois for WHOIS, dnspython for DNS queries, tldextract for splitting a hostname, and ipaddress for parsing and comparing addresses.

## Page 23

Resolving a name takes the nine steps in the diagram when nothing is cached. The end user's operating system sends the query to a DNS resolver, run by the ISP, the organization or a public service (step 1). The resolver asks a root name server, which does not know the address but replies with the name servers for the .com top-level domain (steps 2 and 3). The resolver asks a .com server, which replies with the name servers for google.com (steps 4 and 5). The resolver asks Google's name server, which holds the authoritative A record and replies with the address (steps 6 and 7). The resolver returns the address to the operating system (step 8), which connects to the web server directly (step 9). Each server answers only for the part of the hierarchy it is responsible for, and the resolver caches every answer for the record's time to live, so a repeat query for the same name skips steps 2 through 7.

## Page 24

The two lists differ in their characters, and the differences are the features. The blocklist entries carry marks of automated or deceptive construction: a hostname built from a brand name and German words joined by hyphens under the .xyz top-level domain (amazon-sicherheit.kunden-ueberpruefung.xyz), an executable in the path (eng.exe), paths ending in strings with no dictionary words (rxdjna2.html, fx29id1.txt), and a path through the administrator directory of a content management system. The allowlist entries are shorter, use recognizable names and readable path words, and sit under .com, .ru and .org.

The separation is not clean. bohicacapital.com and summerweb.net on the blocklist look like ordinary sites, and 333cn.com and the long numeric user ID in the google.com entry on the allowlist have the digit-heavy look of a generated name. No single rule separates the lists. Each property is a tendency, and a model weighs many tendencies at once, which is the reason for computing many lexical features.

## Page 25

Sahoo, Liu and Hoi's 2017 survey Malicious URL Detection using Machine Learning groups URL features into four families. Blacklist features: whether the URL or its host appears on a published list of known-bad entries; a blacklist misses anything not yet listed, so it has a high false negative rate, and list membership is still an informative column. Lexical features: measurements of the string itself, such as URL length, digit count, the lengths of the parts, and the entropy of the domain name, a measure of how unpredictable its next character is given the mix of characters it contains; they capture the tendency of malicious URLs to look different from benign ones and are computed from the string alone. Host-based features: properties of where the site is hosted, who owns it and how it is managed, such as registration date, geolocation, autonomous system number, connection speed and time to live; each needs WHOIS or DNS queries, so every row costs a network round trip. Content-based features: properties of the page's HTML or JavaScript; they require fetching and possibly executing the page, which is unsafe when the page is malicious and slow at scale, so they are the least used family.

The lab computes lexical features only. They need nothing beyond the string, so every row can be computed offline without a query to an outside service.

## Page 26

This part introduces domain generation algorithms and the lexical features that separate their output from legitimate domain names.

## Page 27

A domain generation algorithm produces a list of pseudo-random domain names from a seed, and malware uses the list to find its command server. The infected machine and the operator run the same algorithm with the same seed, so both compute the same list for the day; the operator registers one name on it, and the infected machine tries names from the list until one resolves. Blocking or seizing that name does not close the channel, because the next day's list is different, and a defender who wants to cut the channel has to register or block every name on it while the operator needs only one.

The technique was made widely known by the Conficker worm of 2008, whose later variants generated tens of thousands of candidate names a day. Detecting generated names is called the hello world of cyber machine learning because labeled examples are easy to obtain, from published algorithm output and from lists of legitimate domains, and because the names differ from real ones in ways that features computed from the string alone capture.

## Page 28

Mark Bowden's Worm: The First Digital World War, published in 2011, is a book-length account of Conficker and of the working group that tried to contain it by registering the domains the worm's algorithm would generate before its operators could.

## Page 29

The exercise derives lexical features from each domain string. Length of URL: the character count of the full string. Length of domain: the character count of the registered name alone. Count of digits: how many characters are numerals. Entropy of domain: Shannon entropy, computed by taking each distinct character's share of the string, multiplying each share by its base-two logarithm, summing, and negating; a name that uses a few characters repeatedly scores low and a name whose characters are spread evenly over the alphabet scores high. Position of the first digit: the one-based index of the first numeral, zero when there is none. Bag-of-words for the top-level domain, domain and path: one column per vocabulary token holding how many times the token occurs in that part.

Worksheet 3.1 computes length, digit count, entropy, the vowel-to-consonant ratio, the first-digit index and an n-gram score, which measures how much of the name is built from character sequences common in English words, for each domain in its data file, using helper functions supplied in the notebook. Each feature encodes a way in which an algorithm's output differs from a name a person chose: a generator drawing characters at random spreads them evenly, which raises entropy, places digits at any position, and does not keep the vowel-to-consonant balance of English words.

## Page 30

The raw table and the feature table are the same records before and after feature engineering. The raw table holds one row per URL with the string itself, the isMalicious label, the extracted domain and a creation timestamp. The feature table holds the same kind of rows as numbers: isMalicious is the target y, and every other column is a feature in X. isIP: whether the host is a bare IP address. Length and LengthDomain: character counts of the URL and of the domain. DigitsCount: the number of numerals. EntropyDomain: the entropy of the domain string. FirstDigitIndex: the position of the first numeral. com, org, net and the columns through w and waset: the bag-of-words columns, one per vocabulary token, holding the token's count in the URL, which for these tokens is zero or one.

The strings themselves do not enter the model; only the numeric columns do.

## Page 31

A bag-of-words model turns text into counts: each token in a fixed vocabulary becomes a column, and a document's row holds how many times each token occurs in it, with word order discarded. scikit-learn's CountVectorizer builds the matrix; fit establishes the vocabulary, here imposed as the three top-level domains .com, .de and .uk, and transform counts the vocabulary tokens in each string. In the example, facebook.com gets a one in the .com column, google.de a one in the .de column, and google.ru zeros in every column because .ru is outside the vocabulary. A fixed vocabulary keeps the column count under control for a part of the URL, such as the top-level domain or the path, that takes a large number of distinct values, and anything outside it becomes invisible.

The example as printed does not run as intended. CountVectorizer's default tokenizer keeps only runs of two or more word characters, so .com is tokenized as com, which is not in a vocabulary spelled with dots, and every row comes back zero. Either spell the vocabulary without dots and pass each top-level domain without its dot, or supply a tokenizer that keeps the dot.

## Page 32

Preprocessing is the set of operations that turn cleaned data into columns a model accepts, and the choice among them is made per dataset and per model; that is the sense of the title. Imputing missing values: filling empty cells with a substitute such as the column mean. Scaling and normalization: putting columns on comparable numeric ranges. One-hot encoding: turning a categorical column into one zero-or-one column per category. Embedding: mapping a token to a learned vector of numbers so that tokens used in similar contexts get similar vectors; word2vec is one method. Binarizing: converting a multi-class label into one zero-or-one column per class, which a neural network's multi-class output layer needs. Encoding strings as integers: replacing each distinct string with a code number. Dimensionality reduction: replacing many correlated columns with fewer uncorrelated ones that keep most of the variation; principal component analysis is the method named on the slide. Augmentation: creating extra training examples by transforming existing ones, such as tilting or zooming images. Feature selection based on a classifier: fitting a model and keeping the columns it relies on. Variance threshold: dropping columns whose values hardly change, since a near-constant column cannot separate classes.

The images at the right are the data types these operations serve: numbers, text, time series, categories and binary flags. The libraries are pandas for the table operations, scikit-learn for the transformers, and SciPy for the numerical routines underneath.

## Page 33

Imputation fills a missing cell with a value computed from the rest of the column, because scikit-learn estimators reject a feature matrix containing missing values. The first line fills missing src_bytes with the column's most frequent value: value_counts sorts the distinct values by frequency, index[0] is the top one, and fillna writes it into every empty cell. The second fills missing dst_bytes with the column mean. The most frequent value suits discrete or categorical columns, where a mean would be a value no record has; the mean suits continuous columns, with the caveat that a few extreme values pull it, in which case the median is the safer fill. Whichever statistic is used, compute it on the training data and reuse the same number on the test data.

## Page 35

One-hot encoding replaces a categorical column with one zero-or-one column per category. The Color column has four categories, so it becomes four columns, Color_Red, Color_Blue, Color_Yellow and Color_Green; each row has a one in the column of its own color and zeros elsewhere, and the original column is deleted. The name comes from digital circuits, where a one-hot signal has exactly one line high.

The encoding exists because a model reads integers as quantities. Coding red, blue, green and yellow as one to four would tell the model that yellow is twice blue and that green lies between them, relations that colors do not have. Four binary columns carry the category with no ordering imposed. The cost is width: a column with a thousand distinct values becomes a thousand columns.

## Page 36

pandas performs one-hot encoding with get_dummies. Called on a Series of six colors, it returns a table with one column per distinct value and one row per element. Called on a whole DataFrame with a columns argument, it encodes only the named columns, here protocol_type and flag, and leaves the rest untouched. prefix=None: name each new column after the source column. prefix_sep='_': join the source name and the category with an underscore, giving protocol_type_tcp. dummy_na=False: do not add a column marking missing values. sparse=False: return an ordinary dense table. pandas 2.0 and later return True and False in the new columns; pass dtype=int for ones and zeros.

## Page 37

Feature-engine is an open-source Python library, written by Soledad Galli, that packages feature engineering steps as scikit-learn style transformers: imputation of missing values, one-hot and other categorical encodings, capping of outliers at a chosen quantile, and more. Each transformer has a fit method that learns its parameters from the training data and a transform method that applies them, so a step fitted once is reapplied to new data unchanged and can sit inside a scikit-learn pipeline.

## Page 38

The encoder is set up, fitted and applied in three steps. OneHotCategoricalEncoder is constructed with two settings. top_categories=3: encode only the three most frequent categories of each variable, so a variable with hundreds of values produces three columns and a row holding any other value gets zeros in all three. drop_last=False: keep every column; True would drop one, because with all categories present the last column is implied by the others. fit scans the training data to find which categories are the top three; transform adds the columns and drops the originals. The fitted encoder is reused on test data, which is what keeps the column set identical between the two.

Current Feature-engine releases moved this class: the import is from feature_engine.encoding import OneHotEncoder, with the same arguments.

## Page 39

A label column of strings is turned into integers with replace. PROBE lists four attack names from the KDD Cup 1999 intrusion dataset, each with the trailing period that dataset uses, and replace rewrites every cell holding one of them to the integer one. Repeating the call for each attack family, with a different integer per family and zero for normal, turns the label column into class codes a classifier can fit to.

A classifier treats each distinct target value as a class label with no order among them, so integer codes suit a target column. A feature column is read as quantities, with three larger than one, which is why categorical features get one-hot encoding.

## Page 40

This part covers feature scaling: putting numeric columns on a common range so that no column dominates a model because of its units.

## Page 41

A scaler is fitted on the training data once, and the fitted scaler transforms both the training data and the test data. The slide's second sentence is cut off. The consequence it was going to state is that fitting the two sets separately produces two different sets of scaling parameters, so the same raw value maps to different scaled values in the two sets and the thresholds the model learned on the training scale no longer line up with the test data. Fitting on the test set also lets its statistics into the preprocessing, so the evaluation stops being a measurement on unseen data. The same rule applies to every fitted preprocessing step: imputers and encoders as well as scalers.

## Page 42

Standard scaling replaces each value with its z-score: the value minus the column mean, divided by the column standard deviation. The result says how many standard deviations the value sits above or below the column's average, so a scaled value of two means two standard deviations above the mean whatever the original units were. Every column ends up with mean zero and standard deviation one, and columns measured in bytes, seconds and counts become comparable.

Scaling matters for models that combine columns arithmetically. A distance-based model such as k-nearest neighbors, or a model fitted by gradient steps such as logistic regression or a neural network, is dominated by whichever column has the largest numeric range; a byte count in the millions outweighs an entropy value near three. Tree-based models split one column at a time against a threshold and are unaffected by scaling.

## Page 43

StandardScaler from sklearn.preprocessing is the transformer for z-scoring. Constructing it creates an object with no parameters yet; fit computes the mean and standard deviation of every column and stores them on the object; transform subtracts and divides using the stored values and returns the scaled matrix. fit_transform does both in one call and is the form to use on the training data. The test data gets transform alone, so that it is scaled with the training statistics.

## Page 44

The example scales a three-by-three matrix. The column means are 0.6, 0.3667 and 50, and the column standard deviations are 0.2449, 0.3091 and 8.165. The top-left value, 0.9, becomes 0.9 minus 0.6 divided by 0.2449, which is 1.2247; the value below it, 0.3, is the same distance below the mean and becomes negative 1.2247; the 0.6 sits on the mean and becomes zero. The means of the scaled columns print as zero, one of them as negative zero, which is a rounding artifact of floating point, and the standard deviations print as one.

StandardScaler divides by the population standard deviation, the root of the mean squared deviation, without the n minus one correction that pandas applies in its std method. A hand check with pandas therefore gives 0.3 for the first column, and the scaled values differ. The slide's numbers are the scikit-learn ones.

## Page 45

Min-max scaling maps each column onto the range zero to one: the value minus the column minimum, divided by the column maximum minus the column minimum. The smallest value becomes zero, the largest becomes one, and every other value keeps its relative position between them, so the shape of the column's distribution is preserved. A single extreme value sets the maximum, which compresses the rest of the column into a narrow band near zero, and a test value outside the training range scales to below zero or above one.

## Page 46

MinMaxScaler has the same interface as StandardScaler. fit records the minimum and maximum of every column; transform applies the formula with the recorded values; fit_transform does both on the training data. The stored minimum and maximum, like the stored mean and standard deviation, are what make the scaling repeatable on new records.

## Page 47

The same matrix under min-max scaling. In the first column the minimum is 0.3 and the maximum is 0.9, so 0.9 becomes one, 0.3 becomes zero, and 0.6, halfway between, becomes 0.5. In the second column 0.2 becomes 0.2 minus 0.1 divided by 0.8 minus 0.1, which is 0.1429. In the third, 40, 50 and 60 become zero, 0.5 and one. The means of the scaled columns are 0.5, 0.381 and 0.5 and the standard deviations are 0.4082, 0.4416 and 0.4082: only the endpoints are fixed by this method, and the mean and spread are whatever the data gives.

## Page 48

This part covers class imbalance: training data in which one class is far rarer than the other, and resampling as the remedy.

## Page 49

In security data the class of interest is rare: malicious records are a small fraction of the total, and the target column is imbalanced. Imbalance distorts fitting. A model that minimizes overall error is pulled toward the majority class, and a classifier that labels everything as normal scores high accuracy while detecting nothing, so the rare class is the one the model learns least about.

imbalanced-learn, a Python library built to work with scikit-learn, resamples the training data to even out the classes. Its methods fall into two families: over-sampling, which adds minority rows by duplicating existing ones or by synthesizing new ones between neighbors, and under-sampling, which discards majority rows.

## Page 50

RandomOverSampler duplicates randomly chosen minority rows until the classes are the same size. random_state=0 fixes the random draw so that the resampled set is the same on every run. fit_resample takes the feature matrix and the target and returns a new pair, X_resampled and y_resampled, longer than the originals by the number of duplicates added. Resample the training data only, after the split. Resampling the test data would score the model on duplicated rows and on a class ratio that the real data does not have, so the evaluation would no longer describe the data the model will be applied to.

## Page 51

This part covers feature selection: deciding which of the engineered columns go into the model and which are dropped.

## Page 52

Whether every engineered column belongs in the model is a decision. A column that carries no information about the target gives the model noise to fit, which costs accuracy on new records; a column that repeats another's information double-counts it; and every column costs compute and memory at training time and at prediction time. The question applies to the lab's six features as much as to a table with hundreds.

## Page 53

Two kinds of evidence answer the question. A scoring statistic rates each feature by how strongly it relates to the target and keeps the top scorers, which is fast and automatic. Plots of the features against the target and against each other show which ones separate the classes and which pairs carry the same information, which a per-feature score cannot detect. Both are applied to the same feature table, and the decision about what to drop comes from reading them together.

## Page 54

Three things are removed by hand before any automated selection runs. Unnecessary features, uninformative or repetitive: a column that is constant or nearly so cannot separate classes, and two columns that encode the same fact double-count it; in the lab's feature set, digits and firstDigitIndex are both zero on exactly the rows with no numerals, since a name without a digit has no first digit, so they share the information about whether a digit is present. Irrelevant features: columns with no relation to the target, such as a row identifier. Duplicate observations: identical rows, which weight one record more than once and, when the copies land on both sides of the train and test split, put training rows into the test set.

Automated scoring does not catch these. A scoring function rates each column against the target on its own, so two redundant columns both score well and both survive, and duplicate rows inflate every statistic computed on them.

## Page 55

SelectKBest scores every feature against the target with a chosen statistic and keeps the k highest; with score_func=chi2 and k=3 it keeps the three features with the largest chi-squared statistic. fit_transform computes the scores and returns the reduced matrix in one call. SelectPercentile keeps a share of the features by score; percentile=3 keeps the top three percent, which for a seven-column table comes to one column. The slide's caption for it, all features above a threshold in the scoring function, is inexact; SelectPercentile ranks the features and keeps a fraction of them, and a score threshold is a different selector.

The scoring functions are chosen by the task. For classification: chi2, the chi-squared test of independence between a non-negative feature such as a count and the class; f_classif, the analysis-of-variance F statistic comparing the feature's mean across classes; and mutual_info_classif, an estimate of mutual information. For regression: f_regression and mutual_info_regression, the same ideas against a numeric target. chi2 requires non-negative features, so it suits bag-of-words counts and rejects a z-scored column. All of these are univariate: each feature is scored alone against the target.

## Page 56

Plotting is the second answer. The views the lab draws from the same feature table are a correlation matrix as a heatmap, a pairplot colored by class, a radviz projection, and a bar chart of mutual information with the target.

## Page 57

The heatmap is the correlation matrix of the lab's feature table with the target included. Each cell is the Pearson correlation between its row's column and its column's column, on a scale from negative 0.6 in dark purple to above 0.8 in yellow; the upper triangle and the diagonal are blank because they would repeat the lower triangle and the self-correlations of one.

The first column is the relation of each feature to isDGA. length and entropy are positively correlated with the target, both around 0.5; ngrams is the most negatively correlated, near negative 0.6, and vowel-cons is also negative, near negative 0.5. Generated names are longer, have more evenly spread characters, contain fewer English letter sequences and have fewer vowels relative to consonants than real names. digits and firstDigitIndex sit near zero and tell the model little on their own.

The remaining cells are the relations among features. length and entropy are the brightest pair, above 0.8, so they carry much of the same information: a longer name has room for more distinct characters. ngrams and vowel-cons are positively correlated with each other, near 0.6, since both measure how English-like a name is. Pairs like these are the candidates for dropping one member.

## Page 58

The three lines produce the heatmap. corr computes the Pearson correlation of every pair of columns in df_final_int, the feature table with isDGA already encoded as an integer so that the target can be correlated too. np.triu(np.ones_like(corr_mat, dtype=bool)) builds a boolean matrix that is true on and above the diagonal; passed as mask, it tells seaborn, the plotting library built on matplotlib and imported as sns, to leave those cells blank. cmap='viridis' picks the purple-to-yellow color scale, and the trailing semicolon suppresses the printed representation of the returned axes in a notebook. The link at the foot of the slide is Yellowbrick's Rank2D visualizer, which draws the same pairwise matrix through a scikit-learn style API.

## Page 59

A pairplot draws every feature against every other. Each off-diagonal cell is a scatter of one feature against another with points colored by the target, and each diagonal cell is the distribution of one feature drawn separately for each class. seaborn's pairplot takes the feature table and the name of the target column as hue. The example on the slide comes from a tumor diagnosis dataset with classes M for malignant and B for benign.

Two readings come out of it. On the diagonal, two class histograms that barely overlap mark a feature that separates the classes on its own; in the example, the malignant class sits to the right of the benign class on every feature. Off the diagonal, points that fall along a line, rising or falling, mark two features that are correlated and so carry the same information, and one of them is a candidate to drop; all three features in the example rise together. The upper and lower triangles are mirror images, so one of them can be ignored.

## Page 60

Mutual information measures how much knowing a feature's value reduces uncertainty about the target. It is zero when the two are independent and grows with any kind of dependence, whatever its shape. Pearson correlation measures straight-line association only, so a feature that flags the positive class at both ends of its range and the negative class in the middle has a correlation near zero and a mutual information well above it. Ranking features by mutual information therefore surfaces predictive columns that a correlation matrix scores near zero.

## Page 61

The bar chart ranks the lab's features by mutual information with isDGA. ngrams, entropy, vowel-cons and length score close together, each around 0.26 to 0.28; digits scores about 0.07 and firstDigitIndex about 0.015. The four strong features each carry roughly the same amount of information about whether a name is generated, and the two digit-based features carry little.

The code separates the table into features, everything except isDGA, and target, the isDGA column as integers, calls mutual_info_classif to get one score per column, wraps the scores in a Series indexed by column name so that they sort and label themselves, and draws a horizontal bar chart. mutual_info_classif estimates the quantity from nearest neighbors and adds a small amount of random noise to break ties, so the scores differ slightly from run to run unless random_state is set.

## Page 62

fg-data-profiling, the current name of the package released earlier as pandas-profiling and then ydata-profiling, generates a full report on a DataFrame in one call: per-column statistics and histograms, missing-value and duplicate counts, warnings, and correlation matrices under several coefficients. ProfileReport takes the DataFrame and a title and returns the report object, which a notebook renders inline or saves as HTML. The computation covers every column and every pair of columns, which is what the slide's computationally intense refers to.

## Page 63

The report's overview tab summarizes the lab's feature table. Number of variables, seven: the six features and isDGA. Number of observations, two thousand: one row per domain. Missing cells, zero: no imputation is needed. Duplicate rows, two: identical rows to drop before selection. Variable types: six numeric columns and one boolean, the target. The Reproduction tab records when and how the report was generated, and the Warnings tab, with four entries, lists the findings the report flags.

## Page 64

The per-variable panel for digits. Distinct count, twenty-two, and unique, 1.1 percent: the column takes twenty-two different values across two thousand rows. Zeros, 1670 or 83.5 percent: most domains contain no digit at all. The quantile block makes the same point: minimum, fifth percentile, first quartile, median and third quartile are all zero, the ninety-fifth percentile is nine and the maximum is twenty-seven, so the interquartile range is zero and the whole spread of the column is confined to its top sixth. The descriptive block shows the consequence: a mean of 1.19 pulled up from the zero median by the tail, a standard deviation of 3.23 larger than the mean, and skewness of 3.1 and kurtosis of 10.9, both marking a long right tail. The histogram at the top right is a single bar at zero with a sliver beside it.

A column shaped like this separates only the sixth of the names that contain digits and says nothing about the rest, which is why its mutual information with the target is low.

## Page 65

The warnings tab lists four findings. Two duplicate rows, 0.1 percent of the table: remove them before selection. digits has 1670 zeros and firstDigitIndex has 1670 zeros, the same count, because both are zero on exactly the names that contain no numeral; on 83.5 percent of the rows the two columns are identical, and they differ only on the remaining sixth, so they are close to redundant. vowel-cons has 87 zeros, 4.3 percent: names with no vowel, and names with no consonant, for which the helper function returns zero in place of a division by zero.

## Page 66

The correlations tab draws the full correlation matrix, diagonal included, with blue for positive and red for negative values on a scale from negative one to one. It is the same Pearson matrix as the heatmap drawn by hand, so the blue cells linking isDGA with length, digits and entropy and the red cells for ngrams and vowel-cons against the target repeat the earlier reading. The other tabs recompute the matrix with different coefficients. Spearman's rho: the Pearson correlation of the ranks, which measures any monotonic relation, straight-line or not. Kendall's tau: the balance of concordant against discordant pairs, another rank measure. Phik: a coefficient that works across numeric and categorical columns and picks up non-linear dependence, with values from zero to one.

## Page 67

Worksheet 3.1 applies the deck to the domain data. Part 1 derives the features listed for the exercise: Task A with the notebook's helper functions, and Task B the n-gram score following Schiavoni, Maggi, Cavallaro and Zanero's 2014 paper Phoenix: DGA-based Botnet Tracking and Intelligence, computed by summing, over each name's one-, two- and three-character sequences, how often the sequence occurs in Google's list of the ten thousand most common English words, dividing by the number of sequences, and averaging over the three lengths. The domain column is then dropped, leaving the numeric table.

Part 2 visualizes the result. The target strings are encoded as integers, the correlation of each feature with the target is computed, and the feature table is drawn as a correlation heatmap, a pairplot colored by class, a radviz projection, in which each feature anchors a point on a circle and each record is placed by the balance of its feature values, and a mutual information ranking. An optional last step generates the profiling report. A breakpoint cell loads a prepared feature file for anyone whose Part 1 did not finish.

## Page 68

Closing slide for questions on the module.
