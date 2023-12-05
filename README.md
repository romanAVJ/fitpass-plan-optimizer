# Fitpass-plan-optimizer
## Participants
Román Alberto Vélez Jiménez: 165462

David Escudero Garcia: 208952

Rodrigo Zavaleta Sosa: 208960

## Overview
An AI model (mixed optimization) to generate the best workout plan of classes in fitpass subject to the user preferences and restrictions. 

# Run interactivly the application
1. Build Docker image and put it up

Navigate to the project directory and run the following command:

```bash
# build and get up the container
docker-compose up -d --build
```

**Note:** Please wait until the container is up and running. The ETA is about 5 minutes.


# 2. Test endpoints
## Dashboard
You can access to the dashboard at `http://localhost:8050`

## API
You can access the API at `http://localhost:8000` 

- `info` endpoint
```bash
curl -X GET http://localhost:8080/info
```

- `predict` endpoint
```bash
curl -X POST -H "Content-Type: application/json" -d '{
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
}' http://localhost:8080/predict
```




3. Stop & remove the container
```bash
# Remove the containers
docker-compose down

# Remove all the images
docker rmi $(docker images -a -q)

# Remove all the volumes
docker volume rm $(docker volume ls -q)
```






Nombre del proyecto: Dashboard de Fitpass

Descripción:
Este proyecto es un dashboard de Fitpass que permite a los usuarios buscar estudios de Fitpass en una ciudad y colonia específica. El dashboard consta de un gráfico de barras que muestra el número de estudios por tipo, una lista de estudios que cumplen con los criterios de búsqueda, y un mapa que muestra la ubicación de los estudios.

Requisitos:
- Python 3.x
- Dash
- Dash Leaflet
- Plotly Express
- Pandas

Instalación:

Clone el repositorio a su máquina local.
Abra una terminal y navegue a la carpeta que contiene el código.
Instale las dependencias requeridas:
pip install -r requirements.txt
Ejecución:
Ejecute el siguiente comando para iniciar la aplicación Dash:
python app.py
La aplicación se iniciará en http://localhost:8050.


Uso:

Para usar el dashboard, seleccione una ciudad y colonia en los menús desplegables. Luego, haga clic en el botón "Buscar". El gráfico de barras se actualizará para mostrar el número de estudios por tipo en la ciudad y colonia seleccionada. La lista de estudios se actualizará para mostrar una lista de todos los estudios que cumplen con los criterios de búsqueda. El mapa se actualizará para mostrar la ubicación de los estudios.


Lógica de actualización de la lista y el mapa:
La lógica para actualizar la lista y el mapa se encuentra en la función actualizar_lista_y_mapa(). Esta función toma tres argumentos:
n_clicks: El número de clics en el botón "Buscar".
ciudad: El valor seleccionado en el menú desplegable "Ciudad".
colonia: El valor seleccionado en el menú desplegable "Colonia".
La función primero verifica si n_clicks es None. Si es así, significa que el usuario aún no ha hecho clic en el botón "Buscar". En este caso, la función devuelve una lista con un mensaje que indica al usuario que debe seleccionar una ciudad y colonia.
Si n_clicks no es None, la función procede a actualizar la lista y el mapa. Para actualizar la lista, la función filtra los datos de data_dummy para encontrar los estudios que se encuentran en la ciudad y colonia seleccionada.
Para actualizar el mapa, la función crea un objeto dl.MarkerCluster() para cada estudio que se encuentra en la ciudad y colonia seleccionada. Luego, la función agrega el objeto dl.MarkerCluster() al mapa.



Próximos pasos:
Agregar filtros adicionales a la búsqueda, como el tipo de estudio y la disponibilidad de clases.
Agregar funcionalidad para guardar los resultados de la búsqueda.
Agregar funcionalidad para compartir los resultados de la búsqueda.
