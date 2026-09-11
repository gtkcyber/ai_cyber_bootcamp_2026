## Page 1

TODO NEW SLIDE

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

TODO NEW SLIDE

## Page 14

This part lays out the stages of a supervised machine learning project and defines the terms for its inputs and outputs.

## Page 15

TODO NEW SLIDE

## Page 16

TODO NEW SLIDE

## Page 17

Three terms name the parts of a dataset. Features: the numeric representation of the original data, one column each; the set of features is a matrix, written X, with a row per record and a column per feature. Observations: the rows of X; in the lab each observation is one domain name. Target: the variable being predicted, written y, a vector with one entry per observation; in the lab it is the isDGA column, which labels each domain as algorithmically generated or legitimate.

The model is fitted to X and y together and applied to X alone. The target exists for the training records and is what the model produces for new ones.

## Page 18

TODO NEW SLIDE

## Page 19

TODO NEW SLIDE

## Page 20

TODO NEW SLIDE

## Page 21

TODO NEW SLIDE

## Page 22

TODO NEW SLIDE

## Page 23

TODO NEW SLIDE

## Page 24

TODO NEW SLIDE

## Page 25

TODO NEW SLIDE

## Page 26

TODO NEW SLIDE

## Page 27

A URL string is not usable input for a model. A classifier computes with numbers: it multiplies feature values by weights or compares them against thresholds, and a string of characters supports neither operation. The string has to be turned into numeric columns before any model can be fitted to it, and choosing which columns is the work of feature engineering.

## Page 28

TODO NEW SLIDE

## Page 29

Features are the representation of the problem that the model receives, and the representation has to be rich enough to describe the problem. The model receives no rules. It receives the columns and finds the pattern that links them to the target, so what it can find is bounded by what the columns encode, and a feature set that leaves out the property separating the classes leaves the model nothing to learn.

A good feature varies with the thing being predicted. The slide's example is a feature that is high when it rains and low when it is sunny; the feature carries information because its value moves with the outcome. A column that takes the same value for malicious and benign records carries none. High variance about the problem means that the feature's value differs between the outcomes.

## Page 30

A URL is made of parts, and each part is measured separately. Protocol: the scheme before the double slash, https here. Subdomain: the label in front of the registered domain, www. Zone apex: the registered domain together with its top-level domain, google.com, which is the name at which the owner's DNS zone begins. Domain: the registered name on its own, google. Top-level domain: the suffix administered by a registry, .com. Path: everything after the host, here /search followed by a query string of parameter and value pairs.

The parts carry different information. The domain is chosen and paid for by the registrant, so its characters reflect who registered it; the path and query string are produced by the server and can be any length and any content. Lexical features are therefore computed per part, and computing them starts with splitting the string correctly. A top-level domain can itself contain a dot, as in co.uk, so the split cannot be done by counting dots; tldextract, a Python library that splits a hostname into subdomain, domain and suffix using the public suffix list, does it correctly.

## Page 31

DNS resolves a domain name to an IP address, and the terms on the slide are the parts of that system. Registrar: the company, GoDaddy for example, accredited to register a unique name on the owner's behalf. Start of Authority record, abbreviated SOA: the record at the top of a zone that names its primary name server and its administrator and sets its timers, including the default time to live, which is how long a resolver may cache a record before asking again, and how long a secondary server waits before checking the primary for updates. The slide's State of Authority is a mislabel; the record's name is Start of Authority. Root zone: the top of the name hierarchy, managed by the Internet Assigned Numbers Authority. NS record: names the servers that hold the authoritative records for a zone, which is how a top-level domain server hands a query on to the zone's own name servers. A record: maps a name to an IPv4 address. CNAME record: maps one name to another name, which is then resolved in turn. Autonomous system number and Border Gateway Protocol data: identify which network announces the address and how traffic reaches it.

These records are the source of host-based features. Registration date and registrant come from WHOIS, the registries' ownership database; time to live and name servers come from DNS; the autonomous system number comes from routing data. The Python libraries on the slide fetch them: python-whois for WHOIS, dnspython for DNS queries, tldextract for splitting a hostname, and ipaddress for parsing and comparing addresses.

## Page 32

