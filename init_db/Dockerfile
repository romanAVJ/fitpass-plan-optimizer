# Stage 2: Install Python 3.9 and its dependencies
FROM python:3.9

# Set the environment variables for PostgreSQL
ENV POSTGRES_DB fitpass
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD skalas-puts-me-an-aplus-in-this-class
ENV POSTGRES_HOST db


# Set the working directory
COPY . /init_db
WORKDIR /init_db

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run init_db.py when the container launches
CMD ["python", "init_db.py"]