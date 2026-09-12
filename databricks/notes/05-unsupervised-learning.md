## Page 1

Module 5 covers unsupervised learning, with clustering as its main subject: grouping observations by the distances between them when no labels say what the groups should be.

## Page 2

The agenda has two parts. Measuring distances: how the similarity of two observations becomes a number, worked through on three departments and their counts of security events. An overview of clustering techniques without the mathematics: the k-means algorithm and its dependence on the number of clusters, on the random start and on the scale of the features; the silhouette coefficient and the elbow plot for judging a clustering; a density based method that needs no cluster count; and principal component analysis for reducing the number of features.

## Page 3

The flowchart sorts a problem into a family of machine learning by asking about labels. Labeled data means each observation carries the value the model is supposed to produce. With labels, the next question is whether that value is a quantity or a category: a quantity calls for regression, which predicts a number and supports inference about which features drive it; a category calls for classification, which predicts the class.

Without labels, the question is whether labels can be obtained. If they can, labeling the data moves the problem into the supervised branch. If they cannot, the problem is clustering or pattern finding, and the chart's verdict on the output is that nothing is proven: the model groups similar observations and flags anomalous ones, and recommender systems are built this way, but with no labels there is no ground truth to score the result against.

## Page 4

The supervised pipeline splits the data before a model is built. Data is gathered and cleaned, preprocessed into features, and narrowed by feature selection. The resulting dataset is divided into a training set and a testing set. The model is built on the training set alone, and evaluation scores it on the testing set, whose labels the model did not see during training. The double-headed arrows record that evaluation results feed back into rebuilding the model and into the data preparation stages. The split exists because the labels make it possible to measure the model's error on examples it was not fit to.

## Page 5

The unsupervised pipeline keeps every stage except the split. Data is gathered, cleaned, engineered into features and narrowed by feature selection exactly as before, and the whole dataset goes into building the model. Evaluation still loops back into model building and data preparation, but there is no testing set, because there are no labels for a prediction to be compared with. Evaluating an unsupervised model therefore measures properties of the result itself, such as how tightly the groups are packed and how far apart they sit, or checks the groups against what is known about the data.

## Page 6

Clustering has four steps. Feature selection: choose the columns that describe each observation, since the groups found depend only on those columns. Distance measure: define how far apart two observations are, for example the Euclidean distance between their feature vectors, which requires the features to be numeric and comparable in scale. Clustering algorithm: apply a procedure that groups observations by that distance. Validation: the question mark marks this as the step without a clean answer, because there are no labels that say the groups are right; validation relies on internal measures of group quality and on inspecting what the members of each group have in common.

## Page 7

The motivating problem is allocating security awareness training across departments: departments with similar histories of security events are candidates for the same training, so the first task is to say which departments are similar. The table lists three departments, and this first version describes each by one number, its count of malware events. With a single number per department, similar means close in that number, and the question is already a question about distance.

## Page 8

A second column adds each department's count of phishing events. Two numbers per department can disagree: a pair of departments can be close on malware events and far apart on phishing events, so similar now has to mean close on both at once, and the plain difference of one column no longer settles it.

## Page 9

A third count is added, so each department is a row of three numbers. The question on the title is answered by a distance: a rule that turns two rows into one number, small when the rows are alike and large when they differ. The slides that follow define that rule for one feature, then two, then three, and read the answer off the results.

## Page 10

With one feature the distance between two departments is the absolute difference of their counts. On malware events Dept1 has six, Dept2 has one and Dept3 has eight. Dept1 to Dept2 is six minus one, five; Dept2 to Dept3 is eight minus one, seven; Dept1 to Dept3 is eight minus six, two. By this feature alone Dept1 and Dept3 are the most similar pair and Dept2 stands apart from both.

## Page 11

With two features per department the plain difference no longer gives one number, and a distance method has to be chosen. The list names six. Euclidean: the length of the straight line between the two points. Manhattan: the sum of the differences along each axis. Maximum: the largest single difference on any one feature. Canberra: a sum of differences each divided by the sum of the two values being compared, which weights differences between small values more heavily. Binary: for presence or absence features, the share of features present in only one of the two observations among those present in either. Minkowski: a family with a parameter, where a parameter of one gives Manhattan and two gives Euclidean. Euclidean is the common choice, and it is the distance k-means uses.

## Page 12

The two counts place each department as a point in a plane, with malware events on the horizontal axis and phishing events on the vertical. Dept1 is at six malware events and six phishing events, Dept2 at one and two, and the third department at eight and one. The dashed segment joining Dept2 to Dept1 is their Euclidean distance, and the next slide computes its length.

## Page 13

The two counts place each department as a point in a plane, with malware events on the horizontal axis and phishing events on the vertical. Dept1 is at six malware events and six phishing events, Dept2 at one and two, and the third department at eight and one. The dashed segment joining Dept2 to Dept1 is their Euclidean distance, and the next slide computes its length.

## Page 14

The dashed segment is the hypotenuse of a right triangle whose legs are the differences on each feature. Side a runs horizontally from Dept2 and is the difference in malware events, six minus one, five. Side b runs vertically up to Dept1 and is the difference in phishing events, six minus two, four. The Pythagorean theorem gives the hypotenuse: a squared plus b squared equals c squared, so c is the square root of twenty five plus sixteen, the square root of forty one, about 6.4. This is the Euclidean formula. It extends to any number of features by adding one squared difference per feature under the root, which is what the code two slides on does.

