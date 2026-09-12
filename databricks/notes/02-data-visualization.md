## Page 1

Module 2 covers data visualization: charts whose drawing misrepresents their own numbers, with 3D bars, radial bars and pie charts as the cases; plotting in Python with pandas, Matplotlib and Seaborn; customizing a Matplotlib chart through its figure and axes objects; and building interactive dashboards with Streamlit.

## Page 2

The chart cannot answer either question. It is drawn in perspective, with the blue, red and green series on three rows receding along a depth axis. Each row rests on its own baseline, so the rows do not share the zero line the value axis on the left assumes, and a column in the back row is placed higher on the page than a front-row column of the same value. Read against the gridlines, the green tops sit level with the tallest blue column, and green appears taller than blue in categories B, C and D.

## Page 3

The same data drawn flat answers both questions. Green is 5 in all four categories. Blue is 7, 6.25, 5.75 and 5.25, so blue is taller than green in every category, the opposite of what the perspective view suggested for B, C and D. Red runs from 1.8 to 3.75.

The flat chart works because all bars rise from one baseline and the reader compares the positions of their tops along a single scale. In Cleveland and McGill's 1984 experiments on graphical perception, judging position along a common scale was the most accurate of the elementary visual tasks they tested.

## Page 4

This chart inverts the trend its own source reports. It is a radial bar chart: each ring is a year, each ring carries two bars, electric in the darker shade and hybrid in the lighter, and a bar's percentage is drawn as the fraction of that ring's circumference it covers. Arc length grows with radius, so a given percentage on an outer ring is a longer arc than the same percentage on an inner ring. The 2023 electric bar on the outermost ring, at 67 percent, is drawn longer than the 2021 electric bar two rings in, at 86 percent. Read from the labels, openness fell from 86 and 93 percent in 2021 to 67 and 72 percent in 2023, which is the decline the headline reports; the arcs show growth.

## Page 5

The interlude covers pie charts: what a reader has to judge to extract a value from one, and what the exploded, donut and 3D variants do to that judgment.

## Page 6

A pie chart suits a rough comparison at a glance and nothing more precise, because it encodes each share as the angle and area of a wedge and comparing the areas of wedges is a weak visual task. The photograph is a pie chart in the literal sense. Its two categories are the pie eaten and the pie not yet eaten, and the eaten wedge is about a quarter of the whole, a share the eye can name because the wedge's two edges meet at a right angle.

## Page 7

The chart is its own data. The title asks what percentage of the chart resembles Pac-Man; the yellow wedge is the portion that does, the gray wedge is the mouth that does not, and the result is a circle with a mouth-shaped gap, which is Pac-Man.

## Page 8

The plain pie is the chart the rest of the section varies, and it keeps both cues a pie offers: the angle at the center and the arc and area of each wedge. Each variant that follows takes away or distorts one of these cues. Six wedges hold 35, 29, 11, 10, 8 and 7 percent. Without the printed labels a reader recovers each share from the angle its wedge subtends at the center, and angle is a weak cue: Cleveland and McGill's experiments ranked angle judgments below position judgments in accuracy. The four small wedges show the cost. They differ by one to three percentage points, their angles differ by a few degrees, and nothing in the drawing lets a reader order them without the labels.

## Page 9

Exploding the pie removes the shared center. Each wedge is pushed outward along its own bisector, so the tips no longer meet at one vertex and the angles have no common point to be compared from. The gaps between wedges are area that stands for no value. The data is the same six percentages.

## Page 10

The donut removes the center and with it the angle cue. What remains is a ring of arcs whose lengths are proportional to the shares, so a reader compares arc lengths. Skau and Kosara's 2016 experiments on pie and donut perception found that readers estimate shares from arc length and area rather than from the center angle, and that a donut is read about as accurately as a pie. The four small arcs remain hard to order: their lengths differ by one to three percent of the circumference.

## Page 11

