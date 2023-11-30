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
logging.basicConfig(level=logging.DEBUG)

# %% debugging
FLASK_ENV = os.environ.get('FLASK_ENV')

def log_debugg(text):
    if FLASK_ENV == 'development':
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
    log_debugg("validating data")
    log_debugg(f"request: {request}")
    # validate parameters
    params = [
        "location", "distance_sensitivity", "preferences", "is_pro",
        "max_allowed_classes_per_class", "num_classes_per_month"
    ]
    for param in params:
        if param not in request.keys():
            raise Exception(f'{param} not in request')
    # validate location
    params_location = ["longitude", "latitude"]
    for param in params_location:
        if param not in request['location']:
            raise Exception(f'{param} not in request')
    # validate preferences
    params_preferences = ["love_activities", "hate_activities"]
    for param in params_preferences:
        if param not in request['preferences']:
            raise Exception(f'{param} not in request')
    # validate distance sensitivity
    if request['distance_sensitivity'] not in ['low', 'medium', 'high']:
        raise Exception('distance_sensitivity not in ["low", "medium", "high"]')
    # validate is_pro
    if request['is_pro'] not in [0, 1]:
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
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'request is None'})

    # parse request
    try:
        log_debugg("parsing request")
        # validate data
        log_debugg("validating data")
        validate_data(data)
        # get output
        log_debugg("getting output")
        output = fitpass_optimization(data, WEIGHTS)
        # return output
        log_debugg("returning output")
        return jsonify(output), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Aquí capturas los datos del formulario inicial, como el código postal
#         # y los pasas a la siguiente pantalla (filtros.html)
#         codigo_postal = request.form['cp']
#         return render_template('filtros.html', codigo_postal=codigo_postal)
#     return render_template('index.html')

# @app.route('/filtros', methods=['POST'])
# def filtros():
#     # Procesa los datos del formulario de filtros y pasa a la pantalla de recomendaciones
#     # Aquí debes capturar los datos de los filtros
#     tipo_estudios_preferidos = request.form['preferred-studios']
#     # ... otros campos del formulario ...
#     return render_template('recomendaciones.html', filtros=filtros)

# @app.route('/recomendaciones', methods=['POST'])
# def recomendaciones():
#     # Extract form data
#     latitude = request.form['latitude']
#     longitude = request.form['longitude']
#     tipo_preferido = request.form['preferred-studios']
#     tipo_no_gustado = request.form['disliked-studios']
#     es_fitpass_pro = request.form['fitpass-pro'] == 'yes'
#     frecuencia_visitas = request.form['visit-frequency']

#     # Llama a tu función del modelo aquí
#     recomendaciones = obtener_recomendaciones_con_filtro(latitude, longitude, tipo_preferido, tipo_no_gustado, es_fitpass_pro, frecuencia_visitas)
    
#     # Renderiza la página de recomendaciones con los resultados del modelo
#     return render_template('recomendaciones.html', recomendaciones=recomendaciones)


# %% main
if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') != 'development':
        log_debugg("Running in production mode...")
        app.run(host='0.0.0.0', port=8080) # production
    else:
        log_debugg("Running in development mode...")
        app.run(host='0.0.0.0', debug=True, port=8080) # development / debugging