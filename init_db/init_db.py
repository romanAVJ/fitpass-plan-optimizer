import psycopg2
from psycopg2 import sql
import pandas as pd
import os
import time

# Wait for the PostgreSQL database to be ready
def wait_for_db():
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            print(f"Trying to connect to the PostgreSQL database... ({retries}/{max_retries})")
            conn = psycopg2.connect(
                host=os.environ.get('POSTGRES_HOST', 'localhost'),
                user=os.environ.get('POSTGRES_USER', 'postgres'),
                password=os.environ.get('POSTGRES_PASSWORD', ''),
                database=os.environ.get('POSTGRES_DB', 'fitpass')
            )
            print("Connected to the PostgreSQL database.")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Error: {e}")
            print(f"Waiting 10 seconds for PostgreSQL to be ready... ({retries}/{max_retries})")
            retries += 1
            time.sleep(10)

    print("Max retries reached. Unable to connect to the PostgreSQL database.")
    return None

# Connect to the PostgreSQL database
print('Connecting to the PostgreSQL database...')
time.sleep(5) # wait for postgres to be ready
print('Waiting 10 seconds for postgres to be ready...')

conn = wait_for_db()
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