## Page 15

Manhattan distance is a plus b: the same two legs added rather than squared and rooted, five plus four, nine, against a Euclidean 6.4 for the same pair. The name comes from a street grid, where travel between two corners follows the blocks rather than cutting through them. Manhattan distance is never smaller than the Euclidean distance for the same pair, and it grows in proportion to each feature's difference, so one large difference on a single feature counts less than it does under Euclidean distance, where the differences are squared before they are summed.

## Page 16

The Euclidean formula applied to all three pairs on the two-feature table. Dept1 to Dept2 is the square root of five squared plus four squared, 6.4. Dept2 to Dept3 is the square root of seven squared plus one squared, the square root of fifty, 7.1. Dept1 to Dept3 is the square root of two squared plus five squared, the square root of twenty nine, 5.4. Dept1 and Dept3 remain the closest pair, as they were on malware events alone, but by a smaller margin: on one feature they were two apart against five for the next closest pair, and with phishing events included they are 5.4 apart against 6.4.

## Page 17

The function computes Euclidean distance for any number of features. NumPy, the Python array library, subtracts two rows element by element, squares every difference, sums the squares and takes the square root, which is the two-feature formula with one squared term per feature. The array holds the three departments with three features each: Dept1 is six, six and three, Dept2 is one, two and one, and Dept3 is eight, one and nine. Dept1 to Dept2 is the square root of twenty five plus sixteen plus four, 6.7. Dept2 to Dept3 is the square root of forty nine plus one plus sixty four, 10.7. Dept1 to Dept3 is the square root of four plus twenty five plus thirty six, 8.1. The third feature changed the answer: Dept1 and Dept3, the closest pair on two features, differ by six on the new one, and are now farther apart than Dept1 and Dept2.

## Page 18

The three distances drawn on the table: 6.7 between Dept1 and Dept2, 8.1 between Dept1 and Dept3, 10.7 between Dept2 and Dept3. The question on the title has a numeric answer. On these three features Dept1 and Dept2 are the most similar pair and Dept2 and Dept3 the least, so if two departments are to share a training allocation, Dept1 and Dept2 are the pair. The answer depended on which features were included, since on malware events alone, and on malware and phishing events together, Dept1 and Dept3 were the closest pair. That dependence is why feature selection is the first step of the four-step clustering procedure. A clustering algorithm does for thousands of rows what this table does for three: it computes distances between observations and groups the ones that are close.

## Page 19

The scatter plot is unlabeled data in two dimensions: each dot is one observation, and its position is its value on two features. Three concentrations are visible, one on the left, one at the upper right and one at the lower middle, with scattered points between and around them. Clustering turns that visual impression into an explicit assignment of every point to a group, using only the distances between points.

## Page 20

One clustering of the points into three groups, drawn as ellipses: orange on the left, green at the upper right, blue at the lower middle. The ellipses overlap where the groups meet, and a point in the overlap could belong to either neighbor. A clustering algorithm settles each of those points by a rule, and different rules and different settings settle them differently. The outlying points at the far left fall inside the orange ellipse only because it was drawn wide enough to include them.

## Page 21

The same points split into two groups instead of three. The orange ellipse on the left is unchanged, and a single green ellipse now covers both the upper right and the lower middle concentrations. Both partitions are consistent with the plot; the data alone does not decide between two groups and three. The number of groups is a choice the analyst makes.

## Page 22

K-means takes the number of clusters, K, as an input and finds K centroids. A centroid is the point at the mean position of a set of points. Step 1 places K centroids at random within the range of the data. Step 2 assigns every observation to the centroid nearest to it, which partitions the data into K groups. Step 3 recomputes each centroid as the mean of the points assigned to it, which is where the name comes from. Step 4 repeats the assignment and the recomputation until the centroids stop moving, which happens when a pass reassigns no points.

Each pass of steps 2 and 3 lowers, or leaves unchanged, the sum of squared distances from every point to its centroid, and there are finitely many ways to partition the data, so the loop ends. The partition it ends at depends on where step 1 put the centroids.

## Page 23

Step 1 on the example data: K is three, and the three starting centroids, drawn as red, green and blue asterisks, are placed at random within the range of the data. None of them sits inside a visible concentration. The red and green markers are near the top of the plot, where there are few points, and the blue marker is at the lower left. These positions and the value of K are the only inputs; everything that follows is determined by them.

## Page 24

First assignment: each point takes the color of the nearest centroid. The red centroid at the upper left claims only the handful of points near it. The green centroid claims the whole upper right concentration plus a few points in the middle. The blue centroid at the lower left claims the lower middle concentration and most of the left one, since both are closer to it than to the red or green markers. The coloring at this stage reflects where the random centroids landed, not the concentrations in the data.

## Page 25

First move: each centroid relocates to the mean position of the points colored with it in the previous step. The red centroid drops from the top of the plot into the middle of its small red group. The green centroid moves right into the center of the upper right concentration. The blue centroid moves up and right from the corner to the mean of the large blue set that spans the left and lower middle concentrations, and so ends up between them. The point colors are unchanged, because reassignment is the next step.

## Page 26

