## Page 1

Module 5 covers unsupervised learning: clustering data that carries no labels, the k-means algorithm and its dependence on the number of clusters, the random start and the scale of the features, the silhouette coefficient and the elbow plot for judging a clustering, and principal component analysis for reducing the number of features.

## Page 2

The flowchart sorts a problem into a family of machine learning by asking about labels. Labeled data means each observation carries the value the model is supposed to produce. With labels, the next question is whether that value is a quantity or a category: a quantity calls for regression, which predicts a number and supports inference about which features drive it; a category calls for classification, which predicts the class.

Without labels, the question is whether labels can be obtained. If they can, labeling the data moves the problem into the supervised branch. If they cannot, the problem is clustering or pattern finding, and the chart's verdict on the output is that nothing is proven: the model groups similar observations and flags anomalous ones, and recommender systems are built this way, but with no labels there is no ground truth to score the result against.

## Page 3

The supervised pipeline splits the data before a model is built. Data is gathered and cleaned, preprocessed into features, and narrowed by feature selection. The resulting dataset is divided into a training set and a testing set. The model is built on the training set alone, and evaluation scores it on the testing set, whose labels the model did not see during training. The double-headed arrows record that evaluation results feed back into rebuilding the model and into the data preparation stages. The split exists because the labels make it possible to measure the model's error on examples it was not fit to.

## Page 4

The unsupervised pipeline keeps every stage except the split. Data is gathered, cleaned, engineered into features and narrowed by feature selection exactly as before, and the whole dataset goes into building the model. Evaluation still loops back into model building and data preparation, but there is no testing set, because there are no labels for a prediction to be compared with. Evaluating an unsupervised model therefore measures properties of the result itself, such as how tightly the groups are packed and how far apart they sit, or checks the groups against what is known about the data.

## Page 5

Clustering has four steps. Feature selection: choose the columns that describe each observation, since the groups found depend only on those columns. Distance measure: define how far apart two observations are, for example the Euclidean distance between their feature vectors, which requires the features to be numeric and comparable in scale. Clustering algorithm: apply a procedure that groups observations by that distance. Validation: the question mark marks this as the step without a clean answer, because there are no labels that say the groups are right; validation relies on internal measures of group quality and on inspecting what the members of each group have in common.

## Page 6

The scatter plot is unlabeled data in two dimensions: each dot is one observation, and its position is its value on two features. Three concentrations are visible, one on the left, one at the upper right and one at the lower middle, with scattered points between and around them. Clustering turns that visual impression into an explicit assignment of every point to a group, using only the distances between points.

## Page 7

One clustering of the points into three groups, drawn as ellipses: orange on the left, green at the upper right, blue at the lower middle. The ellipses overlap where the groups meet, and a point in the overlap could belong to either neighbor. A clustering algorithm settles each of those points by a rule, and different rules and different settings settle them differently. The outlying points at the far left fall inside the orange ellipse only because it was drawn wide enough to include them.

## Page 8

The same points split into two groups instead of three. The orange ellipse on the left is unchanged, and a single green ellipse now covers both the upper right and the lower middle concentrations. Both partitions are consistent with the plot; the data alone does not decide between two groups and three. The number of groups is a choice the analyst makes.

## Page 9

K-means takes the number of clusters, K, as an input and finds K centroids. A centroid is the point at the mean position of a set of points. Step 1 places K centroids at random within the range of the data. Step 2 assigns every observation to the centroid nearest to it, which partitions the data into K groups. Step 3 recomputes each centroid as the mean of the points assigned to it, which is where the name comes from. Step 4 repeats the assignment and the recomputation until the centroids stop moving, which happens when a pass reassigns no points.

Each pass of steps 2 and 3 lowers, or leaves unchanged, the sum of squared distances from every point to its centroid, and there are finitely many ways to partition the data, so the loop ends. The partition it ends at depends on where step 1 put the centroids.

## Page 10

Step 1 on the example data: K is three, and the three starting centroids, drawn as red, green and blue asterisks, are placed at random within the range of the data. None of them sits inside a visible concentration. The red and green markers are near the top of the plot, where there are few points, and the blue marker is at the lower left. These positions and the value of K are the only inputs; everything that follows is determined by them.

