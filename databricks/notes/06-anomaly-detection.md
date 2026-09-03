## Page 1

Module 6 covers anomaly detection: finding the observations in a dataset that differ from the rest, and the statistical, forecasting, unsupervised and string-distance methods for scoring that difference.

## Page 2

Four parts. Overview: the definition of an outlier, the families of detection method, the Python libraries that implement them, and the two questions about a dataset that decide which family applies. Statistical techniques: thresholds set from the mean and standard deviation of the data, and what happens to them when the data is skewed. Supervised techniques: forecasting with ARIMA, where the training signal is the series' own past. Unsupervised techniques: the one-class support vector machine and the isolation forest, which learn the shape of the data without labels.

## Page 3

The module opens with a data validation problem from the instructors' own work: rejecting corrupt records at ingest time, across too many columns to write a rule for each.

## Page 4

The problem has three constraints. A reference set of good data existed. Corrupt records had to be rejected before ingest. The table had too many columns for a hand-written validity rule per column, which rules out listing allowed values and formats field by field.

The reference set is the one asset. It describes good data by example, so any solution has to extract that description from the examples and measure new records against it.

## Page 5

The prompt asks for a design under those constraints. A design has to answer two questions: how to summarize the reference set so that a new record can be compared with it, and how much difference from that summary counts as corrupt.

## Page 6

The photo is an arctic fox on snow: white fur on white ground, visible only by its outline and its dark eyes and nose. Anomaly detection is hard for the reason the fox is hard to see. An anomaly is defined by contrast with the surrounding data, and when its values overlap the range normal observations occupy, no threshold isolates it without also flagging normal points. The detector needs a feature in which the contrast exists.

## Page 7

Anomalous means unusual relative to the rest of the data, and nothing more. A detector separates the unusual from the usual; whether an unusual observation is harmful is a separate judgment made outside the detector, with knowledge of what the data measures. Treating every flagged observation as bad turns every rare legitimate event into a false alarm.

## Page 8

The quote is from Pierre Lafaye de Micheaux (pronounced roughly la-FAY duh mee-SHOW), a statistician and textbook author. His example is a rat that survives an experiment that killed all the others. The survivor is an outlier: it differs from every other observation. It is also the observation with the most to teach, because explaining it could expose a mechanism the other rats cannot. Detecting outliers matters because detection is what surfaces such cases.

## Page 9

The module uses anomaly and outlier interchangeably. Both words name the same property, an observation that differs from the others in its dataset, and libraries label methods either way: scikit-learn's outlier detection module and a paper on anomaly detection describe the same problem.

## Page 10

The word is literal. An outlier is a point that lies outside the region the rest of the observations occupy, so it can only be identified against a particular set of observations.

## Page 11

The definition needs two things made concrete before it can be computed. Differs from the rest requires a measure of difference: a distance from the other observations, or from a summary of them such as their mean. A data point which differs requires a threshold: how much distance counts. Each method in the module fixes both.

The definition is relative to the dataset. The same value is an outlier in one dataset and typical in another, because the comparison set changed while the value did not.

## Page 12

The distinction between the two rests on the training data: whether it already contains the outliers the model is meant to find.

## Page 13

Anomaly detection learns from contaminated data. The training set mixes inliers and outliers with no labels saying which is which, so the method has to find the outliers inside the data it learned from, and whatever it learns about normal is pulled toward the outliers present. Novelty detection learns from clean data. The training set holds only normal observations; the model learns the boundary of that region and scores new observations by whether they fall inside it, so anything outside is novel by construction. scikit-learn's outlier detection documentation draws the line the same way: outlier detection when the training data contains outliers, novelty detection when it does not.

The data validation problem is novelty detection under this split. The reference set was known good, and the question was whether incoming records belonged to it.

## Page 14

Five families of method, by what they compare an observation against. Forecasting: predict the next value of a series from its past and score the gap between forecast and observation; it is supervised because the series' own later values serve as labels. Statistical metrics: measure how far a value sits from the center of its distribution in units of the spread, as with standard deviation bands and z-scores. Unsupervised techniques: learn the shape of the data without labels and score points by how poorly they fit that shape, as with the one-class support vector machine and the isolation forest. Density based methods: score a point by how sparse its neighborhood is compared with its neighbors' neighborhoods, as with the local outlier factor. Goodness of fit tests: compare the observed distribution of a sample with an expected distribution and flag the sample when the two disagree, as with the chi-square and Kolmogorov-Smirnov tests.

## Page 15

