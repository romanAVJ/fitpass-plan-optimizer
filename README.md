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

## Dashboard
You can access to the dashboard at `http://localhost:8050`


3. Stop & remove the container
```bash
# Remove the containers
docker-compose down

# Remove all the images
docker rmi $(docker images -a -q)

# Remove all the volumes
docker volume rm $(docker volume ls -q)
```