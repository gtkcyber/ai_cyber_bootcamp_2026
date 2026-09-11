## Page 1

TODO NEW SLIDE

## Page 2

This part gives the evidence behind deep learning's adoption: the results of the ImageNet image classification challenge from 2011 onward.

## Page 3

ImageNet is a labeled image collection, and the ImageNet Large Scale Visual Recognition Challenge is the annual competition that ran on it from 2010 to 2017. Entrants trained a classifier on 1.2 million labeled images spanning 1000 object classes and were scored on 100,000 held-out test images. The classes are fine grained: mite, container ship, motor scooter and leopard are four of them, and the alternatives a classifier has to rule out include black widow and tick for the mite, or jaguar and cheetah for the leopard.

The grid is from the paper that introduced AlexNet, the convolutional neural network by Alex Krizhevsky, Ilya Sutskever and Geoffrey Hinton that won the 2012 challenge. Each image carries the network's five highest-scoring labels as bars, and the correct label is written beneath it. For the cherry the five guesses are dalmatian, grape, elderberry, Staffordshire bullterrier and currant; for the Madagascar cat they are five kinds of monkey and lemur. Both count as misses under the challenge's scoring, which asks only whether the correct label is somewhere in the five. AlexNet's win is the event the caption calls a quantum leap: it was the first deep convolutional network to win the challenge, and it beat the hand-engineered systems of the previous year by a wide margin.

## Page 4

The chart plots the top-5 error of each year's winning entry: the share of test images on which the correct label is missing from the entry's five highest-scored guesses. The 2011 winner, from the Xerox Research Centre Europe, scored 26 percent with hand-designed features feeding a conventional classifier. AlexNet cut that to 16.4 percent in 2012, and every winner after it was a deeper convolutional network: ZF, from Zeiler and Fergus, in 2013; VGG, from Oxford's Visual Geometry Group, and GoogLeNet, from Google, in 2014; ResNet, Microsoft Research's residual network, in 2015; and GoogLeNet-v4 in 2016, at 3.1 percent.

The red bar is an estimate of human top-5 error on the same test set, about 5 percent, measured with a trained annotator. The 2015 winner passed it. That is the answer to the question in the title: within three years of AlexNet, a network with learned features labeled these images more accurately than a person.

## Page 5

Deep learning replaces engineered feature extraction with feature extraction learned from data. In the traditional computer vision pipeline at the top, a person designs the feature detectors, edge and corner detectors, color histograms and the like, and only the classifier at the end is fit to labeled data. Any pattern the hand-crafted features fail to capture is invisible to the classifier.

In the deep learning pipeline at the bottom every stage is trainable. The first layers learn low-level features such as edges and blobs, the middle layers combine those into parts and textures, and the later layers combine parts into object-level features that the final classifier separates. The whole stack is fit to the labeled images by one training procedure, so the features are selected by the training data.

## Page 6

Deep learning is a subset of machine learning, which is itself a subset of artificial intelligence. The diagram gives the working definitions: artificial intelligence is a program that can sense, reason, act and adapt; machine learning is the set of algorithms whose performance improves as they are exposed to more data; deep learning is the part of machine learning in which multilayered neural networks learn from large amounts of data. Because the terms nest, everything in this module is also machine learning and also artificial intelligence. What sets deep learning apart is the model class, multilayered neural networks, and the volume of data those networks are trained on.

## Page 7

Learning algorithms fall into two categories by whether the answer is available during training. Supervised learning has a teacher signal: each training observation comes with a label, the gold standard the model's output is compared against, and the support vector machines and regression models of earlier modules are examples. Unsupervised learning has no labels; the algorithm searches for structure in the observations, such as clusters, with nothing to compare against. Neural networks can be trained either way, and this module trains them the supervised way: the labels are the person a fingerprint belongs to and whether a URL is malicious.

## Page 8

This part builds a neural network up from its unit: the biological neuron, the artificial neuron that abstracts it, the perceptron, and layers of perceptrons trained by repeated prediction, error and weight correction.

## Page 9