Six library groups, by the part of the job each does. pandas, SciPy and NumPy: the mean, standard deviation, absolute deviation and z-score computations, which need nothing beyond array arithmetic and SciPy's stats functions. PyOD: a library dedicated to outlier detection, with dozens of algorithms behind one fit and predict interface modeled on scikit-learn's. pmdarima: an ARIMA toolkit whose auto_arima function searches the model orders automatically, a port of R's auto.arima. Prophet: Meta's forecasting library, which fits an additive model of trend, seasonality and holiday effects and returns a forecast with an uncertainty band. statsmodels: estimation and testing for statistical models, including the stationarity test and the seasonal decomposition the lab runs before fitting ARIMA. scikit-learn: OneClassSVM and IsolationForest, plus LocalOutlierFactor and EllipticEnvelope, all behind the same fit and predict calls.

Worksheet 6.1 imports pandas, pmdarima, statsmodels and Prophet.

## Page 16

Every method in the module runs the same three stages. Predict: use the known data to produce an expected value for the observation, whether that is the mean of a column, the next value of a series, or a learned region of feature space. Score: compare the prediction with the actual value and express the difference as a distance, the anomaly score. Decide: compare the score with a threshold; a score within the threshold marks the observation as an inlier, and a score beyond it marks an outlier.

The threshold is set by the analyst. Lowering it flags more observations, including more normal ones; raising it misses more true anomalies. In Worksheet 6.1 the anomaly score is the difference between an ARIMA forecast and the observed CPU utilization, plotted over time so that a threshold can be read off the plot.

## Page 17

Two properties of a dataset decide which methods apply to it: how many variables each observation has, and what distribution the values follow.

## Page 18

Univariate data has one variable per observation; multivariate data has several. A CPU utilization series is univariate, one number per timestamp. The data validation table is multivariate, one record spanning many columns. The split matters because methods differ in what they accept. Standard deviation bands, z-scores and forecasting operate on a single variable at a time. The one-class support vector machine and the isolation forest take a feature vector and score the whole record. A multivariate outlier can be typical in every column taken alone and unusual only in the combination of columns, which no per-column method can detect.

## Page 19

The distribution decides whether summary statistics describe the data. If values are approximately normal, the mean locates the center and the standard deviation sets the spread, and a threshold expressed in standard deviations has a known coverage: about 68 percent of values fall within one standard deviation of the mean, about 95 percent within two, and about 99.7 percent within three. If values are skewed or heavy-tailed, the mean is pulled toward the tail, the standard deviation is inflated by it, and the coverage figures no longer hold. Methods that assume a distribution are parametric; methods that do not, such as the isolation forest, are non-parametric. A histogram with a fitted curve drawn over it is the check.

## Page 20

This part builds outlier thresholds from the summary statistics of the data itself: its mean, its standard deviation, and deviations expressed in those units.

## Page 21

The running example is a series of 1000 observations, indexed 0 to 1000 on the horizontal axis. Values are centered on zero and nearly all lie between minus 0.3 and 0.3, with no trend and no repeating pattern across the index. Nothing in the plot marks any point as an outlier, since no threshold has been drawn; the extreme values near 0.3 and minus 0.3 are the largest of the thousand and no more.

## Page 22

The same 1000 values as a histogram, with a normal curve in red. The vertical axis is density: the bar areas sum to one, so the bars can be compared with the curve directly. The bars follow the curve across the whole range, which answers the distribution question for this series: a normal distribution with mean zero fits it. The curve's peak height of about four also gives the spread, since a normal density peaks at one divided by the product of the standard deviation and the square root of two pi, and a peak of four corresponds to a standard deviation of one tenth.

## Page 23

Thresholds drawn on the series. The red lines sit one standard deviation above and below the mean, at about 0.1 and minus 0.1; the magenta lines sit two standard deviations out, at about 0.2 and minus 0.2. Each pair of lines is a band, and an observation is flagged when it falls outside the band. The inner band cuts through the body of the series, with points crossing it throughout; the outer band is crossed only by the spikes.

## Page 24

Counting the points outside each band shows how much the threshold matters. Under the normal fit, about 317 of the 1000 values are expected beyond one standard deviation in either direction and about 46 beyond two. The count of 44 beyond the two-deviation band matches that expectation. The count of 167 beyond the one-deviation band is about half the two-sided expectation and close to the one-tail figure of about 159, so read it as a count of one side only.

A threshold applied to pure noise flags noise. Every point beyond a band here is a random draw from the same distribution as the rest, so a one-deviation rule produces hundreds of false alarms per thousand observations and a two-deviation rule about fifty. The threshold is set by how many false alarms per thousand the consumer of the alerts will tolerate. Shewhart control charts, used to monitor manufacturing processes, place their limits at three standard deviations, which flags about three per thousand.

