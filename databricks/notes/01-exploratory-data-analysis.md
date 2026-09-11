## Page 1

Exploratory data analysis, the inspection and summary of a dataset before any model is built, is the first phase of a data science project, which is why the course opens with it. Module 1 introduces pandas, the Python library for tabular data, from the vectorized data structures it is built on up to the operations used to explore a dataset. Worksheet 1.1 is the lab for this module.

## Page 2
The module has two goals. Vectorized data structures: what they are, why they replace loops, and the two pandas objects that implement them, the Series and the DataFrame. Exploring tabular data: loading a dataset into a DataFrame and using pandas to inspect, filter and summarize it. The code throughout targets pandas 2.0 and later.

## Page 3
Using AI to write the lab code is expected. The quality of what a model produces depends on the direction it is given, and giving good direction about pandas requires knowing what a Series and a DataFrame are, how indexing works, and which operation a task calls for. Write the early exercises by hand until those concepts are familiar, then hand the typing to a model.

## Page 4
Pasting a dataset into a language model prompt is a poor way to analyze it. Context limits: a model accepts a bounded number of tokens per request, and a full telemetry table exceeds it. Cost and speed: every row sent is billed and processed as text, so a question over a large table is slow and expensive next to a pandas operation on the same data. Auditability: a model's answer arrives without the computation that produced it, so nobody can rerun or check it. Accuracy: a model can state a wrong figure with the same fluency as a right one.

## Page 5

The working pattern is to have the model write pandas code, or a SQL query when the data sits in a database, and to run that code over the data locally. Give the prompt the schema: column names, types, and what each column holds, plus a few sample rows if the values need illustrating. Ask for Python or SQL that performs the task. The code runs over the full dataset at the speed of pandas or the database, its output can be inspected, and the code itself is the audit trail. Module 10, Prompt Engineering, covers how to write such prompts.

## Page 6
This part defines vectorized data structures and explains why pandas is built on them.

## Page 7
A definition of vectorized data structures follows, with the loop they replace and the table layout they assume.

## Page 8
A vectorized data structure applies an operation to every element it holds in one call. Adding one to a column, comparing a column against a threshold, or multiplying two columns together is written once, as an expression over whole columns, and the library carries it out across all the rows. The plain Python alternative is a loop that visits each element in turn.

## Page 9
Three properties follow from operating on whole columns. Readability: an expression over a column states what is computed, and the bookkeeping of loop variables and positions disappears. Performance: the library sees the whole operation at once, so it can run it in compiled code over a contiguous block of memory instead of interpreting one Python statement per element, and it can pick a compact storage type for the column. Interchange: a column or table is one object with a known layout, so it can be serialized whole and passed to another process or system.

## Page 11

The loop increments each element one at a time: Python fetches an element, adds one, stores it back, and advances the position, once per row, with the interpreter's overhead paid on every pass. The vectorized form states the same computation once for the entire column. With `evens` holding a column of even numbers, `odds = evens + 1` produces a new column with one added to every element, and the addition runs inside the library. If you find yourself writing a loop over the rows of a pandas object, stop and look for the vectorized form; one exists for nearly every per-row computation.

## Page 12
Column arithmetic depends on a table layout in which each variable has its own column and each observation has its own row. In that layout, `F = M * A` multiplies column M by column A one row at a time and writes the products into a new column F, with the expression written once for every row. The layout is what makes the expression meaningful: a column is a vector of one variable's values, so arithmetic between two columns pairs up values that belong to the same observation.

## Page 13
Python and R both provide vectorized structures. An R vector or data frame column takes an operation applied to every element with no loop written by the analyst, which is the same idiom pandas provides in Python.

## Page 14

The pandas name does not refer to the animal. It is drawn from panel data, the econometrics term for a table that follows several variables across several time periods.

## Page 15

The pandas library is the open-source foundation of Python data analysis. Its core is a set of vectorized data structures, the Series and the DataFrame, with a large library of operations over them. The rest of the Python data science stack assumes it: scikit-learn accepts DataFrames as input, and Matplotlib and Seaborn plot from them. Version 2.0, released in April 2023, added optional Apache Arrow-backed column types and a copy-on-write mode, a memory model in which an object derived from another shares its storage until one of the two is modified. Version 3.0, released in January 2026, made copy-on-write the only behavior and gave text columns a dedicated string type in place of the general object type. The code in this course runs on 2.0 and later.

## Page 16

The components of pandas. Labeled array structures: the Series, one-dimensional, and the DataFrame, two-dimensional, each carrying an index of labels alongside its values; a Series whose index holds timestamps is a time series and needs no class of its own. Index objects: the label axis itself, which supports single-level lookup and hierarchical indexing, several levels of labels on one axis. A group by engine: splitting rows into groups that share a column's value and aggregating or transforming each group. Date range generation: `date_range` builds sequences of timestamps at a chosen frequency, with custom offsets for business calendars and similar schedules. Input and output: readers for delimited text and Excel, and the binary HDF5 format for saving and reloading pandas objects. Sparse structures: memory-efficient variants for data that is mostly missing or mostly one constant. Moving window statistics: rolling means, rolling standard deviations and the like over a sliding window of rows.

Timestamps are written in ISO 8601, the international standard that orders a date from year down to second, as in 2026-01-21T14:30:00. The three-dimensional Panel was deprecated in pandas 0.20 and removed in 0.25 in 2019; a third dimension is now represented with a hierarchical index on a DataFrame or with the xarray library.

## Page 17
A DataFrame is a table. Each column has a name and holds one variable, here a registration number, a name and a mark; each row is one record, here one student. Every column is a Series, and all of the columns share one row index, so a value is addressed by a row label and a column name.

## Page 18

This section covers Python libraries: what one is, the four forms an import statement takes, and where third-party libraries come from and how they are installed.

## Page 19

A Python library is a file or package of Python code that defines classes, functions and variables for other code to use. The language documentation calls the same thing a module; this course says library. The standard library ships with the interpreter: its modules are installed wherever Python is, so they are imported with no download or install step, which matters on an air-gapped machine, one kept off every external network, where nothing can be fetched. `import ipaddress` loads the standard module for inspecting and manipulating IP addresses, and the same statement works in a script or in a notebook cell.

## Page 20

The first import form loads the whole library under its own name, and everything inside it is reached through dot notation: the library name, a period, then the function. `ipaddress.ip_address(...)` builds an address object from a string, here an IPv4 address embedded in IPv6 notation, and the object carries its own methods, so `user_address.is_private` reports whether the address falls in a range reserved for private networks. A method is a function attached to an object, the same construction as the string methods.

The answer shown is False, and it depends on the Python release: older releases classified the whole IPv4-mapped range as private and returned True for this address, while current releases delegate the check to the embedded IPv4 address, 185.15.58.226, which is publicly routable. In a Jupyter cell, typing the library name, a period and the first letter of a name, then pressing Tab, lists the library's names that begin with that letter; this is tab completion.

## Page 21

Two keyboard aids in Jupyter. Tab completion: after a library name and a period, Tab lists the names the library defines, filtered by whatever letters are already typed; Tab after a partly typed variable name lists the variables defined so far in the notebook. Shift and Tab together: with the cursor on a function's name or inside its parentheses, this opens the function's documentation in a floating panel, the same text `help()` prints into the cell output, without dumping it there.

## Page 22