The biological neuron is the template for the artificial one. Dendrites receive signals from other neurons; the cell body sums them; when the sum crosses a threshold the neuron fires, sending a pulse down the axon; the axon terminals pass that pulse to the dendrites of the next neurons. The whole cell reduces to an input side, an integrating body with a threshold, and an output side, and the connections between cells strengthen or weaken with use.

## Page 10

The artificial neuron computes a weighted sum of its inputs and passes the sum through a function, and each piece corresponds to a part of the biological cell. The inputs x1 through xn stand in for the signals arriving on the dendrites. Each is multiplied by a weight w1 through wn, the counterpart of a synapse's strength. The sum node plays the cell body, adding the weighted inputs. The activation function f plays the firing threshold, turning the sum into the output. The single output line is the axon.

## Page 11

Three properties of the biological neuron survive in the artificial one. Thresholding: the unit fires, meaning its output switches, when the weighted input crosses a level. Nonlinearity: the relationship between input and output bends, since a threshold cannot be expressed as a straight line. Adaptivity: the weights, the artificial synapse strengths, change during training. Together these abstract integrate-and-fire behavior: add up the inputs, fire when the total is large enough.

The standard unit is the perceptron. Frank Rosenblatt introduced it in 1958 as a trainable version of the McCulloch-Pitts neuron of 1943, which summed binary inputs and fired on a threshold. The citation here, Marvin Minsky and Seymour Papert's 1969 book Perceptrons, is the analysis that established what a single such unit can and cannot compute. The perceptron is still the basic unit of the networks in this module.

## Page 12

A perceptron has six parts.

- Inputs: here three, x1, x2 and x3.
- Weights: one per input, here 1.0, negative 0.75 and 0.25, so the second input pulls the sum down and the other two push it up.
- Combination function: the rule that merges the weighted inputs, ordinarily a sum.
- Activation function: the threshold rule applied to the sum, here the hyperbolic tangent, tanh.
- Output: the single value y.
- Bias: a constant input of one with its own weight, here negative 0.5, which sets the unit's resting sum when every input is zero.

One perceptron can compute little on its own; it draws a single straight boundary through its input space. The capacity of a neural network comes from connecting many of them in layers, so that the outputs of one layer are the inputs of the next.

## Page 13

The same perceptron written out. The bias b is negative 0.5 and the weight vector w is 1.0, negative 0.75 and 0.25. The combination function c multiplies each input by its weight and adds the products. The activation a is the hyperbolic tangent of that sum, and the output y is the activation applied to the bias plus the weighted sum.

The worked example feeds in the inputs negative 0.8, 0.2 and negative 0.4. The bias plus the three weighted inputs comes to negative 1.55, and the hyperbolic tangent of negative 1.55 is negative 0.91, the unit's output. The graph explains the choice of tanh: it maps any sum onto the interval from negative one to one, is close to a straight line near zero, and flattens toward either limit, so a large sum in either direction saturates the output and the unit behaves as a soft switch.

Every neuron and every network is a variation on these pieces. The parameters b and w, the combination function and the activation function are what differ between designs.

## Page 14

A multi-layer perceptron arranges perceptrons in layers. The input layer holds the observation's values x0 through xi and does no computation. Each unit in the hidden layer is a perceptron that receives every input, weights it, sums and applies its activation. Each unit in the output layer is another perceptron whose inputs are the hidden layer's outputs. Every unit in one layer connects to every unit in the next, the arrangement called fully connected or dense, and the number of hidden units and hidden layers is the designer's choice.

## Page 15

Training a neural network is a loop of guess, compare and correct. The example network takes three inputs and produces one output, and the training data is four observations with three values each and a target of 0 or 1.

- Initialize with random weights: the first output is therefore meaningless.
- Present a training pattern: the first observation, 1.4, 2.7 and 1.9, goes into the input layer.
- Feed through to output: the values flow through the hidden layer to the output unit, which produces 0.8.
- Compare to target and calculate the error: the target for that observation is 0, so the error is 0.8 minus 0, which is 0.8.
- Modify weights based on the loss function: every weight is nudged in the direction that would have reduced that error; the green and red connections mark the weights that changed.
- Present a new pattern and repeat: the third observation, 6.4, 2.8 and 1.7 with target 1, produces 0.9 and the cycle runs again.