Tilting the pie into a 3D view changes every angle. The disk is drawn as an ellipse, which compresses it top to bottom, and the compression does not treat wedges equally: a wedge centered on the vertical axis of the ellipse spreads to a wider apparent angle, and a wedge centered on the horizontal axis narrows. The rendering also paints the front rim, adding a band of area to the wedges at the bottom of the ellipse and none to the wedges at the back. The 29 percent green wedge sits at the front with a widened angle and a visible rim, and it reads at least as large as the 35 percent blue wedge at the side.

## Page 12

A steeper tilt and a rotation push the distortion further. The rim is now thick and runs along the left edge, so the yellow 11 percent and red 10 percent wedges carry a dark side face that the wedges on the right lack, and the yellow wedge covers far more of the page than the purple 8 percent wedge, a gap that three percentage points cannot account for. The angles at the center belong to a tilted ellipse, not to the data. The six labels are the only reliable source of the values.

## Page 13

The two drawings measure the same pie. On the left are the angles as they appear in the 3D rendering; on the right, the same seven wedges drawn flat with their true angles. Wedge 7 is drawn at 27.8 degrees but holds 14.4, almost twice its share. Wedge 6 is drawn at 37.4 against a true 22.7. Wedge 4, on the horizontal axis of the ellipse, is drawn at 25 degrees against a true 48.2, about half its share. Wedges near the vertical axis of the ellipse widen and wedges near the horizontal axis narrow, which is what projecting a circle onto a tilted plane does to its angles. The measurements come from the source post, titled "3D pie charts are lie charts".

## Page 14

UNRESOLVED

## Page 15

This part covers plotting in Python: the libraries available, the pandas plot method for a chart in one line, and Seaborn's functions for scatter plots, distributions, regression fits and grids of small charts.

## Page 16

Five libraries cover the plotting in this course, at different levels of abstraction.

- Matplotlib: the base library that pandas and Seaborn draw with, and the oldest of the five. John Hunter first released it in 2003 to give Python the plotting commands of MATLAB, and its `pyplot` module, a set of functions that draw on whichever figure is current, still follows that model. Every element of a figure can be set, at the cost of writing code for each one.
- pandas plotting: the `plot` method on a Series or DataFrame, which calls Matplotlib's pyplot interface with defaults. A line, bar or histogram takes one line of code; a more complex chart requires reshaping the data first.
- Seaborn: statistical charts such as distributions, regression fits and pairwise plots, built from a DataFrame and column names, with grouping and styling handled by the function.
- Altair: a declarative library, meaning the code states which columns map to which visual channels and the library decides how to draw them. It is built on the Vega-Lite grammar and renders in the browser.
- Plotly, with Cufflinks as its pandas binding: charts rendered as interactive web graphics with hover, zoom and pan.

## Page 17

These five lines open a plotting notebook. The four imports bind the libraries to their conventional short names: `pd` for pandas, `plt` for Matplotlib's pyplot module, `np` for NumPy and `sns` for Seaborn. Code found in documentation and answers assumes these aliases.

The last line is not Python. `%matplotlib inline` is an IPython magic command, an instruction to the notebook kernel, and it tells the kernel to render Matplotlib figures as images in the output cell under the code rather than in a separate window. Jupyter and Databricks notebooks now render inline by default, and a plain Python script rejects the line as a syntax error.

## Page 18

A pandas Series has a `plot` method and its default is a line chart. The Series here holds seven integers, and the call draws them in order, with the index 0 through 6 on the horizontal axis and the values on the vertical axis. The gray background and dotted grid come from a plotting style setting rather than from pandas; Matplotlib's own default is a white background with no grid. The return value assigned to `graph` is the Matplotlib axes object the line was drawn on, which is the handle for any later customization.

## Page 19

The `kind` argument selects the chart type, and `kind="bar"` draws one vertical bar per element, positioned by index. Bars start at zero on the vertical axis, so their heights are directly comparable. pandas accepts `line`, `bar`, `barh`, `hist`, `box`, `kde`, `density` and `area` for a Series or a DataFrame, `pie` for a Series, and `scatter` and `hexbin` for a DataFrame.

