# Use an official Python image as a base image, use 3.9 version
FROM python:3.9

#### POSTGRESQL ####
# Set the environment variables for PostgreSQL
ENV POSTGRES_DB fitpass
ENV POSTGRES_USER postgres
ENV POSTGRES_HOST db
ENV POSTGRES_PASSWORD skalas-puts-me-an-aplus-in-this-class

#### PYTHON ####
# Switch to the root directory
WORKDIR /

# install GDAL dependencies for fiona
RUN apt-get update \
    && apt-get install -y libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt file and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the files from app directory to the root directory
COPY . /app

# # Set the working directory
WORKDIR /app

#### RUN FLASK PYTHON SERVER ####
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["python", "init_db.py"]