Thousands of passes over the data are needed before the weights settle on values that map each observation onto its target, because each correction moves the weights only a small step.

## Page 16

TensorFlow Playground, the page at the link, is a browser demonstration published by the TensorFlow team that animates the training loop described earlier. It trains a small fully connected network on a two-dimensional toy dataset chosen from a menu: the inputs are a point's coordinates and simple transforms of them, the target is the point's color, and the output is a colored map of the network's prediction over the plane. While training runs, the thickness and color of each connection show the current weight, the small image inside each hidden unit shows the pattern that unit responds to, and the loss curve at the top right tracks the error falling. Hidden layers, units per layer, activation function, learning rate and batch size are all adjustable, so the effect of each setting on the boundary and on the loss can be watched directly.

## Page 17

The supervised learning vocabulary, each term matching a box in the diagram.

- Observations: the items to predict something about, also called inputs; the table of rows in the data box.
- Targets: the labels attached to each observation, the column of zeros and ones, and the thing being predicted.
- Model: a function that takes an observation x and outputs a value for its target.
- Parameters: the numbers inside the model that determine what it computes, called weights and written w, or w with a hat once they have been estimated from data.
- Predictions: the model's guesses at the targets, also called estimates, written y with a hat to distinguish them from the true y.
- Loss function: the box that takes predictions and targets and returns a number measuring how far apart they are over the training data. Lower loss means better predictions.

## Page 18

Supervised modeling is one procedure regardless of the model: fit the parameters on labeled data, then apply the fitted model to new data.

- Start with a large set of correctly labeled observations.
- Pass each observation through the model and compute the error, also called the loss or cost, by comparing the prediction to the correct label.
- Use a second function to adjust the parameters so that the error falls; the gradients arrow from the loss function to the parameters box is that adjustment.

The goal is the set of parameter values that makes the loss as small as possible on the given data. A minimum of a smooth function sits where its slope is zero, so the task is the root-finding problem of elementary calculus applied to the loss's derivative.

Most of the design work is three choices: which model, linear, nonlinear or neural network; which error measure, the cost function; and which minimization algorithm, gradient descent, simulated annealing or another. The third choice depends on the second, since the algorithm that minimizes a function fastest depends on the shape of that function.

## Page 19

The toy example and the general diagram describe the same two steps. On the left are the two panels from the training loop: compare the network's output with the target to get the error, then modify the weights according to the loss. On the right are the boxes those panels correspond to: the loss function, which takes the predictions and the targets and produces the error, and the arrow back to the parameters, which is the weight modification. The model box and the data box are the rest of the loop, the forward computation that produced the prediction.

## Page 20

A loss function turns the gap between predictions and targets into a single number to minimize. The formula here is the least mean squares cost. Theta stands for the parameters, the same quantities called w before; h sub theta of x is the model's prediction for input x; y is the target; i indexes the training observations and m is how many there are. The cost adds up the squared difference between prediction and target over every observation and halves the total. Squaring makes every error positive and penalizes large misses more than small ones; the one half is bookkeeping that cancels the two produced when the square is differentiated.

Gradient descent is the algorithm that minimizes it. Start from an initial guess for theta. Find the direction in which the cost rises fastest around the current location, take a step the opposite way, and repeat from the new location. The update rule states the same thing: each parameter theta sub j is replaced by itself minus alpha times the partial derivative of the cost with respect to that parameter. The partial derivative is the slope of the cost along that one parameter, so subtracting it moves downhill.

Alpha is the learning rate, the step size. It is not learned; it is set by hand before training begins. Settings of that kind, fixed by the person before training, are called hyperparameters.

## Page 21

Batch gradient descent walks down the loss surface using the full training set at every step. The surface in the middle plots the error for every pair of values of two weights; it is bowl shaped, and the bottom of the bowl is the pair of weights with the lowest error. The contour plot on the right is the same bowl seen from above, each ellipse a ring of equal loss, with the ellipses tightening toward the minimum at the center. The blue path is one run of batch gradient descent: it starts at the right edge, and each segment is one update, computed from the gradient of the loss summed over every training observation. The path runs roughly perpendicular to the contours, the direction of steepest descent, and the steps shrink as the slope flattens near the bottom. When the path stops moving, the current thetas are the model's parameters.