## Page 20

`kind="pie"` draws the Series as wedges, each labeled with its index and sized as that element's fraction of the sum of all elements. A pie assumes the values are parts of one whole. A Series of separate measurements is not, so the chart assigns each value a share of a total that has no meaning. The pie is also an ellipse here because the axes were left at the figure's proportions; current Matplotlib releases set the aspect ratio to equal inside the pie function and draw a circle.

## Page 21

Seaborn is a statistical plotting library built on Matplotlib, and `sns` is its conventional alias. Its functions take the DataFrame as the `data` argument and name the columns for the axes and for grouping, color the groups when asked, and apply a consistent style, so a chart that would take a block of Matplotlib code is one call. Everything it draws is still a Matplotlib figure, so Matplotlib's customization methods apply to the result.

## Page 22

A scatter plot can carry more than two columns at once: two on the axes, and others through the shape, color and size of the marker, which the pages that follow add. The DataFrame is built from random integers so that the chart has no structure to find. `np.random.randint(0, 100, size=(100, 4))` fills a 100 by 4 array with integers from 0 to 99, the columns are named A through D, and a fifth column, `category`, holds the remainder of C divided by three, which is 0, 1 or 2. `sns.scatterplot` draws one dot per row at the position given by columns A and B. Because the columns were drawn independently, the dots spread evenly with no trend, which is the correct picture of independent variables.

## Page 23

The `style` argument maps a column to marker shape. Each `category` value gets its own marker, circle for 0, cross for 1 and square for 2, and a legend is added with the column name as its title. Shape is a categorical channel: it distinguishes groups but carries no order, so it suits a column with a few discrete values and would not suit a numeric column with many.

## Page 24

Two more arguments map columns to properties of the marker. `hue` maps column D to color; because D is numeric, Seaborn uses a sequential palette from light to dark and labels the legend at 0, 40, 80 and 120 even though the data stops at 99. `size` maps column C to marker area, with its own legend. The chart now encodes four columns per row: A and B as position, D as color and C as size. Position is read most accurately, color and size less so, so the columns that matter most belong on the axes.

## Page 25

Two more arguments map columns to properties of the marker. `hue` maps column D to color; because D is numeric, Seaborn uses a sequential palette from light to dark and labels the legend at 0, 40, 80 and 120 even though the data stops at 99. `size` maps column C to marker area, with its own legend. The chart now encodes four columns per row: A and B as position, D as color and C as size. Position is read most accurately, color and size less so, so the columns that matter most belong on the axes.

## Page 26

`distplot` draws the distribution of one numeric variable as a histogram with a kernel density estimate overlaid. The bars count observations per bin, scaled so the total area is one, which is why the vertical axis reads as density rather than count. The smooth curve is the kernel density estimate, a continuous estimate of the same distribution made by placing a kernel, a small smooth curve, at every observation and summing them. The example is a sample centered on zero with the bell shape of a normal distribution. Seaborn deprecated `distplot` in version 0.11; `histplot` with `kde=True` produces the same picture in current versions.

## Page 27

`pairplot` draws every pairwise combination of the numeric columns in one grid. Each off-diagonal cell is a scatter plot of one column against another, and each diagonal cell is a histogram of a single column. `hue` names a column whose values color the points and split the histograms, so the grid doubles as a check of how well the measurements separate the classes. That check is a first pass at feature selection, choosing which columns to give a model: a column whose classes separate in its cells carries signal a classifier can use, and one whose classes overlap in every cell contributes little on its own. The example is the iris dataset: 150 flowers of three species with four measurements each. Petal length and petal width separate setosa from the other two species with a clear gap, and the two remaining species overlap on sepal width. A grid of n columns has n squared cells, so the plot suits a handful of columns.

## Page 28

