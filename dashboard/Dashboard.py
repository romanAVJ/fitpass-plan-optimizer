import dash
import dash_leaflet as dl
from dash import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import requests
from sqlalchemy import create_engine
import psycopg2
import time

import math
import os
import logging

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)

def log_debugg(text):
    if os.environ.get('DASH_ENV') == 'development':
        logging.debug(text)

logging.basicConfig(level=logging.DEBUG)

def get_db_conn():
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            log_debugg(f"Trying to connect to the PostgreSQL database... ({retries}/{max_retries})")
            host = os.environ.get('POSTGRES_HOST', 'localhost')
            user = os.environ.get('POSTGRES_USER', 'postgres')
            password = os.environ.get('POSTGRES_PASSWORD', '')
            database = os.environ.get('POSTGRES_DB', 'fitpass')
            conn = create_engine(f'postgresql://{user}:{password}@{host}/{database}')
            log_debugg("Connected to the PostgreSQL database.")
            return conn
        except psycopg2.OperationalError as e:
            log_debugg(f"Error: {e}")
            log_debugg(f"Waiting 10 seconds for PostgreSQL to be ready... ({retries}/{max_retries})")
            retries += 1
            time.sleep(10)

    log_debugg("Max retries reached. Unable to connect to the PostgreSQL database.")
    return None

# Inicializacion de la aplicacion Dash
app = dash.Dash(__name__)

# Layout de la Aplicacion
app.layout = html.Div([
    html.H1("Dashboard de Estudios de Fitness"),
    dcc.Input(id='input-name', type='text', placeholder='Tu nombre'),
    dcc.Input(id='input-lat', type='text', placeholder='Latitud'),
    dcc.Input(id='input-lon', type='text', placeholder='Longitud'),
    dcc.Checklist(
        id='input-is-pro',
        options=[{'label': 'Fitpass Pro', 'value': 'is_pro'}],
        inline=True
    ),
    dcc.Input(id='input-max-classes', type='number', placeholder='Máximo clases por clase'),
    dcc.Input(id='input-frequency', type='number', placeholder='Número de clases al mes'),
    dcc.Dropdown(
        id='distance-dropdown',
        options=[
            {'label': 'Cerca', 'value': 'low'},
            {'label': 'Medio', 'value': 'medium'},
            {'label': 'Lejano', 'value': 'high'}
        ],
        placeholder="Selecciona la distancia"
    ),
    dcc.Dropdown(
        id='activity-dropdown',
        options=[{'label': activity, 'value': activity} for activity in ['barre', 'box', 'crossfit', 'cycling', 'dance', 'ems', 'functional', 'gym', 'hiit', 'mma', 'pilates', 'pool', 'running', 'sports', 'virtual_class', 'wellness', 'yoga']],
        multi=True,
        placeholder="Selecciona actividades que te gustan"
    ),
    dcc.Dropdown(
        id='dislike-dropdown',
        options=[{'label': activity, 'value': activity} for activity in ['barre', 'box', 'crossfit', 'cycling', 'dance', 'ems', 'functional', 'gym', 'hiit', 'mma', 'pilates', 'pool', 'running', 'sports', 'virtual_class', 'wellness', 'yoga']],
        multi=True,
        placeholder="Selecciona actividades que no te gustan"
    ),
    html.Button('Buscar', id='search-button', n_clicks=0),
    dl.Map(id='map-view', style={'width': '1000px', 'height': '500px'}, center=[19.432608, -99.133209], zoom=10, children=[dl.TileLayer()]),
    dcc.Graph(id='fig_graph'),
    html.Div(id='table-view')  # Div para mostrar la tabla de resultados
])

# Funcion para calcular la distancia utilizando la formula de Haversine
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Funcion para generar la consulta SQL con las nuevas entradas
def generate_sql_query():
    query = "SELECT * FROM cdmx_studios"
    return query

# Funcion para combinar DataFrames
def combine_dataframes(df1, df2):
    combined_df = pd.concat([df1, df2], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=['gym_id'])
    return combined_df

