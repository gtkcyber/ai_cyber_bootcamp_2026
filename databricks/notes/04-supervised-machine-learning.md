## Page 1

TODO NEW SLIDE

## Page 2

TODO NEW SLIDE

## Page 3

TODO NEW SLIDE

## Page 5

TODO NEW SLIDE

## Page 6

TODO NEW SLIDE

## Page 7

TODO NEW SLIDE

## Page 9

TODO NEW SLIDE

## Page 11

TODO NEW SLIDE

## Page 13

TODO NEW SLIDE

## Page 14

TODO NEW SLIDE

## Page 15

TODO NEW SLIDE

## Page 17

TODO NEW SLIDE

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

A decision tree is a chain of questions. Each box is a node that tests one feature; each arrow is one outcome of the test; each red box is a leaf that holds the prediction. Reading a prediction starts at the root and follows the branch that matches the observation until a leaf is reached. In the example, credited to Charles Givre, one of the course's instructors, the root asks whether the gadget costs under two hundred dollars; if it does, the answer is yes. If not, the next node asks whether Charles's wife approves; if she does, yes. If she does not, the last node asks whether she will notice, and the branch drawn leads to yes. Every leaf is yes, which is the joke, and the structure is what a fitted tree looks like: features at the internal nodes, thresholds on the branches, class labels at the leaves.

## Page 24

A boundary that traces individual observations is a sign of overfitting. Left: hand-drawn outlines around the cyber observations, curving to include each one and exclude the beer observations between them. Right: a fitted tree's regions on the same data, with a red cyber region that has a notch, a step and a gray island inside it, each produced by a split that exists to capture one or two observations. A model overfits when it learns the particular training observations, including their noise and mislabeled records, rather than the pattern that generated them. Training accuracy reaches one hundred percent while the boundaries are set by single points, so new observations near those points are misclassified. A tree can always be grown deep enough to give every training observation its own pure region, which is why trees need limits on growth: in scikit-learn, max_depth bounds the number of tests from root to leaf and min_samples_leaf sets the fewest observations a leaf may hold.

## Page 26

TODO NEW SLIDE

## Page 27

TODO NEW SLIDE

## Page 28

TODO NEW SLIDE

## Page 29

TODO NEW SLIDE

## Page 30

TODO NEW SLIDE

## Page 31

TODO NEW SLIDE

## Page 32

Group A is purer. Fifteen of its sixteen observations are blue, so a leaf made from it would predict blue and be wrong once. Group B is half blue and half red, the most impure a two-class group can be, and a leaf made from it would be wrong half the time whichever class it predicted. A split is good when its child groups are purer than the parent.

## Page 33

TODO NEW SLIDE

## Page 34

Information gain is the entropy of the parent minus the weighted average entropy of the children, each child weighted by its share of the parent's observations. The parent here holds two white and two red circles, so its entropy is one bit, the most impure a two-class group can be. Three candidate features are compared. Feature one sends three circles left, two white and one red, and one red circle right; the gain is 0.3112 bits. Feature two sends one white and one red each way; each child is as mixed as the parent, so the gain is zero. Feature three sends both whites left and both reds right; both children are pure, so the gain is the full one bit. Feature three gives the best split. A tree grows by computing this number for every feature and every threshold at a node, taking the largest, and repeating in each child.

## Page 35

The advantages of a single decision tree. Regression or classification: a leaf can hold a class label or a numeric value. Graphical display: the fitted tree can be drawn as a diagram of tests and outcomes. Interpretability: the path from the root to a leaf is the complete reason for a prediction. Rules: each root-to-leaf path reads as an if-then rule, close to how people write down a decision procedure. Fast prediction: one comparison per level of the tree. No scaling: each test compares one feature with a threshold in that feature's own units, so the range of one feature has no effect on another. Feature interactions: a test lower in the tree applies only within the region the tests above it defined, so the effect of one feature can depend on the value of another, which makes a tree a non-linear model. Irrelevant features: a feature that does not produce the best split at any node is not used, even when there are many such features. Non-linear relationships: when the relationship between the features and the target is far from a straight line, a tree fits it where a linear model cannot.

## Page 36

The disadvantages of a single decision tree. Accuracy: one tree is generally beaten by the best supervised methods, including the ensembles of trees covered next. Overfitting: without limits on growth a tree keeps splitting until every leaf is pure, so tuning of depth and leaf size is required. High variance: a small change in the training data can change the first split, and every split below it is then chosen inside different regions, so the whole tree changes. Greedy splitting: the tree picks the split with the best information gain at each node without looking ahead, and a sequence of locally best splits need not be the best tree. Unbalanced classes: when one class dominates, the purest groups are the ones that contain only the majority class, so the tree learns little about the minority. Very small datasets: with few observations there are too few per leaf for the leaf's class proportions to mean anything.

## Page 37

This part covers the k-nearest neighbors classifier, which predicts the class of an observation from the classes of the training observations closest to it. The mathematics is again left out.

## Page 38

The k-nearest neighbors algorithm has one setting, k, the number of neighbors consulted. For each observation to be classified: find the k training observations nearest to it by distance; assign the class held by the majority of those neighbors; optionally give each neighbor a weight that decreases with its distance, so nearer neighbors count more in the vote. There is no fitting step in the usual sense. The model is the stored training data, and every prediction is computed from it at prediction time. The distance is Euclidean, the straight-line distance in feature space, unless another measure is chosen.

## Page 40

The example plots training observations from a host by two features, proc and mem, colored by state, infected or normal. The star is the observation to classify. With k equal to one, the single nearest training observation decides: it is normal, so the star is assigned normal, even though infected observations lie a short distance beyond it.

## Page 41