The second form gives the library a shorter name at import time, and every later call uses the alias in the dot notation in place of the full name. `import ipaddress as ip` makes `ip.ip_address("185.15.58.226")` the same call as before, this time on a plain dotted-quad address, four decimal numbers separated by periods. `import pandas as pd` is the convention for pandas across the data science ecosystem, so `pd.DataFrame()`, which creates an empty DataFrame, is how the call reads in the documentation and in every notebook of this course.

## Page 23

The third form names the functions to bring in, `from library import name1, name2`, and those names are then called directly, with no library prefix. Here `ip_address`, `ip_network` and `ip_interface` come in from ipaddress, and `ip_interface(...)` builds an interface object, an address paired with its network, straight from the string. Only the named functions are bound in the namespace; the rest of the library's names stay out of it, which keeps a script's set of names small and states in one line where each imported name came from.

## Page 24

The fourth form, `from ipaddress import *`, binds every public name the library defines into the current namespace, so `ip_network("192.0.2.0/24")` works with no prefix and so does everything else in the module. Do not use it, for three reasons. Naming conflicts: an imported name silently replaces a function or variable of the same name defined earlier, or is replaced by one defined later. Readability: a reader cannot tell which library a bare name came from without searching every wildcard import in the file. Namespace clutter: dozens of names the code never uses are now defined, and they show up in tab completion. The form is common in tutorials and notebooks regardless, so it has to be recognized when read.

## Page 25

A third-party library is one written outside the Python project: pandas for tabular data, NumPy for numeric arrays and requests for HTTP calls are all third-party. None ships with the interpreter, so each has to be installed into the Python environment before it can be imported, with pip or conda from a shell, or with pip from a notebook cell. The packages come from the Python Package Index, PyPI, pronounced pie-pee-eye, the public repository at pypi.org; pip installs from it directly, and conda installs from its own channels, which repackage most of the same libraries. Once installed, a third-party library is imported with the same four forms as a standard one.

## Page 26

PyPI's search page, queried for security and filtered by the classifier Intended Audience: System Administrators, which returns 1,245 projects. Every project carries classifiers, labels its author chose from a fixed list covering framework, topic, development status, license, Python version, operating system and audience, and the left-hand filters narrow a search by them. Each result shows the package name, its current version, a one-line description and the date of its latest release, which is how a package's maintenance is judged at a glance.

## Page 27

A project's own page on PyPI, here fastapi-security 0.5.0. The header gives the exact `pip install fastapi-security` command, the latest version and its release date; the left column links to the homepage, the documentation and the source repository; the body is the project description with its installation options.

The exact name matters because anyone can publish to PyPI. For a period, attackers uploaded packages whose names were common misspellings of popular ones, so that a mistyped install command fetched malicious code with no error; this is typosquatting. PyPI now scans uploads for it, and the check before any install remains to copy the name from the project page rather than type it from memory.

## Page 28
This part covers the Series: creating one, reading elements by position and by label, and filtering and transforming its values.

## Page 31
A Series is an ordered sequence of values, readable by position and sliceable as a list is, and each value also carries a label in the index, so a value can be looked up by label as in a dictionary. Beyond either container, a Series is vectorized: an arithmetic operation, a comparison or a string method applies to every element in a single operation, and the values sit in a typed array that the library can process at native speed.

## Page 32
The DataFrame is built from Series: each of its columns is a Series, and the columns share one index. Every operation covered for a Series, indexing, slicing, filtering, arithmetic and string methods, therefore carries over to a DataFrame column unchanged, and a row or column extracted from a DataFrame comes back as a Series.

## Page 33
These three imports open every notebook in this course, each under its conventional alias. pandas as `pd`: the data structures and operations this module covers. NumPy as `np`: the array library pandas builds on, which also supplies values such as `np.nan` for missing data. Matplotlib's pyplot as `plt`: the plotting interface used to draw charts from Series and DataFrames. The aliases are followed across the Python data ecosystem and in the documentation, so code that uses them reads the same everywhere.

## Page 34
A Series is constructed from data plus an optional index. The data is the values: a list, a NumPy array, a dictionary or a scalar. The index is the sequence of labels, one per value; when it is omitted, pandas assigns integer positions starting at zero. When the data is a dictionary, its keys become the index and its values become the elements, so no index argument is needed.

## Page 35
Two ways to build a Series. From a list: `series1` holds the five strings a through e, and because no index was given, the labels are the integers zero to four. From a dictionary: `series2` takes the keys firstName and lastName as its index and Charles and Givre as its values. The dictionary form produces a labeled record, which is how a single row of a DataFrame is represented when it is pulled out on its own.

## Page 36
Printing a Series lists the index beside the values, with the data type on a final line. The left column is the index, here the default positions zero to four; the right column holds the values. `dtype: object` is the storage type pandas chose for these values: object is the catch-all for Python strings and mixed content, where a numeric column would report int64 or float64 and support fast arithmetic.

## Page 37
Reading one element by index looks like list indexing. `series1[3]` returns d, the element at position three, because the default index labels the elements zero through four and label three is position three. The bracket looks up a label in the index; that label coincides with the position only because the index is the default. A Series built with custom labels is looked up by those labels, and position-based access goes through `.iloc`.

## Page 38

A slice between the brackets returns a run of elements, as it does on a list: `series1[1:3]` returns the elements at positions one and two, b and c, because the end position is excluded. The result is a new Series that keeps the original labels, 1 and 2, and reports its dtype on the last line.

## Page 39

A slice keeps the source labels, and that has a consequence: `series2 = series1[1:3]` holds b and c under the labels 1 and 2, so `series2[0]` raises a KeyError because no element is labeled zero. `reset_index(drop=True)` renumbers the index from zero; `drop=True` discards the old labels, and without it they would become a new column and the result would be a DataFrame. The method returns a new Series and leaves `series2` untouched unless the result is assigned back or `inplace=True` is passed; as written, the last line computes the renumbered Series and discards it.

## Page 41
Passing a list of labels inside the brackets selects several elements at once. `record[['firstname','lastname']]` returns a new Series holding just those two entries, labels included, in the order the list gives them. The outer brackets are the indexing operator and the inner brackets build the Python list of labels. A single label between one pair of brackets returns the bare value, while a list returns a Series.

## Page 42
An integer between the brackets on a Series with string labels is treated as a position, so `record[0]` returns Charles, the first element. pandas 2.x still honors this with a FutureWarning, because the same bracket is label-based on an integer index and the warning states that a future version will treat integer keys as labels everywhere. Position-based access that is stable across versions is `record.iloc[0]`; label-based access is `record.loc['firstname']` or `record['firstname']`.

## Page 43
`head()` returns the first five elements of a Series, with their labels and the dtype line; `head(n)` returns the first n. Here the Series is fifty random integers between 1 and 100 drawn with NumPy, and the dtype is int64 because every value is a whole number. `head()` is the standard first look at any column or table, since it shows the shape of the values without printing thousands of rows. NumPy deprecated `np.random.random_integers` in version 1.11 in favor of `np.random.randint(1, 101, 50)`, whose upper bound is exclusive, or the generator form `np.random.default_rng().integers(1, 101, 50)`.

## Page 44
`tail(n)` returns the last n elements; `tail(7)` gives positions forty-three through forty-nine of the fifty-element Series. The labels are retained, so the output starts at 43, and the highest label is 49, one less than the length, because the default index starts at zero. head and tail together bracket a dataset: the first rows confirm the load parsed correctly, and the last rows catch trailing content such as a totals row or a truncated final record.

