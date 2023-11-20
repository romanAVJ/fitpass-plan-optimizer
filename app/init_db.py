import psycopg2
from psycopg2 import sql
import pandas as pd
import os

# Connect to the PostgreSQL database
print('Connecting to the PostgreSQL database...')
conn = psycopg2.connect(
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
    host="db", # docker-compose service name
    port="5432"
)
# Open a cursor to perform database operations
print('Opening a cursor to perform database operations...')
cur = conn.cursor()

# Read the data from the Parquet file
print('Reading the data from the Parquet file...')
parquet_file_path = 'tidy_fitpass_cdmx.parquet'
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