Second assignment: with the centroids in their new positions, every point is again colored by the nearest one. The red centroid, now inside the left concentration, takes most of it from blue. The blue centroid, sitting between the left and lower middle concentrations, keeps the lower middle one and a band of points along the boundary. The green centroid keeps the upper right. A point changes color only where a centroid's move changed which centroid is nearest to it.

## Page 27

Second move: the centroids relocate to the means of their new memberships. The red centroid shifts a short distance to the center of its enlarged group. The blue centroid moves down into the lower middle concentration, since the points on the left that it lost no longer pull its mean leftward. The green centroid barely moves. The moves are smaller than in the first round, because the memberships changed less.

Third assignment: the points along the boundary between the red and blue groups switch to red, now that the blue centroid has moved down and away from them. The green and blue memberships are otherwise the same. The three colored groups now coincide with the three concentrations visible in the unlabeled plot, apart from a few points along the red and blue boundary.

## Page 28

Second move: the centroids relocate to the means of their new memberships. The red centroid shifts a short distance to the center of its enlarged group. The blue centroid moves down into the lower middle concentration, since the points on the left that it lost no longer pull its mean leftward. The green centroid barely moves. The moves are smaller than in the first round, because the memberships changed less.

Third assignment: the points along the boundary between the red and blue groups switch to red, now that the blue centroid has moved down and away from them. The green and blue memberships are otherwise the same. The three colored groups now coincide with the three concentrations visible in the unlabeled plot, apart from a few points along the red and blue boundary.

## Page 29

Third move: the centroids relocate to the means of the updated groups. Each shift is small, because few points changed membership in the assignment before it. All three centroids now sit near the middle of the concentrations they represent.

## Page 30

Fourth assignment: the coloring is nearly identical to the previous one. Only a couple of points on the boundary between the red and blue groups change color, from blue to red.

## Page 31

Fourth move: the centroids relocate by a distance too small to see. The memberships are almost fixed, so the means they are computed from are almost fixed too.

## Page 32

Fifth assignment: no point changes color. Every point is already assigned to its nearest centroid, so the partition is stable.

## Page 33

Fifth move: with no membership changes, each centroid is recomputed from the same points as before and stays where it was. This is the stopping condition of step 4. The result is the final partition, three clusters and three centroids, each centroid the mean of its cluster.

## Page 34

The converged clusters with an ellipse drawn around each: orange around the red cluster on the left, green at the upper right, blue at the lower middle, with each centroid at the center of its cluster. The ellipses are drawn to enclose each cluster's points and overlap slightly where they meet; the partition itself does not, because k-means assigns each point to exactly one centroid, and the true boundary between two clusters is the straight line of points equidistant from their centroids. That includes the outlying points at the far left of the red group and the stray points between concentrations; k-means has no notion of noise, and a point that is far from every centroid still goes to whichever one is nearest.

## Page 35

The annotations mark two weaknesses of the algorithm. The choice of K is subjective: the number of clusters is an input, and k-means returns exactly K clusters whether or not the data contains that many. The random placement of the starting centroids is underlined because different starting positions can converge to different partitions of the same data.

The third annotation, sensitive to scale, applies to the arithmetic of the loop. The nearest-centroid assignment and the centroid mean are both computed from raw feature values, so a feature with a large numeric range contributes more to the distance between two points than a feature with a small range. Groups then form along the large-range feature and the others barely influence the result.

## Page 36

The annotations mark two weaknesses of the algorithm. The choice of K is subjective: the number of clusters is an input, and k-means returns exactly K clusters whether or not the data contains that many. The random placement of the starting centroids is underlined because different starting positions can converge to different partitions of the same data.

The third annotation, sensitive to scale, applies to the arithmetic of the loop. The nearest-centroid assignment and the centroid mean are both computed from raw feature values, so a feature with a large numeric range contributes more to the distance between two points than a feature with a small range. Groups then form along the large-range feature and the others barely influence the result.

## Page 37

A broad cloud of points with no gaps between concentrations. The density varies across the plot, but there is no place where the data separates into groups. K-means run on this data returns three clusters if K is three and four if K is four, and the output alone does not reveal that the split is arbitrary.

## Page 38

One k-means run on the cloud with K set to four. The four clusters are red at the upper left, purple at the lower left, green at the upper right and teal at the lower right, and the asterisks are the converged centroids. The boundary between two adjacent clusters is the set of points equidistant from their two centroids, so the boundaries are straight lines and every cluster is a convex region around its centroid.

## Page 39

A second run on the same data with the same K and a different random start. The red cluster now sits at the upper left and center, the teal cluster has taken the upper right, the green cluster covers the lower center and right, and purple keeps the lower left. Many points have a different color than in the first run, although nothing about the data changed.

## Page 40

A third run, and a third partition: green at the upper left, purple at the upper right, teal at the lower left and red at the lower center. Each of the three runs converged, so each result is a local minimum of the sum of squared distances from points to centroids, and the random starting positions decided which minimum a run reached. Nothing in a single run's output says whether its partition reflects structure in the data or only the start it was given.

## Page 41

The figure is a k-means partition of data made of many compact groups. Each black polygon is the region of the plane closer to one centroid than to any other, the small plus sign inside it is that centroid, and the colored points are the group assigned to it. The groups here are tight and well separated, so the partition looks orderly, and a partition of data with no groups at all would be drawn with the same kind of polygons and look just as orderly.