## Page 45
A Series indexed with a boolean condition returns only the elements for which the condition is true. `randomNumbers < 10` is itself a vectorized operation: it compares every element against ten and produces a Series of True and False values with the same index. Placing that boolean Series inside the brackets keeps the rows where it is True. The result retains the original labels, 12, 21, 24, 27 and 29 here, which record where in the source each kept element sat. Conditions combine with `&` for and, `|` for or, and `~` for not, each side wrapped in parentheses because those operators bind more tightly than the comparisons.

## Page 46
String conditions filter the same way as numeric ones, through the `.str` accessor. `record.str.contains('Cha')` tests every value for the substring and returns a boolean Series with the original labels; only firstname holds a value containing Cha. Indexing with that boolean Series filters the record down to the matching entry. The `.str` accessor exposes Python's string methods, plus regular-expression variants, as vectorized operations over a Series of strings.

## Page 47

The `.str` accessor's methods for matching and editing text; the link at the foot of the slide is the method summary in the pandas user guide, which lists many more. contains: True where the pattern occurs anywhere in the value; the pattern is a regular expression unless `regex=False` is passed. count: how many non-overlapping matches of the pattern each value holds. extract: the text captured by the pattern's parenthesized groups, one column per group, so the result is a DataFrame. find: the position of the first occurrence of a literal substring, or minus one if absent; no regular expressions. findall: every match of the pattern in each value, as a list per element. len: the number of characters in each value. replace: each match of the pattern replaced with the replacement string; since pandas 2.0 the pattern is treated as a literal unless `regex=True` is passed. Two related methods the table omits: match tests the pattern at the start of the value, and fullmatch requires the pattern to cover the whole value.

## Page 48
`pd.to_datetime` converts a Series of timestamp strings, or a list of them, into pandas datetime values. The format argument is a strftime pattern, for example `'%Y-%m-%d %H:%M:%S'` for 2024-05-01 13:45:00, that states how each string is laid out. Supplying it avoids guessing: pandas 2.0 infers a single format from the first value and applies it to all of them, and a value that does not fit the format raises an error. Once converted, the values are stored as 64-bit integers counting nanoseconds since 1970 by default, so comparisons, differences and sorting work as arithmetic, and the `.dt` accessor becomes available.

## Page 49

The `.dt` accessor exposes the parts of a datetime column as vectorized properties; the linked page is the time series chapter of the user guide, which covers the rest. year, month and day: the calendar components as integer Series. weekday: the day of the week as an integer, Monday being zero and Sunday six. is_month_start: True for values that fall on the first day of their month. strftime: the datetimes rendered back into strings according to a format pattern, the inverse of to_datetime; it requires the pattern as an argument. These components are how a timestamp becomes a feature: an hour-of-day or day-of-week column extracted from an event time is what a model or a plot can use.

## Page 50

Arithmetic between two Series also has a method form. `series1.add(series2)` computes the same element-wise sum as `series1 + series2`: the elements are matched by index label rather than by position, and a label present in only one of the two produces a missing value in the result. The method form exists for its `fill_value` argument, which substitutes a number for the absent side of such a pair so the result holds a value there instead of NaN. sub, mul, div, floordiv, mod and pow are the method forms of the other operators, with the same arguments.

## Page 51
`apply` runs a Python function on every element and collects the results into a new Series. `addTwo` takes one value and returns it plus two; `odds.apply(addTwo)` calls it once per element and keeps the index. The cost is that each call is a Python function call, interpreted one element at a time, so apply gives up the compiled-code speed of a vectorized expression. For this example `odds + 2` computes the same result as one vectorized operation; apply is for logic that has no vectorized equivalent, such as a lookup or a multi-branch transformation.

## Page 52
A lambda is an unnamed function written inline, and apply accepts one in place of a named function. `lambda x: x + 1` takes one argument and adds one to it, so `odds.apply(lambda x: x + 1)` adds one to every element. It is the same element-by-element Python call as the named version, with the same speed penalty, and `odds + 1` does the same work vectorized.

## Page 53
The Series section ends here. Summary statistics come next.

## Page 54

The section that follows introduces the statistics used to summarize a column and the vocabulary around them: populations and samples, numerical and categorical variables, the histogram and the distributions it reveals, measures of center and spread, quartiles and the box plot, outliers, rescaling a column to a common range, and the pandas methods that compute each. Counting distinct values and plotting a column close the part.

## Page 55

The statistics section covers the descriptive methods used while cleaning, analyzing and visualizing data, and it uses the pandas skills from the Series section to turn each equation into code. Five outcomes are set. Compute and distinguish the mean, median, mode, range, standard deviation and variance of a dataset. Decide when the median is the better measure of center than the mean. Read a histogram and a box plot to understand a column's distribution. Identify outliers and decide what to do with them. Normalize or scale a feature and say when the step is necessary.

## Page 56

Probability is the mathematics of randomness: it assigns a number between zero and one to the chance that an event occurs. Statistics uses it to state predictions, so a forecast of an earthquake, or of a rise in web traffic, takes the form of a probability rather than a yes or a no.

## Page 57

A population is the whole collection under study, every user on the internet, for example. A sample is the portion of it that can be observed, such as the users who visited one website, and it is studied to learn about the population it was drawn from. Data is what sampling produces, so every dataset in this course is a sample, and every statistic computed from it estimates the population figure rather than stating it.

## Page 58

A variable is a characteristic or measurement recorded for each member of a population, which in a table is a column. Numerical: a quantity, such as weight, bytes transferred or connection time, on which arithmetic makes sense. Categorical: a label from a set of categories, such as user or bot, or a location, where the only operations are equality and counting.

## Page 59

The variable types under the names statisticians use. Qualitative: categorical data, the non-numeric labels such as a user's status, a URL or a gender. Quantitative: numeric data, which splits again. Discrete: whole numbers that come from counting, such as the number of site visits or logins. Continuous: values on a continuum, decimals and fractions such as a weight or an amount of time, where any value between two observed ones is possible. The split decides the plots and summaries that fit: counts per category for qualitative data, a bar per value for discrete, and histograms over binned ranges for continuous.

## Page 60

The dataset used through the rest of the section: server connection logs joined to a user table, one row per session on a given date. company: the organization the user belongs to. username and name: the account and the person. mail: the address on the account. connected: the length of the session in minutes, a decimal. The discrete and continuous examples, the histograms and the summary statistics that follow all come from this table.

## Page 61

Number of users per company is a discrete variable: it comes from counting rows, so every value is a whole number. The bar chart puts one bar per company, sorted by count, from three users at Booth Ltd to twenty-seven at Peacemakers, with the count on the vertical axis. A bar chart is the plot for a discrete or categorical variable because each bar stands for one distinct value.

## Page 62

Connection time is a continuous variable: the minutes are decimals on a continuum rather than counts. The plot is a density curve, a smoothed estimate of how the values are distributed, with time in minutes across the bottom and density up the side; density is scaled so that the area under the curve is one, which is why the vertical axis reads in fractions rather than counts. Most sessions last between about five and fifteen minutes, with the peak near ten.

## Page 63