## Page 11

First assignment: each point takes the color of the nearest centroid. The red centroid at the upper left claims only the handful of points near it. The green centroid claims the whole upper right concentration plus a few points in the middle. The blue centroid at the lower left claims the lower middle concentration and most of the left one, since both are closer to it than to the red or green markers. The coloring at this stage reflects where the random centroids landed, not the concentrations in the data.

## Page 12

First move: each centroid relocates to the mean position of the points colored with it in the previous step. The red centroid drops from the top of the plot into the middle of its small red group. The green centroid moves right into the center of the upper right concentration. The blue centroid moves up and right from the corner to the mean of the large blue set that spans the left and lower middle concentrations, and so ends up between them. The point colors are unchanged, because reassignment is the next step.

## Page 13

Second assignment: with the centroids in their new positions, every point is again colored by the nearest one. The red centroid, now inside the left concentration, takes most of it from blue. The blue centroid, sitting between the left and lower middle concentrations, keeps the lower middle one and a band of points along the boundary. The green centroid keeps the upper right. A point changes color only where a centroid's move changed which centroid is nearest to it.

## Page 14

Second move: the centroids relocate to the means of their new memberships. The red centroid shifts a short distance to the center of its enlarged group. The blue centroid moves down into the lower middle concentration, since the points on the left that it lost no longer pull its mean leftward. The green centroid barely moves. The moves are smaller than in the first round, because the memberships changed less.

## Page 15

Third assignment: the points along the boundary between the red and blue groups switch to red, now that the blue centroid has moved down and away from them. The green and blue memberships are otherwise the same. The three colored groups now coincide with the three concentrations visible in the unlabeled plot.

## Page 16

Third move: the centroids relocate to the means of the updated groups. Each shift is small, because few points changed membership in the assignment before it. All three centroids now sit near the middle of the concentrations they represent.

## Page 17

Fourth assignment: the coloring is nearly identical to the previous one. Only a couple of points on the boundary between the red and blue groups change color, from blue to red.

## Page 18

Fourth move: the centroids relocate by a distance too small to see. The memberships are almost fixed, so the means they are computed from are almost fixed too.

## Page 19

Fifth assignment: no point changes color. Every point is already assigned to its nearest centroid, so the partition is stable.

## Page 20

Fifth move: with no membership changes, each centroid is recomputed from the same points as before and stays where it was. This is the stopping condition of step 4. The result is the final partition, three clusters and three centroids, each centroid the mean of its cluster.

## Page 21

The converged clusters with their boundaries drawn as ellipses: red on the left, green at the upper right, blue at the lower middle, with each centroid at the center of its ellipse. The boundaries do not overlap, because k-means assigns each point to exactly one centroid. That includes the outlying points at the far left of the red group and the stray points between concentrations; k-means has no notion of noise, and a point that is far from every centroid still goes to whichever one is nearest.

## Page 23

The annotations mark two weaknesses of the algorithm. The choice of K is subjective: the number of clusters is an input, and k-means returns exactly K clusters whether or not the data contains that many. The random placement of the starting centroids is underlined because different starting positions can converge to different partitions of the same data.

The third annotation, sensitive to scale, applies to the arithmetic of the loop. The nearest-centroid assignment and the centroid mean are both computed from raw feature values, so a feature with a large numeric range contributes more to the distance between two points than a feature with a small range. Groups then form along the large-range feature and the others barely influence the result.

## Page 24

A broad cloud of points with no gaps between concentrations. The density varies across the plot, but there is no place where the data separates into groups. K-means run on this data returns three clusters if K is three and four if K is four, and the output alone does not reveal that the split is arbitrary.

## Page 25

One k-means run on the cloud with K set to four. The four clusters are red at the upper left, purple at the lower left, green at the upper right and teal at the lower right, and the asterisks are the converged centroids. The boundary between two adjacent clusters is the set of points equidistant from their two centroids, so the boundaries are straight lines and every cluster is a convex region around its centroid.

## Page 26

A second run on the same data with the same K and a different random start. The red cluster now sits at the upper left and center, the teal cluster has taken the upper right, the green cluster covers the lower center and right, and purple keeps the lower left. Many points have a different color than in the first run, although nothing about the data changed.

