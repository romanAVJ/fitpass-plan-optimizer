Fitpass Database Setup

This Dockerfile sets up a PostgreSQL database for the Fitpass application. It uses the official PostgreSQL image as a base image and sets the following environment variables:

POSTGRES_DB: The name of the database to create.
POSTGRES_USER: The username for the database.
POSTGRES_PASSWORD: The password for the database.
POSTGRES_HOST: The hostname of the database server.
The Dockerfile also copies the create_table.sql script to the /docker-entrypoint-initdb.d directory. This script will be run when the container starts up and will create the tables for the Fitpass application.

Instructions
To use this Dockerfile, follow these steps:

Save the Dockerfile as Dockerfile in the root directory of your project.
Build the Docker image using the following command:
docker build -t fitpass-db .
Run the Docker container using the following command:
docker run -d -p 5432:5432 fitpass-db
This will create a container running the PostgreSQL database. You can connect to the database using the following connection string:

postgresql://postgres:skalas-puts-me-an-aplus-in-this-class@db:5432/fitpass
License
This Dockerfile is licensed under the MIT License.
