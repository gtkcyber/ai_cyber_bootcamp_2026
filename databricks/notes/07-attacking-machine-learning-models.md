## Page 1

Module 7 covers attacks on trained machine learning models: evasion, poisoning, membership inference, and model extraction and inversion, then the evasion methods in detail and their implementation in the Adversarial Robustness Toolbox.

## Page 3

A trained model is attackable through every interface it exposes. Its inputs can be crafted to produce a chosen wrong answer, its training data can be altered to move where it draws its decisions, and its outputs can be mined to reconstruct what it learned or what it was trained on.

## Page 4

Four attack families cover the ways a model can be turned against its owner. Model evasion: an input is crafted so the model misclassifies it. Poisoning: training data is altered so the model that comes out of training draws its boundary where the attacker wants. Membership inference: the attacker determines whether a particular record was in the training set. Model extraction and inversion: the attacker copies the model's function, or recovers training data or internal state, from what the model returns.

Access level splits every family into two settings. A white box attack has the model itself: architecture, parameters, and therefore gradients. A black box attack has only what the model returns for an input, and that return can be a probability score or a bare class label. The evasion methods in this module are presented in order from the most access to the least.

## Page 5

The attack surface is the whole model lifecycle, and each phase is tagged as a training activity or an inference activity. Data collection: data is gathered from public and platform sources with a specific model in mind, and gathering continues after the model ships, so an attacker who can place records in those sources reaches the training set. Data processing: the collected data is transformed before it reaches an algorithm, for training and for inference. Model training: the processed data is fed to an algorithm to produce the model. Model validation: the trained model is checked for accuracy, robustness, explainability or other metrics, and a poisoned model that keeps its accuracy on clean validation data passes this check.

Model deployment: the model is embedded in a production system, which may be an autonomous vehicle, a web API, or a client side application, and the deployment form decides what an attacker can reach. System monitoring: the running system is watched, including parts unrelated to the model. The training and inference labels are the axis on which each attack type is placed.

## Page 6

Each attack type maps to one side of the lifecycle. Functional extraction, inference: the adversary copies what the model does. Model evasion, inference: the adversary causes a misclassification. Model inversion, inference: the adversary recovers internal state such as trained weights. Membership inference, inference: the adversary recovers data the model was trained on. Model poisoning, training: the adversary alters the inputs to training. System compromise, no activity type: conventional attacks on the infrastructure that hosts the model, which need no machine learning at all.

The two recovery rows use the terms more loosely than the research literature does. Model inversion (Fredrikson, Jha and Ristenpart, 2015) reconstructs inputs that the model associates with a given class, which is the facial recognition example this module uses. Membership inference (Shokri et al., 2017) answers a yes or no question: was this specific record in the training set.

## Page 7

This part covers model evasion: adversarial examples, the demonstrations that established them, and the diagram that explains where they come from.

## Page 8

The title is that of a paper by Anh Nguyen, Jason Yosinski and Jeff Clune (2015). They generated images, by evolutionary search and by gradient ascent, that no human recognizes as anything, and convolutional networks trained on ImageNet and on MNIST labeled those images as a specific class with confidence above 99 percent. A high prediction score therefore measures how far an input sits on one side of a boundary, and says nothing about whether the input resembles the class.

## Page 9

A perturbation does not have to be small or hidden. The sticker is an adversarial patch (Brown et al., 2017): a printed image optimized so that a classifier labels any scene containing it as a toaster, at any position, scale and rotation the optimization covered. With the sticker on the table beside the banana, the classifier's output moves from banana at about 0.97 to toaster at about 0.97, and banana falls to a trace. The patch works because the optimization makes it a stronger toaster signal than any real object in the frame is a signal for its own class.

## Page 10

Physical stickers on a real stop sign made a road sign classifier read it as a 45 mph speed limit sign. Evtimov et al. (2017) computed the black and white rectangles with an optimization that includes the variation a camera introduces, so the perturbation holds across the distances, viewing angles and lighting conditions the authors tested rather than for one photograph. The stickers pass for graffiti, which is the constraint the authors set: a change that a human driver would ignore.

## Page 11

The same method turned a right turn warning sign into a stop sign for the classifier. The perturbation is the pixelated overlay on the arrow, printed to look like a low resolution graphic. The direction of the error matters as much as its existence: a vehicle that reads a turn warning as a stop sign brakes where it should steer, and one that reads a stop sign as a speed limit does not brake at all.

## Page 12

Adding a computed noise pattern, scaled by a small epsilon, moved a classifier from panda at 57.7 percent to gibbon at 99.3 percent. The pattern in the middle is the sign of the gradient of the model's loss with respect to each input pixel: for every pixel, the direction of change that most increases the error. Epsilon is the size of that change per pixel, and for this image it is 0.007 on a zero to one scale, below what a display can render. The confidence on the wrong answer exceeds the confidence the model had on the right one.

## Page 13

The perturbation survives printing and being photographed again. The figure is Figure 1 of Kurakin, Goodfellow and Bengio, Adversarial Examples in the Physical World (2016); the citation on the page names the 2014 paper. The dataset image was printed on paper, then a phone running an image classifier photographed the clean print and two adversarial prints. The clean print is classified as a washer at 0.54. At epsilon 4 the top class becomes safe at 0.35 with washer second at 0.22. At epsilon 8 safe stays on top, loudspeaker takes second place, and washer leaves the top two. Epsilon here is measured on the zero to 255 pixel scale. The attack therefore does not depend on delivering exact pixel values to the model; a camera's blur, color shift and lighting leave enough of the perturbation intact.

## Page 14