With k equal to five, the circle around the star encloses its five nearest training observations: four normal and one infected. The vote is four to one, so the star is again assigned normal. A larger k averages over a wider neighborhood, so a single stray training observation of the wrong class can no longer decide a prediction on its own, and the boundary between the classes becomes smoother. Too large a k and the neighborhood reaches into the other class's territory, so the majority class of the whole dataset starts to win everywhere. An odd k avoids tied votes between two classes.

## Page 42

Further reading: Kevin Zakka's 2016 post, A Complete Guide to K-Nearest-Neighbors with Applications in Python and R, which works through the algorithm, the choice of k, and code.

## Page 43

The advantages of k-nearest neighbors. Noisy, non-linear data: the boundary is whatever the local votes produce, with no assumed shape, and a few mislabeled observations are outvoted by their neighbors when k is larger than one. Feature and distance choices: any set of features and any distance measure can be used. Large datasets: more stored observations make each neighborhood denser. Multi-class problems: a vote works for any number of classes with no change to the method.

The disadvantages. The value of k: it must be chosen, and the chart on the previous slides is one way to see why it matters. Slow prediction: fitting only stores the training data, but each prediction computes the distance to every stored observation; a spatial index such as a k-d tree or ball tree, which scikit-learn builds by default, reduces the number of distances computed. Meaningful distance: Euclidean distance adds up differences across features, so a feature with a large numeric range dominates the sum, and features must be scaled to comparable ranges before the distances mean anything.

## Page 44

This part covers ensembles, models built by combining the predictions of several models. The photo is the word's original sense, a group of musicians playing together.

## Page 45

Ensemble learning combines several predictive models into one combined model that is more accurate than any of its members. The combination rule depends on the task. Regression: average the members' predictions. Classification: take a vote and use the most common prediction, or average the members' predicted class probabilities and take the class with the highest average.

## Page 46

Two conditions make ensembling work. Accuracy: each member does better than random guessing. Independence: the members' predictions come from different processes, so their errors are not the same errors. Under those conditions the mistakes that one member makes on its own are unlikely to be shared by the rest, and averaging or voting discards them. Condorcet's jury theorem, published by the Marquis de Condorcet in 1785 for juries, is the formal version: if each voter is right with probability above one half and the voters are independent, the probability that the majority is right increases toward one as voters are added.

## Page 47

Bagging, short for bootstrap aggregating, is the simplest tree ensemble. A bootstrap sample is a sample the size of the training set drawn with replacement, so some observations appear more than once and others not at all; each sample differs from the others. Grow n trees, one on each of n bootstrap samples. Have each tree predict. Combine the predictions: the average for regression trees, a majority vote for classification trees. The reason it helps is the high variance of single trees. Each tree's errors depend on its particular sample, and averaging trees grown on different samples cancels much of that variation.

## Page 48

A random forest is bagging with one change at each split. The ensemble is still decision trees grown on bootstrap samples of the training set. When a tree considers a split, it draws a random subset of m features from the full p and may only split on one of those m; a new subset is drawn for every split of every tree. For classification, m is typically the square root of p; for regression, somewhere between a third of p and p. The change decorrelates the trees. Without it, a single strong feature would be chosen at the top of nearly every bagged tree, the trees would look alike, and averaging alike trees removes little variance. With it, trees are forced to use different features, their errors differ more, and the average improves.

## Page 49

Two parameters of a random forest need tuning. The number of trees, n_estimators in scikit-learn: how many bootstrap samples are drawn and trees grown. The number of features considered at each split, max_features in scikit-learn: the m of the previous slide.

## Page 50

The second tuning chart plots the same error against max_features from one to seven. Error drops from about 4.7 with one feature per split to about 3.5 at six, then rises slightly at seven, so for this data considering six features per split is best. With too few candidates the probability that the best feature for a split is among them is low, and the trees are weak; with all seven the trees are strongly correlated and the average gains less.

The diagram is how a fitted forest classifies one instance. The instance is passed down every tree; each tree follows its own path of tests to a leaf and returns a class. Tree one returns class A, trees two and n return class B. The votes are tallied as a proportion, class A with p percent and class B with the rest, and the majority wins. The proportion is also the forest's predicted probability for each class.

## Page 52

TODO NEW SLIDE

## Page 53

The advantages of a random forest. Accuracy: competitive with the best supervised methods. Feature importance: the importance of a feature can be averaged across hundreds of trees that each used different features, which is more reliable than the estimate from one tree. Out-of-sample error without a holdout: each bootstrap sample leaves out about a third of the training observations, and those observations can be predicted by the trees that were not fitted on them; the resulting out-of-bag error estimates performance on new data without a train and test split or cross-validation.

The disadvantages. Interpretability: with hundreds of trees there is no single path to read as the reason for a prediction. Training time: hundreds of trees are grown instead of one. Prediction time: every tree must be evaluated for every prediction.

## Page 54

TODO NEW SLIDE

## Page 55

TODO NEW SLIDE

## Page 56

Every supervised model in scikit-learn is used the same way. Create the classifier or regressor object, such as a random forest classifier. Call its fit method with the training feature matrix X, a two-dimensional array with one row per observation and one column per feature, and the training target vector y, a one-dimensional array with one label per row. Call its predict method with a feature matrix of the same width, which returns a vector with one prediction per row. The uniform interface is why the deck can switch between models with a single changed line.

## Page 57

TODO NEW SLIDE

## Page 58

TODO NEW SLIDE

## Page 60