Resolving a name takes the nine steps in the diagram when nothing is cached. The end user's operating system sends the query to a DNS resolver, run by the ISP, the organization or a public service (step 1). The resolver asks a root name server, which does not know the address but replies with the name servers for the .com top-level domain (steps 2 and 3). The resolver asks a .com server, which replies with the name servers for google.com (steps 4 and 5). The resolver asks Google's name server, which holds the authoritative A record and replies with the address (steps 6 and 7). The resolver returns the address to the operating system (step 8), which connects to the web server directly (step 9). Each server answers only for the part of the hierarchy it is responsible for, and the resolver caches every answer for the record's time to live, so a repeat query for the same name skips steps 2 through 7.

## Page 33

TODO NEW SLIDE

## Page 34

Sahoo, Liu and Hoi's 2017 survey Malicious URL Detection using Machine Learning groups URL features into four families. Blacklist features: whether the URL or its host appears on a published list of known-bad entries; a blacklist misses anything not yet listed, so it has a high false negative rate, and list membership is still an informative column. Lexical features: measurements of the string itself, such as URL length, digit count, the lengths of the parts, and the entropy of the domain name, a measure of how unpredictable its next character is given the mix of characters it contains; they capture the tendency of malicious URLs to look different from benign ones and are computed from the string alone. Host-based features: properties of where the site is hosted, who owns it and how it is managed, such as registration date, geolocation, autonomous system number, connection speed and time to live; each needs WHOIS or DNS queries, so every row costs a network round trip. Content-based features: properties of the page's HTML or JavaScript; they require fetching and possibly executing the page, which is unsafe when the page is malicious and slow at scale, so they are the least used family.

The lab computes lexical features only. They need nothing beyond the string, so every row can be computed offline without a query to an outside service.

## Page 35

This part introduces domain generation algorithms and the lexical features that separate their output from legitimate domain names.

## Page 36

TODO NEW SLIDE

## Page 37

TODO NEW SLIDE

## Page 38

TODO NEW SLIDE

## Page 39

The raw table and the feature table are the same records before and after feature engineering. The raw table holds one row per URL with the string itself, the isMalicious label, the extracted domain and a creation timestamp. The feature table holds the same kind of rows as numbers: isMalicious is the target y, and every other column is a feature in X. isIP: whether the host is a bare IP address. Length and LengthDomain: character counts of the URL and of the domain. DigitsCount: the number of numerals. EntropyDomain: the entropy of the domain string. FirstDigitIndex: the position of the first numeral. com, org, net and the columns through w and waset: the bag-of-words columns, one per vocabulary token, holding the token's count in the URL, which for these tokens is zero or one.

The strings themselves do not enter the model; only the numeric columns do.

## Page 40

TODO NEW SLIDE

## Page 41

Preprocessing is the set of operations that turn cleaned data into columns a model accepts, and the choice among them is made per dataset and per model; that is the sense of the title. Imputing missing values: filling empty cells with a substitute such as the column mean. Scaling and normalization: putting columns on comparable numeric ranges. One-hot encoding: turning a categorical column into one zero-or-one column per category. Embedding: mapping a token to a learned vector of numbers so that tokens used in similar contexts get similar vectors; word2vec is one method. Binarizing: converting a multi-class label into one zero-or-one column per class, which a neural network's multi-class output layer needs. Encoding strings as integers: replacing each distinct string with a code number. Dimensionality reduction: replacing many correlated columns with fewer uncorrelated ones that keep most of the variation; principal component analysis is the method named on the slide. Augmentation: creating extra training examples by transforming existing ones, such as tilting or zooming images. Feature selection based on a classifier: fitting a model and keeping the columns it relies on. Variance threshold: dropping columns whose values hardly change, since a near-constant column cannot separate classes.

The images at the right are the data types these operations serve: numbers, text, time series, categories and binary flags. The libraries are pandas for the table operations, scikit-learn for the transformers, and SciPy for the numerical routines underneath.

## Page 42

TODO NEW SLIDE

## Page 43

TODO NEW SLIDE

## Page 44

TODO NEW SLIDE

## Page 45

TODO NEW SLIDE

## Page 46