`regplot` draws a scatter plot and fits a straight line to it by ordinary least squares. The shaded band around the line is a 95 percent confidence interval for the fitted line, computed by bootstrap resampling, so the band widens where the data is sparse, at the high end of the bill here. The example is Seaborn's built-in tips dataset, 244 restaurant bills with the tip left on each, and the fit shows tips rising with the bill. The function returns the Matplotlib axes, which is what `ax` receives.

## Page 29

`lmplot` fits the same kind of line but works at the level of a whole figure, which is what lets it split the data. `hue="smoker"` divides the rows by that column and fits a separate line to each group, with its own color and its own confidence band, and adds a legend. In the tips data the line for non-smokers is steeper than the line for smokers, so the tip grows faster with the bill among non-smokers. Because `lmplot` builds a figure, it also accepts `col` and `row` to split the data into a grid of panels, and it returns a `FacetGrid` object rather than an axes, which is why the result is assigned to `g`.

## Page 30

`FacetGrid` builds a grid of panels, one per combination of the values in the `row` and `col` columns, and `map` draws the same chart in each panel. Here `col="time"` gives one column of panels for lunch and one for dinner, `row="smoker"` gives one row for smokers and one for non-smokers, and `g.map(plt.hist, "total_bill")` draws a histogram of the bill in each of the four panels. The panels share axes, so heights are comparable across them: dinner bills are more numerous and spread wider than lunch bills in both rows. The `>>>` prompt on the second line is copied from an interactive session and is not part of the code.

## Page 31

A Seaborn axes-level function returns a Matplotlib axes, and `get_figure` on that axes returns the figure that contains it. `savefig` on the figure writes it to disk, with the format chosen from the file extension: PNG here, and PDF or SVG for vector output. The call is needed when a chart has to leave the notebook, for a report or a slide, because the inline rendering exists only in the notebook output. Adding `bbox_inches="tight"` trims the margin around the figure and keeps long tick labels inside the saved image.

## Page 32

The figure is Matplotlib's own anatomy diagram and it names the parts a customization call can touch. The figure is the whole canvas. The axes is one plot inside it, with its own x axis and y axis; each axis carries major and minor ticks, tick labels and an axis label. Inside the axes are the drawn data, lines for a line plot and markers for a scatter plot, plus the grid, the legend, the title and the spines, which are the four lines that frame the plotting area. Every one of these is an object with setter methods, and customizing a chart means getting hold of the right object and calling them.

## Page 33

The figure is Matplotlib's own anatomy diagram and it names the parts a customization call can touch. The figure is the whole canvas. The axes is one plot inside it, with its own x axis and y axis; each axis carries major and minor ticks, tick labels and an axis label. Inside the axes are the drawn data, lines for a line plot and markers for a scatter plot, plus the grid, the legend, the title and the spines, which are the four lines that frame the plotting area. Every one of these is an object with setter methods, and customizing a chart means getting hold of the right object and calling them.

## Page 34

Matplotlib's two container terms are easy to confuse because one is named for the other. An Axes object is a single plot: the region where data is drawn, together with its two axis objects, its title and its legend. A Figure is the whole image, and it holds one or more Axes objects. A chart with two panels side by side is one Figure with two Axes. The word axes in this sense is singular, and the x axis and y axis inside it are Axis objects of a different class.

## Page 35

Matplotlib has two interfaces to the same objects. The state-based interface is the `pyplot` module: calls such as `plt.plot` and `plt.xlabel` act on whichever figure and axes are current, and the library tracks that state. The object-oriented interface holds explicit Figure and Axes objects and calls methods on them, such as `ax.set_xlabel`. Both produce the same chart, and answers found online mix them freely, so a snippet that calls `plt.title` and one that calls `ax.set_title` are doing the same thing through different handles.

The recommended division of labor:

- Simple plots: the pandas `plot` method.
- Complex statistical charts: Seaborn, or Yellowbrick, a library of diagnostic charts for scikit-learn models such as learning curves and confusion matrices.
- Adjustments to a simple plot: the object-oriented interface, through the axes that pandas or Seaborn return.

## Page 36

`plt.subplots` creates a Figure and one Axes in a single call and returns both. Passing that Axes to the pandas `plot` method through `ax=ax` tells pandas to draw into it instead of creating its own, so the code ends up holding `fig` and `ax` as explicit handles. The handles are the entry point to the object-oriented interface: every later adjustment is a method call on `ax` for the plot or on `fig` for the whole image. Without the `ax` argument pandas still returns the Axes it drew on, but the figure has to be recovered from it afterward.

## Page 37

The Axes class is where most customization methods live, and the linked page is its reference. The methods fall into groups: setters for the title and axis labels, limits and scale for each axis, tick positions and tick labels, the legend, the grid, and the drawing methods themselves such as `plot`, `bar`, `scatter` and `hist`. The link points at the documentation for version 3.1.0; the current version's reference is at matplotlib.org/stable/api/axes_api.html.

## Page 38

Three method calls on the axes turn a bare chart into a labeled one. `set_xlim` fixes the horizontal range, here from minus 10,000 to 140,000, which leaves room to the left of the zero line and to the right of the longest bar. `set_xlabel` and `set_ylabel` put text on the two axes; without them the y axis would carry the DataFrame's index name, if it has one, and the x axis nothing. `kind='barh'` draws horizontal bars, which suits long category names such as these customer names, since the labels run horizontally. The semicolon after the last line suppresses the printed return value in a notebook. The example comes from Chris Moffitt's Practical Business Python article on effective Matplotlib.

## Page 39

Annotations add reference marks that the data alone does not carry. `axvline` draws a vertical line across the axes at a given x position, here the mean of the Sales column computed with pandas, and the keyword arguments set its color to blue, its style to dashed, its width to one point and its legend label to Average. `ax.text` places a string at a data coordinate: the loop writes "New Customer" at x equal to 115,000 beside the bars at positions 3, 5 and 8, which are the fourth, sixth and ninth bars from the bottom because bar positions count from zero. The chart on the right also has a title and dollar-formatted ticks, which come from calls the listing omits.

## Page 40

`plt.subplots` with `nrows=1` and `ncols=2` creates one figure holding two axes side by side, returned as the pair `(ax0, ax1)`. `sharey=True` makes the two panels use one vertical axis, so the customer names appear once on the left and the bars in the two panels line up row for row. `figsize=(7, 4)` sets the figure's width and height in inches. Each `df.plot` call is directed to its own panel with `ax=ax0` or `ax=ax1`, and each axes is then customized independently: `ax1.set` sets the title, x label and an empty y label in one call, and `axvline` draws the average line for units on the second panel as it did for revenue on the first. The title above both panels, 2014 Sales Analysis, belongs to the figure and is set with `fig.suptitle`.

## Page 41

Worksheet 2.1 applies the pandas and Matplotlib material to the daily botnet data. The task is a line chart comparing the number of hosts infected by the Bedep and ConfickerAB bot families in the Government/Politics sector: read `dailybots.csv`, filter it by industry and by bot family, merge the two families into one DataFrame with a date column and a count column per family, and plot it. The second half customizes the result through the axes: convert the date column to datetime so the x axis is a time axis, move the legend, enlarge the figure, add axis labels, and split the two lines into two subplots with `plt.subplots`.

## Page 42

This part covers interactive visualization: the limits of interactive notebooks, and Streamlit as a way to turn a Python script into a web application with charts, tables, layout and input widgets.

## Page 43

A Jupyter notebook can be made interactive with ipywidgets, which adds sliders, dropdowns and buttons whose values feed back into Python, or with Plotly and Altair, which render charts that respond to hover, zoom and selection. Widgets need a running kernel to respond, so the notebook has to be hosted where the reader can execute it; an exported HTML file keeps only the last rendered state. The reader also sees code cells, a toolbar and execution order, a working surface for an analyst and an obstacle for a manager or anyone else who is not going to run code.