## Page 22

Stochastic gradient descent updates the parameters after every single training observation. Batch gradient descent computes the gradient over all m observations before it can take one step, so a large dataset makes each step expensive. Stochastic gradient descent computes the gradient from one observation, takes a step, and moves to the next observation. Each such gradient is an estimate of the full one, so the path zigzags, as in the right-hand plot, but it takes many steps for the cost of one batch step and reaches the neighborhood of the minimum sooner. That trade makes it the more common choice in machine learning.

Loss functions and optimization algorithms are active research areas, with new variants appearing across several disciplines. All of them share one premise: move across the error surface quickly to a minimum that is good enough for the data and task at hand.

## Page 23

Backpropagation is the algorithm that makes computing the gradient affordable for a network with many parameters. Gradient descent needs the partial derivative of the loss with respect to every weight in the network, and a deep network can have millions of them. Computing each one separately is too slow to be practical. In 1986 David Rumelhart, Geoffrey Hinton and Ronald Williams adapted a method with roots in work from the late 1960s and early 1970s, called backpropagation, that shares work between the derivatives and made training networks with many parameters tractable.

Backpropagation is a special case of automatic differentiation, a family of techniques that computes exact derivative values of a function at given inputs. The procedure has three stages for each training example.

- Forward pass: compute the activation of every unit from the input layer through the hidden layers to the output layer.
- Error: compare the output with the target using the loss function.
- Backward pass: send the error back through the network from the output layer to the input layer, assigning each unit its share of the error and producing the derivative for each weight along the way.

## Page 24

The listing is the backpropagation algorithm for one training input, in four steps.

- Feedforward pass: compute the activations of every layer in order, from the first hidden layer up to the output layer.
- Output error terms: for each output unit, compute delta, the derivative of the cost with respect to that unit's weighted input. It equals the negative of the target minus the activation, times the derivative of the activation function at the unit's weighted input.
- Hidden error terms: work backward through the layers. Each hidden unit's delta is the weighted sum of the deltas of the units it feeds in the next layer, times the derivative of its own activation function. This is the step that moves from output toward input and gives the algorithm its name.
- Derivatives: the derivative of the cost with respect to a weight is the activation of the unit the weight comes from times the delta of the unit it goes to; the derivative with respect to a bias is that unit's delta alone.

Each delta is reused by every unit in the layer before it, so the work of one layer's derivatives is done once and shared.

Backpropagation is decades old. What changed to make it widespread is software: libraries such as TensorFlow, Google's deep learning library, and PyTorch, Meta's, both used in this module's worksheets, implement backpropagation and general automatic differentiation on top of computational graphs, so the derivatives of any model written in the library are computed by the library.

## Page 25

A computational graph is an equation drawn as nodes and edges. Each node is an operation, each edge carries a value from one operation to the next, and walking the graph from inputs to output evaluates the expression. The sum p equals x plus y becomes a single plus node with edges in from x and y and one edge out to p. The product g equals x plus y, all times z, becomes two nodes: the plus node produces p, and a multiply node takes p and z and produces g. The intermediate variable p is the same device the chain rule uses when it differentiates a nested expression, naming the inner result so the outer operation can be handled on its own.

## Page 26

The worked example runs the graph for g equals x plus y, all times z, forward and then backward, with x equal to 1, y equal to 3 and z equal to negative 3.

Forward pass, left to right. The plus node takes 1 and 3 and produces p equal to 4. The multiply node takes p equal to 4 and z equal to negative 3 and produces g equal to negative 12. Each node keeps the values it saw, because the backward pass needs them.