pandas performs one-hot encoding with get_dummies. Called on a Series of six colors, it returns a table with one column per distinct value and one row per element. Called on a whole DataFrame with a columns argument, it encodes only the named columns, here protocol_type and flag, and leaves the rest untouched. prefix=None: name each new column after the source column. prefix_sep='_': join the source name and the category with an underscore, giving protocol_type_tcp. dummy_na=False: do not add a column marking missing values. sparse=False: return an ordinary dense table. pandas 2.0 and later return True and False in the new columns; pass dtype=int for ones and zeros.

## Page 47

Feature-engine is an open-source Python library, written by Soledad Galli, that packages feature engineering steps as scikit-learn style transformers: imputation of missing values, one-hot and other categorical encodings, capping of outliers at a chosen quantile, and more. Each transformer has a fit method that learns its parameters from the training data and a transform method that applies them, so a step fitted once is reapplied to new data unchanged and can sit inside a scikit-learn pipeline.

## Page 48

This part covers feature scaling: putting numeric columns on a common range so that no column dominates a model because of its units.

## Page 49

Standard scaling replaces each value with its z-score: the value minus the column mean, divided by the column standard deviation. The result says how many standard deviations the value sits above or below the column's average, so a scaled value of two means two standard deviations above the mean whatever the original units were. Every column ends up with mean zero and standard deviation one, and columns measured in bytes, seconds and counts become comparable.

Scaling matters for models that combine columns arithmetically. A distance-based model such as k-nearest neighbors, or a model fitted by gradient steps such as logistic regression or a neural network, is dominated by whichever column has the largest numeric range; a byte count in the millions outweighs an entropy value near three. Tree-based models split one column at a time against a threshold and are unaffected by scaling.

## Page 50

StandardScaler from sklearn.preprocessing is the transformer for z-scoring. Constructing it creates an object with no parameters yet; fit computes the mean and standard deviation of every column and stores them on the object; transform subtracts and divides using the stored values and returns the scaled matrix. fit_transform does both in one call and is the form to use on the training data. The test data gets transform alone, so that it is scaled with the training statistics.

## Page 51

The example scales a three-by-three matrix. The column means are 0.6, 0.3667 and 50, and the column standard deviations are 0.2449, 0.3091 and 8.165. The top-left value, 0.9, becomes 0.9 minus 0.6 divided by 0.2449, which is 1.2247; the value below it, 0.3, is the same distance below the mean and becomes negative 1.2247; the 0.6 sits on the mean and becomes zero. The means of the scaled columns print as zero, one of them as negative zero, which is a rounding artifact of floating point, and the standard deviations print as one.

StandardScaler divides by the population standard deviation, the root of the mean squared deviation, without the n minus one correction that pandas applies in its std method. A hand check with pandas therefore gives 0.3 for the first column, and the scaled values differ. The slide's numbers are the scikit-learn ones.

## Page 52

Min-max scaling maps each column onto the range zero to one: the value minus the column minimum, divided by the column maximum minus the column minimum. The smallest value becomes zero, the largest becomes one, and every other value keeps its relative position between them, so the shape of the column's distribution is preserved. A single extreme value sets the maximum, which compresses the rest of the column into a narrow band near zero, and a test value outside the training range scales to below zero or above one.

## Page 53

MinMaxScaler has the same interface as StandardScaler. fit records the minimum and maximum of every column; transform applies the formula with the recorded values; fit_transform does both on the training data. The stored minimum and maximum, like the stored mean and standard deviation, are what make the scaling repeatable on new records.

## Page 54

The same matrix under min-max scaling. In the first column the minimum is 0.3 and the maximum is 0.9, so 0.9 becomes one, 0.3 becomes zero, and 0.6, halfway between, becomes 0.5. In the second column 0.2 becomes 0.2 minus 0.1 divided by 0.8 minus 0.1, which is 0.1429. In the third, 40, 50 and 60 become zero, 0.5 and one. The means of the scaled columns are 0.5, 0.381 and 0.5 and the standard deviations are 0.4082, 0.4416 and 0.4082: only the endpoints are fixed by this method, and the mean and spread are whatever the data gives.

## Page 55

This part covers class imbalance: training data in which one class is far rarer than the other, and resampling as the remedy.

## Page 56

In security data the class of interest is rare: malicious records are a small fraction of the total, and the target column is imbalanced. Imbalance distorts fitting. A model that minimizes overall error is pulled toward the majority class, and a classifier that labels everything as normal scores high accuracy while detecting nothing, so the rare class is the one the model learns least about.