## Page 26

The two views are of a second series whose distribution is skewed. The histogram runs from zero upward with the bulk of the values below 0.25 and a tail past 1.25; the red curve is the normal density from the earlier histogram, mean zero and standard deviation one tenth, which reaches zero by 0.3 while the data continues for another unit. No normal curve fits this shape, because the data has a hard floor at zero and a long tail on one side only.

The series plot shows the consequence for a threshold. The red line is a threshold at about 0.5, and 123 of the 1000 observations lie above it, about one in eight. The tail those points come from is ordinary behavior for a skewed distribution, so a threshold built from the mean and standard deviation flags ordinary values. A mirror line below the mean would sit at or under zero, where there is no data to flag at all. The threshold rule is unchanged from the previous series; what changed is that its assumption about the distribution no longer holds.

## Page 27

Mean absolute deviation measures spread as the average distance of the values from their mean: subtract the mean from each value, drop the sign, and average the results. It is an alternative to the standard deviation, which squares the deviations before averaging and so weights a single extreme value more heavily. The absolute version moves less when one outlier enters the data. A threshold can be set in mean absolute deviations from the mean the same way standard deviation bands are set.

Three corrections to the slide. The title's "Absolution" is a typo for absolute. The pseudocode line drops the absolute value that the formula above it shows; without it the deviations from the mean sum to zero by the definition of the mean, and the result is zero for any data. The `data.mad()` call was removed in pandas 2.0; compute it as `(data - data.mean()).abs().mean()`.

One more term to keep apart: the acronym MAD is also used for the median absolute deviation, the median of the distances from the median, which is a different statistic and the one SciPy's `median_abs_deviation` computes.

## Page 29

A z-score expresses an observation's distance from the mean in standard deviations: subtract the mean from the value and divide by the standard deviation. A z of 2 is two standard deviations above the mean, a z of minus 1.5 is one and a half below, and a z near zero is at the center. The score is dimensionless, so one threshold on the absolute z applies to every column of a table regardless of the units each column is measured in, which is what makes it usable across the many columns of the validation problem. A threshold on absolute z is the standard deviation band from the earlier plots expressed per observation: flagging absolute z above 2 is the same rule as flagging points outside the two-deviation band.

The mean and standard deviation come from the reference data. For novelty detection that is the clean set. For anomaly detection it is the mixed set, and the outliers in it shift the mean toward themselves and enlarge the standard deviation, which shrinks their own z-scores, an effect called masking.

## Page 30

Two ways to compute z-scores for every column of a DataFrame. SciPy: `zscore` from `scipy.stats`, applied column by column with `df.apply`. pandas: subtract the column means from the frame and divide by the column standard deviations, which pandas broadcasts across the columns in one expression. Both fail on a column of strings, since subtraction is undefined for text; select the numeric columns first with `df.select_dtypes('number')`.

The two do not return identical numbers. SciPy's `zscore` divides by the population standard deviation, with the sum of squares divided by n; pandas `std` uses the sample standard deviation, dividing by n minus 1. The pandas scores are slightly smaller in magnitude, and the gap shrinks as n grows. Pass `ddof=1` to `zscore` or `ddof=0` to `std` to make them agree.

## Page 31

The chart divides the standard normal curve into strips half a standard deviation wide and labels each strip with the share of a normal population it holds. The horizontal axis is the z-score. Reading outward from zero on one side: 19.1 percent between 0 and 0.5, 15.0 between 0.5 and 1, 9.2 between 1 and 1.5, 4.4 between 1.5 and 2, 1.7 between 2 and 2.5, 0.5 between 2.5 and 3, and 0.1 beyond 3. The other side mirrors it.

The strips give the tail mass for any z threshold. Beyond an absolute z of 2 lies 2.3 percent per side, 4.6 in total; beyond 2.5, 0.6 per side; beyond 3, 0.1 per side, which is 0.27 in total before rounding. A threshold chosen on this chart fixes the fraction of normal data that will be flagged.

## Page 32

The pros and cons come from the source article. Effective under a Gaussian distribution: the z-score's meaning as a tail fraction, read off the previous chart, holds only when the data is normal; on the skewed series from earlier, a z of 2 corresponds to no particular fraction. Easy to implement: the two listings shown before. Low dimensional feature space: z-scores are computed one column at a time, so a table with many columns yields many scores per observation and no built-in way to combine them into one verdict. Small to medium datasets: the size limit is the article's judgment, since the arithmetic is one subtraction and one division per value and has no limit of its own. Not recommended without a parametric assumption: when no distribution can be assumed, a z-score is still computable, but its threshold no longer maps to a known fraction of the data.