The supervised learning chapter of the scikit-learn user guide lists these families. Generalized linear models: logistic regression and its relatives, a weighted sum of the features passed through a link function. Kernel ridge: ridge regression combined with the kernel trick. Support vector machines, nearest neighbors and trees: covered above. Gaussian processes: a Bayesian method that returns a probability distribution with each prediction. Naive Bayes: applies Bayes' theorem under the assumption that features are independent given the class; it appears later in this deck as GaussianNB. Neural networks: the multilayer perceptron, the subject of the deep learning module. AdaBoost: boosting, which fits models in sequence with each new model weighting the observations the earlier ones got wrong. Gradient tree boosting: boosting where each new tree fits the remaining errors of the ensemble so far. Ensemble methods: bagging, random forests and voting combinations of any models.

<!-- MERGE: a second old note landed on this page; fold or drop -->

The grid is the classifier comparison example from the scikit-learn documentation. Each row is one synthetic two-class dataset: two interleaved crescents, a ring around a central cluster, and two clusters that a straight line nearly separates. Each column is one classifier fitted to that data, with the colored background as its decision regions and its accuracy on held-out points in the corner. The shapes of the regions are the point. The linear support vector machine can only draw a straight line, so it scores 0.40 on the ring, no better than chance. The decision tree and random forest draw rectangles. The radial basis function support vector machine, the Gaussian process and nearest neighbors draw smooth curves that follow the crescents and the ring. Naive Bayes and quadratic discriminant analysis draw ellipses. No classifier wins every row, which is why the model is chosen by measuring it on the data at hand.

## Page 61

The scikit-learn home page organizes the library into six areas. Classification: assigning a category, with support vector machines, nearest neighbors and random forests as examples. Regression: predicting a continuous value. Clustering: grouping similar objects without labels. Dimensionality reduction: reducing the number of variables, with principal component analysis as the first example. Model selection: comparing and tuning models, with grid search, cross-validation and metrics as the modules, which is the rest of this deck. Preprocessing: feature extraction and normalization. The library is built on NumPy, SciPy and matplotlib and is released under the BSD license, which permits commercial use.

## Page 62

The cheat sheet is the library's own flowchart for choosing an algorithm. The first question is whether there are more than fifty samples; fewer means get more data. The next is what is being predicted. A category with labeled data leads to the classification branch: under a hundred thousand samples, start with a linear support vector classifier; if that does not work and the data is text, try naive Bayes; otherwise try the k-neighbors classifier, then a kernel support vector classifier or an ensemble. Over a hundred thousand samples, use the stochastic gradient descent classifier, with kernel approximation as the fallback. A category without labels leads to clustering, a quantity to regression, and no target at all to dimensionality reduction. The chart encodes rules of thumb about sample size and model cost, and the recommendation to start simple and escalate only when the simple model fails.

## Page 63

The reference page for a classifier begins with its constructor signature, every parameter with its default. For the decision tree classifier the first three are criterion, gini impurity by default with entropy as the alternative; splitter, whether the best split or the best of a random subset is chosen at each node; and max_features, the number of features considered per split. Every parameter has a description beneath the signature, and the growth limits that control overfitting are all here.

## Page 64

The same page documents the two methods every classifier shares, with the shapes of their arguments. The feature matrix X passed to fit has shape n_samples by n_features, one row per observation and one column per feature; the target y has shape n_samples, one label per row. The matrix passed to predict has the same width as the one used to fit, and the return value has one entry per row of it. Most shape errors in a scikit-learn script are a one-dimensional array passed where the two-dimensional X is expected, or a matrix whose column count differs from the one the model was fitted on.

## Page 65

Fitting sets attributes on the classifier object, and the documentation lists them under Attributes. The names end in an underscore, the library's convention for a value computed by fit rather than supplied by the user. For a decision tree they include classes_, the labels the model knows; feature_importances_, one number per feature measuring how much the splits on that feature reduced impurity across the tree, normalized to sum to one; and n_features_, the number of columns fit was given. Reading feature_importances_ after fitting is the direct way to see which features the tree used.

## Page 66

Clustering and dimensionality reduction methods have a different set of methods. The k-means page has fit with y equal to None, because there are no labels; fit_predict, which fits and returns a cluster index per sample; transform, which maps each sample to its distances from the cluster centers; and fit_transform, which does both in one call. Transform in place of predict is the pattern for any method whose output is new features rather than a label, including principal component analysis and the scalers used in preprocessing. The distinction matters for pipelines, where each intermediate step must have transform and only the last step has predict.

## Page 67

TODO NEW SLIDE

## Page 68

The code applies LIME to a tabular model, with the library from Ribeiro's GitHub repository. The explainer is built once from the training data, the feature names and the class names; discretize_continuous set to False keeps the numeric features as they are. The explain_instance call takes one test row, the model's predict_proba method, which LIME calls on its perturbed copies of the row, the number of features to report, and the number of classes to explain. The result renders in the notebook in three parts. Prediction probabilities: the model gives this domain a probability of one for the DGA class. Contributions: horizontal bars, one per feature, on the side of the class the feature pushed toward; the n-gram score pushes hardest toward DGA, length pushes toward legitimate, and vowel-to-consonant ratio, entropy and digit count contribute less. Values: the feature values of the row itself. The features are the ones engineered for the domain generation algorithm task in the feature engineering module.

## Page 69

TODO NEW SLIDE

## Page 70

TODO NEW SLIDE

## Page 71

A classifier's mistakes come in two kinds. A false positive, also called a type I error, is a prediction of the positive class for an observation that belongs to the negative class; the picture is a doctor telling a man he is pregnant. A false negative, a type II error, is a prediction of the negative class for an observation that belongs to the positive class; the picture is a doctor telling a visibly pregnant woman she is not. With malicious as the positive class, a false positive is a benign record flagged and a false negative is a malicious record passed through. The two kinds cost different things, so the metrics that follow count them separately.