Backward pass, right to left. The goal is the derivative of the final output g with respect to each input, x, y and z. Step 1 starts at the output: the derivative of g with respect to itself is 1. Step 2 goes back through the multiply node. Because g is p times z, the derivative of g with respect to z is p and the derivative with respect to p is z; the values kept from the forward pass make those 4 and negative 3. Step 3 goes back through the plus node using the chain rule: the derivative of g with respect to x is the derivative of g with respect to p times the derivative of p with respect to x. Since p is x plus y, the derivative of p with respect to x is 1, and likewise for y. Negative 3 times 1 gives negative 3 for both x and y. Three derivatives came out of one backward pass over the values kept from the forward pass.

## Page 27

Every node in a computational graph does the same two-stage job, whatever operation it holds. Stage 1, the forward pass: the node receives its inputs x and y, applies its operator f, and emits z equal to f of x and y, keeping the inputs for later. Stage 2, the backward pass: the node receives the derivative of the overall loss J with respect to its output z, multiplies it by the local derivative of z with respect to each input, and passes the results, the derivative of J with respect to x and with respect to y, to the nodes that fed it. The chain rule is applied one node at a time, and a node needs nothing beyond its own operator and the number handed to it from the right. Computing the gradient of an entire network therefore becomes a local computation, and a library can differentiate any model it can assemble from such nodes.

## Page 28

This part covers how the layers of a fully connected network come to detect features, and the two architectures that depart from full connectivity, convolutional and recurrent networks.

## Page 29

The running example is handwritten digit recognition. Each digit is a small grayscale image, drawn here as a grid of 7 columns by 9 rows, 63 pixels in all, numbered 1 to 63 across the rows. The input layer has one node per pixel, so 63 input nodes, and the value of each node is whether that pixel is dark.

The network is the fully connected feedforward design from before, with two hidden layers and one output layer. Feedforward: nodes in a layer connect only to the next layer, with no backward connections and none that skip a layer. Fully connected: every node connects to every node in the following layer. For ten digits the output layer has ten nodes, and the network's answer is the output node with the largest value.

## Page 30

The question is how a network of weighted sums comes to recognize a 9. The answer is in the weights of the hidden units. Each hidden unit connects to all 63 inputs, and after training its 63 weights form a pattern: large weights on some pixels, near-zero weights on others. A unit responds strongly when the dark pixels of the image line up with its large weights, so each unit is a detector for one spatial pattern in the input, and the pattern emerged during training.

The two examples at the bottom unroll the 63 pixels into a single row. The left unit has strong connections, the red lines, to inputs 3 through 6, the dark pixels of the top row of the 9, so it sends a strong signal whenever the top stroke is present. The right unit has strong connections to the pixels in the highlighted block at the upper left of the digit, and fires when that region is dark. The weights organized themselves under the training loop, which is why hidden units are called self-organized pattern detectors.

## Page 31

The first layers of a digit network detect basic strokes. Three kinds are marked on the digit grid: vertical lines, small circles and horizontal lines, each of which appears in several different digits. Each is a pattern over a handful of neighboring pixels, exactly what a hidden unit with a compact block of strong weights detects. A single stroke does not identify a digit: a vertical line is in the 1, the 4 and the 7, and a small circle is in the 6, the 8, the 9 and the 0. Identification requires combining them.

## Page 32

Later layers detect combinations of the strokes found by the first layer. The first-layer units along the top each respond to a line at a specific position: a horizontal bar across the top row, a vertical bar in one column, and so on. A unit in the next layer takes those units as its inputs, and its weights select a combination of them. Several horizontal detections at neighboring rows make a horizontal line detector that tolerates position; several vertical detections make a vertical stroke detector; the ring of small detections on the right makes an upper loop detector. A top stroke, an upper loop and a descending stroke together are a 9, so the layer after that can hold a unit for the digit itself. Feature complexity grows with depth: pixels, then lines at fixed positions, then lines and loops, then digits. This is the low-level, mid-level, high-level hierarchy of the deep learning pipeline.

## Page 33

Two architectures are used in the rest of the module. Convolutional neural networks, CNNs, are built for images and other static data, inputs whose structure is spatial and whose size is fixed. Recurrent neural networks, RNNs, are built for sequences and time-stamped data, inputs whose structure is an order in time and whose length varies. Both are modifications of the fully connected feedforward network.

## Page 34

This part covers convolutional neural networks: convolution and pooling as spatial filters, and the assignment of subsets of units to parts of the input.