A model evasion attack feeds the model an adversarial example, an input crafted so that the model assigns it the wrong class. The attack predates deep learning: Dalvi et al. described it in 2004 against linear spam classifiers, where the adversary edits a spam message until the filter passes it. It works in the white box setting, where the attacker uses the model's gradients, and in the black box setting, where the attacker uses only outputs. Model complexity is no defense, because a larger model has more input dimensions and more learned cues, and each one is a place a perturbation can act.

## Page 15

Adversarial examples live in the gap between what a model was trained on and what it will be asked about. The dotted circle is the theoretical distribution space: every input the model could receive. The large solid circle is the training data distribution, the region the model has seen. The small circle is the test data distribution, the inputs the deployed model actually receives. The shaded crescent is the adversarial space: valid inputs that arrive at inference time but fall outside the training distribution, where the model's output is whatever its learned function extrapolates to. An attacker who can steer an input into that crescent gets an output the training process did not constrain.

## Page 16

This part covers functional extraction: copying a model's behavior through its outputs, and what a copy is used for.

## Page 17

Functional extraction builds a substitute that reproduces the target model's behavior without access to the target's parameters. The photographs illustrate biological mimicry: the bull snake, which has no venom, copies the prairie rattlesnake's coiled posture, hiss and tail vibration and receives the same protection. The model version works by querying: the attacker sends chosen inputs to the target, records the labels or scores it returns, and trains a model of the attacker's own choosing on those input and output pairs (Tramèr et al., 2016). The result answers the same way the target does across the inputs that were queried, which is all an attacker needs.

## Page 18

A local copy of the target lets the attacker rehearse other attacks where the defender cannot see them. Evasion: adversarial inputs are developed against the copy with unlimited queries, no rate limit and no logging, then sent to the target. Adversarial examples crafted against one model transfer to other models trained for the same task (Papernot, McDaniel and Goodfellow, 2016), which is why work done on the copy carries over. Poisoning: the attacker practices injecting data into the copy's training set and measures how much data of what kind moves its boundary, which gives a baseline estimate for the target. An open source or open weight model, one whose trained parameters are published with or without its training code and data, hands the attacker this copy with no extraction at all: the released weights are the model, so a defender who deploys them unchanged is running the exact function the attacker rehearses against, and a defender who fine tunes them first is running a function that differs from the copy only by that fine tuning.

## Page 19

This part covers model inversion and membership inference: recovering training data, or facts about it, from a model's outputs.

## Page 20

The setup is the one studied by Fredrikson, Jha and Ristenpart (2015). A facial recognition model W is produced by a training procedure Y from a set of face images X, and the model is released, so the attacker has it in full. The model's output labels are the names of the people it recognizes. The question is whether, holding W and the label set, the attacker can recover the faces in X.

## Page 21

The answer is yes, to the degree the pair of images shows. The left image was reconstructed from the model; the right is a training photograph of the same person. The attacker had only the person's name and query access to a facial recognition system that returns a confidence score for each name. The reconstruction is gradient descent over the input: start from a blank image, and repeatedly adjust the pixels in the direction that raises the confidence for the target name until the image is what the model most associates with that person. Because the score is enough, this version of the attack works without the model's internals, whereas the setup on the previous page assumed a released model.

## Page 22

Whatever a model was trained on can come back out of it. Credit card numbers and addresses that appear in text a language model trained on can be extracted from the model (Carlini et al., 2019). The excerpt is from Fredrikson, Jha and Ristenpart (2015), which trained decision trees on two surveys: a FiveThirtyEight survey of 553 people that asked about smoking, infidelity and steak preference, and a second survey with 11 variables that asked about marital happiness and whether the respondent had watched X-rated films in the past year. Given the tree and a respondent's non sensitive attributes, the inversion attack recovers that respondent's answer to the underlined questions. The survey data was collected as anonymous statistics; the model turned it into per person records.

## Page 23

This part covers poisoning: altering a model by altering what it trains on.

## Page 24

A poisoning attack injects data into a model's training stream so that the retrained model moves its decision boundary in a direction the attacker chose. The definition names online learning systems, models that keep training on the inputs they receive after deployment, because there every input is a candidate training record. The same attack applies to any pipeline that periodically retrains on data collected from outside.

## Page 25

An online learning system updates its parameters over time from the inputs it receives, so an attacker who controls inputs controls part of the training set. The decision boundary sits where the training data puts it; records inserted near the boundary, labeled or shaped to pull it in one direction, move it on the next retraining. The attacker's goal is a boundary under which a chosen class of malicious input is classified as benign, or a chosen class of benign input is classified as malicious.

## Page 26

The screenshot is a poisoning channel in a consumer product. Google Translate renders "i love cheese" as "j'aime le fromage", and the suggest an edit feature lets a user strike that out and submit "je déteste le fromage", which means the opposite. The notice states that the contribution will be used to improve translation quality: user corrections feed the retraining data. Enough coordinated false corrections change what the system outputs, and the individual submissions are indistinguishable from good faith fixes. The example is from Chio and Freeman, Machine Learning and Security (2018), page 322.

## Page 27

The figure is the starting state of a poisoning sequence from Chio and Freeman, Machine Learning and Security (2018), page 322. Two classes are plotted on two standardized features, open circles above and filled circles below, and the curve is the decision boundary a classifier learned from those points. A handful of points already sit on the wrong side of the curve, which is ordinary for a boundary fit to overlapping data. Everything that follows is the same plot after the attacker adds records and the system retrains.

## Page 28

The attacker's first move is five records, drawn as stars, placed just above the boundary on the left at the edge of the open circle class. They carry the open circle label, and they sit where the classifier's margin for the filled class begins. Retraining on the data with the stars included moves the left half of the boundary downward by a small amount: the gray curve is where the boundary was, the black curve is where it is now. Any single retraining looks like the normal adjustment a model makes when new data arrives.