## Page 72

TODO NEW SLIDE

## Page 73

TODO NEW SLIDE

## Page 74

TODO NEW SLIDE

## Page 75

TODO NEW SLIDE

## Page 76

TODO NEW SLIDE

## Page 77

TODO NEW SLIDE

## Page 78

The targets illustrate the everyday meanings of accurate and precise. Accurate means close to the center, the true value; precise means tightly grouped, the same result each time. The four combinations are all possible: a tight group in the center, a tight group off to one side, a loose scatter around the center, and a loose scatter off center. The classification metrics with the same names are defined differently: accuracy is the fraction of all predictions that are correct, and precision is the fraction of positive predictions that are correct. The picture is a caution that the words carry a second meaning.

## Page 79

TODO NEW SLIDE

## Page 80

TODO NEW SLIDE

## Page 81

TODO NEW SLIDE

## Page 83

Precision and recall pull against each other. Precision is the proportion of positive identifications that are correct; recall is the proportion of actual positives that were identified. A model that flags only the observations it is surest of makes few false positives, so its precision is high, and misses the doubtful positives, so its recall is low. A model that flags anything doubtful finds the positives, so its recall is high, and sweeps in negatives, so its precision falls. Which to favor depends on the cost of each kind of error.

<!-- MERGE: a second old note landed on this page; fold or drop -->

The chart, from Google's machine learning crash course, is the mechanism behind the trade-off. Each dot is an observation placed by the score the classifier gave it, from zero to one; circles are true negatives and crossed squares are true positives. The classification threshold, here 0.67, converts a score into a label: everything to its right is called positive. At this threshold no negative crosses the line, so the false positive count is zero and precision is one, but twenty-one positives fall short of it and are called negative, so recall is 0.56.

## Page 84

The same scores with the threshold lowered to 0.23. Every positive now clears the line, so false negatives are zero and recall is one, but twenty-seven negatives clear it too, so precision falls to 0.64. Nothing about the model changed between the two charts; only the cutoff moved. A classifier with a score output has a whole family of precision and recall pairs, one per threshold, and choosing the threshold is choosing which error to accept.

## Page 85

The threshold set to 0.55, between the two extremes. Forty positives clear it and eight do not; four negatives clear it and forty-seven do not. Precision is 0.91 and recall 0.83, and accuracy, at 0.88, is higher than at either extreme, because both kinds of error are now small. Neither metric is at its maximum, which is the usual result of a threshold chosen to balance them.

## Page 86

The receiver operating characteristic curve plots the true positive rate against the false positive rate. The true positive rate is recall, the fraction of positives found; the false positive rate is the fraction of negatives wrongly called positive, false positives over false positives plus true negatives. Each point on the curve is one threshold, and sweeping the threshold from one down to zero traces the curve from the lower left, where nothing is called positive, to the upper right, where everything is. The curve needs the classifier's scores rather than its labels, so the plotting call takes the predicted probabilities. The code uses the scikit-plot library's plot_roc function with matplotlib to draw it. The name comes from radar operators in the Second World War, whose ability to tell signal from noise was measured the same way.

## Page 87

The area under the receiver operating characteristic curve summarizes the whole curve in one number, so it measures the classifier across every threshold rather than at one. It runs from zero to one. A classifier whose every prediction is wrong scores zero; one whose every prediction is right scores one; one that assigns scores at random scores one half, the diagonal from corner to corner. The area equals the probability that a randomly chosen positive receives a higher score than a randomly chosen negative, which is why it does not depend on a threshold. In scikit-learn it is roc_auc_score, and like the curve it expects scores or probabilities. Passing hard zero-or-one predictions, as the variable name on the slide suggests, collapses the curve to a single point and returns the average of the true positive rate and the true negative rate at that one threshold.

## Page 88

TODO NEW SLIDE

## Page 89

TODO NEW SLIDE

## Page 91

TODO NEW SLIDE

## Page 92

ConfusionMatrixDisplay draws the matrix as a colored grid. The confusion_matrix call takes the true labels, the predictions, and the model's classes_ attribute as the label order, so the rows and columns are guaranteed to line up with the names passed to the display. The example is a decision tree on the domain generation task. Of two hundred forty-four generated domains in the test set, two hundred twenty-three were called dga and twenty-one legit; of two hundred fifty-six legitimate domains, two hundred nineteen were called legit and thirty-seven dga. The colormap argument sets the color scale; summer maps low counts to dark green and high counts to yellow.

## Page 93

A classification report lists precision, recall and F1 score for every class; the heatmap is the same table with color for magnitude. F1 score is the harmonic mean of precision and recall, a single number that is high only when both are high. For this random forest on a benign-versus-malignant dataset, benign has precision 0.903, recall 0.953 and F1 0.927, and malignant has precision 0.914, recall 0.828 and F1 0.869. The lighter cells of the malignant row are the model's weak spot: about seventeen percent of malignant cases are missed. The heatmap needs a separate library; Charles Givre submitted a pull request to add the display to scikit-learn itself.

## Page 94

Two reports side by side compare a random forest with a support vector classifier on the same data. The forest's cells are all dark, every value above 0.82. The support vector classifier's malignant row has recall 0.594 and F1 0.731, so it misses four of every ten malignant cases even though its malignant precision is 0.950. The color makes the comparison immediate: one weak cell in the second report is the reason to prefer the first model, and no single accuracy number would have located it.

## Page 95

The code uses Yellowbrick, a visualization library that wraps scikit-learn models. ClassificationReport takes the model and the class names. Its fit method fits the model on the training data, its score method computes the metrics on the test data, and poof renders the heatmap. Yellowbrick renamed poof to show in its 1.0 release, so current versions require the newer name.