The distribution of a variable is the frequency of each of its values, and it is the first thing to describe about a column. The normal distribution, also called Gaussian or the bell curve, is the shape many measurements take: symmetric around the mean, densest at the center, thinning toward both tails. Two parameters fix it completely, the mean μ, which locates the center, and the standard deviation σ, which sets the width. The percentages on the figure are areas under the curve: 34.1 percent of the values lie between the mean and one standard deviation above it, so 68.2 percent lie within one standard deviation of the mean, 95.4 percent within two, and about 99.7 percent within three. A normal distribution with mean zero and standard deviation one is the standard normal.

## Page 64

A histogram shows a distribution directly and is the starting plot for a new numeric column. The range of the variable is cut into intervals called bins, and the bar over each bin counts the values that fall in it, so the outline of the bars is the shape of the distribution. Here the bins are about three minutes wide; the tallest, with just over forty sessions, runs from about seven to ten minutes, no session falls in the bin around twenty, and a lone bar of fourteen sits between twenty-one and twenty-four. An empty bin followed by an isolated bar is the pattern to notice: it separates a small group of long sessions from the rest.

## Page 65

The mode is the value that occurs most often, and on a histogram it is a peak. Unimodal: one peak, as on the left, where the values cluster around a single center. Bimodal: two peaks, as in the middle, which usually means two different groups have been mixed in one column. Multimodal: several peaks. The mean and the median of a bimodal column can land in the trough between the peaks, where few values sit, so the histogram is checked before either is trusted.

## Page 66

The mean is the most common summary statistic and a measure of central tendency, the value the data clusters around. It is the sum of the values divided by their count. In the formula, x̄, read x bar, is the sample mean and μ, the Greek letter mu, is the population mean; n is the number of data points, and the sum runs over every x sub i from one to n. The example computes the mean of 3, 2, 9, 4 and 1 as nineteen divided by five, which is 3.8. Every value contributes to the sum, so one extreme value moves the mean; that is its sensitivity to outliers.

## Page 67

The mean connection time is 10.11 minutes. On the histogram it falls inside the tallest bin, so here the mean sits where the data is densest, but the lone bar of long sessions on the right and the sessions near zero on the left both pull on it: the mean is the balance point of the histogram, not its peak.

## Page 68

Variation is the spread of the data around the mean, and every dataset has some. Two measures quantify it. Variance: the mean squared deviation. The deviation of a value is its distance from the mean, x sub i minus x bar; squaring each deviation makes it positive, so values below and above the mean do not cancel, and the average of the squares is the variance, written s squared. The formula divides by n minus one rather than n because the data is a sample: the sample mean sits closer to the sample's own values than the population mean would, and the smaller denominator corrects for it. pandas uses the same denominator in `var` and `std` by default. Standard deviation: the square root of the variance, written s or σ, which puts the measure back in the units of the data. Both square the deviations, so a single extreme value contributes a term that grows with the square of its distance, and both are inflated by it.

## Page 69

For the connection times the variance is 44.73 and the standard deviation is 6.68. The variance is in minutes squared, a unit with no direct reading; the standard deviation is in minutes, the same unit as the data, so it reads against the histogram: a typical session lies within about six and a half minutes of the mean of 10.11. That is why the standard deviation is the measure reported and the variance is the intermediate step.

## Page 70

Two distributions described by histogram, mean and standard deviation together: the ages of Best Actress winners and of Best Actor winners, ninety-two of each. The actresses' mean age is 36.2 with a standard deviation of 11.9; the actors' is 43.8 with a standard deviation of 8.83. The histograms show what the numbers say: the actress distribution is centered lower and spreads wider, with a tail reaching past eighty, while the actor distribution is centered in the forties and is tighter. The three together, histogram, mean and standard deviation, are the standard description of any numeric column.

## Page 71

The median is the middle value of the sorted data, the point that separates the greater half from the lesser half. All three histograms have a mean of zero and a standard deviation of one, and they differ in shape: two spikes at minus one and one, a bell, and a peak near minus one with a long tail to the right. Mean and standard deviation do not tell them apart, so a second measure of center is needed, and the median is it. For the skewed distribution at the bottom the median sits nearer the peak than the mean does, because the tail values pull the mean and only reorder the median.

## Page 72

The median is computed by sorting. The list 8, 3, 1, 8, 3, 9, 2, 0 sorts to 0, 1, 2, 3, 3, 8, 8, 9; with eight values there is no single middle element, so the two middle values, the fourth and the fifth, are averaged: three plus three over two, which is three. With an odd count the middle element is the median directly. Because the values must be sorted first, the median costs more to compute than the mean on a large column, whose sum needs a single pass.

## Page 73
Covariance measures how two variables move together. For each observation, multiply x's deviation from its mean by y's deviation from its mean; the covariance is the average of those products. When x and y tend to be above their means together and below together, the products are positive and the covariance is positive; when one is high while the other is low, the covariance is negative; when there is no relation, positive and negative products cancel toward zero. The magnitude is hard to interpret. It carries the units of x times the units of y, so it is on a different scale from either mean, and covariances of different variable pairs cannot be compared with each other. Dividing by the product of the two standard deviations removes the units and gives the Pearson correlation, which is bounded between minus one and one; `Series.corr` computes it and `Series.cov` computes the covariance.

## Page 74
The five-number summary describes a distribution with its minimum, lower quartile, median, upper quartile and maximum. It is named for John Tukey, pronounced TOO-kee, the American statistician who coined the term exploratory data analysis and, in his 1977 book of that name, introduced this summary and the box plot that draws it. Each quartile is a cut point: the lower quartile is the value below which a quarter of the data lies, and the upper quartile is the value below which three quarters lie, so half of the data sits between them. All five come from the sorted order of the values, so a few extreme values move only the minimum and the maximum.

## Page 75

The interquartile range is the distance between the 75th and 25th percentiles, the span that holds the middle half of the sorted values. Where the range locates the two ends of a dataset, the interquartile range locates where the bulk of the values lie, and unlike the range, which two extreme values determine, it is unchanged by an outlier at either end. In pandas, `quantile(q)` returns the value below which a fraction q of the data lies, so subtracting the 0.25 quantile from the 0.75 quantile computes it.

## Page 76

A box plot draws the quartiles. The box runs from the first quartile, Q1, to the third quartile, Q3, the cut points of the five-number summary, and the line inside is the median, the second quartile. The box therefore holds the middle fifty percent of the data, and its width is the interquartile range, Q3 minus Q1. The whiskers extend from the box toward the extremes but stop at the last value within one and a half interquartile ranges of the box; any value beyond that is drawn as a separate dot, and those dots are the outliers, two of them here near twenty-four minutes.

## Page 77

`describe` reports the same quantities as numbers. On the connected column: count, 180 sessions; mean, 10.11; std, 6.69; min, minus 1.87; the 25 percent, 50 percent and 75 percent rows, which are Q1 at 5.31, the median at 9.33 and Q3 at 15.35; and max, 24.19. The interquartile range is therefore about ten minutes, and the median falls below the mean, which the long sessions on the right pull upward. A negative minimum is impossible for a session length and is the first figure on this output to investigate.

## Page 78

One box plot per company on a shared axis shows whether the distribution of connection time differs between groups. The eight boxes have medians between about eight and eleven minutes and interquartile ranges of similar width, and every group's whiskers reach the same extremes near minus two and twenty-four; Savage LLC alone shows an outlier dot, because its box is narrower and its maximum falls past the whisker limit. Grouped box plots are the quickest check of whether a category matters to a numeric variable, and here the groups look alike.

## Page 79

