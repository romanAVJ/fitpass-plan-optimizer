import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import requests
import sqlalchemy as sa
import math

# Configuración de la conexión a la base de datos
db_name = 'fitpass'
db_user = 'postgres'
db_host = 'localhost'
db_password = 'skalas-puts-me-an-aplus-in-this-class'
database_url = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
engine = sa.create_engine(database_url)

# Inicialización de la aplicación Dash
app = dash.Dash(__name__)

# Layout de la Aplicación
app.layout = html.Div([
    html.H1("Dashboard de Estudios de Fitness"),
    dcc.Input(id='input-lat', type='text', placeholder='Latitud'),
    dcc.Input(id='input-lon', type='text', placeholder='Longitud'),
    dcc.Dropdown(
        id='activity-dropdown',
        options=[{'label': activity, 'value': activity} for activity in ['barre', 'box', 'crossfit', 'cycling', 'dance', 'ems', 'functional', 'gym', 'hiit', 'mma', 'pilates', 'pool', 'running', 'sports', 'virtual_class', 'wellness', 'yoga']],
        multi=True,
        placeholder="Selecciona actividades que te gustan"
    ),
        dcc.Dropdown(
        id='distance-dropdown',
        options=[
            {'label': 'Cerca', 'value': 'cerca'},
            {'label': 'Medio', 'value': 'medio'},
            {'label': 'Lejano', 'value': 'lejano'}
        ],
        placeholder="Selecciona la distancia"
    ),
    html.Button('Buscar', id='search-button', n_clicks=0),
    dcc.Graph(id='map-view')


])

# Función para calcular la distancia utilizando la fórmula de Haversine
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

def generate_sql_query(lat, lon, love_activities, distance_option):
    query = "SELECT * FROM cdmx_studios WHERE TRUE"

    # # Lógica para manejar la distancia
    # if lat is not None and lon is not None:
    #     # Define la lógica para cada opción de distancia
    #     if distance_option == 'cerca':
    #         distance_value = 5  # Ejemplo: 5 km para "cerca"
    #     elif distance_option == 'medio':
    #         distance_value = 15  # Ejemplo: 15 km para "medio"
    #     elif distance_option == 'lejano':
    #         distance_value = 30  # Ejemplo: 30 km para "lejano"
    #     else:
    #         distance_value = 10  # Valor por defecto o manejo de casos no definidos

    #     query += f" AND calculate_distance(latitude, longitude, {lat}, {lon}) <= {distance_value}"
    
    # Lógica para filtrar por actividades favoritas
    if love_activities:
        love_conditions = " OR ".join([f"{activity} = 1" for activity in love_activities])
        query += f" AND ({love_conditions})"

    return query

# # Función para generar la consulta SQL
# def generate_sql_query(lat, lon, love_activities):
#     # Inicia la consulta SQL base
#     query = "SELECT * FROM cdmx_studios WHERE TRUE"

#     # Añade condiciones basadas en la ubicación
#     # Nota: Debes reemplazar 'calculate_distance' con tu función real de cálculo de distancia
#     if lat is not None and lon is not None:
#         # Aquí puedes definir la lógica para cada opción de distancia
#         if distance_option == 'cerca':
#             distance_value = 5  # Ejemplo: 5 km para "cerca"
#         elif distance_option == 'medio':
#             distance_value = 15  # Ejemplo: 15 km para "medio"
#         elif distance_option == 'lejano':
#             distance_value = 30  # Ejemplo: 30 km para "lejano"
#         else:
#             distance_value = 10  # Valor por defecto o manejo de casos no definidos

#         query += f" AND calculate_distance(latitude, longitude, {lat}, {lon}) <= {distance_value}"
#     # Filtra por actividades favoritas
#     if love_activities:
#         love_conditions = " OR ".join([f"{activity} = 1" for activity in love_activities])
#         query += f" AND ({love_conditions})"

        

#     # # Excluye actividades que no le gustan
#     # if hate_activities:
#     #     hate_conditions = " AND ".join([f"{activity} = 0" for activity in hate_activities])
#     #     query += f" AND ({hate_conditions})"

#     # # Considera si el usuario es profesional
#     # if is_pro:
#     #     query += " AND pro_status = 1"

#     # Agrega cualquier otra lógica relacionada con max_classes y num_classes_month si es necesario

#     return query

# Función para combinar DataFrames
def combine_dataframes(df1, df2):
    combined_df = pd.concat([df1, df2], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=['gym_id'])
    return combined_df

# Callback para actualizar el mapa

@app.callback(
    Output('map-view', 'figure'),
    [Input('search-button', 'n_clicks')],
    [State('input-lat', 'value'), State('input-lon', 'value'), State('activity-dropdown', 'value'), State('distance-dropdown', 'value')]
)
def update_map(n_clicks, lat, lon, activities, distance_option):
    if lat and lon:
        query = generate_sql_query(lat, lon, activities, distance_option)
        df_studios = pd.read_sql_query(query, engine)
            
        if n_clicks > 0 and activities:
            sample_request = {"location": {"latitude": lat, "longitude": lon}, "love_activities": activities}
            response = requests.post('http://localhost:8080/predict', json=sample_request)
            # Verifica si la respuesta JSON es una lista o un diccionario
            response_json = response.json()
            if isinstance(response_json, list):
                df_recommendations = pd.DataFrame(response_json)
            elif isinstance(response_json, dict):
                # Crear un DataFrame a partir de un diccionario con un índice
                df_recommendations = pd.DataFrame([response_json])
            else:
                raise ValueError("Respuesta JSON no reconocida")

            df_combined = combine_dataframes(df_studios, df_recommendations)

           # Asegúrate de que las columnas 'latitude' y 'longitude' sean numéricas
        if 'latitude' in df_combined.columns and 'longitude' in df_combined.columns:
            df_combined['latitude'] = pd.to_numeric(df_combined['latitude'], errors='coerce')
            df_combined['longitude'] = pd.to_numeric(df_combined['longitude'], errors='coerce')

        # Crea el mapa
        if df_combined.notnull().any().any():  # Verifica si hay al menos un valor no nulo
            fig = px.scatter_mapbox(
                df_combined, lat='latitude', lon='longitude', hover_name='gym_name',
                color='gym_name', zoom=10, height=300
            )
            fig.update_layout(mapbox_style="open-street-map")
            return fig
        
    # Crear un DataFrame vacío con columnas lat y lon
    empty_df = pd.DataFrame({'lat': [], 'lon': []})

    # Retornar un gráfico de mapa vacío con el DataFrame vacío
    return px.scatter_mapbox(empty_df, lat='lat', lon='lon')

# Ejecución del servidor
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