The quote is from Anony-Mousse, a pseudonymous contributor to Cross Validated, the statistics question and answer site at stats.stackexchange.com; the name is a pun on anonymous. The point of the quote is that k-means always returns a partition. It has no step that tests whether the groups it found are real, and the output of a run on structureless data is formatted exactly like the output of a run on data with clear groups.

## Page 42

Two results of k-means with K equal to three on the same points, which form three visible groups: upper left, right and lower left. In result A, one centroid sits in the middle of each group. In result B, one centroid sits halfway between the two groups on the left and the other two share the group on the right.

Result B is a converged solution, the same as A. Every point on the left is nearer to the middle-left centroid than to either centroid on the right, so all of them are assigned to it, and that centroid is the mean of the two left groups combined. The two centroids on the right each hold half of the right group, and each is the mean of its half. A further pass of assignment and recomputation changes nothing in either result.

## Page 44

Both are correct in the only sense the algorithm has. Each result is a fixed point of the loop, a configuration in which every point is assigned to its nearest centroid and every centroid is the mean of its points, so the loop stops. The sum of squared distances from points to centroids is smaller in A, where the three groups are tight, than in B, where the left cluster spans two groups. K-means does not compare the fixed point it reached with any other, so it reports B with the same confidence as A. Only a person looking at the plot, or a separate score computed on the result, ranks A above B.

## Page 45

The boundaries of result B are drawn in: a vertical line separating the left cluster from the right, and a line splitting the right group between its two centroids. This is a local minimum of the sum of squared distances, a configuration that no single step of the loop improves, even though a different configuration scores lower overall. The starting positions decide which local minimum the loop lands in, which is what the two lines of text say: the initial guess matters, and two runs with different starts are not guaranteed the same outcome. K-means converges to whichever nearby fixed point the starting positions lead to rather than searching every possible partition, which places it among the local search, or hill climbing, methods of optimization.

The remedy built into the library is to run the whole loop several times from different starts and keep the result with the smallest sum of squared distances. In scikit-learn, the number of such runs is the `n_init` argument of `KMeans`, and the `init` argument selects the starting rule; the worksheet's calls set `n_init` and use the `k-means++` rule, which places each starting centroid far from the ones already chosen so that the starts are spread across the data instead of bunched together.

## Page 46

Scikit-learn's `KMeans` class runs the whole algorithm in two calls. The constructor takes `n_clusters`, which is K. The `fit` method takes the feature matrix and runs the loop to convergence. Two attributes hold the result: `cluster_centers_` is an array with one row per cluster giving the centroid's coordinates, and `labels_` is an array with one entry per row of the input giving the index of the cluster it was assigned to. The trailing letter on the slide's last line is a typo; the attribute is `labels_`.

The plot is a fit with K equal to two on six points. The three green points at the lower left form one cluster and the three red points at the upper right form the other, and the two blue crosses are the rows of `cluster_centers_`.

## Page 47

The data is the iris measurements: sepal length, sepal width, petal length and petal width, in centimeters, for 150 flowers. The species column of that dataset is not among the four features, so nothing in the data says which flower is which kind.

Seaborn's `pairplot` draws every feature against every other as a scatter plot, with the histogram of each feature on the diagonal. The petal length histogram has two separate humps, a narrow one below two centimeters and a broad one from three to seven, and every scatter panel that involves petal length or petal width shows a compact group in the lower left separated from the rest by a gap. Sepal width, by contrast, has a single hump and separates nothing on its own. Those panels are what a clustering of this data has to find.

## Page 48

The two lines fit k-means with two clusters to the four iris columns. Constructing the object sets K, and `fit` runs the assignment and recomputation loop on the rows of `data` and stores the centroids and labels on the object. The call pattern is the one every scikit-learn estimator uses, construct then fit, with one difference from the supervised estimators: `fit` receives only the feature matrix, and there is no target argument.

## Page 49

The cluster labels from `labels_` have been added to the data frame as a column named `kmeans_2`, and passing that column as `hue` colors every point by its cluster. Cluster 0, in blue, is the compact group with petal length under two centimeters and petal width under half a centimeter; cluster 1, in orange, is everything else. The diagonal histograms are split by cluster as well, and the split is clean on petal length and petal width and blurred on sepal length and sepal width, where the two clusters overlap. The algorithm used all four features in its distance and found the gap that the petal measurements contain.

The scatter plot is sepal width against sepal length, colored by cluster, with the two centroids drawn as black crosses. `cluster_centers_` has one row per cluster and one column per feature, and the call to `scatter` takes the two columns that match the plot's axes. The remaining arguments are appearance: `marker` selects the cross, `s` sets its size, `linewidths` its stroke and `c` its color.

In these two features the clusters overlap, and each cross sits at the mean of its cluster's points in the plane of the plot. The centroid of the orange cluster is near a sepal width of 2.9 and a sepal length of 6.3; the blue centroid is near 3.4 and 5.0. Some points carry the color of the cluster whose cross is the farther of the two in this plot. The assignment used the distance across all four features, so a point's cluster reflects its position in the four-feature space, not its position in this two-feature projection of it, and a flower on the orange side of the sepal measurements can belong to the blue cluster because its petal measurements put it there.