## Page 35

A convolutional neural network takes a high-dimensional image and produces a low-dimensional intermediate representation that a classifier can work with. A 160 by 160 grayscale image, the size used in the fingerprint worksheet, is 25,600 input values, and a fully connected first layer of 100 units on top of it would need 2.56 million weights. Two ideas make the dimension manageable.

- Filter the high-dimensional information in space: squeeze the image down by convolution, which extracts local features, and pooling, which shrinks the result, both operating on neighborhoods of pixels.
- Have a subset of neurons learn a part of the input: divide and conquer. Each unit sees only a small patch of the spatially filtered output, so the early layers are no longer fully connected.

CNNs were developed for image processing, where both ideas match the data: features such as edges are local, and the same feature matters wherever in the image it appears.

## Page 37

Convolution slides a small kernel over the image and records, at each position, how strongly the patch under the kernel matches it. The kernel is a small grid of weights, here three by three, in blue. Placing it over the top-left three by three patch of the image, multiplying each pixel by the weight above it and adding the nine products gives one number, the top-left cell of the convolved feature. Sliding the kernel one pixel to the right and repeating fills the next cell, and so on across and down the image; a six by six image with a three by three kernel yields a four by four convolved feature. The kernel's weights are learned by training, so each kernel becomes a detector for one local pattern, and a convolutional layer has many kernels, each producing its own feature map.

Pooling reduces the convolved feature further. A pooling kernel, also a small window, slides over the feature map and replaces each window with a single summary value: the mean of the window for average pooling, the largest value for max pooling. The result is a smaller map that keeps the presence of a feature in each region and drops its exact position, which shrinks the data handed to the next layer and makes the detection tolerant of small shifts.

## Page 38

The same two operations with numbers. The image is a five by five grid of ones and zeros. The kernel is three by three, with a weight of one at the four corners and the center and zero elsewhere; the small subscripts on the highlighted patch are those weights. Multiplying the nine pixels of the bottom-right patch by the weights and adding gives four ones and five zeros, so the bottom-right cell of the convolved feature is 4. Repeating at every position produces the three by three feature map, since a five by five image offers a three by three kernel nine positions. The cells holding 4 mark patches whose ones fall where the kernel's ones are, which is what it means for a kernel to detect a pattern.

Pooling divides the four by four map into four two by two windows. Max pooling keeps the largest value in each window: 20, 30, 112 and 37. Average pooling keeps the mean of each window: 13, 8, 79 and 20, the last rounded. Either way the map shrinks from sixteen values to four, one per window, so the next layer sees a quarter of the data.

## Page 39

A CNN chains spatial filtering with a fully connected classifier. On the left is the digit network again: feedforward and fully connected, every one of the 63 pixel inputs wired to every hidden unit. On the right is the CNN layout. Input images pass through a convolution stage, producing a stack of feature maps, one per kernel; a pooling stage shrinks each map; and the shrunken maps feed a fully connected, or dense, network whose outputs are the class scores. The brackets label the division of labor: convolution and pooling are feature learning, the dense layers are classification. Convolution and pooling can be repeated, a second convolution reading the pooled maps of the first, as many times as the problem needs.

The second idea is in the dashed lines: each unit in a convolution layer is connected only to a small patch of the layer before it, so a subset of the units learns a part of the input. Divide and conquer replaces full connectivity in the feature learning stages, and full connectivity returns at the classifier.

## Page 40

The diagram is the full pipeline for a classifier that labels an image as a car, truck, van or bicycle. The input is a color image, drawn as stacked planes, one per color channel. Convolution plus ReLU produces a block of feature maps; ReLU, the rectified linear unit, is an activation function that outputs its input when the input is positive and zero otherwise, and it is the activation applied after each convolution here. Pooling shrinks the block, and a second convolution plus ReLU and a second pooling repeat the pair on smaller, more abstract maps. That ends feature learning.

Classification begins with flatten, which unrolls the final block of maps into a single vector, the same unrolling of a grid into a row used for the digit pixels earlier. A fully connected layer maps that vector to one score per class, and softmax converts the scores into probabilities that add up to one, so the output reads as the probability that the image is each of the classes.

