import retrieve_data
import collections
import util
import data_format
import pickle
from collections import Counter
import random

#from optparse import OptionParser
import sys
from time import time
from sklearn.svm import LinearSVC
from sklearn import cross_validation
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
#from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction import DictVectorizer
#from sklearn.feature_selection import SelectKBest, chi2
from sklearn.neighbors import NearestCentroid
from sklearn.utils.extmath import density
from sklearn import metrics

import numpy as np
from sklearn import svm 
import gzip

def formatExamples(examples):
	formattedExamples = []
	ytrainList = []
	for sentence, value in examples:
		wordList = sentence.split(' ')
		count = dict(Counter(wordList))
		formattedExamples.append(count)
		ytrainList.append(value)

	return formattedExamples, ytrainList

infilename = 'sentences.pklz'
f = gzip.open(infilename, 'rb')
try:
    sentences = pickle.load(f)
finally:
    f.close()
infilename = 'catchphrases.pklz'
f = gzip.open(infilename, 'rb')
try:
    catchphrases = pickle.load(f)
finally:
    f.close()
infilename = 'examples.pklz'
f = gzip.open(infilename, 'rb')
try:
    examples = pickle.load(f)
finally:
    f.close()

#Globals
totalExampleCount = len(examples)

allDict, yList = formatExamples(examples)
vectorizer = DictVectorizer(sparse = True)
vectorizer.fit(allDict)

X = vectorizer.transform(allDict)
y = np.asarray(yList)

#Tfidf
tfidfTransformer = TfidfTransformer()
X = tfidfTransformer.fit_transform(X, y)
#map from indices to feature names
feature_names = np.asarray(vectorizer.get_feature_names())


categories = [
		'not important',
		'important'
    ]



def predict(classifier, X):
	return classifier.predict(X)

def train(classifer, X, y):
	classifier.fit(X, y)

def benchmark(classifier, X_train, y_train, X_test, y_test):
	def testOnSet(X, y):
		#Prediction
	    pred = predict(classifier, X)


	    score = metrics.f1_score(y, pred)
	    print("f1-score:   %0.3f" % score)

	    if hasattr(classifier, 'coef_'):
	    	#TODO: Not working yet

	        #print("dimensionality: %d" % classifier.coef_.shape[1])
	        #print("density: %f" % density(classifier.coef_))

	        #if feature_names is not None:
	        #    print("top 10 keywords per class:")
	        #    for i, category in enumerate(categories):
	        #        top10 = np.argsort(classifier.coef_[i])[-10:]
	        #        print("%s: %s" % (category, " ".join(feature_names[top10])))
	        print()

	    #Precision, recall for each class
	    print("classification report:")
	    print(metrics.classification_report(y, pred, target_names=categories))
	    
	    #Number of correct positives, false pos, false neg, correct neg
	    print("confusion matrix:")
	    print(metrics.confusion_matrix(y, pred))

	    return score

	print('_' * 80)
	print("Training: ")
	print(classifier)
	classifier.fit(X_train, y_train)

	print('_' * 40)
	print("Testing on Training Set: ")
	testOnSet(X_train, y_train)
	print("Testing on Test Set: ")	
	score = testOnSet(X_test, y_test)

	classifier_descr = str(classifier).split('(')[0]
	return classifier_descr, score


def format():
	infilename = 'sentences.pklz'
	f = gzip.open(infilename, 'rb')
	try:
	    sentences = pickle.load(f)
	finally:
	    f.close()
	infilename = 'catchphrases.pklz'
	f = gzip.open(infilename, 'rb')
	try:
	    catchphrases = pickle.load(f)
	finally:
	    f.close()
	infilename = 'examples.pklz'
	f = gzip.open(infilename, 'rb')
	try:
	    examples = pickle.load(f)
	finally:
	    f.close()

	#Globals
	totalExampleCount = len(examples)

	allDict, yList = formatExamples(examples)
	vectorizer = DictVectorizer(sparse = True)
	vectorizer.fit(allDict)

	X = vectorizer.transform(allDict)
	y = np.asarray(yList)

	tfidfTransformer = TfidfTransformer()
	X = tfidfTransformer.fit_transform(X, y)

	#map from indices to feature names
	feature_names = np.asarray(vectorizer.get_feature_names())

def runTests():
	#This is run globally
	#X_train, y_train, X_test, y_test = format()

	results = []

	#10-fold cross validation - TODO: average the models learned in each fold together
	kf = cross_validation.KFold(totalExampleCount, n_folds=10)	

	for train_index, test_index in kf:
		X_train, X_test = X[train_index], X[test_index]
		y_train, y_test = y[train_index], y[test_index]

		# Train Liblinear model with L1, L2 regularization
		for penalty in ["l2", "l1"]:
		    print('=' * 80)
		    print("%s regularization" % penalty.upper())
		    classifier = LinearSVC(loss='l2', penalty=penalty, dual=False, C = 1000)
		    results.append(benchmark(classifier, X_train, y_train, X_test, y_test))

		# get the separating hyperplane using weighted classes
		classifier = svm.SVC(kernel='linear', class_weight={1: 10000})
		results.append(benchmark(classifier, X_train, y_train, X_test, y_test))

		# Train sparse Naive Bayes classifiers
		print('=' * 80)
		print("Naive Bayes")
		classifier = MultinomialNB(alpha=.01)
		results.append(benchmark(classifier, X_train, y_train, X_test, y_test))
		classifier = BernoulliNB(alpha=.01)
		results.append(benchmark(classifier, X_train, y_train, X_test, y_test))

		#Train using Nearest Centroid classifier (Rocchio Classifier)
		

runTests()