## Page 50

The cluster labels from `labels_` have been added to the data frame as a column named `kmeans_2`, and passing that column as `hue` colors every point by its cluster. Cluster 0, in blue, is the compact group with petal length under two centimeters and petal width under half a centimeter; cluster 1, in orange, is everything else. The diagonal histograms are split by cluster as well, and the split is clean on petal length and petal width and blurred on sepal length and sepal width, where the two clusters overlap. The algorithm used all four features in its distance and found the gap that the petal measurements contain.

The scatter plot is sepal width against sepal length, colored by cluster, with the two centroids drawn as black crosses. `cluster_centers_` has one row per cluster and one column per feature, and the call to `scatter` takes the two columns that match the plot's axes. The remaining arguments are appearance: `marker` selects the cross, `s` sets its size, `linewidths` its stroke and `c` its color.

In these two features the clusters overlap, and each cross sits at the mean of its cluster's points in the plane of the plot. The centroid of the orange cluster is near a sepal width of 2.9 and a sepal length of 6.3; the blue centroid is near 3.4 and 5.0. Some points carry the color of the cluster whose cross is the farther of the two in this plot. The assignment used the distance across all four features, so a point's cluster reflects its position in the four-feature space, not its position in this two-feature projection of it, and a flower on the orange side of the sepal measurements can belong to the blue cluster because its petal measurements put it there.

## Page 51

Euclidean distance adds up the squared difference of every feature, so a feature whose values spread over a wide range produces larger differences than one that spreads over a narrow range, and dominates the sum. In the iris data, petal length runs from about one to seven centimeters and petal width from near zero to two and a half, so two flowers that differ by a typical amount in petal length are farther apart, as k-means measures it, than two that differ by a typical amount in petal width. The weighting comes from the units the features happen to be measured in, and a feature recorded in millimeters would count ten times as much as the same feature recorded in centimeters.

## Page 52

Standardization puts every feature on the same scale. For each column, subtract the column's mean from every value, then divide by the column's standard deviation. Afterward every column has a mean of zero and a standard deviation of one, and a difference of one unit in any column means one standard deviation of that feature.

The quotation marks around equally are apt. Standardization equalizes the spread of the features, and after it a feature that carries no information about the groups weighs as much in the distance as one that carries a lot. Scaling is a choice about weights, made before the algorithm runs, and the choice here is equal weight for every feature.

## Page 53

`StandardScaler` from `sklearn.preprocessing` performs the standardization. The `fit_transform` call does two things: it computes the mean and standard deviation of every column, which the scaler stores, and then it applies the subtraction and division to the data it was given. The scaler's `transform` method can later apply the same stored means and standard deviations to new rows. The result is a NumPy array without column names, which is why the last line wraps it in a `DataFrame` with `columns=features`. The worksheet does the same to the five domain features and keeps the scaled columns beside the raw ones.

## Page 54

The clustering call is unchanged; only the input differs. `KMeans` with two clusters is fit to the scaled data frame instead of the raw one, and the distances inside the loop are now measured in standard deviations. Everything the object stores is in the scaled units as well: the rows of `cluster_centers_` are centroids in scaled coordinates, and the scaler's `inverse_transform` converts them back to centimeters if they are to be plotted on the original axes. The `random_state` argument in the second version of the call fixes the random start, so the run gives the same partition each time.

The two pair plots are the two-cluster result on the scaled features, on the left, and on the unscaled features, on the right. They are indistinguishable at this resolution: both isolate the small-petal group as cluster 0 and put the rest in cluster 1. Scaling made no visible difference on iris because the four features are all a few centimeters wide and the gap in the petal measurements is large relative to every feature's spread.

Scaling matters when the features differ in units. The worksheet's domain data describes each name by a character count, a fraction, an entropy and an n-gram score, and there the scaling step precedes the clustering.

## Page 55

The clustering call is unchanged; only the input differs. `KMeans` with two clusters is fit to the scaled data frame instead of the raw one, and the distances inside the loop are now measured in standard deviations. Everything the object stores is in the scaled units as well: the rows of `cluster_centers_` are centroids in scaled coordinates, and the scaler's `inverse_transform` converts them back to centimeters if they are to be plotted on the original axes. The `random_state` argument in the second version of the call fixes the random start, so the run gives the same partition each time.

The two pair plots are the two-cluster result on the scaled features, on the left, and on the unscaled features, on the right. They are indistinguishable at this resolution: both isolate the small-petal group as cluster 0 and put the rest in cluster 1. Scaling made no visible difference on iris because the four features are all a few centimeters wide and the gap in the petal measurements is large relative to every feature's spread.

Scaling matters when the features differ in units. The worksheet's domain data describes each name by a character count, a fraction, an entropy and an n-gram score, and there the scaling step precedes the clustering.

## Page 56

The same scaled data fit with three clusters instead of two. Cluster 1, in blue, is again the small-petal group and is unchanged. The third centroid split the large group in two along petal length and petal width: cluster 2, in green, holds the flowers with petal length below about five centimeters and petal width below about one and three quarters, and cluster 0, in orange, holds the larger ones. The two new clusters overlap on every panel, so the split runs through a region of the data with no gap in it.

The cluster indices are assigned by the run and carry no meaning: which group is called 0, 1 or 2 changes from one fit to another.