## Page 44

Streamlit is an open source Python library, first released in 2019 and owned by Snowflake since 2022, for building web applications from a script.

## Page 45

Streamlit turns a Python script into a web application. The script runs top to bottom, and every call such as `st.markdown` or `st.dataframe` appends an element to the page in order, so a script that prints text and a chart becomes a page with that text and that chart. The framework generates the HTML, JavaScript and server plumbing itself, so the author writes only Python and handles only the data. Its chat widgets, `chat_input` and `chat_message`, exist for building interfaces to language models.

## Page 46

A Streamlit application is a script started by the Streamlit server, and a notebook cell cannot be that script. The server reruns the whole file from the top on every interaction, which a notebook kernel with its persistent cell state does not do, and Streamlit calls made inside a notebook warn that no script is running and render nothing. Write the application as a `.py` file in a text editor or an IDE and run it from a terminal.

## Page 47

`streamlit run your_script.py` starts a local web server, executes the script, and serves the resulting page on port 8501 of the local machine. The command prints the local and network URLs in the terminal and opens a browser tab at the local one unless headless mode is set. The server watches the file: saving a change offers a rerun in the browser, so the edit and refresh loop needs no restart. Options after the script name set the port, the address the server binds to and whether the browser opens; the Streamlit documentation lists them.

## Page 48

The script is a Streamlit application in its entirety; there is no application object, route or template. `import streamlit as st` is the conventional alias. `st.markdown` renders a Markdown string, here a level one heading followed by a paragraph, into the page. `st.area_chart` draws a filled line chart from a DataFrame, with the index on the horizontal axis and one filled series per column. `st.dataframe` renders a DataFrame as an interactive table that can be scrolled, sorted by clicking a column header and resized; `hide_index=True` drops the row numbers. Each call places its element below the previous one, in script order.

## Page 49

The page as the browser renders it at localhost. The heading and paragraph are the Markdown, the area chart plots one series by date from June through August 2016, and the table beneath is the raw daily botnet records with date, bot family, industry, hosts and orgs columns. The Deploy button and menu at the top right are added by Streamlit and are not part of the script. The table is live: the column headers sort and the scrollbar on the right moves through the rows.

## Page 50

Streamlit's chart functions fall into two tiers. The built-in `line_chart`, `area_chart`, `bar_chart`, `scatter_chart` and `map` take a DataFrame and draw with defaults, which is the tier the basic example used. The second tier renders charts built with another library: `pyplot` for Matplotlib figures, and `altair_chart`, `vega_lite_chart`, `plotly_chart` and `pydeck_chart` for those libraries, which is how a chart gets full customization. The API reference at docs.streamlit.io/develop/api-reference/charts documents both tiers. The complete code for the basic example is in the `streamlit_examples` folder of the course repository.

## Page 51

Layout elements are containers that hold other elements. Streamlit's set includes `tabs`, `columns`, `container`, `expander`, `popover`, `dialog` for modal dialogs, `sidebar`, and multipage apps through a `pages` directory or `st.navigation`. Each container is used with Python's `with` statement: the block opens the container, and every Streamlit call inside the block places its element in that container rather than on the main page. The reference at docs.streamlit.io/develop/api-reference/layout lists the full set.

## Page 52

`st.tabs` takes a list of tab titles and returns one container per title, unpacked here into `chart_tab` and `table_tab`. The `with chart_tab` block puts the area chart under the Chart tab, and the `with table_tab` block puts the table under the Data tab. The page then shows one of the two at a time and the reader switches between them, where the earlier version stacked chart and table vertically. The data calls themselves are unchanged; only the container they run inside differs.

## Page 53

The rendered page with the Chart tab selected. The tab strip sits under the description text, at the point in the script where `st.tabs` was called, and the area chart fills the selected tab; selecting Data swaps the table into the same space. The contents of both tabs are rendered when the script runs and the switch happens in the browser, so changing tabs does not rerun the script.

