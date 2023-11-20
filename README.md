# fitpass-plan-optimizer
An AI model (mixed optimization) to generate the best workout plan in fitpass subject to the user preferences and restrictions 

# Run interactivly the application
1. Build Docker image

Navigate to the project directory and run the following command:

```bash
docker-compose build
```

2. Run Docker container interactively

Command map the container's PostgreSQL port (5432) to local machine's port 5432 and the Dash app port (8050) to local machine's port 8050.

```bash
# Start the Docker container in interactive mode
docker-compose up -d

# Find the name or ID of your running PostgreSQL container
CONTAINER_ID=$(docker-compose ps -q db)

# Connect to the PostgreSQL container interactively
docker exec -it $CONTAINER_ID bash
```

3. Execute programs

Execute any program you want. For example, to run the init_db program, run the following command:

```bash
python init_db.py
```

4. Stop & remove the container

```bash
docker-compose down
```


# Run the application (WIP)
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