## Page 33

The series is figure 3-1 from Machine Learning and Security by Clarence Chio and David Freeman (O'Reilly, 2018), the book the lab's CPU data also comes from. It has a repeating cycle, seven peaks in 160 steps, so a period of about 24 steps, consistent with hourly samples and a daily rhythm, and it has a trend: the dotted regression line climbs from about 92,000 to about 128,000 over the window.

A fixed threshold fails on data like this. The mean shifts as the trend rises, so a band set early in the window sits too low late in it. Within each cycle the peaks reach 160,000 and the troughs 60,000, so a band wide enough to contain both flags nothing, and a band tight enough to flag anything fires at every peak. What counts as normal depends on where in the cycle and how far along the trend the observation sits, so the reference value has to be computed for each point in time.

## Page 34

This part covers forecasting: a model of a series' own past that supplies the expected value for each new observation.

## Page 35

The image is a television seven-day forecast with one impossible value: highs of 101, 700, 102, 96, 93, 90 and 88 degrees. The 700 is detectable only from its neighbors. Nothing about the number alone marks it as wrong; the values before and after it, 101 and 102, do. That is the mechanism forecasting-based detection automates: produce the expected value at each time from the values before it, then measure how far the observation lands from that expectation.

## Page 36

Forecasting is supervised learning with the labels supplied by time. Each training example is a window of past values, and its label is the value that came next, which is already in the series; no one has to annotate anything. The model is fitted on the earlier part of the series and evaluated on the later part, so the split between training and test data is made at a point in time, which is how the lab's paired train and test files for each CPU dataset are cut. A random split would leak future values into training and overstate the model's accuracy.

## Page 37

A forecasting model takes one series ordered in time. The ordering is what it exploits: autocorrelation, the dependence of a value on the values before it, is what makes the past informative about the next step. Data with no time order has no past to forecast from. Data with several series can be forecast one series at a time, at the cost of ignoring how the series move together; vector autoregression models several series jointly and is outside the module.

## Page 38

Three components of a time series. Trend: a slow drift in the level, such as the rising regression line on the earlier chart. Season: a pattern that repeats at a fixed period, such as the 24-step cycle in the same chart, or weekly and yearly rhythms. Cycle: a rise and fall with a recognizable shape and no fixed period, so it cannot be predicted from a calendar the way a season can.

Seasonal decomposition separates these components. The additive model writes each value as trend plus seasonal plus residual, and the residual is what is left once the predictable structure is removed. The lab runs statsmodels' `seasonal_decompose` with the additive model on the CPU series and tries several values for the period.

## Page 39

ARIMA stands for autoregressive integrated moving average, a family of models that forecast a series from its own past values and its own past forecast errors. The chart is the default output of R's forecast package for a model written ARIMA(1,1,2): the black line is the observed series, the blue line the forecast from the last observation onward, the darker band the 80 percent prediction interval and the lighter band the 95 percent interval.

Two things to read off it. The forecast flattens to a constant a few steps out, because once the model's memory of the last values fades it has nothing to predict but the level. The bands widen with the horizon, because each step ahead is forecast from earlier forecasts and the errors compound. A threshold on the gap between forecast and observation is therefore trustworthy near the forecast origin and progressively less so further out.

## Page 40

Three components, each named by one letter. AR, autoregression: the next value is modeled as a weighted sum of the previous p values plus noise, so the weights capture how strongly the series depends on its own recent past. I, integrated: the series is differenced before modeling, each value replaced by its change from the previous step, to remove trend and make the series stationary, meaning its mean and variance stay constant over time; the forecast is then summed back to the original scale. MA, moving average: the next value is modeled as a weighted sum of the previous q forecast errors plus noise, so a surprise at one step carries into the next few predictions. The moving average here is a weighted sum of errors; it is unrelated to the rolling average used to smooth a series.

The lab checks stationarity before fitting, first by plotting a rolling mean and rolling standard deviation and looking for flat lines, then with the augmented Dickey-Fuller test from statsmodels, whose null hypothesis is that the series is non-stationary.

## Page 41

The three orders set how much history each component uses. p, the lag order: how many previous values the autoregressive term includes. d, the degree of differencing: how many times the series is differenced before modeling; one differencing removes a linear trend and two remove a quadratic one. q, the moving average order: how many previous forecast errors the moving average term includes. The parenthesized labels ar, integ and ma tie each order to its letter in the acronym, and the model on the forecast chart, ARIMA(1,1,2), uses one lag, one differencing and two error terms.

Choosing them by hand uses the autocorrelation function for q, the partial autocorrelation function for p, and a stationarity test for d. The lab computes the autocorrelation at lags 1 through 19 and draws pandas' autocorrelation plot, whose horizontal lines mark the 95 and 99 percent confidence bands, before handing the choice to `auto_arima`.

## Page 42

The listing fits an ARIMA model to the CPU column with pmdarima. `auto_arima` searches combinations of p, d and q, fits each candidate, and keeps the one with the lowest Akaike information criterion, a fit score that penalizes each added parameter, so the search prefers the simplest model that explains the series. `seasonal=True` allows seasonal terms in the search, but pmdarima treats a period `m` of one, the default, as non-seasonal and switches the seasonal search off, so the flag changes nothing unless `m` is also set to the period, for example 24 for hourly data with a daily cycle. `error_action='ignore'` skips candidates that fail to fit instead of raising. `summary()` prints the statsmodels table for the chosen model: its orders, the fitted coefficients with their standard errors, and the information criteria. `ADFTest` is imported for the stationarity check; `ADFTest(alpha=0.05).should_diff(series)` returns the test's p-value and whether differencing is needed.

## Page 43

The plot is the model's in-sample fit on the training set: observed CPU utilization in red and the model's predictions in black over about 420 steps. In-sample predictions are one step ahead, each made from the actual values up to the previous step, so the black line follows the red closely and trails it by a step at the sharp turns. The series shows three broad rises and falls with sharper spikes on top, and the model tracks both. The residuals, the small vertical gaps between the lines, are the model's baseline error on normal data and set the scale against which a later gap is judged large. The lab produces this plot with `predict_in_sample()`.

## Page 44

The plot is the 60-step forecast on the test set of dataset B, the set with an injected anomaly. The blue line is the forecast, made once at the end of the training data and declining smoothly from about 1.6 toward 1.2. The red line is what was observed: it tracks the forecast for the first ten steps, drops to near zero at step 10, stays there through step 30, then jumps above 2 and stays high. The forecast does not react because the test values are not in its input; it is a multi-step projection from training data alone.

The gap between the lines is the anomaly score. It is small for ten steps and large from step 10 onward, in both directions. The score at step 10 is the alert: it falls where the forecast is still close to the last observed values, and the lab notes that the first anomaly is enough to investigate. The lab reproduces this plot from the train and test files of dataset B and asks for the time intervals with the highest score.

## Page 45

Two extensions of ARIMA. SARIMA, seasonal ARIMA: adds a second set of orders, P, D and Q, applied at the seasonal period m, so the model differences across one full period and regresses on the values and errors one period back as well as the previous step; it is what `auto_arima` fits when `seasonal=True` and `m` is set. ARIMAX, ARIMA with exogenous variables: adds outside series as regressors, so the forecast draws on the target's past and on other measurements known at each step; pmdarima passes them as `X` and statsmodels as `exog`. statsmodels' SARIMAX class combines both extensions.

## Page 46

Questions on the statistical and forecasting techniques.

## Page 47

This part covers unsupervised detectors, the one-class support vector machine and the isolation forest, which build a description of the data from unlabeled observations and score each point by how well it fits.

## Page 48

The grid is scikit-learn's comparison of outlier detectors on toy datasets. Columns are methods: robust covariance, one-class SVM, isolation forest and local outlier factor. Rows are datasets: one Gaussian blob, two blobs of equal spread, two blobs of unequal spread, two interleaved crescents, and points spread uniformly over the square. Orange points are inliers, blue points the 15 percent of outliers scattered uniformly across each panel, the black line is the boundary each method learned, and the corner figure is fitting time in seconds.

The boundaries show each method's assumption. Robust covariance fits one ellipse, so it succeeds on the single blob and draws one ellipse around both blobs and around the crescents, where the real structure has two parts. The one-class SVM bends around any shape through its kernel and encloses each blob separately, but its boundary is pulled outward by the outliers it was trained on, since it was designed for training data without them. The isolation forest follows the blobs and the crescents with boxy edges, because its splits are axis-aligned. Local outlier factor has no boundary drawn: in outlier detection mode it scores only the points it was fitted on and has no decision function for new points. On the uniform square every method flags only the edges, since nothing inside is rarer than anything else.

## Page 49

A one-class SVM is a support vector machine with a single class. The standard SVM separates two classes with the widest possible margin; the one-class variant, from Bernhard Schölkopf (pronounced roughly SHURL-kopf) and colleagues in 2001, has only the training data and learns a boundary that encloses it, by separating the data from the origin in the kernel's feature space with the widest margin it can. The training data is treated as one class, normal, and a new observation is a member of the class if it falls inside the boundary and an outlier if it falls outside. Because the boundary is learned from data assumed normal, the method is a novelty detector under the distinction drawn earlier.

## Page 50

The listing is from scikit-learn's one-class SVM example. `OneClassSVM` is built with three settings. `nu`: an upper bound on the fraction of training points allowed to fall outside the boundary and a lower bound on the fraction that become support vectors; 0.1 lets about a tenth of the training data be treated as errors, which keeps the boundary from stretching to enclose every stray training point. `kernel="rbf"`: the radial basis function kernel, under which the boundary can be any smooth closed shape. `gamma`: the inverse width of that kernel; small values give a smooth, loose boundary, large values a tight one that wraps individual points and overfits. `fit` learns the boundary from `X_train`, and `predict` returns 1 for a point inside it and minus 1 for a point outside.

## Page 51

The chart is the output of the same example. Training observations, white, form two clusters. The dark red line is the learned frontier around each, and the blue shading is the decision function, darker where a point sits deeper inside the frontier. Purple points are new observations drawn from the same distribution as the training data; yellow points are new observations scattered uniformly across the square.

The error counts below the chart grade the frontier. Twenty-two of 200 training points fall outside it, 11 percent, in line with the tenth that `nu=0.1` allowed. None of the 40 new regular points fall outside. Two of the 40 abnormal points fall inside, the ones that happened to land within a cluster, and no boundary drawn from position alone can separate those from the regulars they sit among.

## Page 52

Two strengths. High dimensional data: the kernel computes the similarity between two points directly, without constructing coordinates in the feature space, so the training cost grows with the number of training points, with the number of features entering only through the distance each kernel evaluation computes. No distribution assumption: the boundary is shaped by the data through the kernel, with `nu` and `gamma` as the only settings, so it is non-parametric and works on the two-cluster data of the previous chart, where no single normal curve applies.

## Page 53

Two weaknesses with one cause. Sensitive to outliers: the frontier is fitted to enclose the training data with at most the `nu` fraction left outside, so outliers present in the training set either stretch the frontier to cover them or consume the allowance that should have gone to stray normal points, and the finished frontier then admits new observations that resemble those outliers. Best for novelty detection: the fix is to train on data known to be clean, which is the novelty setting; for a mixed dataset, scikit-learn's own guidance is to use the isolation forest or the local outlier factor instead.

## Page 54

The listing runs the one-class SVM in the outlier setting anyway: fit on the full dataset `X`, outliers included, then predict on the same `X`. `nu=0.1` caps the training error at a tenth, so about a tenth of the points end up outside the frontier and are labeled outliers; the chart reports a training error rate of 0.113. `tol=0.001` is the optimizer's stopping tolerance. The recipe in the caption, delete the n percent of data flagged as outliers, follows directly: `nu` chooses n.

The catch is that the fraction comes from `nu`, whatever the data contains. The frontier is placed so that the most peripheral tenth of the points fall outside it, so on clean data the method discards a tenth of the legitimate observations, and on heavily contaminated data it keeps everything past the first tenth. The chart, from an older version of the scikit-learn documentation, shows one blob of regular observations in green inside the red frontier and the flagged points in red around its edge, which is the peripheral-tenth behavior on a single cluster.

## Page 55

The isolation forest starts from a different question: how easy is it to separate a point from everything else. The claim behind it, from Liu, Ting and Zhou's 2008 paper Isolation Forest, is that anomalies are few and different: a minority of the data, with attribute values far from the majority's. A point with both properties can be cut off from the rest with few partitions, while a point inside a dense region needs many partitions before it stands alone. The method measures that ease of separation directly instead of first modeling what normal looks like.

## Page 56

The figure, from the source article, shows the structure. An isolation forest is a set of isolation trees, each built on a random subsample of the data by random splits that continue until every point sits alone in its own leaf. A point's path length in a tree is the number of splits it took to isolate it. In each tree drawn, the red point is alone after one split, the dark blue points after two, and the light blue point after five.

The score on the left converts path length to a number between 0 and 1. The forest averages a point's path length over all its trees and normalizes it by the average path length of a tree of that size, so the score is near 1 for points that isolate quickly, and those are the outliers; well below 0.5 for points deep in the trees, the common normal cases; and near 0.5 for points between, labeled normal uncommon on the bar. Liu, Ting and Zhou's reading is that a dataset whose scores all sit near 0.5 has no distinct anomalies.

## Page 57

One tree is built by recursive random splitting. At each node, pick a feature at random, pick a split value uniformly between that feature's minimum and maximum among the points in the node, send the points below the value to one child and the rest to the other, and repeat in each child until a node holds a single point or a depth limit is reached. The second bullet compresses this: the splitting repeats until every observation in the subsample is isolated, and the whole procedure repeats for each tree in the forest, each on its own random subsample.

Path length is short for an outlier because a point far from the bulk on some feature falls on the sparse side of a random split with high probability, and once it is on its own side it is isolated. A point in a dense cluster shares every split with its neighbors until the splits become fine enough to separate them, which takes many levels. To score a new point, drop it down every tree, record the depth at which it ends, average the depths, and convert the average to the score.

## Page 58

Four advantages, each from the source article. No feature scaling: a split compares one feature against a threshold drawn between that feature's own minimum and maximum, so a linear rescaling of a feature rescales the thresholds with it and leaves every tree's behavior unchanged; the standard deviation and z-score methods, by contrast, mix features only after scaling. No distribution assumption: the method estimates no density and fits no curve, so it is non-parametric and unaffected by skew. Few parameters: the number of trees, the subsample size and the contamination fraction, with the paper's defaults of 100 trees and 256 samples per tree. scikit-learn: `IsolationForest` in the ensemble module, with the same fit and predict calls as the other detectors.

## Page 59

Two disadvantages. Visualization: the fitted model is a hundred or more trees of random axis-aligned splits, with no equation or single boundary to plot; in two dimensions the decision region can be drawn as a contour, as in the comparison grid, and beyond two it cannot, so explaining why a point scored high needs a separate tool such as SHAP values over the features. Training time: cost grows with the number of trees, the subsample size and the depth of each tree; the paper's subsampling of 256 points per tree keeps training fast regardless of dataset size, and setting the subsample to the full dataset on a large table, or growing many trees, is what makes it slow. Scoring also traverses every tree for every point, so prediction on a large table has a cost of its own.

## Page 60

The listing is from scikit-learn's isolation forest example. `max_samples=100`: each tree is built on a random subsample of 100 training points. `random_state=rng`: the seed for the random feature and split choices, so a run can be reproduced. `contamination='auto'`: the score threshold is placed at the paper's natural cutoff, a score of 0.5; passing a float instead sets the fraction of training points to flag. `predict` returns 1 for inliers and minus 1 for outliers, and the example scores the training data, a held-out set of regular points, and a set of generated outliers.

`behavior='new'` fails on any version. scikit-learn spelled the parameter `behaviour`, and it selected the current scoring convention, with the decision function centered at zero, during the transition in versions 0.20 to 0.22; it was removed in 0.24, so on a current install the line raises a TypeError either way. Delete the argument.

## Page 61

The chart is the example's output. White points are the training observations, in two clusters at about (2, 2) and (minus 2, minus 2); green points are new regular observations, drawn from the same clusters; red points are new abnormal observations, scattered across the square. The shading is the decision function: palest where a point is scored as an inlier, darkening as the score moves toward outlier.

The pale cross-shaped bands extending horizontally and vertically from each cluster are the signature of axis-aligned splits. A point that shares its horizontal coordinate with a cluster but sits far above it still takes several splits on the vertical axis before it is isolated, so its path is longer than that of a point off in both coordinates, and its score is milder. The red points sit in the dark regions except for the few that landed at the cluster edges, and every green point sits in the pale region.

## Page 62

The last part returns to the data validation problem, with the tools for text fields that the numeric methods leave uncovered.

## Page 63

Every method so far needed a numeric distance between an observation and the reference. Text columns have no arithmetic, so validating them needs a distance defined on strings: a number that is zero when two strings match and grows as they diverge.

## Page 64

Such distances exist, defined either on the characters of two strings directly or on the sets and vectors built from them.

## Page 65

Four string distance functions, by what they compare. Cosine similarity: represent each string as a vector of counts, of characters or of short character sequences, and take the cosine of the angle between the two vectors; 1 means the same composition in the same proportions, 0 means nothing shared, and length does not enter. Jaccard distance, after the Swiss botanist Paul Jaccard: treat each string as a set of tokens, divide the size of the intersection by the size of the union to get the similarity, and subtract from 1. Jaro distance, after Matthew Jaro, who devised it for matching census records: count the characters that match within a window of each other, penalize the matched characters that are out of order, and combine the fractions; the slide's "from each file" means from each string. Levenshtein distance (pronounced LEV-en-shtine), after the Soviet mathematician Vladimir Levenshtein: the smallest number of single-character insertions, deletions and substitutions that turns one string into the other, so kitten to sitting is 3.

Levenshtein is the one the next listing uses. It counts edits, so it is the natural measure for detecting a value that is one or two characters off a template.

## Page 66

The example is a column of MAC addresses, hardware addresses written as pairs of hexadecimal digits separated by colons. A MAC address has six pairs, so the format is XX:XX:XX:XX:XX:XX; the slide's pattern shows five.

Tokenizing replaces every letter and digit with the single character A and leaves the separators alone. Every well-formed address then collapses to the same string, AA:AA:AA:AA:AA:AA, whatever its digits were. That string is the template, and a value's distance from the template measures how far its format departs from the format of the good data, with the digits themselves out of the comparison.

## Page 67

The listing applies the idea. `good_macs` holds eleven known-good addresses. `unknown_macs` holds eight to check, one of which, BB-1E-FB-A3-CE-DF, uses dashes as separators. `tokenize_data` substitutes A for every character matched by the regular expression `\w`, which covers letters, digits and the underscore. The loop tokenizes each unknown address, takes its Levenshtein distance from the template token, and reports any address whose distance is above zero. The dashed address tokenizes to AA-AA-AA-AA-AA-AA, five substitutions from AA:AA:AA:AA:AA:AA, and is the one reported.

Three defects in the listing as printed. `tokenize_data` takes a parameter `d` but substitutes on `mac`, so it works only because `mac` happens to be the loop variable at module level; the body should use `d`. `template_token` is used without being defined; it is the tokenized form of a good address. `pandas` is imported and `good_macs` is built, and neither is used.

The detector sees format only. A value with the right separators and the wrong characters, such as GG in place of a hex pair, tokenizes to the template and passes, because `\w` maps G to A the same as it maps F. Checking the characters as well as the shape needs a second rule or a tokenization that distinguishes hex digits from other letters.

## Page 68

Questions on the unsupervised techniques and string distance, before the group discussion and the lab.

## Page 69

The two examples work by different mechanisms. faceboook.com is a typosquat: one extra character, Levenshtein distance 1 from facebook.com, and a reader skimming the string misses it. The second is a homoglyph: its first letter is the Cyrillic letter er, which is drawn the same as a Latin p, so the string is visually identical to papajohns.com and is a different domain. The slide calls the letter a Russian rho; rho is the Greek letter, and the Cyrillic one is er.

The three questions map onto the module. Data: a list of the legitimate domains the spoofs imitate, since a spoof is defined by its distance from a real name, plus examples of known spoofs to test against. Technique: a string distance from each domain to its nearest legitimate domain catches typosquats, and a check on which script each character belongs to catches homoglyphs, which by construction have a small edit distance and a large visual similarity; internationalized domains are transmitted in an encoded form beginning xn--, so a mixed-script name reveals itself there. Success: the fraction of known spoofs caught against the fraction of legitimate domains wrongly flagged, since a detector that flags every domain within distance 1 of a brand also flags legitimate names that happen to be close.

## Page 70

Worksheet 6.1 applies the forecasting part of the module to CPU utilization data from Chio and Freeman's book, in two datasets: A without an anomaly and B with one, each split into a training and a test file.

Part one works through the ARIMA pipeline on dataset A. Load the training file with dates parsed, then check stationarity twice: plot a rolling mean and rolling standard deviation over the series and look for flat lines, and run the augmented Dickey-Fuller test from statsmodels. Compute the autocorrelation at lags 1 through 19 and draw the autocorrelation plot to see how far back the series remembers itself. Run seasonal decomposition with the additive model, trying several periods. Confirm the stationarity verdict with pmdarima's `ADFTest`. Fit `auto_arima` with `seasonal=True`, print the summary, and plot the in-sample predictions over the data. Then switch to dataset B: fit on its training file, forecast 60 steps, subtract the forecasts from the test values to get the anomaly score, plot the score, and find the intervals where it peaks; the anomaly begins at the tenth step.

Part two forecasts the full B series with Prophet, Meta's forecasting library. Prophet needs a two-column frame named `ds` for the timestamp and `y` for the value, so rename the columns first. Fit the model, build a future frame of the timestamps to forecast, and predict; the result carries `yhat`, the forecast, with `yhat_lower` and `yhat_upper` as the bounds of the uncertainty interval, set to 90 percent in the worksheet. The interval comes from simulated trend paths, so the bounds vary slightly between runs. Plot the forecast with its interval and the components plot, which shows the trend and seasonality Prophet extracted. The worksheet is sized for 20 to 30 minutes.