## Page 96

TODO NEW SLIDE

## Page 97

TODO NEW SLIDE

## Page 98

TODO NEW SLIDE

## Page 99

TODO NEW SLIDE

## Page 100

TODO NEW SLIDE

## Page 101

A single holdout split gives a score that depends on which rows happened to land in the test portion. The better approach is to make several different train and test splits, compute the test score for each, and average them. The average is a more stable estimate, and every observation gets used for testing once and for training the rest of the time.

## Page 103

K-fold cross-validation is the standard way to make those splits. Divide the dataset into K equal partitions, called folds. Use fold one as the testing set and the union of the other folds as the training set, and compute the testing accuracy. Repeat K times, with a different fold as the testing set each time. Take the average of the K testing accuracies as the estimate of out-of-sample accuracy. Each observation is tested once and trained on K minus one times.

## Page 104

In scikit-learn the whole procedure is one call. cross_val_score takes the classifier, the features, the target and the number of folds as cv, and returns an array of one score per fold; the mean of that array is the estimate. The function fits a fresh copy of the classifier for each fold, so the classifier object passed in is left unfitted. The default score for a classifier is accuracy, and a scoring argument selects another metric such as F1 or the area under the receiver operating characteristic curve.

## Page 106

A learning curve plots the training score and the cross-validation score against the number of training examples. In the chart the training score, in red, starts at one with eighty examples and falls toward 0.95 as more are added; the cross-validation score, in green, starts at 0.875 and rises to meet it near 0.94. The gap between the curves is the overfitting: with few examples the model fits them perfectly and generalizes worse. Converging curves at a high score are a good fit. Two curves that converge at a low score mean the model is too simple for the data, and a cross-validation curve still rising at the right edge means more data would help. In scikit-learn, LearningCurveDisplay.from_estimator draws the chart from a model, the data and a scoring choice; the code uses Gaussian naive Bayes with weighted F1, though the chart's title is a linear support vector classifier from a different run.

## Page 107

Topics the module has left for later. Saving models: a fitted model is serialized to disk with pickle so it can be loaded and used without refitting. Feature importances: the list at the right, from a domain classifier, gives each feature's share of the impurity reduction; DurationCreated carries more than half of the total and the top-level-domain indicator columns com, net, org and ru carry almost none. Bag-of-words features: a vocabulary of tokens produces a matrix that is mostly zeros, stored as a sparse matrix. Production readiness: an accuracy of 0.86 is not acceptable, because fourteen of every hundred predictions are wrong, and applied to the volume of lookups a network produces, the wrong ones on the benign side are a stream of false alerts. Improvement comes from more and better data, changes to feature engineering and selection, and a different model. Word2vec embeddings with deep learning are one route for text features, covered in the deep learning module.

## Page 108

TODO NEW SLIDE

## Page 109

TODO NEW SLIDE

## Page 110

This part covers hyperparameter tuning. A hyperparameter is a setting fixed before fitting, such as the number of trees, the maximum depth, or the C of a support vector machine, as opposed to the parameters that fit computes. The picture is a flashlight over a mountain range at night: the score as a function of the settings is a landscape that cannot be seen whole, and tuning is a search over it. The general form of the problem is optimization, of which gradient descent, which follows the local slope downhill, is the method used inside the fitting of many models.

## Page 111

The constructor signature of a random forest classifier is the list of its hyperparameters with their defaults. The ones in red are candidates for tuning: the class weights, the split criterion, the depth limit, the features per split, the leaf limit, the minimum impurity decrease for a split, the minimum samples per leaf and per split, the number of trees, and the number of parallel jobs. The defaults on the slide are from an older release: the number of trees now defaults to one hundred rather than ten, max_features now defaults to sqrt rather than auto, and min_impurity_split has been removed.

## Page 112

Two search strategies in scikit-learn. GridSearchCV: the user lists the candidate values for each hyperparameter, and every combination is fitted and scored by cross-validation. RandomizedSearchCV: a fixed number of combinations is drawn at random from the lists or distributions supplied, and only those are fitted. The grid is exhaustive and its cost multiplies with every added value; the random search bounds the cost in advance.

## Page 113

A parameter grid for a support vector classifier. The grid is a list of two dictionaries, and each dictionary is searched on its own. The first tries the linear kernel with C at one, ten, one hundred and one thousand. The second tries the radial basis function kernel with the same four values of C and two values of gamma. Gamma applies only to the radial basis function kernel; it sets how far the influence of a single training observation reaches, with a large gamma giving a boundary that bends tightly around individual points. Listing the kernels in separate dictionaries keeps gamma out of the linear kernel's combinations, so the grid has four plus eight, twelve candidates rather than sixteen.

## Page 114

A full grid over a random forest. Six hyperparameters with two or three values each give two hundred sixteen combinations, and each combination is scored by cross-validation, so the number of fits is that times the number of folds. GridSearchCV takes the classifier and the grid; its fit method runs every candidate on the features and target. The cv_results_ attribute afterward holds the parameters and the fold scores of every candidate, and the report function prints the best ones. The timing lines around the fit are there to compare the cost with the random search on the next slide. The code is the randomized search example from the scikit-learn documentation.

## Page 115

The same hyperparameters as distributions rather than lists. Where the grid gave three fixed values, sp_randint, the discrete uniform distribution from SciPy, draws any integer in a range: one to ten for the features per split and the minimum samples per leaf, two to ten for the minimum samples per split. RandomizedSearchCV draws n_iter combinations, here twenty, and scores each by cross-validation. The search covers values the grid did not list, at less than a tenth of the grid's cost, and the count of candidates is fixed in advance no matter how many hyperparameters are included.