A box plot with values far beyond the whiskers, three above forty minutes and one below zero, and the histogram of the same column, where those values sit as isolated bars away from the mass. Handling outliers is a step of its own in statistics and in machine learning, and it begins with finding out where each came from. The negative session length cannot be real, so it points at a processing error; the place to check first is the datetime conversion, and time zone handling is the common source of such errors in duration arithmetic.

The high values may be real. If they are, the choice is between removing them and keeping them while using methods that are robust to outliers, such as the median in place of the mean; in a security investigation they are also the first records to examine, since a session many times longer than any other is the kind of record an investigation drills into. When an outlier turns out to be irrelevant to the question, such as a login count beyond what a person could produce in a minute when the question is about human users, it is removed, because one extreme value can dominate every statistic computed on the column.

## Page 80

Features on different scales distort methods that combine them. In the sample table, connected is in the tens and number_logins is a small integer; a model that weighs raw magnitudes, such as one built on distances between rows, lets the larger-scaled column dominate for no reason but its units. Two rescalings fix that. Normalization, the min-max scaler: subtract the column's minimum and divide by its range, which maps every value into the interval from zero to one. Standardization: subtract the mean and divide by the standard deviation, which gives the column mean zero and standard deviation one; each result is the value's z-score, its distance from the mean measured in standard deviations.

Standardization assumes the column is roughly normal, so it is the choice for a bell-shaped column and normalization for one that is not; either applies whether the raw values run in the hundreds or in the thousandths. A column already near the zero-to-one range with a standard deviation near one can be left alone. The describe output on the right gives the figures each formula uses, min, max, mean and std, for both columns.

## Page 81

UNRESOLVED

## Page 82

The Series methods for these statistics, a selection from a longer list. abs: each value's absolute value, as a new Series. count: the number of non-missing values, which is the denominator the mean uses. max and min: the largest and smallest values. mean and median: the average and the middle value. mode: the most frequent value, returned as a Series because more than one value can tie. quantile: the value at a given fraction, or one value per fraction when given a list. sum: the total. std: the sample standard deviation. Every method skips missing values, so count can be smaller than the length of the Series.

## Page 83

`describe` computes the statistics of this section together, as the box plot slide showed for the connected column, and returns them as a Series, with the set of statistics chosen by the column's data type.

## Page 84
For a numeric Series, describe returns eight statistics. count: fifty non-missing values. mean: 50.62, the average. std: 30.10, the sample standard deviation. min and max: 1 and 99, the extremes. 25%, 50% and 75%: the quartiles, 25.5, 54 and 73, so half of these random integers lie between 25.5 and 73, and the median 54 sits a little above the mean. The result has dtype float64 because one Series holds all eight numbers and the count is stored alongside the fractional quantiles.

## Page 86
For a Series of strings, describe switches to a categorical summary. count: nine values. unique: seven distinct names. top: the most frequent value. freq: how many times it appears. Jim and Bob each occur twice, so top reports one of the tied values, here Jim, with freq 2. The list in the code is missing a closing quote after Jim and will not parse as written; with the quote restored it holds the nine names counted here.

## Page 87

Finding the distinct values in a column, and how often each occurs, is the subject of this section. It is among the first steps of any analysis or cleaning pass: the set of distinct values shows what a column holds, its misspellings, its placeholder values and how many categories it has, before anything is computed on it.

## Page 88
The loop collects the distinct values of a Series by hand: it walks every element with `iteritems`, checks whether the value is already in a Python list, and appends it if it is absent. Three things are wrong with it. The walk is one interpreted Python step per element. The membership test scans the list from the start every time, so the work grows with the square of the number of distinct values. `iteritems` was deprecated in pandas 1.5 and removed in 2.0, so under the version this course uses the code raises an AttributeError; `items` is the surviving name.

## Page 89

Do not write the loop. pandas computes the distinct values of a column with hash-based methods in one pass over the data, with no Python-level iteration.

## Page 91

Two methods return the distinct values of a Series. `drop_duplicates()` returns a Series: by default the first occurrence of each value is kept with its original index label and later repeats are dropped; `keep='last'` keeps the last occurrence instead, and `keep=False` drops every value that occurs more than once. `inplace=True` modifies the Series in place and returns None. `unique()` returns a NumPy array of the distinct values in order of first appearance, with no index attached. Both hash the values, so the cost grows linearly with the length of the Series. `nunique()` returns just the number of distinct values, which is the figure the unique row of describe reports for a string column.

## Page 95

`value_counts` tallies how many times each distinct value appears and returns the tallies as a Series, indexed by the values and sorted with the largest count first. Three arguments change what is counted. bins: for a numeric Series, the values are split into that many equal-width intervals and the count is per interval, which is a histogram in table form. normalize: each count is divided by the total, so the result is the fraction of rows each value or interval accounts for. dropna: missing values are excluded by default; passing False adds a row that counts them, which is how a column's missing-value rate is checked. Since pandas 2.0 the returned Series is named count, or proportion when normalized.

## Page 96

The output of `value_counts` on a Series of telephone area codes. Each row pairs a distinct value with the number of times it occurs, 833 seven times, 811 and 822 five times each, down to 855 twice, and the rows are ordered by count, largest first. The values have become the index and the counts are the data, with dtype int64. The counts add up to the number of non-missing rows in the source.

## Page 97

`hist` draws a histogram of a numeric Series, the plot the statistics section used to show a distribution. pandas delegates the drawing to Matplotlib, which is why the pyplot import at the start of the module is needed, and the bin count defaults to ten.

## Page 99

With the default ten bins over the fifty random integers, each bin is about ten wide and the bar heights run from one to eight. The values were drawn uniformly, so every bin's expected count is five, and the variation between bins is sampling noise from a draw of only fifty values; this is what a uniform distribution looks like at a small sample size.

With forty bins, each interval is about two and a half units wide and holds zero, one or two values, with one bin reaching six. The bars now record where individual values happened to land, and the spread of the distribution is no longer readable. Too many bins for the number of values turns a histogram into a picture of noise.

## Page 100

With five bins, each twenty units wide, the counts are fourteen, nine, eight, twelve and seven. The bars are smoother than the ten- and forty-bin versions because each one aggregates more values, and the price is resolution: a feature narrower than twenty units cannot show. Bin count is the one choice a histogram forces. Try two or three bin counts on any new column; the same data can look uniform, bumpy or spiky depending on the choice.

## Page 101

`plot` with no arguments draws a line chart of the Series through Matplotlib, with the index on the horizontal axis and the values on the vertical axis.

## Page 102

The line plot of the fifty random integers: position zero through forty-nine along the bottom, the value at each position up the side, consecutive points joined by a line. A line implies that the order of the index carries meaning, as it does when the index is time. These values were drawn independently, so the line joins unrelated points and the zigzag conveys nothing. The line plot is the right choice for a Series with a datetime index, where it shows how a quantity changes over time.

## Page 103

`plot(kind='box')` draws the five-number summary as the box plot from the statistics section, vertical this time: the box spans the quartiles, the median is the line across it, and the whiskers run out toward the extremes. No value here lies past the whisker limit, so the whiskers end at the minimum and maximum as labeled. The None under the box is the Series' name, which was not set.

## Page 104

