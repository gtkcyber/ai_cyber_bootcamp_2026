## Page 1

Module 1 introduces pandas, the Python library for tabular data, from the vectorized data structures it is built on up to the operations used to explore a dataset. Worksheet 1.1 is the lab for this module.

## Page 2

The module has two goals. Vectorized data structures: what they are, why they replace loops, and the two pandas objects that implement them, the Series and the DataFrame. Exploring tabular data: loading a dataset into a DataFrame and using pandas to inspect, filter and summarize it. The code throughout targets pandas 2.0 and later.

## Page 3

Using AI to write the lab code is expected. The quality of what a model produces depends on the direction it is given, and giving good direction about pandas requires knowing what a Series and a DataFrame are, how indexing works, and which operation a task calls for. Write the early exercises by hand until those concepts are familiar, then hand the typing to a model.

## Page 4

Pasting a dataset into a language model prompt is a poor way to analyze it. Context limits: a model accepts a bounded number of tokens per request, and a full telemetry table exceeds it. Cost and speed: every row sent is billed and processed as text, so a question over a large table is slow and expensive next to a pandas operation on the same data. Auditability: a model's answer arrives without the computation that produced it, so nobody can rerun or check it. Accuracy: a model can state a wrong figure with the same fluency as a right one.

## Page 5

The working pattern is to have the model write pandas code and to run that code over the data locally. Give the prompt the schema: column names, types, and what each column holds, plus a few sample rows if the values need illustrating. Ask for Python that performs the task. The code runs over the full dataset at pandas speed, its output can be inspected, and the code itself is the audit trail. Module 10, Prompt Engineering, covers how to write such prompts.

## Page 6

This part defines vectorized data structures and explains why pandas is built on them.

## Page 7

A definition of vectorized data structures follows, with the loop they replace and the table layout they assume.

## Page 8

A vectorized data structure applies an operation to every element it holds in one call. Adding one to a column, comparing a column against a threshold, or multiplying two columns together is written once, as an expression over whole columns, and the library carries it out across all the rows. The plain Python alternative is a loop that visits each element in turn.

## Page 9

Three properties follow from operating on whole columns. Readability: an expression over a column states what is computed, and the bookkeeping of loop variables and positions disappears. Performance: the library sees the whole operation at once, so it can run it in compiled code over a contiguous block of memory instead of interpreting one Python statement per element, and it can pick a compact storage type for the column. Interchange: a column or table is one object with a known layout, so it can be serialized whole and passed to another process or system.

## Page 11

The loop increments each element one at a time: Python fetches an element, adds one, stores it back, and advances the position, once per row, with the interpreter's overhead paid on every pass. The vectorized form states the same computation once for the entire column. With `evens` holding a column of even numbers, `odds = evens + 1` produces a new column with one added to every element, and the addition runs inside the library.

## Page 12

Column arithmetic depends on a table layout in which each variable has its own column and each observation has its own row. In that layout, `F = M * A` multiplies column M by column A one row at a time and writes the products into a new column F, with the expression written once for every row. The layout is what makes the expression meaningful: a column is a vector of one variable's values, so arithmetic between two columns pairs up values that belong to the same observation.

## Page 13

Python and R both provide vectorized structures. An R vector or data frame column takes an operation applied to every element with no loop written by the analyst, which is the same idiom pandas provides in Python.

## Page 14

TODO NEW SLIDE

## Page 15

The pandas library is the open-source foundation of Python data analysis. Its core is a set of vectorized data structures, the Series and the DataFrame, with a large library of operations over them. The rest of the Python data science stack assumes it: scikit-learn accepts DataFrames as input, and Matplotlib and Seaborn plot from them. Version 2.0.0 was released on April 3, 2023; its headline additions were optional Apache Arrow-backed column types and a copy-on-write mode, and the code in this course assumes 2.0 or later.

## Page 16

TODO NEW SLIDE

## Page 17

A DataFrame is a table. Each column has a name and holds one variable, here a registration number, a name and a mark; each row is one record, here one student. Every column is a Series, and all of the columns share one row index, so a value is addressed by a row label and a column name.

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

TODO NEW SLIDE

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

