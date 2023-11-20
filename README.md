# fitpass-plan-optimizer
An AI model (mixed optimization) to generate the best workout plan in fitpass subject to the user preferences and restrictions 

# Run interactivly the application
1. Build Docker image and put it up

Navigate to the project directory and run the following command:

```bash
# build and get up the container
docker-compose up -d --build
```

2. Run interactivly the application

Execute any program you want. For example, to run the init_db program, run the following command:

```bash
docker-compose run --rm -p 8000:8000 app bash
```

3. Execute programs

Execute any program of the app container. For example, to run the init_db program, run the following command:
```bash
# Run the init_db program
python init_db.py
```

4. Stop & remove the container
```bash
# Remove the containers
docker-compose down

# Remove all the images
docker rmi $(docker images -a -q)

# Remove all the volumes
docker volume rm $(docker volume ls -q)
```

# Run the application in production (WIP)
1. Build Docker image

Navigate to the project directory and run the following command:

```bash
docker build -t fitpass-app .
```

2. Run Docker container

Command map the container's PostgreSQL port (5432) to local machine's port 5432 and the Dash app port (8050) to local machine's port 8050.

```bash
docker run -p 5432:5432 -p 8050:8050 -it fitpass-app bash
```

Now you are inside the container.