## Page 41

Deep learning became accessible through a three-part stack: hardware, a framework and a wrapper. NVIDIA graphics processors supply the arithmetic; training is millions of weighted sums and their derivatives, which a graphics processor executes in parallel. The worksheets run on a CPU, and a GPU shortens their training. TensorFlow, released by Google in 2015, is the framework: a backend written in C that runs the computational graph, and a frontend in Python for defining it. Keras is the high-level wrapper: a Python API in which a network is a list of layers and training is a single call, so the graph construction and the training loop are handled by the library.

Each layer of the stack has alternatives. The list here names Theano and Torch as other backends, and Lasagne, Caffe, Pylearn2 and Chainer as other high-level APIs. Torch's Python successor, PyTorch, is the library the URL worksheet uses.

## Page 42

Training processes the data in batches, and three terms count the work.

- Batch size: the number of training examples pushed through one forward and backward pass together, so one weight update. Memory sets the ceiling, since the whole batch and its activations must fit in RAM at once. In the URL worksheet a batch is a set of URLs.
- Iterations: the number of batches processed, one weight update each.
- Epoch: one forward and backward pass over all of the training data, that is, enough iterations to visit every example once.

With 1000 training examples and a batch size of 500, two iterations make one epoch. A batch of one is stochastic gradient descent and a batch of the whole set is batch gradient descent; sizes in between, called mini-batches, keep most of the speed of the stochastic version with less noise per step. Batch size and number of epochs are both hyperparameters that the training call requires, in Keras and PyTorch alike. A batch size of 32 is a common default; the fingerprint worksheet uses 64 for 20 epochs and the URL worksheet uses 512 for 3 epochs.

## Page 43

TODO NEW SLIDE

## Page 44

This part covers recurrent neural networks: why a feedforward network cannot use order, how a feedback loop in the hidden layer gives a network memory of a sequence, and the gated cells, LSTM and GRU, that keep that memory stable over long sequences.

## Page 45

Everything so far treats the order of the inputs as meaningless. The two digit networks make the point: one reads the pixels row by row and the other column by column, and for classification they are equivalent, because a fully connected layer applies a separate weight to every input and any consistent reordering of the inputs is absorbed by reordering the weights. Nothing in the network records that pixel 2 came after pixel 1.

Many data are ordered. Time-dependent data such as stock prices, logins and server logs, and sequences such as language and video, carry information in the order of their elements, and a model that discards the order discards that information. The class of networks that can read order is the recurrent neural network.

## Page 46

A recurrent neural network has feedback connections as well as feedforward ones. In a feedforward network, drawn on the left in its layer form, information moves in one direction, input to hidden to output. Such a network has a fixed number of inputs and no way to relate one input to the one before it, so it cannot take a sequence whose length varies; text is the standard example.

The recurrent network adds a loop on the hidden layer. At each step of the sequence the hidden layer receives the current input and its own output from the previous step, so its state at step t depends on step t minus 1, which depended on step t minus 2, and so on back to the start. A relation in which each term is defined by the one before it is a recurrence relation, hence the name. The loop runs once per element, so one network handles a sequence of any length.

## Page 47

Unfolding the loop turns a recurrent network into a feedforward one with a copy of the hidden layer per step. On the left is the compact form: input x, hidden state h with a loop back to itself, output y, with a weight set W sub x on the input, W sub y on the output and a third on the loop. On the right is the unfolded form: at step t the hidden state h sub t is computed from the input x sub t and the previous state h sub t minus 1, and produces y sub t. The same three weight sets are used at every step, so unfolding adds no parameters, only copies.

- Memory: the influence of the sequence's history on the current step. The state carried along the chain is what the network remembers, and the weights determine what is kept.
- Memory length: how many steps back the current step is influenced by, set by how many steps the loop is unfolded during training.
- Instability: basic RNNs become unstable as the memory length grows. Training runs backpropagation along the unfolded chain, and the gradient at an early step is a product of one factor per step between it and the loss. A long product of factors below one shrinks toward zero and a long product of factors above one grows without bound, so the weights at early steps either stop learning or diverge. This is the vanishing and exploding gradient problem.