TODO NEW SLIDE

## Page 39

Slicing a Series by position returns the elements from the start position up to, and excluding, the end position. `series1[1:3]` returns b and c, and each keeps its original label, one and two, because a slice carries the index entries along with the values. The kept labels matter: the sliced Series `series2` no longer starts at zero, so `series2[0]` raises a KeyError. `reset_index(drop=True)` renumbers the index from zero; `drop=True` discards the old labels, and without it they would become a new column and the result would be a DataFrame. The method returns a new Series and leaves `series2` untouched unless the result is assigned back or `inplace=True` is passed; as written, the last line computes the renumbered Series and discards it.

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

TODO NEW SLIDE

## Page 48

`pd.to_datetime` converts a Series of timestamp strings, or a list of them, into pandas datetime values. The format argument is a strftime pattern, for example `'%Y-%m-%d %H:%M:%S'` for 2024-05-01 13:45:00, that states how each string is laid out. Supplying it avoids guessing: pandas 2.0 infers a single format from the first value and applies it to all of them, and a value that does not fit the format raises an error. Once converted, the values are stored as 64-bit integers counting nanoseconds since 1970 by default, so comparisons, differences and sorting work as arithmetic, and the `.dt` accessor becomes available.

## Page 49

TODO NEW SLIDE

## Page 50

TODO NEW SLIDE

## Page 51

`apply` runs a Python function on every element and collects the results into a new Series. `addTwo` takes one value and returns it plus two; `odds.apply(addTwo)` calls it once per element and keeps the index. The cost is that each call is a Python function call, interpreted one element at a time, so apply gives up the compiled-code speed of a vectorized expression. For this example `odds + 2` computes the same result as one vectorized operation; apply is for logic that has no vectorized equivalent, such as a lookup or a multi-branch transformation.

## Page 52

A lambda is an unnamed function written inline, and apply accepts one in place of a named function. `lambda x: x + 1` takes one argument and adds one to it, so `odds.apply(lambda x: x + 1)` adds one to every element. It is the same element-by-element Python call as the named version, with the same speed penalty, and `odds + 1` does the same work vectorized.

## Page 53

The Series section ends here. Summary statistics come next.

## Page 54

The section that follows introduces the statistics used to summarize a column: measures of center and spread, the quantile-based five-number summary, the pandas methods that compute each, and counting distinct values.

## Page 55

TODO NEW SLIDE

## Page 56

TODO NEW SLIDE

## Page 57

TODO NEW SLIDE

## Page 58

TODO NEW SLIDE

## Page 59

TODO NEW SLIDE

## Page 60

TODO NEW SLIDE

## Page 61

TODO NEW SLIDE

## Page 62

TODO NEW SLIDE

## Page 63

TODO NEW SLIDE

## Page 64

TODO NEW SLIDE

## Page 65

TODO NEW SLIDE

## Page 66

TODO NEW SLIDE

## Page 67

TODO NEW SLIDE

## Page 68

TODO NEW SLIDE

## Page 69

TODO NEW SLIDE

## Page 70

TODO NEW SLIDE

## Page 71

TODO NEW SLIDE

## Page 72

TODO NEW SLIDE

## Page 73

Covariance measures how two variables move together. For each observation, multiply x's deviation from its mean by y's deviation from its mean; the covariance is the average of those products. When x and y tend to be above their means together and below together, the products are positive and the covariance is positive; when one is high while the other is low, the covariance is negative; when there is no relation, positive and negative products cancel toward zero. The magnitude is hard to interpret. It carries the units of x times the units of y, so it is on a different scale from either mean, and covariances of different variable pairs cannot be compared with each other. Dividing by the product of the two standard deviations removes the units and gives the Pearson correlation, which is bounded between minus one and one; `Series.corr` computes it and `Series.cov` computes the covariance.

## Page 74

The five-number summary describes a distribution with its minimum, lower quartile, median, upper quartile and maximum. It is named for John Tukey, pronounced TOO-kee, the American statistician who coined the term exploratory data analysis and, in his 1977 book of that name, introduced this summary and the box plot that draws it. Each quartile is a cut point: the lower quartile is the value below which a quarter of the data lies, and the upper quartile is the value below which three quarters lie, so half of the data sits between them. All five come from the sorted order of the values, so a few extreme values move only the minimum and the maximum.