## Page 57

A one-class support vector machine draws a boundary around the bulk of the data and treats what falls outside it as outliers. `OneClassSVM` from `sklearn.svm` is fit on the feature matrix alone, with no labels; `nu` is an upper bound on the fraction of training points allowed to fall outside the boundary, so a value of one tenth asks for a boundary that leaves out about ten percent of the data, and `tol` is the tolerance at which the optimizer stops. `predict` returns one for a point inside the boundary and minus one for a point outside it.

In the figure, the red contour is the learned frontier, the green points inside it are the regular observations, the red points outside it are the outliers, and the shading is the decision function, darker the farther a location is from the frontier. The training error rate printed beneath, a little over eleven percent, is the fraction of training points classed as outliers, close to the value of `nu`.

The text on the left gives the use in this module: remove roughly the outlying tenth of the data before clustering it. A centroid is a mean, and a mean is pulled toward extreme values, so a few distant points can drag a centroid away from the group it should represent.

## Page 58

The silhouette coefficient scores a clustering from the distances alone, with no labels. For one point, a is the mean distance to the other points in its own cluster and b is the mean distance to the points of the nearest other cluster. The coefficient is b minus a, divided by the larger of the two. It ranges from minus one to one: a value near one means the point is much closer to its own cluster than to the neighboring one, a value near zero means it sits on the boundary between the two, and a negative value means it is on average closer to the neighboring cluster than to its own and is probably assigned to the wrong one. The score for a whole clustering is the mean coefficient over all its points.

## Page 59

The loop fits k-means once for every K from two through fifteen, because `range(2, 16)` stops before sixteen, and records the silhouette score of each fit. `random_state=1` fixes the random seed, so the initialization is reproducible and rerunning the loop gives the same scores. `silhouette_score` takes the data and the fitted labels and returns the mean coefficient over all points. The range starts at two because the coefficient needs a nearest other cluster, which a single cluster does not have. The data passed to `silhouette_score` has to be the same scaled data the model was fit on, so the distances it measures are the ones the clustering used.

The curve is the silhouette score against the number of clusters, from two to fifteen, on the scaled iris data. It is highest at two clusters, about 0.58, drops steeply through three and four, reaches its lowest value at six, about 0.32, and then wanders between 0.33 and 0.37 for larger K.

By the definition of the coefficient, a higher score means points sit closer to their own cluster than to the next one, so the curve favors two clusters, the partition that isolates the small-petal group. The arrow marks six, which is the minimum of the curve and by this measure the worst choice in the range, so the annotation contradicts the score it is drawn on.

## Page 60

The loop fits k-means once for every K from two through fifteen, because `range(2, 16)` stops before sixteen, and records the silhouette score of each fit. `random_state=1` fixes the random seed, so the initialization is reproducible and rerunning the loop gives the same scores. `silhouette_score` takes the data and the fitted labels and returns the mean coefficient over all points. The range starts at two because the coefficient needs a nearest other cluster, which a single cluster does not have. The data passed to `silhouette_score` has to be the same scaled data the model was fit on, so the distances it measures are the ones the clustering used.

The curve is the silhouette score against the number of clusters, from two to fifteen, on the scaled iris data. It is highest at two clusters, about 0.58, drops steeply through three and four, reaches its lowest value at six, about 0.32, and then wanders between 0.33 and 0.37 for larger K.

By the definition of the coefficient, a higher score means points sit closer to their own cluster than to the next one, so the curve favors two clusters, the partition that isolates the small-petal group. The arrow marks six, which is the minimum of the curve and by this measure the worst choice in the range, so the annotation contradicts the score it is drawn on.

## Page 61

Yellowbrick is a visualization library that wraps scikit-learn estimators, and its `KElbowVisualizer` fits the model once for every K in a range and plots a score against K. The range `k=(4, 12)` covers four through eleven. The score on the left axis is the distortion, the sum of squared distances from every point to its assigned centroid, which `KMeans` also exposes as `inertia_`. Adding a centroid can only shorten those distances, so the best possible distortion falls as K grows and there is no minimum to look for. The criterion is instead the elbow: the K past which adding clusters brings little further reduction. The blue line falls steeply from four to eight and then goes flat, so the elbow is at eight.

The dashed green line, on the right axis, is the time each fit took in seconds. The small rise in distortion after eight is a sign of the runs at larger K stopping at worse local solutions, since the best partition for a larger K has a distortion no higher than the best partition for a smaller one. The figure's title names `MiniBatchKMeans`, a variant that updates the centroids from random subsets of the data to run faster on large sets, while the code on the slide passes plain `KMeans`; the reading of the elbow is the same for either. The `poof` method renders the plot, and newer Yellowbrick versions call this method `show`.

## Page 62

The silhouette plot shows the coefficient of every point, grouped by cluster. The model is `MiniBatchKMeans` with six clusters on a dataset of a thousand samples. Each colored band is one cluster: the points are sorted by coefficient and drawn as horizontal bars from zero to their value, so the band's height is the cluster's size and its shape is the distribution of its coefficients. The dashed red line is the mean coefficient over all points, about 0.65.

