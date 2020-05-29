from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from nltk.stem.lancaster import LancasterStemmer
import pandas as pd
import pickle
import pathlib
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.backend import set_session
import util
import constants

# get script directory
scriptDirectory = pathlib.Path(__file__).parent
global graph
global sess
# use Lancaster implementation for stemmer
stemmer = LancasterStemmer()
# load pickle data file
data = pickle.load(open(f'{scriptDirectory}/model-data.pkl', 'rb'))
vocabulary = data['vocabulary']
classes = data['classes']
# in order to load the model you need to use the session and graph variables
graph = tf.get_default_graph()
sess = tf.Session()
set_session(sess)
model = load_model(f'{scriptDirectory}/model.h5')
model._make_predict_function()

def classify(sentence, vocabulary, classes, model, stemmer, errorThreashold = 0.25):
    bag = util.getBagFromSentence(sentence, vocabulary, stemmer)
    input = pd.DataFrame([bag], dtype=float, index=['input'])
    with graph.as_default():
        set_session(sess)
        results = model.predict([input])[0]
    # filter predictions below error threshold
    results = [[i, res] for i, res in enumerate(
        results) if res > errorThreashold]
    results.sort(key=lambda x: x[1], reverse=True)
    intentsProbabilities = []
    for res in results:
        intentsProbabilities.append((classes[res[0]], str(res[1])))
    return intentsProbabilities

app = Flask(__name__)
api = Api(app)
CORS(app)

class Start(Resource):
    def get(self):
        return {'message': 'Hello World'}, 200

class Classifier(Resource):
    def post(self):
        sentence = request.json['sentence']
        intent = classify(sentence, vocabulary, classes, model, stemmer, errorThreashold=constants.ERROR_THRESHOLD)[0]
        return intent, 200

api.add_resource(Start, '/')
api.add_resource(Classifier, '/api/v1.0/classify')

if __name__ == "__main__":
    app.run(debug=False, port=5001, threaded=True)