## Page 75

TODO NEW SLIDE

## Page 76

TODO NEW SLIDE

## Page 77

TODO NEW SLIDE

## Page 78

TODO NEW SLIDE

## Page 79

TODO NEW SLIDE

## Page 80

TODO NEW SLIDE

## Page 81

TODO NEW SLIDE

## Page 82

TODO NEW SLIDE

## Page 83

`describe` computes the statistics of this section together and returns them as a Series, with the set of statistics chosen by the column's data type.

## Page 84

For a numeric Series, describe returns eight statistics. count: fifty non-missing values. mean: 50.62, the average. std: 30.10, the sample standard deviation. min and max: 1 and 99, the extremes. 25%, 50% and 75%: the quartiles, 25.5, 54 and 73, so half of these random integers lie between 25.5 and 73, and the median 54 sits a little above the mean. The result has dtype float64 because one Series holds all eight numbers and the count is stored alongside the fractional quantiles.

## Page 86

For a Series of strings, describe switches to a categorical summary. count: nine values. unique: seven distinct names. top: the most frequent value. freq: how many times it appears. Jim and Bob each occur twice, so top reports one of the tied values, here Jim, with freq 2. The list in the code is missing a closing quote after Jim and will not parse as written; with the quote restored it holds the nine names counted here.

## Page 87

Finding the distinct values in a column, and how often each occurs, is the subject of this section.

## Page 88

The loop collects the distinct values of a Series by hand: it walks every element with `iteritems`, checks whether the value is already in a Python list, and appends it if it is absent. Three things are wrong with it. The walk is one interpreted Python step per element. The membership test scans the list from the start every time, so the work grows with the square of the number of distinct values. `iteritems` was deprecated in pandas 1.5 and removed in 2.0, so under the version this course uses the code raises an AttributeError; `items` is the surviving name.

## Page 89

TODO NEW SLIDE

## Page 91

Two methods return the distinct values of a Series. `drop_duplicates()` returns a Series: the first occurrence of each value is kept with its original index label, and later repeats are dropped. `unique()` returns a NumPy array of the distinct values in order of first appearance, with no index attached. Both hash the values, so the cost grows linearly with the length of the Series. `nunique()` returns just the number of distinct values, which is the figure the unique row of describe reports for a string column.

## Page 95

TODO NEW SLIDE

## Page 96

TODO NEW SLIDE

## Page 97

TODO NEW SLIDE

## Page 99

TODO NEW SLIDE

## Page 100

TODO NEW SLIDE

## Page 101

TODO NEW SLIDE

## Page 102

TODO NEW SLIDE

## Page 103

`plot(kind='box')` draws the five-number summary. The box spans the first quartile to the third quartile, so its height is the interquartile range; the line inside is the median; the whiskers reach out toward the extremes. In Matplotlib's default, a whisker extends at most one and a half interquartile ranges beyond its quartile, and any value further out is drawn as a separate point, an outlier. In this plot no value lies that far out, so the whiskers end at the minimum and maximum as labeled. The None under the box is the Series' name, which was not set.

## Page 104

TODO NEW SLIDE

## Page 105

Correlation is the subject here: the measure of how two numeric columns vary together, and the pandas method that computes it.

## Page 106

Correlation measures the strength and direction of the linear relationship between two continuous variables. The coefficient, written r, is the covariance scaled by the two standard deviations, which strips the units and confines the result to the interval from minus one to one. An r of 1 means the points lie exactly on a rising line; minus one, exactly on a falling line; zero, no linear relationship. Values in between grade how tightly the points cluster around a line. The coefficient defined this way is Pearson's r, and it is the default that pandas computes.

## Page 107

TODO NEW SLIDE

## Page 108

TODO NEW SLIDE

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

## Page 116

`read_excel` loads one worksheet of a spreadsheet into a DataFrame, with the first row as column names by default. The keyword that selects the sheet is `sheet_name`, by name or by zero-based position; the `sheetname` spelling was removed from pandas in 2017, so the call as written raises a TypeError. Reading .xlsx files requires the openpyxl package to be installed alongside pandas.