## Page 116

Bayesian search chooses each candidate from the results of the ones before it. BayesSearchCV, from the scikit-optimize package, has the same interface as the randomized search: a classifier, distributions and an iteration count. After each candidate is scored, it fits a probabilistic model of the score as a function of the hyperparameters and picks the next candidate where that model expects improvement, so the twenty iterations concentrate on the promising region instead of falling at random. The package is installed separately with pip.

## Page 117

This part covers pipelines, the scikit-learn object that chains preprocessing steps and a model into a single estimator.

## Page 118

Preprocessing written by hand. The categorical columns are one-hot encoded with get_dummies from pandas, cast to integers, and the last column is dropped because a set of k indicator columns carries its full information in k minus one of them. The numeric columns are standardized with a scaler fitted and applied in one call. The target is pulled out, and the two feature blocks are concatenated back into one matrix. Two things are wrong with this approach beyond its length. The scaler was fitted on every row, including rows that will later serve as test data, so information from the test rows leaks into the preprocessing. And every transformation has to be repeated by hand, in the same order with the same fitted values, on any new data the model is asked to score.

## Page 119

Cross-validating the hand-built matrix. A random forest regressor is scored by ten-fold cross-validation with the scoring choice neg_mean_squared_error; scikit-learn's scorers are all defined so that higher is better, so an error is returned negated, and the absolute value undoes that. The square root turns each fold's mean squared error into a root mean squared error. The leakage from the previous slide is still present: the scaler saw the test fold's rows when it was fitted, so each fold's score is slightly optimistic.

## Page 120

A pipeline is built from a list of named steps, each a tuple of a name and an estimator; here a standard scaler and then a k-nearest neighbors classifier. Calling fit on the pipeline fits the scaler on the training rows, transforms them, and fits the classifier on the result. Calling predict transforms new rows with the already fitted scaler and passes them to the classifier. The scaling and the model travel together as one object, so the same fitted transformation is applied to every row the model ever sees. The import line on the slide misspells StandardScaler.

## Page 121

Any transformer can be a step. This pipeline puts feature selection before the model: SelectKBest keeps the hundred features with the highest univariate score against the target and discards the rest, and the random forest is fitted on those hundred. Inside a pipeline the selection is refitted on each training fold during cross-validation, so the choice of features is made without the test rows.

## Page 122

The steps attribute prints the full structure of a larger pipeline. The first step is a FeatureUnion named all_features, which runs several transformers on the same input side by side and concatenates their outputs. One branch, named categoricals, is itself a pipeline: an ItemSelector that picks a list of named columns, an imputer that fills missing values with the most frequent value, and a one-hot encoder. A second branch, cut off in the printout, handles the numeric columns with a median imputer and a standard scaler. The last step is the random forest classifier with its full parameter list. The printout is from an older release: the Imputer class has since been replaced by SimpleImputer, and ItemSelector is a custom transformer from a documentation example, not part of the library.

## Page 123

Using a pipeline is the same as using a model: fit on the training features and target, predict on the test features, and pass the true and predicted labels to classification_report, which prints precision, recall, F1 score and support for each class. The slide stores the predictions in y_prediction and then passes target_prediction to the report, so as written the third line refers to a variable that was not assigned.

## Page 124

The pipeline goes into cross_val_score in place of the bare model, with the raw features rather than the hand-built matrix. In each of the ten folds the whole pipeline is refitted on the training portion, so the imputers, the encoder and the scaler are fitted without the test fold, and the leakage of the hand-built version is gone. The remaining lines convert the negated mean squared errors to root mean squared errors as before. The opening quotation mark of the scoring string on the slide is a typographic quote, which Python rejects.

## Page 125

The reasons to use a pipeline. Readability: the sequence of steps is declared in one place. No intermediate bookkeeping: the transformed data passes from step to step inside the object, with no variables to keep straight between transforming and estimating. Rearrangement: reordering steps or swapping one transformer or model for another is an edit to the list. Tuning the whole workflow: GridSearchCV accepts a pipeline and can search the settings of every step at once, with a parameter named by its step and its name joined by a double underscore. A fifth reason follows from the previous slides: preprocessing inside a pipeline is refitted per fold during cross-validation, so test data does not leak into it.

## Page 126

Pickling saves a fitted model to disk so it can be loaded and used later without refitting. The name is Python's: the pickle module serializes an object to bytes and restores it, and the cucumber is the pun.

## Page 127

A pickle alone is not enough to rebuild a model in the future, because the file is tied to the class definitions of the library version that wrote it and may not load, or may behave differently, under a later one. The scikit-learn documentation lists what to save alongside it. The training data, as a reference to an immutable snapshot. The Python source that produced the model. The versions of scikit-learn and its dependencies. The cross-validation score obtained on the training data. With those four the model can be refitted under a new version and checked against the score it had before.

## Page 128

The code saves the classifier with pickle.dump and restores it with pickle.load. Two details of the slide are out of date. The import from six.moves is a compatibility shim from the Python 2 era; in current Python the pickle module is imported directly. And both dump and load take an open file object, not a filename, so the calls as written raise a type error; the worksheet's version opens the file in binary write mode first. Loading a pickle executes code stored in the file, so a pickle from an untrusted source must not be loaded. For scikit-learn models, joblib's dump and load, used later in the deck, are the documented alternative and handle the large numeric arrays inside a model more efficiently.

## Page 129

FastAPI is a Python web framework for building HTTP APIs with little code. An endpoint is a Python function with a decorator that names the path and method, and the function's type hints define the request and response and are validated automatically. FastMCP is a companion library with the same decorator style for building Model Context Protocol servers, the subject of the MCP module.