A box plot per TCP destination port of the time between scanning attempts observed against exposed services, in hours. Each box is one port: the box holds the central fifty percent of the observed gaps, the bar inside is the median, and the whiskers reach the rest. The ports are sorted by median, so the left side holds services that get probed within minutes of appearing, Remote Desktop on 3389 and SQL Server on 1433 among them, and the right side holds ports probed only every several hours, with MySQL on 3306 at about eight. Read this way, the plot answers a security question directly: how long a newly exposed service on each port goes before an opportunistic scanner finds it. A bar chart of the means would give one number per port; the boxes show the median, the spread of the middle half and the reach of the extremes as well, and the annotated figures are means, as the footnote states.

## Page 105
Correlation is the subject here: the measure of how two numeric columns vary together, and the pandas method that computes it.

## Page 106

Correlation measures the strength and direction of the linear relationship between two continuous variables. The coefficient, written r, is the covariance scaled by the two standard deviations, which strips the units and confines the result to the interval from minus one to one. An r of 1 means the points lie exactly on a rising line; minus one, exactly on a falling line; zero, no linear relationship. Values in between grade how tightly the points cluster around a line. The coefficient defined this way is Pearson's r, and it is the default that pandas computes. Two highly correlated columns carry nearly the same information, so keeping both in a feature set adds complexity without adding signal, and one of them is a candidate for removal.

## Page 107

Six scatterplots with their correlation coefficients. Across the top row, r rises from 0.25 to 0.48 to 0.94 as the cloud of points narrows toward a rising line; across the bottom, r falls from minus 0.12 to minus 0.37 to minus 0.94 as the cloud narrows toward a falling line. The sign gives the direction of the slope and the magnitude gives how much of the scatter the line accounts for; at 0.25 or minus 0.12 the points fill the square and the trend is barely visible. Pearson's r sees only straight-line relationships: two variables tied by a curve, such as a U shape, can score near zero while being perfectly dependent. A high r establishes that the two variables rise and fall together; which one drives the other, if either does, is a separate question that the coefficient cannot answer.

## Page 108

`series1.corr(series2)` returns the Pearson correlation between two Series as a single number. The values are paired by index label, so the two Series must share an index, and any pair with a missing value is left out. `method='spearman'` or `method='kendall'` switches to a rank-based coefficient, which measures whether the relationship is monotonic and is less sensitive to outliers. `DataFrame.corr()` computes the coefficient for every pair of numeric columns at once and returns the results as a square matrix, which is how related features in a dataset are found.

## Page 109
Part 1, the Series and the statistics of a single column, ends here.

## Page 110
Part 2 covers two-dimensional data: the DataFrame, how to load one from a file or a security platform, and how to select, filter and summarize its rows and columns.

## Page 111
Every model in this course is trained on tabular data, and the data begins in a security platform. Elasticsearch, abbreviated ES: the search and analytics engine that stores logs for the Elastic stack and its security information and event management product. Splunk: a commercial platform for indexing and searching machine data, queried with its own search language. PCAP: the packet capture file format written by tcpdump and Wireshark, holding raw network traffic. Whatever the source, the analysis and modeling libraries in Python take their input as a pandas DataFrame, so the first step of any project is getting the platform's data into one.

## Page 112
Extracting data from a security platform into a DataFrame is the entry point to every pipeline in this course. The route is the same across platforms: query the platform through its API or export, receive rows as JSON or CSV, and load them with a pandas reader. Once the data is a DataFrame, everything from Part 1 applies to each of its columns, and the model-building libraries in later modules accept it directly.

## Page 113
This part covers the DataFrame: building one, loading one from a file or a query, and reading its structure.

## Page 114
A DataFrame takes data, optional row labels and optional column names. The data can take several shapes: a dictionary whose keys become column names and whose values are the columns, as lists or Series; a list of dictionaries, each one a row; a two-dimensional NumPy array; or a list of lists. The index labels the rows and defaults to positions from zero, as it does for a Series. The columns argument names the columns and is needed when the data carries no names of its own, such as an array or a list of lists; the placeholder column_names stands for the `columns` keyword.

## Page 115

`read_csv` builds a DataFrame from comma-separated text. The argument is a path to a local file or a URL; given a URL, pandas fetches the file over HTTP before parsing it. By default the first line is taken as the column names, the separator is a comma, and each column's dtype is inferred from its contents, so a column of digits becomes int64 and a column of text becomes object. Keyword arguments cover the departures: `sep` for another delimiter, `header=None` with `names` when the file has no heading row, `parse_dates` to convert timestamp columns on load, `usecols` and `nrows` to read a subset, and `dtype` to fix a column's type in place of inference.

Further arguments cover other shapes of file. `delim_whitespace=True` splits on runs of spaces and tabs; pandas 2.2 deprecated it in favor of `sep=r'\s+'`, which the C parser handles as the same fast path, quicker than a general regular-expression separator. A compressed file, .gz, .bz2, .zip or .xz, is decompressed on the fly, with the format inferred from the extension. `skip_blank_lines`, True by default, ignores empty lines; `skiprows` skips a count of lines, or a list of line numbers, at the top; `index_col` names the column to use as the row index instead of the default positions.

## Page 116
`read_excel` loads one worksheet of a spreadsheet into a DataFrame, with the first row as column names by default. The keyword that selects the sheet is `sheet_name`, by name or by zero-based position; the `sheetname` spelling was removed from pandas in 2017, so the call as written raises a TypeError. Reading .xlsx files requires the openpyxl package to be installed alongside pandas.

## Page 117

`read_json` builds a DataFrame from JSON in a file or at a URL. A top-level list of objects becomes one row per object; a top-level object of lists becomes one column per key. Two arguments cover the formats that platforms export. `lines=True` reads JSON Lines, where each line of the file is a separate object, which is how log exports and API dumps are laid out. `orient` states the layout when it is not the default, which is columns for a DataFrame and index for a Series; the allowed values are split, records, index, columns and values, each naming how the document is nested. `dtype` controls type inference on load: True, the default, infers a type per column, False leaves the values as JSON delivered them, and a dictionary fixes the type of the columns it names. Since pandas 2.1, passing a literal JSON string to read_json is deprecated; wrap it in `io.StringIO` first.

## Page 118
`read_sql` runs a query against a database and returns the result set as a DataFrame, with the column names the query produces. The connection is a SQLAlchemy engine or a DBAPI connection object such as one from the sqlite3 module. The filtering and joining in the query execute inside the database, so only the rows needed reach Python; `read_sql_table` pulls a whole table by name instead of a query.

## Page 119
`read_parquet` loads an Apache Parquet file into a DataFrame. Parquet is a binary, columnar format from the Hadoop ecosystem: each column is stored and compressed separately with its type recorded, so a read recovers the exact dtypes with no inference, and a reader can pull only the columns it names. It is the storage format of Spark, Databricks and data lake tables, which makes it the interchange format between those systems and pandas. Reading it requires the pyarrow or fastparquet package.

## Page 120
Text logs whose lines carry no delimiters take a different loading route, shown in this section: read each line whole, then split it into columns.

## Page 122

A MySQL general query log has one event per line: a date and time, a connection id, a command such as Connect or Query, and the command's argument. The lines are separated by runs of spaces, with the argument itself containing spaces, so no delimiter splits them into fields cleanly, and the file carries no header naming the fields. `read_table` defaults to a tab separator, which these lines lack, and `names=['raw']` supplies the single column name, so each line lands whole in a column called raw with no header row consumed. The result, the table under the call, is a one-column DataFrame of five rows that the string methods can take apart.