Clusters 1, 3, 4 and 5 have most of their points above the mean, with values up to about 0.8, which marks them as compact and well separated. Clusters 0 and 2 have lower values, from about 0.5 down to 0.4 and all below the mean, and they are the two tallest bands, about twice the height of the others, so those two clusters are less well separated from their neighbors than the rest. No band extends left of zero, so no point in this fit is closer to another cluster than to its own. The plot is useful for spotting cluster size imbalance, which shows as bands of unequal height, and for choosing K by comparing the output across several candidate values.

## Page 63

DBSCAN, density-based spatial clustering of applications with noise, defines a cluster as a region where points are packed densely and treats the sparse space between such regions as separation rather than as territory to divide. K-means has no notion of density: it splits the whole feature space among K centroids, and every point, however isolated, goes to the nearest one. DBSCAN starts from the assumption on the slide, that regions of high density are the clusters, and two consequences follow that the next slides spell out. The number of clusters is a result rather than an input, and points that lie outside every dense region are labeled noise instead of being forced into a cluster.

## Page 64

DBSCAN takes no cluster count. Its two parameters define what dense means. Epsilon is a distance: two points are neighbors when they lie within epsilon of each other. min_samples is a count: a point whose epsilon neighborhood, counting the point itself, holds at least min_samples points is a core point, the kind that can anchor a cluster. Both settings are in the units of the feature space, so on standardized data epsilon is a number of standard deviations, and a value that works on scaled features means something else on the raw ones. A point that is not a core point and is not within epsilon of any core point is noise. All such points receive the label minus one, which is not a cluster but one bin for everything left over, and the slide's quotation marks around cluster mark that distinction.

## Page 65

The procedure grows each cluster outward from a core point. Pick a point not yet visited and count the points within epsilon of it. If the count reaches min_samples, start a cluster there; if not, label the point noise for now. That label is provisional: a point marked noise can later fall inside the neighborhood of a core point found afterward, in which case it joins that cluster as a border member, a point that belongs to the cluster without being dense enough to extend it. Once a cluster is started, every point in the core point's neighborhood joins it, and each of those that is itself a core point contributes its own neighborhood, so the cluster spreads through chains of core points until none can be reached. Then pick another unvisited point and repeat until every point is visited. A cluster is whatever a chain of core points connects, which is why it can take any shape, where a k-means cluster is always the convex region around a centroid.

Two differences from k-means follow. The number of clusters comes out of the density settings instead of going in as a parameter, and DBSCAN works with any distance measure, where k-means is tied to Euclidean distance because the mean of a group is the point that minimizes the squared Euclidean distances to its members. The cost is that the outcome depends on the distance measure chosen and on the two settings, and the slides that follow show how far the same data moves as the settings change.

## Page 66

The scikit-learn call has the same shape as the k-means one: construct with the parameters, then fit on the feature matrix alone. `DBSCAN` from `sklearn.cluster` takes `eps`, which is epsilon, and `min_samples`. The values here are an epsilon of one and a minimum of three on the standardized iris features, so two flowers are neighbors when they are within one standard deviation of each other in the four-feature space, and a neighborhood of three flowers makes a core point. After `fit`, `labels_` holds one entry per row: a cluster index counted from zero, or minus one for noise. There is no `cluster_centers_`, because a density cluster has no centroid.

## Page 67

The labels are attached as a column and the pair plot is colored by it. The list comprehension prefixes each integer label with the word cluster, so the legend reads cluster_0, cluster_-1 and cluster_1 rather than bare numbers. With an epsilon of one and a minimum of three, DBSCAN found two clusters: cluster 0, in blue, is the small-petal group, and cluster 1, in green, is everything else, the same two groups k-means with K equal to two produced, found here without the number being supplied. One point, in orange, is labeled minus one: the flower at the lower left of the sepal panels, with a sepal width near 2.3 and a sepal length near 4.5. It belongs to the small-petal group by its petals, but in four dimensions it has fewer than two other flowers within one standard deviation and is not within that distance of any core point, so it is noise under these settings.

## Page 68

The same epsilon with min_samples raised from three to ten. The two clusters are the same in substance: cluster 0, in blue, is still the small-petal group and cluster 1, in red, the rest. The change is at the edges. The green points labeled minus one are more numerous and sit at the fringes of both groups: the flowers with the largest sepal lengths, the longest petals and the lowest and highest sepal widths. Raising min_samples raises the density a point needs to be a core point, so points at the thin edge of a group that had three neighbors within epsilon but not ten stop being core points, and any of them not within epsilon of a surviving core point become noise. The colors are assigned per plot in label order and do not match the previous slide.

## Page 69

Epsilon raised from one to two, with min_samples back at three. The result is one cluster holding every flower and no noise: the legend has a single entry, cluster 0, and the plot is one color. At two standard deviations a neighborhood is wide enough to bridge the gap between the small-petal group and the rest, so the chain of core points runs through the whole dataset and no flower is far enough from every core point to be left out. Too large an epsilon fails in the opposite direction from too large a K: k-means splits groups that are not there, and DBSCAN with a wide epsilon merges groups that are.

## Page 70