## Page 29

A second retraining widens the gap. The stars stay where they were, and the boundary moves down again, so the region between the gray and black curves on the left has grown. Nothing about the new records is anomalous on its own: each has plausible feature values and a label consistent with its neighbors on the open circle side.

## Page 30

By the third retraining the stars are well inside the open circle region, and the boundary continues to move away from them. The mechanism is the same one that makes the model learn at all: the training procedure places the boundary to separate the labeled points it is given, and it has no way to distinguish a record the attacker chose from a record that arrived on its own.

## Page 31

The fourth retraining leaves the left end of the boundary well below where it started, and the shift now covers a band of feature space that the original model assigned to the filled class. The stars themselves did not move. The attacker gained the shift by inserting five records once and letting the retraining schedule do the rest.

## Page 32

The end state is a boundary whose left side has dropped by roughly a third of a unit on the feature scale, and the band between the original curve and the current one is now classified as the open circle class. If the filled class is malicious and the open circle class is benign, a malicious record placed in that band passes as benign. The sequence is the boiling frog attack: a series of shifts, each small enough to pass as drift, whose sum is a boundary the attacker chose. The name comes from the folk claim that a frog in slowly heated water does not jump out.

## Page 33

A poisoning attacker needs feedback, and the defenses restrict the retraining loop. The feedback is the model's predictions or probabilities: without seeing how the model responds after each retraining, the attacker cannot tell whether the injected records moved the boundary or by how much.

Three defenses follow from the mechanism. Longer periods between retraining: each retraining is one step of the attack, so fewer retrainings per month means fewer steps and more time to review the data before it is used. Periodic analysis of the retraining data: the injected records cluster near the boundary and shift the feature distribution, and a comparison of each retraining batch against the previous ones exposes the gradual movement that no single batch reveals. Avoiding real time online learning unless the application requires it: a model that trains on each input as it arrives gives the attacker an unlimited number of steps and the defender no review window at all.

## Page 34

The four readings are the sources behind the evasion demonstrations. Kurakin, Goodfellow and Bengio (2016): adversarial images printed on paper and photographed with a phone camera still fool the classifier, the source of the washer figure. Athalye, Engstrom, Ilyas and Kwok (2017): a 3D printed turtle that a classifier labels as a rifle from most viewing angles, produced by optimizing the texture over a distribution of rotations, lighting and camera positions. Evtimov et al. (2017): the stop sign stickers, published in final form as Eykholt et al. (2018). Xu, Qi and Evans (2016): a genetic search that mutates malicious PDF files, keeping each variant that still executes its payload and scores lower on the detector, until the PDFrate and Hidost malware classifiers pass it. The last paper is the one closest to security practice: the target is a malware detector, and the constraint is that the file must remain functional malware.

## Page 35

The survey of attack families ends here. The rest of the module treats the evasion methods one at a time and then their implementation in code.

## Page 36

The remainder of the module is the technical detail behind the evasion attacks surveyed so far.

## Page 37

This part covers model evasion methods, grouped by what the attacker can observe of the model: its gradients, its output scores, or its output labels only.

## Page 38

Evasion methods are classified by the access they need. Gradient based attacks, white box: the attacker computes the gradient of the model's loss with respect to the input, which requires the model's parameters. Score based attacks, black box with scores: the attacker sees the probability or confidence the model returns for each class and estimates the gradient from how those scores change. Decision based attacks, labels only: the attacker sees only the predicted class and locates the boundary by testing which inputs flip it. Physical world attacks: the perturbation is realized as a printed object or a modification to a physical one, and it has to survive the camera, distance, angle and lighting between the object and the model. Each step down the list needs less access to the model and more queries against it.

## Page 39

This part covers gradient based attacks, the white box evasion methods.

## Page 40

A gradient based attack runs training's own mechanism against the model. Training computes the gradient of the loss with respect to the weights and moves the weights in the direction that reduces error. The attack computes the gradient of the loss with respect to the input and moves the input in the direction that increases error. Both operations need the same thing: the model's parameters and a differentiable path from input to loss.

That requirement fixes which models are exposed. Neural networks, logistic regression, other linear classifiers and support vector machines all compute a differentiable function of the input. A tree based model does not: its output is constant within each region and jumps at the split thresholds, so the gradient with respect to the input is zero almost everywhere and undefined at the splits. Worksheet 7.1 attacks a decision tree with a different method, ART's DecisionTreeAttack, which searches the tree's split structure for the nearest leaf of the target class.

## Page 41

The decision boundary is the surface in input space that separates one class from another, and in a trained model it passes close to real data points. The gradient of the loss at a data point is the direction of steepest increase in error, which locally is the shortest route to that boundary. A perturbation along that direction, sized to the distance, moves the input across the boundary into the wrong class. The change in each input feature is too small for a person to see, and the model's output changes class.

## Page 42

Crafting a gradient based adversarial example is four steps. Compute the gradient direction: for each input feature, determine whether increasing or decreasing it raises the model's error, and by how much. Perturb the input: add a pattern that follows that direction. Keep it subtle: constrain the perturbation to a budget, which for images is a cap on the change to any one pixel or on the total change across the image, and for structured or text data is a change that leaves the record valid and its meaning intact. Test the model: feed the perturbed input back and confirm that the model misclassifies it, and with what confidence.

## Page 43

