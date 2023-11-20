# Use an official PostgreSQL image as a base image
FROM postgres:latest

# Set the environment variables for PostgreSQL
ENV POSTGRES_DB fitpass
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD skalas-puts-me-an-aplus-in-this-class

# Copy the SQL script to the initdb directory
COPY create_table.sql /docker-entrypoint-initdb.d/