## Page 48

Gated cells replace the single activation of a basic RNN unit with several functions whose outputs are combined. In a basic RNN every unit is a plain artificial neuron with one activation, tanh, drawn as the green block with a single blue tanh symbol: it takes the current input and the previous hidden state, applies tanh, and passes the new hidden state h sub t to the next step.

The modified unit for longer memory holds several functions inside one cell: sigmoid functions, in red, the S-shaped logistic curve whose output lies between zero and one, and tanh functions, in blue, whose output lies between negative one and one. Their outputs are combined by pointwise multiplication and pointwise addition, and inputs are joined by vector concatenation. Multiplying a signal by a sigmoid output scales it: a value near zero blocks the signal and a value near one passes it. A sigmoid used this way is a gate, and the gates decide how much of the previous state and how much of the current input is allowed forward. The cell has more functions and more parameters than a plain unit, and those extra parameters are what give it control over its own memory at every step.

## Page 49

Two gated cells are in common use. Long short-term memory, LSTM, carries a separate cell state along the top of the diagram, the horizontal line that crosses the cell touched only by one multiplication and one addition, and controls it with four gates.

- Forget gate: a sigmoid that decides what to erase from the previous cell state and what to keep, by multiplying the state elementwise.
- Input gate: a sigmoid that decides which values from the current input will be written.
- Cell gate: a tanh that generates the candidate values for the new cell state, which the input gate admits or blocks before they are added to the state.
- Output gate: a sigmoid that decides what part of the updated cell state becomes the hidden state passed to the next step and to the output.

Because the cell state is changed only by a gated multiplication and a gated addition, information can travel along it for many steps without passing through an activation function at each one, which is what lets an LSTM keep track of inputs over long sequences and avoids the instability of the basic unit.

Gated recurrent units, GRUs, are a simplified LSTM that folds the four gates into two, a reset gate and an update gate, and drops the separate cell state, keeping only the hidden state. Fewer parameters mean less to train, and GRUs are widely used.

## Page 50

Worksheet 8.2 trains a recurrent network to classify URLs as malicious or benign. A URL is a sequence of characters, so the sequence model applies with characters as the steps. The preprocessing encodes each character as an integer index into Python's set of printable characters, then cuts or left-pads every sequence to 75 integers so that a batch of URLs can be stacked into one array. The labels come from an isMalicious column, and the data is split 70, 15, 15 into training, validation and test sets, stratified so each split has the same malicious fraction.

The model, written in PyTorch, is an embedding layer that turns each character index into a vector of 32 values, an LSTM that reads the 75 vectors in order and returns its final hidden state, dropout, which zeroes a random fraction of the values during training to limit overfitting, and a linear layer that produces one score. The training loop is written by hand: for each batch of 512 URLs, clear the gradients, run the forward pass, compute the loss with a function that combines the sigmoid and binary cross-entropy in one step, run backward to get the gradients, and step the optimizer. Three epochs are run, with validation accuracy measured after each and test accuracy at the end. Prediction repeats the same encoding on a new URL, and a sigmoid on the model's score gives the probability that it is malicious, called malicious above one half.

## Page 51

Four conclusions.

- Deep learning is not magic. The mechanism is the one this module walked through: weighted sums, a loss, gradient descent and backpropagation. The size of the datasets is what changed the results; the networks reached their ImageNet accuracy because 1.2 million labeled images existed to train them on.
- Certain problems fit deep learning and others do not. Problems with large labeled datasets and inputs with spatial or sequential structure, such as images, audio, text and logs, fit it. Problems with little labeled data or a handful of tabular features do not, because the network has nothing to learn its features from.
- Deep learning is hard to implement, and the tools keep getting easier. The worksheets build and train each network in a short notebook of Keras or PyTorch.
- Of the two architectures, recurrent networks have the wider application in cybersecurity, because the field's data, logs, network flows, command histories, URLs and domain names, arrives as ordered streams.

## Page 52

This closes Module 8. The two worksheets, 8.1 on convolutional networks and 8.2 on recurrent networks, are where the material is put to use.