## Page 124
`str.extract` with named groups splits the raw lines into columns in one expression. Each parenthesized group in the pattern captures one field, and the `(?P<name>...)` syntax names the group, so the result is a DataFrame whose column names are the group names. The pattern reads left to right: six digits, a space and a time of day for the date; a run of spaces; digits for the connection id, labeled PID here; non-space characters for the command; and everything remaining for the argument. Rows that do not match the pattern get missing values in every column, which makes a malformed line visible. The number MySQL writes in that position is the connection thread id, and the Date column in the table corresponds to the group named date.

## Page 125
Web server access logs come next, parsed into a DataFrame with the Apache log parser package.

## Page 127

An Apache access log line in the combined format, and the format string that describes it. The fields left to right are the client address, two placeholder dashes for the identd and authenticated user, the timestamp with its zone in brackets, the request line in quotes with method, path and protocol, the status code, the response size in bytes, the referring page, and the browser's user agent string. `apache_log_parser` is a Python package that takes an Apache LogFormat string and returns a function that parses one line into a dictionary. The directives in the format string are Apache's own: `%h` the host, `%l` the logname, `%u` the user, `%t` the time, `%r` the request line, `%>s` the final status, `%b` the bytes, and `%{Referer}i` and `%{User-agent}i` the named request headers. The string handed to the parser has to match the LogFormat directive the server was configured with, which lives in the Apache configuration, httpd.conf or a file it includes; a string that does not match the configured format fails on every line or assigns fields to the wrong names.

## Page 128
The full loading sequence for an access log. The parser is built once from the format string. The log file is opened and read line by line; each line goes through the parser and comes back as a dictionary keyed by field name, and the dictionaries are collected into a list. `pd.DataFrame` on that list of dictionaries builds the table, with one row per line and a column per key. The loop here is over lines of unstructured text, where each line needs the parser's grammar applied, so a Python loop is the appropriate tool; the vectorized work begins once the DataFrame exists. The `data = {}` line is overwritten on the next line and has no effect.

## Page 129
The DataFrame built from the access log, with columns named by the parser: request_first_line, request_header_referer, request_header_user_agent, request_http_ver, request_method and request_url, with the host, time, status and byte-count columns off the edge of the screenshot. The parser has already separated the request line into its method, path and protocol version, so those are queryable columns without further string work. The rows themselves record repeated GET and POST requests to a join_form page followed by a request to a credentials path, a sequence that reads as an automated account-creation or login attempt against the site.

## Page 130
Nested data, JSON records whose values are themselves objects, has to be flattened before it fits a table; this section shows how.

## Page 131
A packet decoded to JSON, one record per packet. The top level holds time and timestamp, and beneath them a key per protocol layer: IP is an object with version, ttl, protocol number, length, source, destination, flags and checksum, and Ethernet is an object with source and destination MAC addresses and the frame type. A table has no place for an object inside a cell; every value in a column is supposed to be a scalar of one type. Loading this as it stands leaves the protocol layers as dictionaries stuffed into single cells, which none of the vectorized operations can reach into.

## Page 132
`read_json` on the nested file loads the records without flattening them.

## Page 133
The result of `read_json` on the packet records. The top-level keys became columns: DNS, Ethernet, IP, TCP, UDP, time and timestamp. Every column whose values were objects holds a Python dictionary in each cell, shown as the braces in the Ethernet, IP and TCP columns. DNS and UDP are NaN for these rows because the packets are TCP and carry no such layer. A dictionary in a cell is dtype object, so the IP source address or TCP source port cannot be filtered, counted or plotted as a column until it is extracted from the dictionaries.

## Page 134
`json_normalize` flattens nested objects into columns. The file is read with the standard library's json module, which yields a Python list of dictionaries with the nesting intact. json_normalize walks each record and turns every nested key into its own column named by the path to it, joined with dots, so the IP object's src key becomes a column called IP.src. The import from pandas.io.json has been deprecated since pandas 1.0; the function lives at `pd.json_normalize`. It already returns a DataFrame, so the `pd.DataFrame` wrapper around it does nothing.

## Page 135
The flattened DataFrame, with the nested TCP fields now top-level columns: TCP.seq, TCP.sport, TCP.urgptr and TCP.window, each holding a scalar per row and usable by every column operation. The values print as floats, 3372.0 in place of 3372, because rows for packets without a TCP layer have missing values in these columns, and a column that mixes integers with NaN is upcast to float64. Casting to pandas's nullable Int64 type restores integer display while keeping the missing values.

## Page 136
Querying Elasticsearch and Splunk directly into a DataFrame is the topic of this section.

## Page 137
huntlib is a threat-hunting helper library published by Target's security team; it wraps the Elasticsearch and Splunk client libraries so that a query returns a DataFrame. Elasticsearch: `ElasticDF` takes the cluster URL and credentials; `search_df` takes a Lucene query string, an index pattern and a time window in days, and returns the matching documents as rows. `normalize=False` leaves nested fields as dictionaries in cells, and True flattens them the way json_normalize does. Splunk: `SplunkDF` takes the host and credentials; `search_df` takes a search in Splunk's SPL and a start and end time, here the last two days computed with datetime and timedelta. The code as written omits the imports it needs, `from huntlib.elastic import ElasticDF`, `from huntlib.splunk import SplunkDF` and `from datetime import datetime, timedelta`. Credentials written into a notebook end up in version control and in shared copies; keep them in environment variables or a secrets store.

## Page 138
This part covers selecting columns from a DataFrame, adding new ones, and the difference between bracket and dot access.

## Page 139
Assigning to a column name that does not exist adds the column. The right-hand side is a vectorized expression: `df['column1'] + 3` adds three to every element of column1 and yields a Series, which is aligned to the DataFrame by index and stored under the new name. The right-hand side can be any expression over existing columns, including sums or ratios of two columns and string or datetime accessor results. Assigning a scalar fills every row with that value.

## Page 140
A column can also be read as an attribute, `df.column1`, and the bracket form is the one to use. Attribute access fails for a column name that contains spaces or punctuation, for one that is not a valid Python identifier, and for one that collides with a DataFrame method or attribute such as count, shape or index, where the dot returns the method instead of the column. It cannot create a column: `df.new_col = values` sets a plain Python attribute on the object, the DataFrame gains no column, and pandas only warns. It also cannot take a name held in a variable. The bracket form has none of these limits.

## Page 141

`loc` reaches the same column through explicit row and column selection: the colon before the comma selects every row, the label after it selects one column, and the result is that column as a Series with the row index attached, the same object `df['column1']` returns. The `loc` form is for selecting rows and columns in one step; for a whole column on its own, the bracket form returns the same Series in fewer characters.

## Page 142
A list of column names in brackets returns a DataFrame holding those columns, ordered as listed. Two pairs of brackets appear because the outer pair indexes the DataFrame and the inner pair builds the list. A single name returns a Series; a list, even a list of one name, returns a DataFrame. Assigning the result back to `df` keeps only the listed columns and discards the rest, which trims a wide table down to the fields an analysis needs.

## Page 143
A DataFrame filters the way a Series does: a boolean condition in the brackets selects the rows where it holds. The condition is a Series of booleans built from one or more columns, such as `df['col3'] > 5`, and pandas lines it up with the rows through the index, so it selects rows whether or not the column it tests is among the columns being returned. The second form chains two selections: the list picks the columns col1 and col2, and the condition then picks the rows. Chained brackets are fine for reading. For assignment they trigger a SettingWithCopyWarning, because pandas cannot tell whether the write reaches the original; `df.loc[df['col3'] > 5, ['col1', 'col2']]` does both selections in one step and is the form to use when writing.