## Page 130

A complete prediction service. The application object is created, and the model is loaded from a joblib file once when the module is imported, so every request reuses the same object rather than reading the file again. The health endpoint answers a GET request with a fixed status, which is what a load balancer or a monitor polls. The predict endpoint answers a POST request whose body is a list of floats; the type hint makes FastAPI parse and validate the JSON. The list is reshaped into a one-row matrix, because predict expects two dimensions, the model is called, and the first element of the result is converted to a plain Python integer so it can be serialized as JSON.

## Page 131

The demo runs the example service from the repository's ai_examples folder with uvicorn, the server that hosts a FastAPI application; the reload flag restarts it whenever the source file changes. The docs path opens the interactive documentation that FastAPI generates from the endpoint signatures, where each endpoint can be called from the browser. The predict path in this script takes a raw domain as a text query parameter, computes the features, and returns the model's verdict, a fuller version of the endpoint on the previous slide. A service like this is packaged into a Docker container by copying the script, the model file and the dependencies into an image.

## Page 132

Other open source tools for putting a model into service. MLflow: tracks experiments, stores versioned models in a registry, and serves a registered model behind an HTTP endpoint. BentoML: packages a model with its dependencies and serving code into a deployable unit. AWS Lambda, or the equivalent on another cloud: runs the prediction function on demand without a server to maintain, billed per invocation.

## Page 133

Worksheet 4.2, titled Tuning your Classifier in the notebook, takes thirty minutes. It loads the domain feature table, splits it, and fits a k-nearest neighbors classifier with default settings, which reaches about eighty-five percent accuracy. Wrapping the classifier in a pipeline with a standard scaler raises that to about eighty-eight, because the neighbor distances now weigh every feature equally. A randomized or grid search over the number of neighbors, the weighting, the algorithm, the leaf size and the distance exponent then improves it further. The last task fits a random forest with a search of its own and compares the two.

## Page 134

TODO NEW SLIDE

## Page 135

TODO NEW SLIDE

## Page 137

Everything in this part of the deck, the choice of preprocessing, the choice of model and the hyperparameter search, can itself be automated. TPOT, the tree-based pipeline optimization tool from the Epistasis Lab at the University of Pennsylvania, searches over whole scikit-learn pipelines. The teapot is its logo.

## Page 138

TPOT searches the space of pipelines by genetic programming. It starts with a population of random pipelines, each a chain of preprocessing steps and a model with hyperparameters, and scores each by cross-validation. The best pipelines are kept, mutated by changing a step or a setting, and crossed by combining parts of two, to form the next generation, and the process repeats for a set number of generations or a time budget. The result is the best pipeline found, which it can export as scikit-learn code. Thousands of candidate pipelines are evaluated along the way, which is the tedious part it removes from the person and the reason a run takes minutes to hours.

## Page 139

The diagram, from the TPOT repository, marks which stages of a project the tool takes over. Raw data and data cleaning at the left stay with the person, and model validation at the right does too. Everything in the shaded box is automated: feature selection, feature preprocessing and feature construction, which feed one another in any order; model selection; and parameter optimization. The tool searches over the whole shaded region at once, so a candidate pipeline is a particular choice at every one of those stages together.

## Page 140

An example of a pipeline TPOT can produce, and the reason for the word tree in its name. Two copies of the whole dataset enter separately. One passes through polynomial features, which adds products and powers of the original columns; the other through principal component analysis, which replaces the columns with a smaller set of uncorrelated combinations. The two results are combined into one feature set, recursive feature elimination drops the weakest columns, and a random forest classifies the rest. Each operator modifies the features and passes them on, branches can merge, and the final model sees only the final feature set. A search that can build shapes like this covers far more than a list of models with their settings.

## Page 141

The TPOT classifier is set up like any scikit-learn model and then fitted. The search_space argument, here linear-light, restricts the search to unbranched pipelines built from a small set of fast operators, which keeps a short run productive. The scorers list and its weights define what the search maximizes, here the area under the receiver operating characteristic curve alone. The cv argument sets the folds used to score each candidate, population_size the number of candidates alive in each generation, max_time_mins the budget in minutes, n_jobs the parallel workers, and verbose how much progress is printed. The fit call runs the whole search on the training data. Afterward the object predicts like any classifier, and its fitted_pipeline_ attribute holds the winning pipeline.

## Page 142

The TPOT documentation, at epistasislab.github.io/tpot, covers the search spaces, the scorers, and how to export a finished pipeline.

## Page 143

The main body of the module ends here. A case study on detecting SQL injection follows the last worksheet.

## Page 144

Worksheet 4.3 takes thirty minutes. It loads the same domain feature table, converts the dga and legit labels to one and zero, and splits the data. A TPOT classifier is created with a time budget under five minutes and a number of parallel jobs, and fitted on the training portion, which is the step that takes the time. The fitted model is scored on the test portion with a classification report and a confusion matrix display, for comparison with the models built by hand in the earlier worksheets. The last step exports the winning pipeline, either as a joblib file to load later or as scikit-learn source code.

## Page 145

This part is a case study: a supervised classifier applied to a security problem end to end.

## Page 146

The case study is finding SQL injection attempts. It follows the SQL injection notebook in the data_hacking repository published by Click Security, a collection of notebooks applying data analysis to security data, and runs through five steps: tokenizing the statements, building n-grams of the tokens, turning those into a feature vector, training a classifier, and evaluating it.

## Page 147

SQL, the structured query language, is the language applications use to read and write relational databases. SQL injection is the attack in which a user's input is made to become part of a query.

## Page 148

