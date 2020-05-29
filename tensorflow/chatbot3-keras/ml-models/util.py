import numpy as np
import nltk

def cleanSentence(sentence, stemmer):
    #tokenizing
    sentenceWords = nltk.word_tokenize(sentence);
    #stemming
    sentenceWords = [stemmer.stem(word.lower()) for word in sentenceWords ]
    return sentenceWords

# function to get the bag of a sentence
def getBagFromSentence(sentence, vocabulary, stemmer):
    sentenceWords = cleanSentence(sentence, stemmer)
    bag = [0] * len(vocabulary)
    for sWord in sentenceWords:
        for index, word in enumerate(vocabulary):
            if word == sWord:
                bag[index] = 1
    
    return np.array(bag)