## Page 117

`read_json` builds a DataFrame from JSON in a file or at a URL. A top-level list of objects becomes one row per object; a top-level object of lists becomes one column per key. Two arguments cover the formats that platforms export. `lines=True` reads JSON Lines, where each line of the file is a separate object, which is how log exports and API dumps are laid out. `orient` states the layout when it is not the default. Since pandas 2.1, passing a literal JSON string to read_json is deprecated; wrap it in `io.StringIO` first.

## Page 118

`read_sql` runs a query against a database and returns the result set as a DataFrame, with the column names the query produces. The connection is a SQLAlchemy engine or a DBAPI connection object such as one from the sqlite3 module. The filtering and joining in the query execute inside the database, so only the rows needed reach Python; `read_sql_table` pulls a whole table by name instead of a query.

## Page 119

`read_parquet` loads an Apache Parquet file into a DataFrame. Parquet is a binary, columnar format from the Hadoop ecosystem: each column is stored and compressed separately with its type recorded, so a read recovers the exact dtypes with no inference, and a reader can pull only the columns it names. It is the storage format of Spark, Databricks and data lake tables, which makes it the interchange format between those systems and pandas. Reading it requires the pyarrow or fastparquet package.

## Page 120

Text logs whose lines carry no delimiters take a different loading route, shown in this section: read each line whole, then split it into columns.

## Page 122

TODO NEW SLIDE

## Page 124

`str.extract` with named groups splits the raw lines into columns in one expression. Each parenthesized group in the pattern captures one field, and the `(?P<name>...)` syntax names the group, so the result is a DataFrame whose column names are the group names. The pattern reads left to right: six digits, a space and a time of day for the date; a run of spaces; digits for the connection id, labeled PID here; non-space characters for the command; and everything remaining for the argument. Rows that do not match the pattern get missing values in every column, which makes a malformed line visible. The number MySQL writes in that position is the connection thread id, and the Date column in the table corresponds to the group named date.

## Page 125

Web server access logs come next, parsed into a DataFrame with the Apache log parser package.

## Page 127

An Apache access log line in the combined format, and the format string that describes it. The fields left to right are the client address, two placeholder dashes for the identd and authenticated user, the timestamp with its zone in brackets, the request line in quotes with method, path and protocol, the status code, the response size in bytes, the referring page, and the browser's user agent string. `apache_log_parser` is a Python package that takes an Apache LogFormat string and returns a function that parses one line into a dictionary. The directives in the format string are Apache's own: `%h` the host, `%l` the logname, `%u` the user, `%t` the time, `%r` the request line, `%>s` the final status, `%b` the bytes, and `%{Referer}i` and `%{User-agent}i` the named request headers.

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

TODO NEW SLIDE

## Page 142

A list of column names in brackets returns a DataFrame holding those columns, ordered as listed. Two pairs of brackets appear because the outer pair indexes the DataFrame and the inner pair builds the list. A single name returns a Series; a list, even a list of one name, returns a DataFrame. Assigning the result back to `df` keeps only the listed columns and discards the rest, which trims a wide table down to the fields an analysis needs.

## Page 143

A DataFrame filters the way a Series does: a boolean condition in the brackets selects the rows where it holds. The condition is a Series of booleans built from one or more columns, such as `df['col3'] > 5`, and pandas lines it up with the rows through the index, so it selects rows whether or not the column it tests is among the columns being returned. The second form chains two selections: the list picks the columns col1 and col2, and the condition then picks the rows. Chained brackets are fine for reading. For assignment they trigger a SettingWithCopyWarning, because pandas cannot tell whether the write reaches the original; `df.loc[df['col3'] > 5, ['col1', 'col2']]` does both selections in one step and is the form to use when writing.

## Page 144

TODO NEW SLIDE

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

This part covers grouping: splitting a DataFrame's rows by the values of one or more columns and computing an aggregate for each group.

<!-- MERGE: a second old note landed on this page; fold or drop -->