Three gradient based methods differ in how they spend the perturbation budget. Single step, the Fast Gradient Sign Method (Goodfellow et al., 2014): one jump of the full budget in every feature at once, fast, and the least subtle because every feature moves by the maximum allowed. Iterative, Projected Gradient Descent (Madry et al., 2017): many small steps, each followed by a projection that pulls the input back inside the budget, which finds stronger adversarial examples and defeats defenses that stop the single step version. Optimized, Carlini and Wagner (2017): an optimization over the perturbation itself that finds the smallest change that still flips the class, at the cost of far more computation.

## Page 44

One face under nine treatments shows how visible each method's perturbation is. FGSM, BIM and PGD leave a grain across the whole image that is visible at this size; BIM is the Basic Iterative Method (Kurakin et al., 2016), an iterated FGSM without PGD's random start. DeepFool (Moosavi-Dezfooli et al., 2016), C&W, and the two GAMA variants (Guided Adversarial Margin Attack, Sriramanan et al., 2020, in Frank Wolfe and PGD forms) produce images that cannot be told from the clean one at this size, because each searches for a minimal perturbation instead of spending a fixed budget on every pixel. Recon is a reconstruction of the input, included in the source figure as a reference. All nine images are adversarial or reference images for the same face; the method decides how much of the budget shows.

## Page 45

Adversarial examples work because of how the input dimensions add up. A network learns statistical cues that predict the label in the training data, and those cues are distributed across thousands of input dimensions rather than concentrated in the shapes a person uses. For a linear model, a perturbation of epsilon in every dimension, each with the sign of that dimension's weight, changes the activation by epsilon times the sum of the absolute weights, and that sum grows with the number of dimensions (Goodfellow et al., 2014). A per pixel change too small to see therefore produces a large change in the output. Human perception is tuned to shapes, edges and textures, and does not register the cues the model relies on, so the change is invisible to the person and decisive to the model.

## Page 46

The Fast Gradient Sign Method is the simplest gradient based attack and the fastest. The acronym is FGSM; the pages spell it FSGM. It computes the gradient once and takes a single step of the full budget in the direction that raises the loss most, with no iteration and no search for a smaller perturbation.

## Page 47

FGSM moves every feature by the same amount, in the direction its gradient indicates. Compute the gradient: the derivative of the loss with respect to each input feature says how sensitive the prediction is to that feature. Choose a direction: the sign of each derivative says whether raising or lowering the feature increases the error. Take the step: add epsilon to features with a positive sign and subtract epsilon from features with a negative sign. The result is an input at the maximum per feature distance from the original, and the model misclassifies it.

Using the sign and discarding the magnitude is deliberate. Under a budget that caps the change to any one feature, the perturbation that raises a linear model's output the most is the one that moves every feature by the full cap in its own direction, and the sign of the gradient is exactly that perturbation.

## Page 48

FGSM's advantages are cost and reach. Speed: one gradient computation, which is one backward pass through the model. Effectiveness: Goodfellow et al. (2014) reported that FGSM with an epsilon of 0.25 caused a maxout network to misclassify 89.4 percent of adversarial examples on MNIST.

Its drawbacks follow from being a single step. Benchmark status: FGSM is the standard introductory attack and the first test applied to a proposed defense, so a defense that stops it has passed the weakest test. Defensibility: training on FGSM examples, and defenses that flatten the gradient at the data point, stop the single step while iterative methods such as PGD still get through. Access: like every gradient based attack, it needs the model's parameters, so it is white box.

## Page 49

Projected Gradient Descent is FGSM repeated many times under a constraint. Instead of one step of the full budget, PGD takes many small steps in the gradient direction, recomputing the gradient after each. After each step it projects the perturbed input back into the valid region, the set of inputs within epsilon of the original, so the accumulated perturbation stays within the budget. Repeating the step and the projection lets the attack follow the curved loss surface that a single straight step misses, which is why PGD examples fool the model more reliably at the same epsilon.

## Page 50

Madry et al. (2017) defined PGD with three parameters: the budget epsilon, the step size, and the number of iterations. The valid region depends on the norm chosen for the budget. Under the L infinity norm, the region is a box: after each step, every feature's perturbation is clipped to the range from minus epsilon to plus epsilon. Under the L2 norm, the region is a sphere: the perturbation vector is rescaled to length epsilon whenever it grows longer. PGD also starts from a random point inside the region rather than from the original input, so repeated runs explore different paths and one run's failure does not mean the model is robust at that point. This page repeats the previous one.

FGSM is one shove toward the boundary and PGD is many checked steps. The shove is a single move of the full budget along the gradient at the original input. Each PGD step moves a fraction of the budget along the gradient at the current point, and the projection after it is the check: any part of the accumulated perturbation that has left the region is pulled back inside, so the input stays within epsilon of the original through every iteration and crosses the decision boundary from inside the budget.

## Page 51

PGD is a loop of six steps. Start with the original input. Compute the gradient of the loss with respect to the input, which is the direction of greatest sensitivity at the current point. Take a small step in that direction. Check the constraint: if the accumulated perturbation exceeds the budget, pull it back inside the allowed range. Repeat the gradient, step and check for a fixed number of iterations. End with an adversarial input that a person cannot distinguish from the original and that the model classifies wrongly. The code example on page 84 runs this loop with a budget of 0.2, a step of 0.01, and 40 iterations.

## Page 52

PGD's advantages come from iteration and its disadvantages from the cost of iterating. Strength: the iterations search the whole region within the budget instead of one corner of it, so PGD finds adversarial examples at an epsilon where FGSM fails. Benchmark status: Madry et al. proposed PGD as the attack a robust model must withstand, and PGD accuracy is the standard robustness figure reported for a defense. Resistance to defenses: a defense that stops FGSM by distorting the gradient at the data point leaves the rest of the region unprotected, and PGD's later steps find it. Flexibility: the projection step accepts any budget shape, a per pixel range, an L2 distance, or another norm.