SQL injection is a vulnerability, found most often in web applications, in which an attacker gets the application to execute queries of the attacker's choosing on the application's own database server. The mechanism is string building: the application assembles a query by pasting user-supplied text into SQL, so text that contains SQL syntax changes what the query does.

## Page 149

A normal login query selects every column from the users table where the username is charles and the password is pass1234. The application expects one row back when the pair is correct and none when it is not, and grants access on the row count.

## Page 150

The pseudocode for the login check. The username and password come from the user. The query is a string with the two values inserted into it. The string is executed against the database, and if the result contains any rows the user is authenticated; otherwise they are refused. Nothing in the code checks what the two values contain before they become part of the query.

## Page 152

With the username charles and the password 12345 the query is the normal one, and the comment quotes the film Spaceballs on the quality of the combination. With the password changed to 12345 OR 1=1, the WHERE clause becomes username equals charles and password equals 12345, or one equals one. AND binds more tightly than OR, so the condition is true whenever one equals one, which is always. Every row in the table comes back, the row count is above zero, and the attacker is authenticated without knowing any password. The standard defense is a parameterized query, in which the database receives the query text and the values separately and does not parse the values as SQL. The case study takes the other side: recognizing injection attempts in traffic.

## Page 153

Three legitimate queries from the dataset. One counts products above a price. One selects the system columns ctid and xmin along with every other column from a table, which is PostgreSQL syntax. One selects the current date from dual, the one-row table Oracle provides for expressions that need no table. Each is a complete statement that begins with a keyword and names a table.

## Page 154

Four malicious fragments from the dataset. Each begins with a single quote, which closes the string the application was building, and then adds an OR with a condition that is always true, so the WHERE clause matches every row. The four conditions are variations on the same idea: a string compared with itself, a string compared with a concatenation that produces it, a string compared with its national-character form, and a LIKE with a wildcard. The variations exist to defeat filters that look for the literal pattern of one equals one. None of the four is a complete statement; each is meant to be spliced into someone else's.

## Page 155

Step one turns each statement into a sequence of token types with sqlparse, a Python SQL parser. The parse_it function parses the text and returns the type name of every token except whitespace. The table has the raw statement, its label, and the token list: a stored-procedure call to xp_cmdshell that pings an address becomes Single for the quoted string, Identifier, three Floats for the pieces of the address, and Error for what the parser could not place; a create user statement becomes DDL, Keyword, Identifier, Keyword, Single. The classifier will see these type sequences rather than the literal text, so a new statement with different names and values but the same shape is treated the same. The unicode call is Python 2 syntax, as is the print statement later in the case study.

## Page 156

Step two counts n-grams of token types, sequences of one, two or three consecutive tokens, and scores each by how strongly it is tied to one class. The score is a G-test, a likelihood-ratio test of whether an n-gram occurs independently of the label; the chart signs it so that positive means more common in malicious statements. The n-grams most tied to injections are a single-quoted string alone, a string followed by an identifier, punctuation, and alternations of identifier and string, which is the shape of a fragment that closes a quote and adds a condition. The n-grams most tied to legitimate statements are a keyword alone, keyword followed by identifier, and DML, the data manipulation statements select, insert, update and delete, which is the shape of a statement that begins properly. Parentheses and function calls score near zero and tell the two apart hardly at all.

## Page 157

TODO NEW SLIDE

## Page 158

Step three builds the feature vector for each statement. Entropy: the character-level entropy of the statement text. Length: the number of tokens. G-test scores: the sum of the n-gram scores from step two over the statement's own n-grams, computed separately for the malicious-associated and the legitimate-associated n-grams, giving two numbers per statement.

## Page 159

The box plot compares statement length by class. Legitimate statements have a median of about five tokens with a long tail of outliers up to thirty-four; malicious statements have a median of about four with outliers up to seventeen. The two boxes span nearly the same range, so length on its own separates little.

## Page 161

The scatter of entropy against length gives the same result with two features. Legitimate statements in blue and injections in red overlap across the whole range from one to seventeen tokens and from entropy two to five; only the longest statements, all legitimate, and a few very low-entropy fragments, all injections, sit apart. These two features alone would leave most of the data in a mixed region.

## Page 162

The two G-test features separate the classes where entropy and length could not. Each statement is placed by its legitimate score on the vertical axis and its malicious score on the horizontal. Legitimate statements cluster at the upper left, with a high legitimate score and a negative malicious score; injections cluster at the lower right, with a high malicious score and a legitimate score near zero. The two groups still touch along the diagonal in the middle, and a few points of each class sit inside the other's cluster, but a boundary drawn across the diagonal would get most statements right.

## Page 163

Step four fits a random forest of twenty trees and scores it by ten-fold cross-validation with four parallel jobs, which returns ten accuracies. The cross_validation module used on the slide was removed from scikit-learn in 2018; the function now lives in model_selection.

## Page 164

The ten fold accuracies all fall between 0.9964 and one, for a mean of about 0.998. The number on its own is less informative than it looks: the dataset is about ninety-four percent malicious, so a classifier that called everything malicious would score about 0.94, and the accuracy says little about how the legitimate minority is handled.

## Page 165

Step five reads the confusion matrix, here normalized by true class so each cell is a percentage of its row. Of one hundred seventy-six legitimate statements, one hundred seventy were called legitimate and six were called malicious, a recall for the legitimate class of 96.59 percent. Of two thousand six hundred three malicious statements, two thousand six hundred one were caught and two were missed, a recall for the malicious class of 99.92 percent. The six false alarms are the number to watch: three and a half percent of legitimate statements are flagged, and in live traffic, where legitimate statements outnumber injections by far more than they do in this dataset, that rate is multiplied by a much larger count.