## Page 27

A third run, and a third partition: green at the upper left, purple at the upper right, teal at the lower left and red at the lower center. Each of the three runs converged, so each result is a local minimum of the sum of squared distances from points to centroids, and the random starting positions decided which minimum a run reached. Nothing in a single run's output says whether its partition reflects structure in the data or only the start it was given.

## Page 28

The figure is a k-means partition of data made of many compact groups. Each black polygon is the region of the plane closer to one centroid than to any other, the small plus sign inside it is that centroid, and the colored points are the group assigned to it. The groups here are tight and well separated, so the partition looks orderly, and a partition of data with no groups at all would be drawn with the same kind of polygons and look just as orderly.

The quote is from Anony-Mousse, a pseudonymous contributor to Cross Validated, the statistics question and answer site at stats.stackexchange.com; the name is a pun on anonymous. The point of the quote is that k-means always returns a partition. It has no step that tests whether the groups it found are real, and the output of a run on structureless data is formatted exactly like the output of a run on data with clear groups.

## Page 29

Two results of k-means with K equal to three on the same points, which form three visible groups: upper left, right and lower left. In result A, one centroid sits in the middle of each group. In result B, one centroid sits halfway between the two groups on the left and the other two share the group on the right.

Result B is a converged solution, the same as A. Every point on the left is nearer to the middle-left centroid than to either centroid on the right, so all of them are assigned to it, and that centroid is the mean of the two left groups combined. The two centroids on the right each hold half of the right group, and each is the mean of its half. A further pass of assignment and recomputation changes nothing in either result.

## Page 30

Both are correct in the only sense the algorithm has. Each result is a fixed point of the loop, a configuration in which every point is assigned to its nearest centroid and every centroid is the mean of its points, so the loop stops. The sum of squared distances from points to centroids is smaller in A, where the three groups are tight, than in B, where the left cluster spans two groups. K-means does not compare the fixed point it reached with any other, so it reports B with the same confidence as A. Only a person looking at the plot, or a separate score computed on the result, ranks A above B.

## Page 31

The boundaries of result B are drawn in: a vertical line separating the left cluster from the right, and a line splitting the right group between its two centroids. This is a local minimum of the sum of squared distances, a configuration that no single step of the loop improves, even though a different configuration scores lower overall. The starting positions decide which local minimum the loop lands in, which is what the two lines of text say: the initial guess matters, and two runs with different starts are not guaranteed the same outcome.

The remedy built into the library is to run the whole loop several times from different starts and keep the result with the smallest sum of squared distances. In scikit-learn, the number of such runs is the `n_init` argument of `KMeans`, and the `init` argument selects the starting rule; the worksheet's calls set `n_init` and use the `k-means++` rule, which places each starting centroid far from the ones already chosen so that the starts are spread across the data instead of bunched together.

## Page 32

Scikit-learn's `KMeans` class runs the whole algorithm in two calls. The constructor takes `n_clusters`, which is K. The `fit` method takes the feature matrix and runs the loop to convergence. Two attributes hold the result: `cluster_centers_` is an array with one row per cluster giving the centroid's coordinates, and `labels_` is an array with one entry per row of the input giving the index of the cluster it was assigned to. The trailing letter on the slide's last line is a typo; the attribute is `labels_`.

The plot is a fit with K equal to two on six points. The three green points at the lower left form one cluster and the three red points at the upper right form the other, and the two blue crosses are the rows of `cluster_centers_`.

## Page 33

The data is the iris measurements: sepal length, sepal width, petal length and petal width, in centimeters, for 150 flowers. The species column of that dataset is not among the four features, so nothing in the data says which flower is which kind.

Seaborn's `pairplot` draws every feature against every other as a scatter plot, with the histogram of each feature on the diagonal. The petal length histogram has two separate humps, a narrow one below two centimeters and a broad one from three to seven, and every scatter panel that involves petal length or petal width shows a compact group in the lower left separated from the rest by a gap. Sepal width, by contrast, has a single hump and separates nothing on its own. Those panels are what a clustering of this data has to find.

## Page 34