The costs scale with the iteration count. Speed: each iteration is a gradient computation, so forty iterations cost forty times what FGSM costs. Queries: PGD needs gradients, so in a black box setting each of those gradients must be estimated from queries, which multiplies the query count into the thousands. Detectability: a black box PGD run sends the target a long series of near identical inputs. The page misspells FGSM as FSGM and "than" as "that".

## Page 53

The Carlini and Wagner attack (2017) treats the adversarial example as the solution to an optimization problem: find the smallest change to the input that makes the model output a chosen wrong class. FGSM takes a step of fixed size and PGD takes many, and both accept whatever perturbation the budget allows. C&W minimizes the perturbation itself, with the misclassification as a constraint, so its output is the smallest change the optimizer can find. The paper's result was that this formulation defeated defensive distillation, a defense that had stopped the earlier attacks, with perturbations smaller than those attacks produced.

## Page 54

C&W minimizes a sum of two terms by gradient descent on the perturbation. Start from the original input. The first term is the distance between the perturbed and original input, by default the L2 distance. The second term is a penalty that is positive while the model's score for the target class trails its score for the true class, and zero once the target class wins by a chosen margin. A constant weights the two terms, and the attack finds it by binary search: too small and the penalty does not reach zero, too large and the perturbation grows past what is needed. The optimizer refines the perturbation, typically with Adam over hundreds or thousands of iterations, until the penalty is zero and the distance has stopped shrinking. Steps four and five on the page are the two terms of step three, and step six is the descent that balances them.

## Page 55

C&W's advantages are precision and reach. Subtlety: its perturbations are the smallest of the three gradient methods at the same success rate, and remain hard to see when magnified. Effectiveness: it bypasses defenses that stop FGSM and basic PGD, defensive distillation among them. Targeting: the penalty term names a target class, so the attack can force a specific wrong answer rather than any wrong answer. Benchmark status: a proposed defense is expected to report its results against C&W, and red team assessments, authorized attacks run against a deployed model to measure its exposure, still include it, because a model that withstands its perturbations has withstood the smallest the gradient methods produce. Domain reach: the formulation applies to any differentiable input, and Carlini and Wagner (2018) used it to make speech recognition transcribe chosen phrases from audio.

Its disadvantages are cost and access. Computation: iterative optimization with an outer binary search, slower than FGSM or PGD per example. Access: it needs gradients and logits, the model's raw class scores before the softmax, so it is white box. Tuning: the step size, the weighting constant and the confidence margin all affect whether it succeeds. Timing: it is too slow for an attack that must produce an adversarial input as the system runs.

## Page 56

This part covers score based attacks, the black box methods that work from the probabilities the model returns.

## Page 57

A score based attack replaces the gradient with an estimate built from the model's output scores. The attacker has no parameters and so no gradients, but sees the probability or confidence the model returns for each class. The estimate comes from probing: change the input by a small amount, observe how the scores move, and treat the ratio of score change to input change as the derivative in that direction. Assembled across directions, those ratios approximate the gradient, and the attack then proceeds as a gradient attack would. A commercial image API is one source of those scores: it returns a score per class, for example 92 percent cat, 7 percent dog and 1 percent raccoon, and a small edit to the image that moves the cat score down and the dog score up is the signal the attacker reads.

## Page 58

A score based attack is a loop of five steps, each of which costs queries. Query the model with the input to get baseline scores. Perturb features by a small amount, a pixel, a word, or a tabular field. Record the output scores for each perturbation. Infer sensitivity: the features whose perturbation moved the scores most are the ones the model depends on. Craft the adversarial input iteratively, using the inferred sensitivities as the gradient estimate. Every perturbation in step two is one query to the model, so the total cost is the number of features probed multiplied by the number of iterations, and that product is what separates the two methods that follow.

## Page 59

Two score based methods differ in how many queries they spend per gradient estimate. Zeroth Order Optimization, or ZOO (Chen et al., 2017): estimates the gradient by finite differences, probing each feature one at a time, which gives an accurate estimate at a query cost that grows with the number of features and becomes prohibitive for images. Natural Evolution Strategies, or NES (Ilyas et al., 2018): samples a batch of random directions, queries the model along each, and aggregates the score changes into a gradient estimate, which trades some accuracy for a query count that is independent of the number of features. NES is the practical choice against an API.

## Page 60

Score based attacks match what an attacker facing a deployed API actually has. Setting: they work black box, with no model internals. Targets: commercial image recognition and sentiment analysis APIs that return probabilities, which is all these attacks need. Domains: images, text and malware, since the method only needs a score that changes when the input changes. Realism: an external attacker has the API and its scores, and the attacks that assume gradients do not describe that attacker.

Their costs are queries and the traces queries leave. Query volume: thousands of API calls per adversarial example on small inputs, and millions on images for ZOO. Speed: the query volume rules out attacks that must finish as the system runs. Detectability: the query stream is visible to the API's rate limiting, logging and anomaly detection, and consists of near duplicate inputs. Dependence on scores: if the API returns only the class label, there is no score to difference and these methods fail.

## Page 61

ZOO is a score based attack for the setting where the attacker cannot see the model's architecture or parameters, cannot compute gradients, and can query the model for confidence scores or probabilities. Zeroth order describes an optimization method that uses only the values of the function being optimized and no derivatives; first order methods such as gradient descent use the derivatives. The problem ZOO solves is how to run an attack shaped like FGSM or PGD, both of which consume a gradient, when the gradient is unavailable.

## Page 62

