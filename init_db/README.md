Data Loader for Fitpass CDMX Studios
This script loads data from a Parquet file into the cdmx_studios table in a PostgreSQL database.

Prerequisites
PostgreSQL database server running and accessible
fitpass database created in PostgreSQL
tidy_fitpass_cdmx.parquet file containing the data to be loaded
Installation
Install the following Python libraries:
psycopg2
pandas
Usage
Ensure the PostgreSQL database is running and accessible.

Modify the connection parameters in the script if necessary:

POSTGRES_HOST: The hostname of the PostgreSQL database server (default: localhost)
POSTGRES_USER: The username for connecting to the PostgreSQL database (default: postgres)
POSTGRES_PASSWORD: The password for connecting to the PostgreSQL database (default: empty)
POSTGRES_DB: The name of the PostgreSQL database to use (default: fitpass)
Run the script using Python:

Bash
python load_data.py
Use code with caution. Learn more

Script Overview
The wait_for_db() function attempts to connect to the PostgreSQL database, retrying if necessary.
The script connects to the PostgreSQL database and opens a cursor for performing database operations.
The tidy_fitpass_cdmx.parquet file is read into a pandas DataFrame.
An INSERT SQL query is constructed using the psycopg2 library's sql module.
The INSERT query is executed, inserting the DataFrame values into the cdmx_studios table.
The changes are committed to the database.
The connection to the database is closed.

A message is printed indicating that the data loading process has completed successfully.