The two lines fit k-means with two clusters to the four iris columns. Constructing the object sets K, and `fit` runs the assignment and recomputation loop on the rows of `data` and stores the centroids and labels on the object. The call pattern is the one every scikit-learn estimator uses, construct then fit, with one difference from the supervised estimators: `fit` receives only the feature matrix, and there is no target argument.

## Page 35

The cluster labels from `labels_` have been added to the data frame as a column named `kmeans_2`, and passing that column as `hue` colors every point by its cluster. Cluster 0, in blue, is the compact group with petal length under two centimeters and petal width under half a centimeter; cluster 1, in orange, is everything else. The diagonal histograms are split by cluster as well, and the split is clean on petal length and petal width and blurred on sepal length and sepal width, where the two clusters overlap. The algorithm used all four features in its distance and found the gap that the petal measurements contain.

## Page 36

The scatter plot is sepal width against sepal length, colored by cluster, with the two centroids drawn as black crosses. `cluster_centers_` has one row per cluster and one column per feature, and the call to `scatter` takes the two columns that match the plot's axes. The remaining arguments are appearance: `marker` selects the cross, `s` sets its size, `linewidths` its stroke and `c` its color.

In these two features the clusters overlap, and each cross sits at the mean of its cluster's points in the plane of the plot. The centroid of the orange cluster is near a sepal width of 2.9 and a sepal length of 6.3; the blue centroid is near 3.4 and 5.0.

## Page 37

Euclidean distance adds up the squared difference of every feature, so a feature whose values spread over a wide range produces larger differences than one that spreads over a narrow range, and dominates the sum. In the iris data, petal length runs from about one to seven centimeters and petal width from near zero to two and a half, so two flowers that differ by a typical amount in petal length are farther apart, as k-means measures it, than two that differ by a typical amount in petal width. The weighting comes from the units the features happen to be measured in, and a feature recorded in millimeters would count ten times as much as the same feature recorded in centimeters.

## Page 38

Standardization puts every feature on the same scale. For each column, subtract the column's mean from every value, then divide by the column's standard deviation. Afterward every column has a mean of zero and a standard deviation of one, and a difference of one unit in any column means one standard deviation of that feature.

The quotation marks around equally are apt. Standardization equalizes the spread of the features, and after it a feature that carries no information about the groups weighs as much in the distance as one that carries a lot. Scaling is a choice about weights, made before the algorithm runs, and the choice here is equal weight for every feature.

## Page 39

`StandardScaler` from `sklearn.preprocessing` performs the standardization. The `fit_transform` call does two things: it computes the mean and standard deviation of every column, which the scaler stores, and then it applies the subtraction and division to the data it was given. The scaler's `transform` method can later apply the same stored means and standard deviations to new rows. The result is a NumPy array without column names, which is why the last line wraps it in a `DataFrame` with `columns=features`. The worksheet does the same to the five domain features and keeps the scaled columns beside the raw ones.

## Page 40

The clustering call is unchanged; only the input differs. `KMeans` with two clusters is fit to the scaled data frame instead of the raw one, and the distances inside the loop are now measured in standard deviations. Everything the object stores is in the scaled units as well: the rows of `cluster_centers_` are centroids in scaled coordinates, and the scaler's `inverse_transform` converts them back to centimeters if they are to be plotted on the original axes.

## Page 41

The two pair plots are the two-cluster result on the scaled features, on the left, and on the unscaled features, on the right. They are indistinguishable at this resolution: both isolate the small-petal group as cluster 0 and put the rest in cluster 1. Scaling made no visible difference on iris because the four features are all a few centimeters wide and the gap in the petal measurements is large relative to every feature's spread.

Scaling matters when the features differ in units. The worksheet's domain data describes each name by a character count, a fraction, an entropy and an n-gram score, and there the scaling step precedes the clustering.

## Page 42

The same scaled data fit with three clusters instead of two. Cluster 1, in blue, is again the small-petal group and is unchanged. The third centroid split the large group in two along petal length and petal width: cluster 2, in green, holds the flowers with petal length below about five centimeters and petal width below about one and three quarters, and cluster 0, in orange, holds the larger ones. The two new clusters overlap on every panel, so the split runs through a region of the data with no gap in it.

The cluster indices are assigned by the run and carry no meaning: which group is called 0, 1 or 2 changes from one fit to another.

## Page 43

