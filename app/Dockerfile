# Use an official Python image as a base image, use 3.9 version
FROM python:3.9

# Set the environment variables for PostgreSQL
ENV POSTGRES_DB fitpass
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD skalas-puts-me-an-aplus-in-this-class

# Switch to the root directory
WORKDIR /

# Copy requirements.txt file and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the files from app directory to the root directory
COPY . /app

# Set the working directory
WORKDIR /app

# Run the app when the container launches in debug mode
CMD ["bash"]