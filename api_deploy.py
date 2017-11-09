from __future__ import print_function # In python 2.7
import os
import subprocess
import json
import re
import copy
from flask import Flask, request, jsonify
from inspect import getmembers, ismethod
import numpy as np
import pandas as pd
import math
import cPickle
import os
import pickle
import xgboost as xgb
import sys

def predict(params):
    model_filename = os.path.join('model.dat')
    # load model from file
    loaded_model = pickle.load(open(model_filename, "rb"))
    X = params 
    x_test = pd.DataFrame(X)
    x_test.sort_index(axis=1,inplace=True)
    x_test = xgb.DMatrix(x_test)
    y_pred = loaded_model.predict(x_test)
    prob = y_pred[0]
    y_pred[y_pred > 0.5] = 1
    y_pred[y_pred <= 0.5] = 0
    return {'class':int(y_pred[0]),'prob':float(prob)}

post_functions_list = [add, predict]
get_functions_list = [test]
app = Flask(__name__)

@app.route('/<func_name>', methods=['POST'])
def api_post(func_name):
    for function in post_functions_list:
        if function.__name__ == func_name:
            try:
                json_req_data = request.get_json()
                if json_req_data:
                    res = function(json_req_data)
                else:
		    return jsonify({"error": "error in receiving the json input"})
            except Exception as e:
                return jsonify({"error": "error while running the function"})
            return jsonify({"result": res})
    output_string = 'function: %s not found' % func_name
    return jsonify({"error": output_string})

@app.route('/<func_name>', methods=['GET'])
def api_get(func_name):
    for function in get_functions_list:
        if function.__name__ == func_name:
            try:
                res = function()
            except Exception as e:
                return jsonify({"error": "error while running the function"})
            return jsonify({"result": res})
    output_string = 'function: %s not found' % func_name
    return jsonify({"error": output_string})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
