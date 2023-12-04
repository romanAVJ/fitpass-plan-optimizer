import dash
import dash_leaflet as dl
from dash import dash_table
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
        id='input-dislike',
        options=[{'label': activity, 'value': activity} for activity in ['barre', 'box', 'crossfit', 'cycling', 'dance', 'ems', 'functional', 'gym', 'hiit', 'mma', 'pilates', 'pool', 'running', 'sports', 'virtual_class', 'wellness', 'yoga']],
        multi=True,
        placeholder="Selecciona actividades que no te gustan"
    ),
    dcc.Input(id='input-frequency', type='number', placeholder='Número de clases al mes'),
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
    dl.Map(id='map-view', style={'width': '1000px', 'height': '500px'}, center=[19.432608, -99.133209], zoom=10, children=[
    dl.TileLayer()
    ]),
    dcc.Graph(id='graph-view'),
    html.Div(id='table-view')  # Div para mostrar la tabla de resultados
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

# Función para generar la consulta SQL con las nuevas entradas
def generate_sql_query(lat, lon, love_activities, dislike_activities, frequency, distance_option):
    query = "SELECT * FROM cdmx_studios WHERE TRUE"

    # Filtrar por actividades favoritas
    if love_activities:
        love_conditions = " OR ".join([f"{activity} = 1" for activity in love_activities])
        query += f" AND ({love_conditions})"

    if dislike_activities:
        dislike_conditions = " AND ".join([f"{activity} = 0" for activity in dislike_activities])
        query += f" AND ({dislike_conditions})"


    return query

# Función para combinar DataFrames
def combine_dataframes(df1, df2):
    combined_df = pd.concat([df1, df2], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=['gym_id'])
    return combined_df

@app.callback(
    [
        Output('map-view', 'children'),  # Para los marcadores del mapa
        Output('graph-view', 'figure'),  # Para la gráfica
        Output('table-view', 'children')  # Para la tabla
    ],
    [
        Input('search-button', 'n_clicks')
    ],
    [
        State('input-lat', 'value'), State('input-lon', 'value'), 
        State('activity-dropdown', 'value'), State('distance-dropdown', 'value'),
        State('input-dislike', 'value'), State('input-frequency', 'value')
    ]
)
def update_outputs(n_clicks, lat, lon, activities, distance_option, dislikes, frequency):
    # Validar y convertir las entradas
    try:
        lat = float(lat) if lat else None
        lon = float(lon) if lon else None
    except ValueError:
        lat, lon = None, None

    if lat is not None and lon is not None:
        # Obtener estudios recomendados de la base de datos
        query = generate_sql_query(lat, lon, activities, dislikes, frequency, distance_option)
        df_studios = pd.read_sql_query(query, engine)
        
        if n_clicks > 0 and activities:
            # Hacer la solicitud a la API
            sample_request = {
                "location": {"latitude": lat, "longitude": lon}, 
                "love_activities": activities, 
                "hate_activities": dislikes, 
                "num_classes_per_month": frequency
            }
            response = requests.post('http://localhost:8080/predict', json=sample_request)
            response_json = response.json()
            if isinstance(response_json, list):
                df_recommendations = pd.DataFrame(response_json)
            elif isinstance(response_json, dict):
                df_recommendations = pd.DataFrame([response_json])
            else:
                raise ValueError("Respuesta JSON no reconocida")

            df_combined = combine_dataframes(df_studios, df_recommendations)

            # Preparar los datos para el mapa y la tabla
            df_combined['latitude'] = pd.to_numeric(df_combined['latitude'], errors='coerce')
            df_combined['longitude'] = pd.to_numeric(df_combined['longitude'], errors='coerce')
            df_combined = df_combined.dropna(subset=['latitude', 'longitude'])

        # Crear marcadores para el mapa
            markers = [dl.TileLayer()]
            if not df_combined.empty:
                for _, row in df_combined.iterrows():
                    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
                        marker = dl.Marker(position=[row['latitude'], row['longitude']], children=[
                            dl.Tooltip(row['gym_name'])
                        ])
                        markers.append(marker)

            # Crear la gráfica de barras
            fig_graph = px.bar(df_combined, x='gym_name', y='pro_status', color='pro_status',
                            title='Tipo de Estudio y Fitpass Pro Status')

            # Crear la tabla
            table = dash_table.DataTable(
                data=df_combined.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df_combined.columns],
                style_table={'overflowX': 'scroll'}
            )

        # Asegúrate de retornar marcadores para el mapa
        return markers, dcc.Graph(figure=fig_graph), table

    # Retornar elementos vacíos si no hay datos válidos
    return [dl.TileLayer()], html.Div(), html.Div()

# Ejecución del servidor
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)