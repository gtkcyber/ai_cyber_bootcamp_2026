# Deck flags from the notes pass

Things the note writers found on the slides themselves while writing the read-alone
notes. The notes teach the correct reading; the slide images are untouched. For whoever
edits the Keynote sources. Page numbers are PDF pages.

## 05-unsupervised-learning
- p46: arrow labeled "Best number of clusters" points at K=6, the silhouette minimum; by the deck's own definition (p44) the best value is the maximum, K=2.
- p32: code reads `labels_f`, meant `labels_`.
- p47: figure title says MiniBatchKMeans, code passes `KMeans()`; `poof()` is `show()` in current Yellowbrick.
- p51: "dimensionality reduction loses no information" is stated unconditionally; the note scopes it.
- p49: worksheet slide; Worksheet 5.1 also covers agglomerative clustering and DBSCAN, which the deck does not.

## 08-deep-learning
- p11: perceptron attributed to "Minksy & Papert, 1969" and "McCulloh-Pitts"; Rosenblatt 1958 introduced it, Minsky and Papert 1969 analyzed its limits. Two misspellings.
- p12: weights "(1,-0,75,0.25)" for (1, -0.75, 0.25).
- p22: "gets their faster". p49: "utilize for gates" for "four gates".
- p42: library list (Theano, Torch, Lasagne, Caffe, Pylearn2, Chainer) is dated; the labs use Keras and PyTorch.
- p41, p50: notes describe the current worksheets; re-check if the notebooks change.

## 12-model-context-protocol
- p3: "we will built".
- p23: code string literal wraps mid-string on the slide.
- p20: bare pointer to https://ai.gtkcyber.com/mcp-lab with no description in the deck (UNRESOLVED note).
- Worksheet 12.1 markdown says "Module 12" and "Module 13" where it means Module 11 (notebook, not deck).

## 02-data-visualization
- p14: URL plus one frame of an animated port-by-country chart, axes unreadable; talking point not inferable (UNRESOLVED note).
- p6, p7: joke slides (pie photo, Pac-Man pie); short descriptive notes written.
- p4: radial bar chart with URL only; note explains the arc-length distortion from the geometry.
- p19, p20: bar and pie charts drawn from different data than the Series on p18 (3,5,7,3,4,8 vs 3,4,6,7,5,8,2); notes avoid quoting their values.
- p20: pie renders as an ellipse; current Matplotlib forces an equal aspect.
- p26: `distplot` is deprecated since Seaborn 0.11; note gives `histplot(kde=True)`.
- p37: link is to Matplotlib 3.1.0 docs; note points at the stable URL. p50: `bokeh_chart` moved out of Streamlit core.

## 03-feature-engineering
- p16: "the are often written as X".
- p22: "State of Authority (SOA)" for Start of Authority; "BlueGtaor" garbled registrar name.
- p27: "First seen with the Conficker worm" is contestable (Kraken and Srizbi used DGAs earlier in 2008); note says "made widely known by".
- p31: CountVectorizer example with a dotted vocabulary ('.com', '.de', '.uk') returns all zeros under the default token pattern, which strips the dot (documented behavior, not executed).
- p32: "tild/zoom" for tilt.
- p38: outdated Feature-engine import; `feature_engine.encoding.OneHotEncoder` is current.
- p41: second sentence truncated ("...you will").
- p55: caption "Selects all features above a given threshold" misdescribes SelectPercentile, which keeps a percentile by rank.
- p61: stray bullet character under the code block.

## 06-anomaly-detection
- p24: "167 outside 1 deviation" matches a one-tail count under the shown normal fit (about 159 of 1000); two-sided would be about 317. The 44 beyond 2 deviations is consistent.
- p27: title "Mean Absolution Deviation"; pseudocode omits the absolute value; `Series.mad()` was removed in pandas 2.0.
- p60: `behavior='new'` fails on every scikit-learn version (spelled `behaviour`, removed in 0.24).
- p66: MAC address shown with five hex pairs; a MAC has six.
- p67: `tokenize_data(d)` substitutes on `mac`, not `d`; `template_token` never defined; pandas and `good_macs` unused.
- p69: the homoglyph is the Cyrillic letter er, not a "Russian Rho" (rho is Greek).
- p15: "algorithms include" for "including". p65: Jaro "from each file" for "each string".

## 10-prompt-engineering
- p4: says an OpenAI API key is needed; the module and both worksheets use Anthropic (and, on Databricks, the workspace endpoint).
- p41, p62: JSON rule asks for confidence to two decimal places; the worked example prints three (0.965, 0.823).
- p17: frequency and presence penalty range shown as 0.0 to 2.0; OpenAI's range is -2.0 to 2.0, and the Anthropic Messages API has neither parameter.
- p9, p56: "Programatically". p28: "doesn't'".
