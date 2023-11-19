import psycopg2
from psycopg2 import sql
import pandas as pd
import time

# Wait for PostgreSQL to be ready
print('Waiting for PostgreSQL to be ready...')
time.sleep(1)

# Connect to the PostgreSQL database
print('Connecting to the PostgreSQL database...')
conn = psycopg2.connect(
    dbname="fitpass",
    user="postgres",
    password="postgres",
    host="fitpass-app",
    port=5432
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Create the table
print('Creating the table...')
table_creation_query = '''
CREATE TABLE IF NOT EXISTS cdmx_studios (
    gym_id          VARCHAR(255),
    gym_name        VARCHAR(255),
    pro_status      INT,
    virtual_status  INT,
    class_minutes   VARCHAR(255),
    notes           VARCHAR(255),
    latitude        VARCHAR(255),
    longitude       VARCHAR(255),
    address         VARCHAR(255),
    barre           FLOAT,
    box             FLOAT,
    crossfit        FLOAT,
    cycling         FLOAT,
    dance           FLOAT,
    ems             FLOAT,
    functional      FLOAT,
    gym             FLOAT,
    hiit            FLOAT,
    mma             FLOAT,
    pilates         FLOAT,
    pool            FLOAT,
    running         FLOAT,
    sports          FLOAT,
    virtual_class   FLOAT,
    wellness        FLOAT,
    yoga            FLOAT
);
'''
cur.execute(table_creation_query)

# Commit the changes
conn.commit()

# Read the data from the Parquet file
print('Reading the data from the Parquet file...')
parquet_file_path = 'data/tidy_fitpass_cdmx.parquet'
df = pd.read_parquet(parquet_file_path)

# Insert data into the table
print('Inserting data into the table...')
columns = ', '.join(df.columns)
values = ', '.join(['%s' for _ in range(len(df.columns))])
insert_query = sql.SQL("INSERT INTO cdmx_studios ({}) VALUES ({});").format(
    sql.SQL(columns), sql.SQL(values)
)

# Execute the insert query
cur.executemany(insert_query, df.values)

# Commit the changes
conn.commit()

# Close communication with the database
cur.close()
conn.close()

print('Done!')