## Page 54

The rendered page with the Data tab selected. The table takes the region the chart occupied, and the toolbar that appears above it includes a CSV download, a search box and a fullscreen view, all supplied by `st.dataframe` without extra code. The rows are the June 1, 2016 records: one line per bot family and industry, with the counts of infected hosts and of affected organizations.

## Page 55

Input widgets are function calls that return the current value of the control. `st.text_input("Enter your name")` draws a text box with that label and returns whatever the box contains, an empty string until the user types. Every change to a widget triggers a rerun of the whole script from the top, and on that rerun the call returns the new value, so the `if` test and the `st.write` line run again with the user's text and the greeting appears. The rerun replaces event handlers: nothing in the script registers a callback. Values that have to survive between reruns, such as a growing list, have to be stored in `st.session_state`, because local variables are recreated on every run.

Validate the input. A value taken from a text box is arbitrary user data, and it should be checked for length, type and content before it reaches a query, a file path or a shell command.

## Page 56

`st.chat_input` draws a message box pinned to the bottom of the page and returns the submitted text, or `None` when nothing has been sent. `st.chat_message` is a container that draws one message with an avatar for its role, user or assistant, and the elements written inside its `with` block appear as that message's body. The two widgets carry no model logic of their own; they are the input and output halves of a chat interface, and the calls to a language model go between them in ordinary Python.

## Page 57

The finished application. The title is a Markdown heading, the two message bubbles are `st.chat_message` containers for the user role and the assistant role, each with its own avatar, and the box at the bottom with the placeholder "What is up?" is `st.chat_input`. The exchange asks whether `sudo rm -rf .*` is risky; the assistant's answer comes from the language model, and the script only relays it.

## Page 58

The script keeps the conversation in `st.session_state`, the dictionary Streamlit preserves across reruns for one browser session. `OpenAI(api_key=os.getenv("OPENAI_KEY"))` builds the API client with a key read from an environment variable, which keeps the key out of the source file. The model name, here `gpt-3.5-turbo`, is stored in session state so that one place controls which model the call uses. `messages` is created as an empty list only when it does not already exist, and that guard is what stops each rerun from wiping the history. The `for` loop replays the history: for each stored message it opens a `chat_message` container for the message's role and writes the content as Markdown, which is how earlier turns stay on the page after a rerun.

The last two lines handle a model response. `st.write_stream` consumes a streaming reply, writes each chunk to the page as it arrives, and returns the full text, which is then appended to the history under the assistant role.

## Page 59

The turn logic runs only when the user has submitted text. `if prompt := st.chat_input("What is up?")` assigns the box's contents to `prompt` and enters the block only when the value is not empty; the `:=` operator, assignment inside an expression, arrived in Python 3.8. The user's message is appended to the history and drawn in a user bubble. Inside an assistant bubble the script builds the request: a system message that tells the model to act as a security bot and to answer only cybersecurity questions, followed by the whole stored history reduced to role and content pairs, so the model sees every earlier turn and answers in context. `stream=True` makes the API return the reply in chunks rather than as one block, which is what `st.write_stream` expects in order to show the answer as it is generated. The restriction to cybersecurity questions lives in the system message alone, so it is an instruction the model follows rather than a check the code performs.

## Page 60

Questions on the module before the second lab.

## Page 61

Worksheet 2.2 is a Streamlit script. It is written in an editor and started with `streamlit run`, and it builds a small dashboard on the daily botnet file: a title and description in Markdown, a `selectbox` listing the industries whose chosen value is kept in a variable, and two tabs. The chart tab holds a bar chart of infected host totals by bot family for the selected industry, which takes a filter on the industry column and a group by bot family before the chart call. The data tab holds the raw records as a table, optionally filtered by the same selection and formatted through the column configuration parameters of `st.dataframe`.
