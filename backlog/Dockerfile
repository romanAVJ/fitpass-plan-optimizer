# Use an official PostgreSQL image as a base image
FROM postgres:latest

# Set the environment variables for PostgreSQL
ENV POSTGRES_DB fitpass
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres

# Switch to the root directory
WORKDIR /

# Install Python 3.9 and pip
RUN apt-get update && \
    apt-get install -y python3.9 python3-venv python3-distutils \
                       libgdal-dev libproj-dev proj-data proj-bin \
                       libgeos-dev

# Create a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the files from app directory to the root directory
COPY app /app

# Set the working directory
WORKDIR /app

# Expose the port for the Dash application
EXPOSE 8050

# Command to run
CMD ["postgres"]