# Dashboard de Estudios de Fitness

Este proyecto es un dashboard interactivo construido con [Dash](https://plotly.com/dash/), diseñado para visualizar y analizar datos de estudios de fitness. El dashboard permite a los usuarios buscar estudios de fitness basándose en sus preferencias y ubicación.

## Características

- **Búsqueda Personalizada:** Los usuarios pueden buscar estudios de fitness basándose en actividades específicas, frecuencia de clases, y distancia.
- **Mapa Interactivo:** Los estudios encontrados se muestran en un mapa interactivo de [Leaflet](https://leafletjs.com/), proporcionando una visión geográfica clara.
- **Análisis de Datos:** Se incluye una gráfica de barras para analizar el estado de los estudios (Pro Status) en relación con sus nombres.
- **Tabla de Resultados:** Los resultados se presentan también en una tabla detallada, mostrando información relevante sobre cada estudio.

## Tecnologías Utilizadas

- **Dash:** Un framework de Python para construir aplicaciones web analíticas.
- **Plotly:** Una biblioteca gráfica para crear gráficos interactivos.
- **Pandas:** Para el manejo y análisis de los datos.
- **SQLAlchemy:** Utilizado para interactuar con la base de datos.
- **Leaflet:** Para mostrar el mapa interactivo.

## Uso
**Visita `http://localhost:8050` en tu navegador para acceder al dashboard.**

Para usar el dashboard:

- Introduce la latitud y longitud para establecer tu ubicación.
- Selecciona tus actividades favoritas y las que no te gustan.
- Ajusta la frecuencia con la que asistes a clases y la distancia preferida.
- Haz clic en "Buscar" para ver los resultados en el mapa, la gráfica y la tabla.

