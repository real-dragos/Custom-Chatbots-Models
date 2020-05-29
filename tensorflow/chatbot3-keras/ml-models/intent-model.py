from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
import numpy as np
import pandas as pd
import pickle
import random
import json
import pathlib
from pymongo import MongoClient

import constants
import util

import nltk
from nltk.stem.lancaster import LancasterStemmer
# use Lancaster implementation for stemmer
stemmer = LancasterStemmer()
# get script directory
scriptDirectory = pathlib.Path(__file__).parent

def processIntents():
    
    # import intents file
    client = MongoClient('mongodb://localhost:27017/');
    db = client.chatbotDB
    intents = db.intents.find({})
    # loop thorugh each sentence in the intents pattern
    words = [] # vocabulary - all words
    classes = [] # intents tags
    corpus = [] # (tokenized expression - intent)
    ignoreWords = ['?','.'] # ignore punctuation
    for intent in intents:
        for pattern in intent['patterns']:
            # tokenize each word in the sentence
            tokens = nltk.word_tokenize(pattern)
            words.extend(tokens)
            # add to corpus the tokens
            corpus.append((tokens, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])
    # stem and lower each word and ignore the ignoreWords
    words = [stemmer.stem(word.lower()) for word in words if word not in ignoreWords]
    # remove duplicates
    words = sorted(list(set(words)))
    # sort classes and remove duplicates
    classes = sorted(list(set(classes)))
    return corpus, classes, words;

def createTrainingData(corpus, classes, vocabulary):
    trainingData = []
    emptyOutput = [0] * len(classes)
    for document in corpus:
        bag = []
        # get tokenized words
        patternWords = document[0]
        # create baseword in attempt to represent related words
        patternWords = [stemmer.stem(word.lower()) for word in patternWords]
        for word in vocabulary:
            if word in patternWords:
                bag.append(1)
            else:
                bag.append(0)
        outputIntent = list(emptyOutput)
        outputIntent[classes.index(document[1])] = 1
        trainingData.append([bag, outputIntent])    
    # shuffle the trainingData
    random.shuffle(trainingData)
    # store trainingData in an numpy array
    trainingData = np.array(trainingData)
    trainingPatterns = list(trainingData[:,0]) # gets the bags of words
    trainingIntents = list(trainingData[:,1]) # gets the corresponding intents
    return trainingPatterns, trainingIntents

def createModel(trainingPatterns, trainingIntents):
    # 3 layers - 2 hidden layers and 3rd layer with the length of the output (number of classes)
    model = Sequential()
    model.add(Dense(constants.HIDDEN_LAYER_NEURONS[0], input_shape=(len(trainingPatterns[0]),), activation = 'relu'))
    model.add(Dropout(constants.DROPOUT))
    model.add(Dense(constants.HIDDEN_LAYER_NEURONS[1], activation='relu'))
    model.add(Dropout(constants.DROPOUT))
    model.add(Dense(len(trainingIntents[0]), activation = 'softmax'))
    # Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
    sgd = SGD(learning_rate=constants.LEARNING_RATE, decay=constants.DECAY, momentum=constants.MOMENTUM, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    model.fit(np.array(trainingPatterns), np.array(trainingIntents), epochs=constants.EPOCHS, batch_size = 5, verbose=1)
    return model;

if __name__ == "__main__":
    # generate corpus, classes and vocabulary from intents
    corpus, classes, vocabulary = processIntents()
    # create training data
    trainingPatterns, trainingIntents = createTrainingData(corpus, classes, vocabulary)
    # create model based on training data
    model = createModel(trainingPatterns, trainingIntents)

    model.save(f'{scriptDirectory}/model.h5')
    # pickle.dump(model, open(f"{scriptDirectory}/model.pkl", "wb"))
    pickle.dump({'vocabulary': vocabulary, 'classes': classes, 'trainingPatterns': trainingPatterns, 'trainingIntents': trainingIntents}, open(f'{scriptDirectory}/model-data.pkl','wb'))

