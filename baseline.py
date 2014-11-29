import retrieve_data
import collections
import util
import data_format
import pickle
import gzip

#Turns printing on and off
DEBUG = True

def extractWordFeatures(x):
    vec = collections.Counter()
    for word in x.split():
        vec[word] = vec.get(word, 0) + 1
    return vec


def learnPredictor(trainExamples, testExamples, featureExtractor):
    weights = collections.Counter()
    def loss(w, phi, y):
        return max(1 - util.dotProduct(w, phi) * y, 0)
    
    eta = 0.1  
    numIters = 3 
    def sgradLoss(w, phi, y):
        if loss(w, phi, y) == 0:
            return collections.Counter()
        for key, value in phi.items():
            phi[key] = -1 * phi[key] * y
        return phi
    
    def predictor(x):
        if x == None:
            return -1
        if util.dotProduct(featureExtractor(x), weights) > 0:
            return 1
        else:
            return 0 

    for iteration in xrange(numIters):
        for input, output in trainExamples:
            if input == None:
                continue
            util.increment(weights, -1 * eta, sgradLoss(weights, 
                featureExtractor(input), output))
        
        if DEBUG:
            print util.evaluatePredictor(trainExamples, predictor) 
            #print util.evaluatePredictor(testExamples, predictor)
    
    return weights

sentences = []
catchphrases = []
retrieve_data.parseFiles(sentences, catchphrases)
examples = data_format.format(sentences, catchphrases)
numExamples = len(examples) * 1/2
firstPart = numExamples * 9 /10

'''outfilename = 'sentences.pklz'
output = gzip.open(outfilename, 'wb')
try:
    pickle.dump(sentences, output, -1)
finally:
    output.close()
outfilename = 'catchphrases.pklz'
output = gzip.open(outfilename, 'wb')
try:
    pickle.dump(catchphrases, output, -1)
finally:
    output.close()'''
outfilename = 'new_examples.pklz'
output = gzip.open(outfilename, 'wb')
try:
    pickle.dump(examples, output, -1)
finally:
    output.close()

#w = learnPredictor(examples[0:firstPart], examples[firstPart:], extractWordFeatures)
#output = open("weights.pkl", "wb")
#pickle.dump(w, output, -1)
#output.close()