Epsilon lowered to 0.6 with min_samples three. Four clusters and a set of noise points appear. Cluster 0, in blue, is still the small-petal group. The large group has broken up: cluster 1, in green, is its dense core; cluster 2, in red, is a pocket of a few flowers with petal lengths near three and a half and sepal widths near two and a half; cluster 3, in purple, is another small pocket with petal lengths between four and a half and five; and the orange points at the edges of both groups are noise. At 0.6 standard deviations a neighborhood no longer spans the thinly populated stretches inside the large group, so the chain breaks where the points thin out, and any three or more mutually close flowers cut off from the core become a cluster of their own.

The four runs together show what the two settings do. Epsilon sets the reach of a neighborhood and min_samples the density it must hold. Too large an epsilon merges everything; too small an epsilon or too large a min_samples fragments the groups and turns their edges into noise. Neither value is read off the data by the algorithm, so choosing them is the same kind of judgment as choosing K, made with a different pair of numbers.

## Page 71

Dimensionality reduction replaces the columns of a dataset with fewer columns while keeping as much of the variation in the data as it can. The reduction is possible when features are correlated: if two columns rise and fall together, one derived column carries most of what both contain, and the data occupies fewer effective directions than it has columns. Fewer columns means less input for a downstream model, a way to plot high-dimensional data in two dimensions, and less room for noise. The method is unsupervised because it uses no labels; it looks only at how the features vary. Principal component analysis is the common technique.

## Page 72

Dimensionality reduction replaces the columns of a dataset with fewer columns while keeping as much of the variation in the data as it can. The reduction is possible when features are correlated: if two columns rise and fall together, one derived column carries most of what both contain, and the data occupies fewer effective directions than it has columns. Fewer columns means less input for a downstream model, a way to plot high-dimensional data in two dimensions, and less room for noise. The method is unsupervised because it uses no labels; it looks only at how the features vary. Principal component analysis is the common technique.

## Page 73

Principal component analysis finds the directions in which the data varies most. The first principal component is the direction, a weighted combination of all the original features, along which the data has the greatest variance. The second is the direction of greatest remaining variance at right angles to the first, which makes it uncorrelated with the first; the third is at right angles to both, and so on until there are as many components as original features. Highly correlated features carry overlapping information, and a single component captures what they share.

The components are ordered by the variance they capture, so projecting the data onto the first few keeps most of the total variance in far fewer columns. Each new column is a principal component score, a linear combination of every original feature, and the components are linearly uncorrelated with one another.

## Page 74

The code is from the dimensionality reduction notebook of Hands-On Unsupervised Learning Using Python, the book by Ankur Patel whose repository the link points to. The 784 features are the pixels of the 28 by 28 images of handwritten digits in the MNIST dataset, which that notebook works on.

`PCA` from `sklearn.decomposition` is constructed with `n_components` equal to 784, as many components as there are features, so this first fit discards nothing. `whiten=False` leaves each component's scores at their natural variance instead of rescaling them all to a variance of one. Setting `whiten=True` instead rescales every component's scores to unit variance, which discards the relative variance scale between components but can improve a downstream estimator's accuracy when that estimator assumes standardized, uncorrelated input. `fit_transform` finds the components from the training features and projects those features onto them, and the result is wrapped in a data frame that keeps the training index. `explained_variance_ratio_` is an array holding the fraction of the total variance each component captures, in decreasing order. Summed over all 784 components it comes to 1.0, all of the variance, which is the line at the bottom. Fitting with every component is what makes it possible to read off how much variance any smaller number of them would keep.

## Page 75

Each line is the sum of `explained_variance_ratio_` over the first N components, that is, the share of the total variance kept if only those N are retained. Ten components keep about 49 percent of the variance of 784 pixel columns, twenty keep 64 percent, fifty keep 82 percent, one hundred keep 91 percent, two hundred keep 97 percent and three hundred keep 98.6 percent. The gain per component falls steeply: the first hundred add 91 points, the second hundred add five, the third hundred add two.

The bottom line on the slide follows: three hundred of the 784 columns hold about 98 percent of the variance, so the dataset can be cut to well under half its width while losing about one and a half percent. The word theoretically carries a caveat. Variance is the quantity PCA preserves, and it is a proxy for the information a model needs; whether the dropped one and a half percent matters to a classifier trained on the 300 component scores is a question the classifier's accuracy answers, and the variance figure does not.

## Page 76

Questions on the module: measuring distance between observations, clustering without labels, the k-means loop and its dependence on K, on the random start and on the scale of the features, the silhouette coefficient and the elbow plot, DBSCAN and its two density settings, and principal component analysis.

## Page 77

Worksheet 5.1 applies the module to about six thousand domain names, five thousand generated by botnet domain generation algorithms and one thousand taken from the Alexa list of popular sites, each described by its length, its share of dictionary words, its entropy, its count of digits and an n-gram score. The steps are to standardize the five features, fit k-means with two clusters on the scaled columns, attach the labels as a column, and count the domain sources within each cluster to see whether the clusters separate generated names from legitimate ones; then to plot the sum of squared distances against K for the elbow method.

The worksheet then uses two other clustering methods. Agglomerative clustering starts with every point as its own cluster and repeatedly merges the two closest clusters; the dendrogram is the tree of those merges, and points that stay unmerged until late in the tree are candidates for anomalies, which the worksheet uses to find twenty generated domains placed among a thousand legitimate ones. DBSCAN is applied to the same scaled features with the epsilon and min_samples settings introduced on the preceding slides, and the names it labels minus one are the ones with too few close neighbors to belong to any dense group.
