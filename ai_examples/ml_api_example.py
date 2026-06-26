from fastapi import FastAPI, Query
from pydantic import BaseModel
import pandas as pd
import numpy as np
import re

# You'll need a full path (not a relative path) to your data here...
DATA_HOME = "/Users/charlesgivre/Documents/CG_Consulting/gtk_cyber/ai_cyber_bootcamp/data"

from six.moves import cPickle as pickle
with open(f'{DATA_HOME}/d_common_en_words.pickle', 'rb') as f:
    d = pickle.load(f)

with open(f'{DATA_HOME}/dga_model.sav', 'rb') as model_file:
    model = pickle.load(model_file)

# For simplicity let's just copy the needed function in here again
def H_entropy(x):
    # Calculate Shannon Entropy
    prob = [float(x.count(c)) / len(x) for c in dict.fromkeys(list(x))]
    H = - sum([p * np.log2(p) for p in prob])
    return H

def firstDigitIndex(s):
    for i, c in enumerate(s):
        if c.isdigit():
            return i + 1
    return 0

def vowel_consonant_ratio(x):
    # Calculate vowel to consonant ratio
    x = x.lower()
    vowels_pattern = re.compile('([aeiou])')
    consonants_pattern = re.compile('([b-df-hj-np-tv-z])')
    vowels = re.findall(vowels_pattern, x)
    consonants = re.findall(consonants_pattern, x)
    try:
        ratio = len(vowels) / len(consonants)
    except:  # catch zero devision exception
        ratio = 0
    return ratio

def ngrams(word, n):
    # Extract all ngrams and return a regular Python list
    # Input word: can be a simple string or a list of strings
    # Input n: Can be one integer or a list of integers
    # if you want to extract multipe ngrams and have them all in one list

    l_ngrams = []
    if isinstance(word, list):
        for w in word:
            if isinstance(n, list):
                for curr_n in n:
                    ngrams = [w[i:i + curr_n] for i in range(0, len(w) - curr_n + 1)]
                    l_ngrams.extend(ngrams)
            else:
                ngrams = [w[i:i + n] for i in range(0, len(w) - n + 1)]
                l_ngrams.extend(ngrams)
    else:
        if isinstance(n, list):
            for curr_n in n:
                ngrams = [word[i:i + curr_n] for i in range(0, len(word) - curr_n + 1)]
                l_ngrams.extend(ngrams)
        else:
            ngrams = [word[i:i + n] for i in range(0, len(word) - n + 1)]
            l_ngrams.extend(ngrams)
    #     print(l_ngrams)
    return l_ngrams


def ngram_feature(domain, d, n):
    # Input is your domain string or list of domain strings
    # a dictionary object d that contains the count for most common english words
    # finally you n either as int list or simple int defining the ngram length

    # Core magic: Looks up domain ngrams in english dictionary ngrams and sums up the
    # respective english dictionary counts for the respective domain ngram
    # sum is normalized

    l_ngrams = ngrams(domain, n)
    #     print(l_ngrams)
    count_sum = 0
    for ngram in l_ngrams:
        if d[ngram]:
            count_sum += d[ngram]
    try:
        feature = count_sum / (len(domain) - n + 1)
    except:
        feature = 0
    return feature


def average_ngram_feature(l_ngram_feature):
    # input is a list of calls to ngram_feature(domain, d, n)
    # usually you would use various n values, like 1,2,3...
    return sum(l_ngram_feature) / len(l_ngram_feature)


def is_dga(domain, clf, d):
    # Function that takes new domain string, trained model 'clf' as input and
    # dictionary d of most common english words
    # returns prediction

    domain_features = np.empty([1, 6])
    # order of features is ['length', 'digits', 'entropy', 'vowel-cons', firstDigitIndex, 'ngrams']
    domain_features[0, 0] = len(domain)
    pattern = re.compile('([0-9])')
    domain_features[0, 1] = len(re.findall(pattern, domain))
    domain_features[0, 2] = H_entropy(domain)
    domain_features[0, 3] = vowel_consonant_ratio(domain)
    domain_features[0, 4] = firstDigitIndex(domain)
    domain_features[0, 5] = average_ngram_feature([ngram_feature(domain, d, 1),
                                                   ngram_feature(domain, d, 2),
                                                   ngram_feature(domain, d, 3)])

    pred = clf.predict(domain_features)
    return pred[0]



class PredictRequest(BaseModel):
    text: str  # Accept a raw string

class PredictResponse(BaseModel):
    result: str

# ---------------------------
# FastAPI App
# ---------------------------
app = FastAPI(title="String Prediction API")

@app.get("/")
def root():
    return {"message": "Model Prediction API is running"}

@app.get("/predict")
def predict(text: str = Query(..., description="The raw string input")):
    """
    Accepts a raw domain, preprocesses it, and returns model prediction.
    """
    cleaned_text = text.strip().lower()

    # Pass to model
    prediction = is_dga(cleaned_text, model, d)
    return str(prediction)
