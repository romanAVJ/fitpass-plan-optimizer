#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 18:09:01 2023

@author: ravj

Flask app for post request for fitpass pulp optimization
"""
# %% import
from flask import Flask, request, jsonify
import json
import os
import logging

from fitpass import fitpass_optimization

# %% debugging
FLASK_ENV = os.environ.get('FLASK_ENV')

def log_debugg(text):
    logging.debug(text)

# %% parameters
MODEL_NAME = 'fitpass class optimization'
VERSION = '1.0'
WEIGHTS = {
        'distance': 0.6,
        'preference': 0.3,
        'activity': 0.075,
        'class': 0.025
    }

# %% functions
def validate_data(request):
    # validate headers
    log_debugg("reading headers")
    log_debugg(request.headers)
    if 'Content-Type' not in request.headers:
        raise Exception('Content-Type not in headers')
    
    # validate content type
    log_debugg("validating content type")
    if request.headers['Content-Type'] != 'application/json':
        raise Exception('Content-Type not application/json')
    # validate parameters
    params = [
        "location", "distance_sensitivity", "preferences", "is_pro",
        "max_allowed_classes_per_class", "num_classes_per_month"
    ]
    for param in params:
        if param not in request.json:
            raise Exception(f'{param} not in request')
    # validate location
    params_location = ["longitude", "latitude"]
    for param in params_location:
        if param not in request.json['location']:
            raise Exception(f'{param} not in request')
    # validate preferences
    params_preferences = ["love_activities", "hate_activities"]
    for param in params_preferences:
        if param not in request.json['preferences']:
            raise Exception(f'{param} not in request')
    # validate distance sensitivity
    if request.json['distance_sensitivity'] not in ['low', 'medium', 'high']:
        raise Exception('distance_sensitivity not in ["low", "medium", "high"]')
    # validate is_pro
    if request.json['is_pro'] not in [0, 1]:
        raise Exception('is_pro not in [0, 1]')

# %% app
# create app
app = Flask(__name__)

# info endpoint
@app.route('/info', methods=['GET'])
def info():
    # return info
    return jsonify({
        'model_name': MODEL_NAME,
        'version': VERSION,
        'weights': WEIGHTS
    })

# predict endpoint
@app.route('/predict', methods=['POST'])
def predict():
    log_debugg("predict endpoint called")
    # get request
    log_debugg("getting request")
    request_json = request.get_json()
    if request_json is None:
        return jsonify({'error': 'request is None'})

    # parse request
    try:
        log_debugg("parsing request")
        request_json = json.loads(request_json)
        # get data
        log_debugg("getting data")
        data = request_json['data']
        # validate data
        log_debugg("validating data")
        validate_data(request_json)
        # get output
        log_debugg("getting output")
        output = fitpass_optimization(data, WEIGHTS)
        # return output
        log_debugg("returning output")
        return jsonify(output), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# %% main
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080) # development / debugging
    # if os.environ.get('FLASK_ENV') != 'development':
    #     print("Running in production mode...")
    #     app.run(host='0.0.0.0', port=8080) # production
    # else:
    #     print("Running in development mode...")
    #     app.run(host='0.0.0.0', debug=True, port=8080) # development / debugging