A MultiIndex result can be reshaped with unstack. The stacked table on the left is a Series with a three-level index, first, second and an innermost level holding A and B. `unstack()` takes the innermost level and turns its values into columns, so the right-hand table has rows indexed by first and second and one column each for A and B, with the values rearranged into the grid. Applied to the two-key groupby result, counts indexed by date and source address, unstack turns them into a table with one row per date and one column per address. The figure is from Jay Alammar's illustrated guide to pandas pivoting and reshaping.

<!-- MERGE: a second old note landed on this page; fold or drop -->

`unstack` takes an argument naming which index level to move into the columns, by position or by name. `unstack(1)` and `unstack('second')` both move the second level, so its values one and two become the columns, and the row index keeps the first level together with the A and B level. The default, with no argument, moves the innermost level. `stack` is the inverse and moves a column level back into the row index.

## Page 154

TODO NEW SLIDE

## Page 155

Missing values in a Series are either dropped or filled. `dropna()` returns the Series with the missing entries removed, labels intact. `fillna(value=...)` returns it with every missing entry replaced by the given value, a zero for a count column or a placeholder string for a category. Both have DataFrame versions: `dropna` there drops whole rows by default, with `subset` limiting which columns are checked, and `fillna` accepts a dictionary of one fill value per column. Which to use depends on what a missing value means in the data; dropping rows loses whatever else those rows contained, and filling invents a value that later statistics will count.

## Page 156

pandas holds the entire dataset in the machine's memory, so the dataset size is bounded by RAM. The guideline of five to ten times the dataset size comes from Wes McKinney, the creator of pandas, and it exists because operations produce copies: selecting, filtering, sorting and the transformation methods return new objects, and intermediate results in a chain of calls each occupy their own memory until they are released. String columns stored as Python objects are a large part of the overhead, since each value is a separate object with its own header. pandas 2.0 addresses both costs with Arrow-backed column types, which store strings compactly, and with copy-on-write, which defers copying until an object is modified.

## Page 157

Libraries that run pandas-style code beyond one machine's memory or on a GPU. Dask: partitions a DataFrame into chunks and runs pandas operations over them in parallel, across cores or a cluster, with a subset of the pandas API. cuDF: NVIDIA's DataFrame library with a pandas-like API that runs on the GPU; its cudf.pandas mode accelerates existing pandas code without changes. Ray: a distributed execution framework for Python and AI workloads; the Modin library uses it to run the pandas API across a cluster. RAPIDS: NVIDIA's suite of GPU libraries, of which cuDF is the DataFrame member, alongside cuML for scikit-learn workloads and cuGraph for NetworkX workloads. Polars: a DataFrame library written in Rust with a Python interface, multithreaded and lazily evaluated, with its own API in place of pandas'. PySpark: the Python interface to Apache Spark, the distributed engine under the Databricks workspace this course runs in, which also offers a pandas API on Spark for familiar syntax.

## Page 158

Apache Arrow is a specification for how columnar data is laid out in memory, plus libraries that implement it in many languages. Because every implementation uses the same layout, a table can pass between pandas, Spark, Polars, DuckDB and other tools without being converted or copied, which is the interoperability advantage. The layout is contiguous and typed, so compute kernels run over it with vectorized instructions, which is the speed advantage, and strings and nested values are stored without one Python object per value, which is the memory advantage. PyArrow is the Python library. Parquet is the matching on-disk format, so a Parquet file reads into Arrow memory with minimal work; Arrow complements Parquet, and the spelling compliment is an error.

## Page 159

Module 1 ends here.

## Page 160

Worksheet 1.1 is this module's lab; its notebook title is Vectorized Data Structures. Part 1 works on a Series: filter a list of email addresses down to .edu domains and extract the account names with the string methods; reduce a Series of IP addresses to the private ones using Python's ipaddress module with apply; extract area codes from phone numbers and count them with value_counts. Part 2 works on DataFrames: parse the hackers-access.httpd web server log into a table and answer questions about the browsers and operating systems in it, using the apachelogs and user_agents libraries; then load dailybots.csv and use filtering, groupby, agg and sorting to find which industry sees the most Ramnit infections, the summary statistics of infected organizations per bot family, and the date with the most infections.