@app.callback(
    [
        Output('map-view', 'children'),
        Output('fig_graph', 'figure'),
        Output('table-view', 'children')
    ],
    [
        Input('search-button', 'n_clicks')
    ],
    [
        State('input-name', 'value'),
        State('input-lat', 'value'),
        State('input-lon', 'value'),
        State('input-is-pro', 'value'),
        State('input-max-classes', 'value'),
        State('input-frequency', 'value'),
        State('distance-dropdown', 'value'),
        State('activity-dropdown', 'value'),
        State('dislike-dropdown', 'value')
    ]
)
def update_outputs(
    n_clicks, name, lat, lon, is_pro, max_classes, frequency, distance_option, activity, dislikes
    ):
    log_debugg("Actualizando salidas...")
    # Validar y convertir las entradas
    try:
        log_debugg(f"Latitud: {lat}, Longitud: {lon}")
        lat = float(lat) if lat else None
        lon = float(lon) if lon else None
    except ValueError:
        log_debugg("Error al convertir latitud y longitud")
        lat, lon = None, None

    if lat is not None and lon is not None:
        log_debugg(f"Latitud: {lat}, Longitud: {lon}")
        # Obtener estudios recomendados de la base de datos
        log_debugg("Obteniendo estudios recomendados de la base de datos...")
        query = generate_sql_query()
        log_debugg(f"Query: {query}")
        log_debugg("Conectando a la base de datos...")
        engine = get_db_conn()
        log_debugg("Conexión exitosa y leyendo datos")
        df_studios = pd.read_sql_query(query, engine)
        
        log_debugg(f"Estudios quereados: {df_studios}")
        log_debugg(f"type df_studios: {type(df_studios)}")
        log_debugg(f"shape df_studios: {df_studios.shape}")
        log_debugg(f"{'='*100}")

        log_debugg(f"numero de clicks: {n_clicks}")
        if n_clicks > 0 and activity:
            # Hacer la solicitud a la API
            # sample_request = {
            #     "name": name if name else "Anónimo",
            #     "location": {"latitude": lat, "longitude": lon}, 
            #     "distance_sensitivity": distance_option,
            #     "preferences": {
            #         "love_activities": activity, 
            #         "hate_activities": dislikes
            #     },
            #     "is_pro": is_pro if is_pro else 0,
            #     "max_allowed_classes_per_class": max_classes if max_classes else 4,
            #     "num_classes_per_month": frequency if frequency else 20
            # }
            sample_request ={
                "name": "roman",
                "location": {
                    "latitude": 19.388900864307445,
                    "longitude": -99.18265186842596
                },
                "distance_sensitivity": "medium",
                "preferences": {
                    "love_activities": ["barre", "yoga", "cycling", "pilates", "gym"],
                    "hate_activities": ["crossfit", "functional"]
                },
                "is_pro": 1,
                "max_allowed_classes_per_class": 4,
                "num_classes_per_month": 23
            }
            log_debugg(f"Solicitud: {sample_request}")
            url = 'http://app:8080/predict'
            try:
                response = requests.post(url, json=sample_request)
                response_json = response.json()
            except Exception as e:
                log_debugg(f"Error during POST request: {e}")
            log_debugg(f"Respuesta: {response}")
            response_json = response.json()
            log_debugg(f"Respuesta JSON: {response_json}")
            df_recommendations = pd.DataFrame(response_json)

            log_debugg("Estudios recomendados:")
            log_debugg(df_recommendations)
            log_debugg(f"shape recomendaciones: {df_recommendations.shape}")
            log_debugg(f"type df_studios: {type(df_recommendations)}")
            df_combined = df_studios.merge(df_recommendations, on='gym_id', how='inner')

            # Preparar los datos para el mapa y la tabla
            log_debugg(df_combined.columns)
            log_debugg(f"shape combined: {df_combined.shape}")
            log_debugg(f"{'='*100}")
            df_combined['latitude'] = pd.to_numeric(df_combined['latitude'], errors='coerce')
            df_combined['longitude'] = pd.to_numeric(df_combined['longitude'], errors='coerce')
            df_combined = df_combined.dropna(subset=['latitude', 'longitude'])

        # Crear los marcadores para el mapa
        log_debugg("Creando marcadores para el mapa...")
        markers = [dl.TileLayer()]
        for i, row in df_combined.iterrows():
            log_debugg(f"row {i}")
            marker = dl.Marker(position=[row['latitude'], row['longitude']], children=[dl.Tooltip(row['gym_name'])])
            markers.append(marker)
            log_debugg(f"Marcador agregado: {marker}")

        # Crear la gráfica (ajustar según los datos disponibles)
        log_debugg("Creando gráfica...")
        fig_graph = px.bar(df_combined, x='gym_name', y='gym_times', title='Numero de veces recomendado')

        # Crear la tabla
        log_debugg("Creando tabla...")
        table = dash_table.DataTable(
            data=df_combined.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df_combined.columns],
            style_table={'overflowX': 'scroll'}
        )

        return markers, fig_graph, table
    
# Ejecución del servidor
if __name__ == '__main__':
    if os.environ.get('DASH_ENV') != 'development':
        log_debugg("Running in production mode...")
        app.run(host='0.0.0.0', port=8050) # production
    else:
        log_debugg("Running in development mode...")
        app.run(host='0.0.0.0', debug=True, port=8050) # development / debugging