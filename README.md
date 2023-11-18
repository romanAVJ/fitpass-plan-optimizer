# fitpass-plan-optimizer
An AI model (mixed optimization) to generate the best workout plan in fitpass subject to the user preferences and restrictions 

# How to run
1. Build Docker image

Navigate to the project directory and run the following command:

```bash
docker build -t fitpass-app .
```

2. Run Docker container

Command map the container's PostgreSQL port (5432) to local machine's port 5432 and the Dash app port (8050) to local machine's port 8050.

```bash
docker run -p 5432:5432 -p 8050:8050 fitpass-app
```

3. Verify PostgreSQL connection