A one-class support vector machine draws a boundary around the bulk of the data and treats what falls outside it as outliers. `OneClassSVM` from `sklearn.svm` is fit on the feature matrix alone, with no labels; `nu` is an upper bound on the fraction of training points allowed to fall outside the boundary, so a value of one tenth asks for a boundary that leaves out about ten percent of the data, and `tol` is the tolerance at which the optimizer stops. `predict` returns one for a point inside the boundary and minus one for a point outside it.

In the figure, the red contour is the learned frontier, the green points inside it are the regular observations, the red points outside it are the outliers, and the shading is the decision function, darker the farther a location is from the frontier. The training error rate printed beneath, a little over eleven percent, is the fraction of training points classed as outliers, close to the value of `nu`.

The text on the left gives the use in this module: remove roughly the outlying tenth of the data before clustering it. A centroid is a mean, and a mean is pulled toward extreme values, so a few distant points can drag a centroid away from the group it should represent.

## Page 44

The silhouette coefficient scores a clustering from the distances alone, with no labels. For one point, a is the mean distance to the other points in its own cluster and b is the mean distance to the points of the nearest other cluster. The coefficient is b minus a, divided by the larger of the two. It ranges from minus one to one: a value near one means the point is much closer to its own cluster than to the neighboring one, a value near zero means it sits on the boundary between the two, and a negative value means it is on average closer to the neighboring cluster than to its own and is probably assigned to the wrong one. The score for a whole clustering is the mean coefficient over all its points.

## Page 45

The loop fits k-means once for every K from two through fifteen, because `range(2, 16)` stops before sixteen, and records the silhouette score of each fit. `random_state=1` fixes the random seed, so the initialization is reproducible and rerunning the loop gives the same scores. `silhouette_score` takes the data and the fitted labels and returns the mean coefficient over all points. The range starts at two because the coefficient needs a nearest other cluster, which a single cluster does not have. The data passed to `silhouette_score` has to be the same scaled data the model was fit on, so the distances it measures are the ones the clustering used.

## Page 46

The curve is the silhouette score against the number of clusters, from two to fifteen, on the scaled iris data. It is highest at two clusters, about 0.58, drops steeply through three and four, reaches its lowest value at six, about 0.32, and then wanders between 0.33 and 0.37 for larger K.

By the definition of the coefficient, a higher score means points sit closer to their own cluster than to the next one, so the curve favors two clusters, the partition that isolates the small-petal group. The arrow marks six, which is the minimum of the curve and by this measure the worst choice in the range, so the annotation contradicts the score it is drawn on.

## Page 47

Yellowbrick is a visualization library that wraps scikit-learn estimators, and its `KElbowVisualizer` fits the model once for every K in a range and plots a score against K. The range `k=(4, 12)` covers four through eleven. The score on the left axis is the distortion, the sum of squared distances from every point to its assigned centroid, which `KMeans` also exposes as `inertia_`. Adding a centroid can only shorten those distances, so the best possible distortion falls as K grows and there is no minimum to look for. The criterion is instead the elbow: the K past which adding clusters brings little further reduction. The blue line falls steeply from four to eight and then goes flat, so the elbow is at eight.

The dashed green line, on the right axis, is the time each fit took in seconds. The small rise in distortion after eight is a sign of the runs at larger K stopping at worse local solutions, since the best partition for a larger K has a distortion no higher than the best partition for a smaller one. The figure's title names `MiniBatchKMeans`, a variant that updates the centroids from random subsets of the data to run faster on large sets, while the code on the slide passes plain `KMeans`; the reading of the elbow is the same for either. The `poof` method renders the plot, and newer Yellowbrick versions call this method `show`.

## Page 48

The silhouette plot shows the coefficient of every point, grouped by cluster. The model is `MiniBatchKMeans` with six clusters on a dataset of a thousand samples. Each colored band is one cluster: the points are sorted by coefficient and drawn as horizontal bars from zero to their value, so the band's height is the cluster's size and its shape is the distribution of its coefficients. The dashed red line is the mean coefficient over all points, about 0.65.