## Page 144

Aggregations on a DataFrame run along an axis, and the axis argument picks which. `axis='index'`, the default, also written `axis=0`, runs down the rows and returns one value per column, so `data.sum(axis='index')` totals each column. `axis='columns'`, also written `axis=1`, runs across the columns and returns one value per row, so `data.sum(axis='columns')` totals each row. The same argument applies to mean, min, max, count and the rest of the aggregation methods. The names are easier to read than the numbers once the rule is known: the axis named is the one collapsed.

## Page 145
`drop` returns a copy of the DataFrame with the named rows or columns removed. labels: one label or a list of them. axis: 0 drops rows by index label and 1 drops columns by name; `columns=` is an equivalent spelling for the column case. level: which level of a hierarchical index the labels refer to. inplace: False returns a new DataFrame and leaves the original alone, which is the default and the form to prefer; True modifies the original and returns None. errors: raise stops on a label that does not exist, and ignore skips it. The pilcrow at the end of the signature is a stray anchor character copied from the online documentation.

## Page 146
Combining tables comes in two forms, both covered here: stacking one on top of another with concat, and joining two on a shared key with merge.

## Page 147
`pd.concat` performs the union. It takes a list of the objects to stack, any number of them, and by default appends along the row axis. `ignore_index=True` discards the incoming labels and assigns a fresh range from zero, which is what produces the zero-to-seven index of the combined Series; without it, the original labels are kept and duplicates are allowed. The same call stacks DataFrames, matching their columns by name and filling a column that one table lacks with missing values; `axis=1` places the objects side by side instead, aligning on the row index.

## Page 148
`pd.merge` joins two DataFrames. The first two arguments are the left and right tables, and `how` names the join type as a string. When how is omitted the join is inner.

## Page 149
`on` names the key column or columns the join matches on. When it is omitted, merge uses every column name the two tables have in common, which is convenient and also the source of surprises when an unrelated column happens to share a name. `left_on` and `right_on` handle keys named differently in the two tables. Non-key columns that exist on both sides come back with the suffixes _x and _y attached, or with whatever `suffixes` specifies.

## Page 153

Grouping is the pattern of splitting a table's rows by the values of a column and computing an aggregate for each group, and it is how a log is summarized. The source table holds four connection records with a date, a source address, a destination address and a port. `groupby` takes a column name, or a list of names, and partitions the rows so that every row sharing a value in that column lands in the same group; the call returns a GroupBy object that has done no computation yet, and an aggregation method applied to it, count, sum or mean, runs once per group and assembles the results into a new object indexed by the group keys. The first form on the build, `df.groupby(['src_ip')`, has a mismatched bracket; `df.groupby('src_ip')` is the runnable form.

`groupby('src_ip')['port'].count()` partitions by source address, selects the port column, and counts the non-missing values in each group: 192.168.20.1 has one row and 192.168.20.2 has three, which answers how many port records each address produced. `groupby(['date','src_ip'])['port'].count()` partitions by the combination of date and source address, so 192.168.20.2 is counted separately on each day, two rows on the 21st and one on the 22nd; the result is indexed by both keys at once, a two-level MultiIndex, which prints with each date shown once and its addresses beneath it. count counts non-missing values in the selected column; size counts rows regardless; sum, mean, min, max, nunique and agg with a list or dictionary of functions follow the same pattern.

## Page 154

`as_index=False` keeps the group keys as ordinary columns instead of moving them into the index. The two-key count comes back as a flat table with date, src_ip and the count as columns and rows numbered from zero, where the default produces the two-level MultiIndex of the previous slide. A flat result can be merged, plotted with one column on each axis, or written to a file without an unstack or reset_index step first, and plotting is the case the option is most often set for.

## Page 155

Missing values in a Series are either dropped or filled. `dropna()` returns the Series with the missing entries removed, labels intact. `fillna(value=...)` returns it with every missing entry replaced by the given value, a zero for a count column or a placeholder string for a category. The usual fill is the column's most frequent value for a categorical column and its median for a numeric one, since each is a value the column already holds and the median is not moved by outliers. Both methods have DataFrame versions: `dropna` there drops whole rows by default, with `subset` limiting which columns are checked, and `fillna` accepts a dictionary of one fill value per column. Which to use depends on what a missing value means in the data; dropping rows loses whatever else those rows contained, and filling invents a value that later statistics will count.

## Page 156
pandas holds the entire dataset in the machine's memory, so the dataset size is bounded by RAM. The guideline of five to ten times the dataset size comes from Wes McKinney, the creator of pandas, and it exists because operations produce copies: selecting, filtering, sorting and the transformation methods return new objects, and intermediate results in a chain of calls each occupy their own memory until they are released. String columns stored as Python objects are a large part of the overhead, since each value is a separate object with its own header. pandas 2.0 addresses both costs with Arrow-backed column types, which store strings compactly, and with copy-on-write, which defers copying until an object is modified.

## Page 157

Libraries that run pandas-style code beyond one machine's memory or on a GPU. Dask: partitions a DataFrame into chunks and runs pandas operations over them in parallel, across cores or a cluster, with a subset of the pandas API; its operations are lazy, building a graph of the computation and executing it only when a result is requested, where pandas evaluates each statement as it runs, and the deferred plan is what lets Dask schedule the work within the memory available. cuDF: NVIDIA's DataFrame library with a pandas-like API that runs on the GPU; its cudf.pandas mode accelerates existing pandas code without changes. Ray: a distributed execution framework for Python and AI workloads; the Modin library uses it to run the pandas API across a cluster. RAPIDS: NVIDIA's suite of GPU libraries, of which cuDF is the DataFrame member, alongside cuML for scikit-learn workloads and cuGraph for NetworkX workloads. Polars: a DataFrame library written in Rust with a Python interface, multithreaded and lazily evaluated, with its own API in place of pandas'. PySpark: the Python interface to Apache Spark, the distributed engine under the Databricks workspace this course runs in, which also offers a pandas API on Spark for familiar syntax.

## Page 158
Apache Arrow is a specification for how columnar data is laid out in memory, plus libraries that implement it in many languages. Because every implementation uses the same layout, a table can pass between pandas, Spark, Polars, DuckDB and other tools without being converted or copied, which is the interoperability advantage. The layout is contiguous and typed, so compute kernels run over it with vectorized instructions, which is the speed advantage, and strings and nested values are stored without one Python object per value, which is the memory advantage. PyArrow is the Python library. Parquet is the matching on-disk format, so a Parquet file reads into Arrow memory with minimal work; Arrow complements Parquet, and the spelling compliment is an error.

## Page 159
Module 1 ends here.

## Page 160
Worksheet 1.1 is this module's lab; its notebook title is Vectorized Data Structures. Part 1 works on a Series: filter a list of email addresses down to .edu domains and extract the account names with the string methods; reduce a Series of IP addresses to the private ones using Python's ipaddress module with apply; extract area codes from phone numbers and count them with value_counts. Part 2 works on DataFrames: parse the hackers-access.httpd web server log into a table and answer questions about the browsers and operating systems in it, using the apachelogs and user_agents libraries; then load dailybots.csv and use filtering, groupby, agg and sorting to find which industry sees the most Ramnit infections, the summary statistics of infected organizations per bot family, and the date with the most infections.