imbalanced-learn, a Python library built to work with scikit-learn, resamples the training data to even out the classes. Its methods fall into two families: over-sampling, which adds minority rows by duplicating existing ones or by synthesizing new ones between neighbors, and under-sampling, which discards majority rows.

## Page 57

RandomOverSampler duplicates randomly chosen minority rows until the classes are the same size. random_state=0 fixes the random draw so that the resampled set is the same on every run. fit_resample takes the feature matrix and the target and returns a new pair, X_resampled and y_resampled, longer than the originals by the number of duplicates added. Resample the training data only, after the split. Resampling the test data would score the model on duplicated rows and on a class ratio that the real data does not have, so the evaluation would no longer describe the data the model will be applied to.

## Page 58

This part covers feature selection: deciding which of the engineered columns go into the model and which are dropped.

## Page 59

Whether every engineered column belongs in the model is a decision. A column that carries no information about the target gives the model noise to fit, which costs accuracy on new records; a column that repeats another's information double-counts it; and every column costs compute and memory at training time and at prediction time. The question applies to the lab's six features as much as to a table with hundreds.

## Page 60

Two kinds of evidence answer the question. A scoring statistic rates each feature by how strongly it relates to the target and keeps the top scorers, which is fast and automatic. Plots of the features against the target and against each other show which ones separate the classes and which pairs carry the same information, which a per-feature score cannot detect. Both are applied to the same feature table, and the decision about what to drop comes from reading them together.

## Page 61

Three things are removed by hand before any automated selection runs. Unnecessary features, uninformative or repetitive: a column that is constant or nearly so cannot separate classes, and two columns that encode the same fact double-count it; in the lab's feature set, digits and firstDigitIndex are both zero on exactly the rows with no numerals, since a name without a digit has no first digit, so they share the information about whether a digit is present. Irrelevant features: columns with no relation to the target, such as a row identifier. Duplicate observations: identical rows, which weight one record more than once and, when the copies land on both sides of the train and test split, put training rows into the test set.

Automated scoring does not catch these. A scoring function rates each column against the target on its own, so two redundant columns both score well and both survive, and duplicate rows inflate every statistic computed on them.

## Page 62

SelectKBest scores every feature against the target with a chosen statistic and keeps the k highest; with score_func=chi2 and k=3 it keeps the three features with the largest chi-squared statistic. fit_transform computes the scores and returns the reduced matrix in one call. SelectPercentile keeps a share of the features by score; percentile=3 keeps the top three percent, which for a seven-column table comes to one column. The slide's caption for it, all features above a threshold in the scoring function, is inexact; SelectPercentile ranks the features and keeps a fraction of them, and a score threshold is a different selector.

The scoring functions are chosen by the task. For classification: chi2, the chi-squared test of independence between a non-negative feature such as a count and the class; f_classif, the analysis-of-variance F statistic comparing the feature's mean across classes; and mutual_info_classif, an estimate of mutual information. For regression: f_regression and mutual_info_regression, the same ideas against a numeric target. chi2 requires non-negative features, so it suits bag-of-words counts and rejects a z-scored column. All of these are univariate: each feature is scored alone against the target.

## Page 63

Plotting is the second answer. The views the lab draws from the same feature table are a correlation matrix as a heatmap, a pairplot colored by class, a radviz projection, and a bar chart of mutual information with the target.

## Page 64

The three lines produce the heatmap. corr computes the Pearson correlation of every pair of columns in df_final_int, the feature table with isDGA already encoded as an integer so that the target can be correlated too. np.triu(np.ones_like(corr_mat, dtype=bool)) builds a boolean matrix that is true on and above the diagonal; passed as mask, it tells seaborn, the plotting library built on matplotlib and imported as sns, to leave those cells blank. cmap='viridis' picks the purple-to-yellow color scale, and the trailing semicolon suppresses the printed representation of the returned axes in a notebook. The link at the foot of the slide is Yellowbrick's Rank2D visualizer, which draws the same pairwise matrix through a scikit-learn style API.

## Page 65

A pairplot draws every feature against every other. Each off-diagonal cell is a scatter of one feature against another with points colored by the target, and each diagonal cell is the distribution of one feature drawn separately for each class. seaborn's pairplot takes the feature table and the name of the target column as hue. The example on the slide comes from a tumor diagnosis dataset with classes M for malignant and B for benign.