ZOO builds the gradient one coordinate at a time from score differences. Take the original input. Nudge one feature by a small amount, for example brighten one pixel. Query the model and compare the new scores to the original scores. The size and sign of the change is that feature's sensitivity, an estimate of the partial derivative of the score with respect to that feature. Repeating the nudge for many features fills in an approximate gradient vector without any access to the model's internals. The paper's estimator uses a symmetric difference, one query with the feature raised and one with it lowered, so each coordinate costs two queries. An ImageNet input of 299 by 299 pixels in three channels has roughly 268 thousand coordinates, so one full gradient estimate is over half a million queries.

## Page 63

ZOO's loop is coordinate descent driven by queries. Pick a feature: a pixel, one dimension of a word embedding, or a tabular value. Apply a small perturbation and query the model again. Record the score change and whether it moved the model toward a wrong class. Repeat for every feature, or for a subset chosen at random or by importance when the input is large. Combine the results into an estimated gradient and use it as FGSM or PGD would. In practice ZOO updates a batch of coordinates per iteration rather than the whole input, so each iteration is cheap and the attack takes many iterations.

## Page 64

ZOO's advantages are generality. Access: query access and scores, no internals. Model type: any model that returns scores, since the method uses only score differences. Attack form: once the gradient estimate exists, the update rule is the same as a gradient attack's.

Its disadvantages are all query count. ZOO probes the way a doctor with no imaging presses each point of the body in turn and notes the reaction: one coordinate, one press, one query, and the map of where the model is sensitive is complete only when every coordinate has been pressed. Volume: probing every feature of a high dimensional input costs millions of queries per adversarial example. Speed: the iterative optimization runs orders of magnitude longer than a white box attack on the same model. Detectability: that query volume, sent as near identical inputs, is what rate limits and monitoring are built to notice. Scale: against a large modern network the attack is impractical without the paper's reductions, which attack a lower resolution version of the input and sample coordinates by importance.

## Page 65

NES is a score based black box attack designed to need far fewer queries than ZOO. Probing features one at a time costs a query per feature per iteration, which for images and text is the dominant cost. NES instead samples whole directions in input space, random perturbations that touch every feature at once, and reads how the model's scores change along each sampled direction. Aggregating those changes gives a usable gradient estimate from a batch of queries whose size the attacker chooses, independent of how many features the input has.

## Page 66

NES adapts an idea from evolutionary algorithms: evaluate a population and move toward the members that scored best. Generate a population of random perturbations, noise vectors drawn from a Gaussian distribution. Add each to the input and query the model. Score each perturbation by how much it moves the model toward misclassification. Aggregate: the weighted average of the noise vectors, each weighted by the score it produced, points in the direction that consistently raises the wrong class. That average is the gradient estimate, and the attack steps along it as a gradient attack would. Ilyas et al. sample each noise vector together with its negative, which cancels the bias in the average and halves the noise in the estimate for the same query count.

## Page 67

NES runs a batch of queries per update. Start with a clean input. Sample a batch of random noise vectors from a Gaussian. Perturb the input with each vector and query the model. Record how the scores shift for each perturbation. Aggregate: perturbations that push the scores toward the wrong class, weighted by how far, average into the approximate gradient direction. Update the input along that direction, project back inside the budget, and repeat until the model's label changes. The query count per update is the batch size, on the order of fifty to a hundred, where ZOO's is two per coordinate. NES reads the slope of a hill by tossing marbles in random directions and averaging which way they roll: each noise vector is one marble, the score change along it is how far it rolled, and the score weighted average of the vectors is the downhill direction, obtained without the per coordinate measurement ZOO makes.

## Page 68

NES's advantages are query efficiency at scale. Efficiency: far fewer queries than ZOO for the same input. Dimensionality: it works on large images where ZOO's per feature probing is infeasible. Access: score access only, no gradients. API suitability: it runs under query budgets that would rule ZOO out, and Ilyas et al. demonstrated it against a commercial image classification API.

Its disadvantages follow from estimation. Speed: each update still needs a batch of queries, where a white box attack needs one gradient computation. Precision: the estimate is noisy, and with a small batch the noise can point the update in a poor direction. Dependence on scores: an API that returns only class labels gives NES nothing to weight the population by, and the attack has to change to a decision based method.

## Page 69

This part covers decision based methods, the strictest black box case: the attacker can query the model, and the only return is the final class label, with no probabilities and no scores. The label says whether the model made the call the attacker wanted and nothing about how close the call was, so the attacks in this part spend queries to recover the closeness a score reports directly.

## Page 70

With neither gradients nor scores, a decision based attack locates the decision boundary directly. The label is a yes or no answer to one question, which side of the boundary is this input on, and repeated answers locate the boundary the way repeated comparisons locate a threshold. Start with an input the model already misclassifies, which can look nothing like the original. Iteratively move it toward the original input, shrinking the perturbation, and after each move confirm that the label is still wrong. The process converges on a minimal adversarial perturbation with no more information than a label per query.

## Page 71

Two decision based attacks differ in how they move along the boundary. Boundary Attack (Brendel, Rauber and Bethge, 2018): start from a heavily perturbed input the model misclassifies, such as noise, and reduce the perturbation in small random steps, keeping each step only if the label stays wrong. It is simple and slow: a random walk along the boundary that rejects most of its proposals. HopSkipJump (Chen, Jordan and Wainwright, 2020): a more efficient method that binary searches along the line between the adversarial and original inputs to land on the boundary, then estimates the boundary's local direction by sampling labels at random points around that spot and uses the estimate to take a directed step toward the original. The directed step replaces the random walk, which is why it needs fewer queries.

## Page 72

