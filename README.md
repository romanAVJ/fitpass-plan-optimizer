# fitpass-plan-optimizer
An AI model (mixed optimization) to generate the best workout plan of classes in fitpass subject to the user preferences and restrictions 

# Run interactivly the application
1. Build Docker image and put it up

Navigate to the project directory and run the following command:

```bash
# build and get up the container
docker-compose up -d --build
```

2. Stop & remove the container
```bash
# Remove the containers
docker-compose down

# Remove all the images
docker rmi $(docker images -a -q)

# Remove all the volumes
docker volume rm $(docker volume ls -q)
```

# Run the application in production (WIP)
1. Compose the application

Navigate to the project directory and run the following command:
```bash
docker-compose up --build
```

Now you can access the application at http://localhost:8000

2. Test endpoints

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