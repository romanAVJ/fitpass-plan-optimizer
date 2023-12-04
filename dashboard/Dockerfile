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

# Copy requirements.txt file and install Python dependencies
COPY requirements.txt /dashboard/requirements.txt
RUN pip install --no-cache-dir -r /dashboard/requirements.txt

# Copy the files from dashboard directory to the root directory
COPY . /dashboard

# Set the working directory
WORKDIR /dashboard

# run the dash dashboard
ENV DASH_ENV development
CMD ["python", "dashboard.py"]