Decision based attacks work in the most restrictive setting a defender can impose. Hiding probabilities and returning only class labels removes the score based attacks and raises the query count, and the boundary can still be located from labels alone. The result is a demonstration that withholding output information reduces what an attacker learns per query without closing the attack.

## Page 73

Decision based attacks trade information for queries. Access: predicted labels only, the true black box case. Applicability: APIs that reveal no confidence score. Output quality: the adversarial examples they converge to are as subtle as those from methods with more information, because the stopping condition is the same, a minimal perturbation that keeps the wrong label.

The price is paid in queries and precision. Volume: thousands of queries to converge on one adversarial example. Speed: slower than gradient or score based methods on the same model. Practicality: an attack that needs thousands of queries fails against a rate limit or a deadline. Noise: every estimate of the boundary's shape comes from labels, so each step is less precise than a step guided by a gradient or a score.

Both costs come from the label being the only signal. The attacker feels for the edge of a cliff blindfolded. The slope underfoot is the gradient and is not felt. An echo of the distance to the edge is the score and is not heard. The only signal is whether the last step went over, which is the label. Mapping the edge means stepping back and forth across it at one query per step, which is why convergence costs thousands of queries and why each estimate of the edge's direction is coarse.

## Page 74

This part covers the Boundary Attack, the original decision based method.

## Page 75

The Boundary Attack assumes the attacker has final labels only, with no scores and no gradients. It begins from an input the model already misclassifies, for example a noise image that the model assigns to some class other than the target's. From there it walks back toward the original input, reducing the perturbation a little at each step while keeping the label wrong. Over many steps the walk converges on an adversarial example close to the original that the model still misclassifies. Each step in the paper's algorithm has two parts: a random move along the sphere of inputs at the current distance from the original, followed by a small move toward the original, and the step sizes for both adapt to the acceptance rate of the proposals.

## Page 76

The Boundary Attack is initialization, refinement and convergence. Initialization: find any input the model misclassifies, which need not resemble the original data. Iterative refinement: move the input slightly closer to the original sample, query the model, and if the label is still wrong keep the new input, otherwise discard it and propose a different move. Convergence: repeat until the adversarial input is nearly indistinguishable from the original while the model remains wrong. The acceptance rate steers the attack: a run of rejections shrinks the step, a run of acceptances grows it, and each proposal costs one query whether it is kept or not.

## Page 77

The Boundary Attack's advantages are its assumptions. Access: class labels only. Domains: images, audio and tabular data, since the method only needs a distance measure and a label oracle. Output: adversarial examples as subtle as the query budget allows. Simplicity: the algorithm is a rejection sampling loop and takes a page to implement.

Its disadvantages are the cost of random search. Queries: thousands to millions per adversarial example, because most proposals are rejected and each proposal is a query. Speed: it cannot run inside the time limit of a live attack. Efficiency: a random move along the boundary has a high chance of leaving the adversarial region, and every rejection is a wasted query. Obsolescence: HopSkipJump and later decision based methods reach the same result in a fraction of the queries. The page title reads How it Works and the content is the pros and cons; the mechanism is a retreat from inside enemy territory. The attack starts at an input the model already misclassifies, well inside the wrong class, and steps back toward the original input, the city gate, keeping each step that ends on the wrong side of the boundary and discarding each step the model classifies correctly, until the input stands as near the original as the boundary allows while the model still names the wrong class.

## Page 78

This part covers HopSkipJump, the decision based attack that Worksheet 7.1 runs.

## Page 79

HopSkipJump (Chen, Jordan and Wainwright, 2020) is a decision based attack built to reach the boundary in far fewer queries than the Boundary Attack. It has the same requirement, class labels only, with no scores and no gradients. Where the Boundary Attack walks back toward the original in small random steps, HopSkipJump binary searches straight to the boundary along the line between the adversarial and original inputs, then samples labels around the boundary point to estimate which way the boundary faces and takes a directed step. Replacing the random walk with a search and an estimate is what cuts the query count.

## Page 80

HopSkipJump is a loop of a search and an estimate. Initialization: any input the model misclassifies. Binary search: on the straight line from the original input to the adversarial input, the label changes once, so bisection finds the crossing point; every query halves the remaining interval, and ten queries locate the boundary to about a thousandth of the line's length. Boundary estimation: at the crossing point, sample random small perturbations, query the label for each, and average the perturbation vectors signed by which side each landed on; the average estimates the direction perpendicular to the boundary. Update: step along that direction, which is the direction in which the adversarial region extends, then binary search back to the boundary at a point closer to the original. Iterate: each round lands on the boundary nearer to the original than the last, until the adversarial input is nearly indistinguishable from it.

## Page 81

HopSkipJump's advantages make it the default decision based attack. Access: predicted class labels only. Query efficiency: far fewer queries than the Boundary Attack for the same perturbation size, because bisection along the line from the adversarial input to the original lands on the boundary in a known number of queries, each halving the interval, where the Boundary Attack's walk back spends a query on every random step and its count grows with the rejection rate. Quality: the examples it converges to are as small as those from gradient methods on the same models in the authors' evaluation. Adoption: it is implemented in ART and in Foolbox and is the decision based baseline in the research literature.

Its disadvantages remain those of the setting. Speed: slower than white box and score based attacks, which get more information per query. Query cost: still high against a very large model or an API with a strict rate limit. Complexity: the search, estimation and step size logic is harder to implement correctly than the Boundary Attack's loop. Continuity: the binary search and the perturbation sampling assume the input space is continuous, so it fits images and audio and does not apply directly to text, where inputs are discrete tokens. Worksheet 7.1 runs it against the domain generation detector's numeric feature vectors, which are continuous.