Two readings come out of it. On the diagonal, two class histograms that barely overlap mark a feature that separates the classes on its own; in the example, the malignant class sits to the right of the benign class on every feature. Off the diagonal, points that fall along a line, rising or falling, mark two features that are correlated and so carry the same information, and one of them is a candidate to drop; all three features in the example rise together. The upper and lower triangles are mirror images, so one of them can be ignored.

## Page 66

TODO NEW SLIDE

## Page 67

Mutual information measures how much knowing a feature's value reduces uncertainty about the target. It is zero when the two are independent and grows with any kind of dependence, whatever its shape. Pearson correlation measures straight-line association only, so a feature that flags the positive class at both ends of its range and the negative class in the middle has a correlation near zero and a mutual information well above it. Ranking features by mutual information therefore surfaces predictive columns that a correlation matrix scores near zero.

## Page 68

The bar chart ranks the lab's features by mutual information with isDGA. ngrams, entropy, vowel-cons and length score close together, each around 0.26 to 0.28; digits scores about 0.07 and firstDigitIndex about 0.015. The four strong features each carry roughly the same amount of information about whether a name is generated, and the two digit-based features carry little.

The code separates the table into features, everything except isDGA, and target, the isDGA column as integers, calls mutual_info_classif to get one score per column, wraps the scores in a Series indexed by column name so that they sort and label themselves, and draws a horizontal bar chart. mutual_info_classif estimates the quantity from nearest neighbors and adds a small amount of random noise to break ties, so the scores differ slightly from run to run unless random_state is set.

## Page 69

fg-data-profiling, the current name of the package released earlier as pandas-profiling and then ydata-profiling, generates a full report on a DataFrame in one call: per-column statistics and histograms, missing-value and duplicate counts, warnings, and correlation matrices under several coefficients. ProfileReport takes the DataFrame and a title and returns the report object, which a notebook renders inline or saves as HTML. The computation covers every column and every pair of columns, which is what the slide's computationally intense refers to.

## Page 70

The per-variable panel for digits. Distinct count, twenty-two, and unique, 1.1 percent: the column takes twenty-two different values across two thousand rows. Zeros, 1670 or 83.5 percent: most domains contain no digit at all. The quantile block makes the same point: minimum, fifth percentile, first quartile, median and third quartile are all zero, the ninety-fifth percentile is nine and the maximum is twenty-seven, so the interquartile range is zero and the whole spread of the column is confined to its top sixth. The descriptive block shows the consequence: a mean of 1.19 pulled up from the zero median by the tail, a standard deviation of 3.23 larger than the mean, and skewness of 3.1 and kurtosis of 10.9, both marking a long right tail. The histogram at the top right is a single bar at zero with a sliver beside it.

A column shaped like this separates only the sixth of the names that contain digits and says nothing about the rest, which is why its mutual information with the target is low.

## Page 71

TODO NEW SLIDE

## Page 72

The warnings tab lists four findings. Two duplicate rows, 0.1 percent of the table: remove them before selection. digits has 1670 zeros and firstDigitIndex has 1670 zeros, the same count, because both are zero on exactly the names that contain no numeral; on 83.5 percent of the rows the two columns are identical, and they differ only on the remaining sixth, so they are close to redundant. vowel-cons has 87 zeros, 4.3 percent: names with no vowel, and names with no consonant, for which the helper function returns zero in place of a division by zero.

## Page 73

The correlations tab draws the full correlation matrix, diagonal included, with blue for positive and red for negative values on a scale from negative one to one. It is the same Pearson matrix as the heatmap drawn by hand, so the blue cells linking isDGA with length, digits and entropy and the red cells for ngrams and vowel-cons against the target repeat the earlier reading. The other tabs recompute the matrix with different coefficients. Spearman's rho: the Pearson correlation of the ranks, which measures any monotonic relation, straight-line or not. Kendall's tau: the balance of concordant against discordant pairs, another rank measure. Phik: a coefficient that works across numeric and categorical columns and picks up non-linear dependence, with values from zero to one.

## Page 74

TODO NEW SLIDE

## Page 75

Closing slide for questions on the module.