Clusters 1, 3, 4 and 5 have most of their points above the mean, with values up to about 0.8, which marks them as compact and well separated. Clusters 0 and 2 have lower values, from about 0.5 down to 0.4 and all below the mean, and they are the two tallest bands, about twice the height of the others, so those two clusters are less well separated from their neighbors than the rest. No band extends left of zero, so no point in this fit is closer to another cluster than to its own.

## Page 49

Worksheet 5.1 applies the module to about six thousand domain names, five thousand generated by botnet domain generation algorithms and one thousand taken from the Alexa list of popular sites, each described by its length, its share of dictionary words, its entropy, its count of digits and an n-gram score. The steps are to standardize the five features, fit k-means with two clusters on the scaled columns, attach the labels as a column, and count the domain sources within each cluster to see whether the clusters separate generated names from legitimate ones; then to plot the sum of squared distances against K for the elbow method.

The worksheet then uses two other clustering methods. Agglomerative clustering starts with every point as its own cluster and repeatedly merges the two closest clusters; the dendrogram is the tree of those merges, and points that stay unmerged until late in the tree are candidates for anomalies, which the worksheet uses to find twenty generated domains placed among a thousand legitimate ones. DBSCAN, density-based spatial clustering of applications with noise, groups points that have at least a minimum number of neighbors within a radius and leaves points with too few neighbors unassigned as noise; its two settings are that radius and that minimum count.

## Page 51

Dimensionality reduction replaces the columns of a dataset with fewer columns while keeping as much of the variation in the data as it can. The reduction is possible when features are correlated: if two columns rise and fall together, one derived column carries most of what both contain, and the data occupies fewer effective directions than it has columns. Fewer columns means less input for a downstream model, a way to plot high-dimensional data in two dimensions, and less room for noise. The method is unsupervised because it uses no labels; it looks only at how the features vary. Principal component analysis is the common technique.

## Page 52

Principal component analysis finds the directions in which the data varies most. The first principal component is the direction, a weighted combination of all the original features, along which the data has the greatest variance. The second is the direction of greatest remaining variance at right angles to the first, which makes it uncorrelated with the first; the third is at right angles to both, and so on until there are as many components as original features. Highly correlated features carry overlapping information, and a single component captures what they share.

The components are ordered by the variance they capture, so projecting the data onto the first few keeps most of the total variance in far fewer columns. Each new column is a principal component score, a linear combination of every original feature, and the components are linearly uncorrelated with one another.

## Page 53

The code is from the dimensionality reduction notebook of Hands-On Unsupervised Learning Using Python, the book by Ankur Patel whose repository the link points to. The 784 features are the pixels of the 28 by 28 images of handwritten digits in the MNIST dataset, which that notebook works on.

`PCA` from `sklearn.decomposition` is constructed with `n_components` equal to 784, as many components as there are features, so this first fit discards nothing. `whiten=False` leaves each component's scores at their natural variance instead of rescaling them all to a variance of one. `fit_transform` finds the components from the training features and projects those features onto them, and the result is wrapped in a data frame that keeps the training index. `explained_variance_ratio_` is an array holding the fraction of the total variance each component captures, in decreasing order. Summed over all 784 components it comes to 1.0, all of the variance, which is the line at the bottom. Fitting with every component is what makes it possible to read off how much variance any smaller number of them would keep.

## Page 54

Each line is the sum of `explained_variance_ratio_` over the first N components, that is, the share of the total variance kept if only those N are retained. Ten components keep about 49 percent of the variance of 784 pixel columns, twenty keep 64 percent, fifty keep 82 percent, one hundred keep 91 percent, two hundred keep 97 percent and three hundred keep 98.6 percent. The gain per component falls steeply: the first hundred add 91 points, the second hundred add five, the third hundred add two.

The bottom line on the slide follows: three hundred of the 784 columns hold about 98 percent of the variance, so the dataset can be cut to well under half its width while losing about one and a half percent. The word theoretically carries a caveat. Variance is the quantity PCA preserves, and it is a proxy for the information a model needs; whether the dropped one and a half percent matters to a classifier trained on the 300 component scores is a question the classifier's accuracy answers, and the variance figure does not.

## Page 55

Questions on the module: clustering without labels, the k-means loop and its dependence on K, on the random start and on the scale of the features, the silhouette coefficient and the elbow plot, and principal component analysis.