## Page 82

This part covers the Adversarial Robustness Toolbox and the code that runs the attacks from this module.

## Page 83

The Adversarial Robustness Toolbox, ART, is a Python library of implemented attacks and defenses for machine learning models. IBM Research created it and donated it to the Linux Foundation's LF AI and Data project in 2020, which is why the repository lives under the Trusted-AI organization. The comparison to Metasploit is about structure: a catalog of ready to run attacks that all operate through one interface, so the work of an attack is choosing and configuring it rather than implementing it.

Its coverage is broad in three directions. Frameworks: scikit-learn, PyTorch, TensorFlow and Keras, XGBoost, LightGBM and CatBoost among others, each wrapped by an estimator class. Attack families: evasion, poisoning, extraction and inference, the four families this module surveyed, plus defenses that preprocess inputs, train adversarially or detect adversarial examples. Access levels: white box attacks that use the wrapped model's gradients and black box attacks that use only its predictions. Model types run from a support vector machine to a deep network.

## Page 84

Every ART attack is the same three calls around an estimator. Wrap the model in an estimator, such as PyTorchClassifier, SklearnClassifier or KerasClassifier: the estimator is the adapter between the framework and the attack, and it exposes the model's gradients, loss and prediction through one interface. Pick an attack class from the evasion or poisoning module and set its parameters, which for evasion are the budget epsilon, the norm the budget is measured in, and for black box attacks the maximum number of queries. Call the attack's generate method on the inputs to produce the adversarial examples; the call is the same for every attack. Evaluate by comparing the model's accuracy on the clean inputs with its accuracy on the adversarial ones, which is the attack's success rate.

The estimator sets the access level. A framework estimator gives an attack gradients, so white box attacks run against it. A black box estimator gives an attack predictions only, and an attack that needs gradients cannot use it. The attack code does not change between the two cases.

## Page 85

The white box example wraps a PyTorch MNIST classifier and runs FGSM and PGD against it. The estimator takes the trained model, its loss function, the input shape of one channel by 28 by 28 pixels, and ten classes, and through the loss it can compute the gradient of the loss with respect to any input. FastGradientMethod takes the estimator and a budget of 0.2. ProjectedGradientDescent takes the same budget with a step of 0.01 and 40 iterations, so its steps can traverse the whole budget twice over. Each attack's generate call turns the test images into adversarial images. The two print lines compare the first five predicted classes on the clean images with the first five on the adversarial ones.

A budget of 0.2 on a zero to one pixel scale is one fifth of the intensity range, large enough to see on an MNIST digit. Worksheet 7.2 attacks a CIFAR-10 classifier with budgets from 2 to 12 on the 255 scale, which is under 5 percent. The second assignment to x_adv overwrites the FGSM examples before they are evaluated, so the printed adversarial predictions are PGD's.

## Page 86

The black box example replaces the framework estimator with a function. BlackBoxClassifier takes a predict function, the input shape and the class count; the function receives a batch of inputs and returns their labels in one hot form, and it can call a local model or a remote API. Nothing else about the model is available to the attacks. HopSkipJump takes the estimator, targeted set to false so any wrong class counts as success, 50 iterations, and a cap of 1,000 model evaluations per iteration for boundary estimation, which caps the boundary estimation at fifty thousand queries per input. BoundaryAttack takes the estimator, the same untargeted setting, and 1,000 iterations. Both produce adversarial examples with the same generate call as the white box attacks. As on the previous page, the second assignment to x_adv discards HopSkipJump's output before anything reads it.

## Page 87

A backdoor is a poisoning attack that installs a trigger. PoisoningAttackBackdoor takes a perturbation function, here add_pattern_bd, which stamps a fixed pixel pattern onto an image. The target is the one hot vector for class 7. The poison call stamps every training image and relabels each as class 7, and broadcast set to true applies that single label to all of them. The example then appends 300 stamped images to the training set, half a percent of MNIST's 60,000, and retrains the victim model on the mixture.

The trained model learns the pattern as a feature of class 7. Clean inputs are classified normally, so the model passes validation on clean data, which is the check in the attack surface table. Any input with the pattern stamped on it is classified as 7 regardless of its content, which the final print line demonstrates on stamped test images. The attack is BadNets (Gu, Dolan-Gavitt and Garg, 2017), and it applies to any model whose training data the attacker can add to.

## Page 88

Four other frameworks automate attacks on models or measure a model's vulnerability. Counterfit (Microsoft): a command line assessment tool that drives ART and TextAttack against a target from a scripted session; the page spells it Counterfeit. TextAttack (QData group, University of Virginia): adversarial examples for natural language models, where the perturbations are word substitutions and character edits rather than pixel changes. CleverHans: created by Ian Goodfellow and Nicolas Papernot, hosted under the TensorFlow organization on GitHub as a separate library; its current version supports JAX, PyTorch and TensorFlow 2. Deep-pwning (Clarence Chio, 2016): presented as Metasploit for machine learning, and unmaintained. The asterisk marks projects that may no longer be supported or developed, which applies to CleverHans and Deep-pwning.

## Page 89

Worksheet 7.1 runs two attacks from this module against the domain generation detector trained earlier in the course. The first is white box: wrap the saved decision tree in ART's SklearnClassifier, run DecisionTreeAttack with every target set to the legitimate class, and compare a classification report on the adversarial feature vectors with the baseline report on the clean ones. The second is black box: write a predict function around the tree, wrap it in BlackBoxClassifier with the feature count and two classes, and run HopSkipJump with the same goal. The result in both cases is a set of feature vectors that the detector classifies as legitimate, produced with two different levels of access to the model.
