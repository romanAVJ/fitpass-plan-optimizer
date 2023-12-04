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

    if love_activities:
        love_conditions = " OR ".join([f"{activity} = 1" for activity in love_activities])
        query += f" AND ({love_conditions})"

    return query

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
    try:
        lat = float(lat) if lat else None
        lon = float(lon) if lon else None
    except ValueError:
        lat, lon = None, None
    print(f"Lat: {lat}, Lon: {lon}, Activities: {activities}, Distance: {distance_option}")

    if lat is not None and lon is not None:
        query = generate_sql_query(lat, lon, activities, distance_option)
        df_studios = pd.read_sql_query(query, engine)
            
        if n_clicks > 0 and activities:
            sample_request = {"location": {"latitude": lat, "longitude": lon}, "love_activities": activities}
            response = requests.post('http://localhost:8080/predict', json=sample_request)
            response_json = response.json()
            if isinstance(response_json, list):
                df_recommendations = pd.DataFrame(response_json)
            elif isinstance(response_json, dict):
                df_recommendations = pd.DataFrame([response_json])
            else:
                raise ValueError("Respuesta JSON no reconocida")

            df_combined = combine_dataframes(df_studios, df_recommendations)

            # Asegurarse de que las columnas 'latitude' y 'longitude' sean numéricas
            df_combined['latitude'] = pd.to_numeric(df_combined['latitude'], errors='coerce')
            df_combined['longitude'] = pd.to_numeric(df_combined['longitude'], errors='coerce')

            # Filtrar filas con datos faltantes o incorrectos en 'latitude' y 'longitude'
            df_combined = df_combined.dropna(subset=['latitude', 'longitude'])
            print(df_combined.head())  # Imprimir las primeras filas para depuración

            # Crear el mapa si hay datos válidos
            if not df_combined.empty:
                fig = px.scatter_mapbox(
                    df_combined, lat='latitude', lon='longitude', hover_name='gym_name',
                    color='gym_name', zoom=10, height=300
                )
                fig.update_layout(mapbox_style="open-street-map")
                return fig
    # Retornar un gráfico de mapa vacío si no hay datos válidos de lat y lon
    return px.scatter_mapbox(pd.DataFrame({'lat': [], 'lon': []}), lat='lat', lon='lon')

# Ejecución del servidor
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

