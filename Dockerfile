# Use an official PostgreSQL image as a base image
FROM postgres:latest

# Set the environment variables for PostgreSQL
ENV POSTGRES_DB fitpass
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres

# Switch to the root directory
WORKDIR /

# Install Python 3 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv \
                       libgdal-dev libproj-dev proj-data proj-bin \
                       libgeos-dev

# Install python3-venv package
RUN apt-get install -y python3-venv

# Create a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the files from app directory to the root directory
COPY app /app
COPY data/tidy_fitpass_cdmx.parquet /app/data

# Copy data from data directory to a data directory in the root directory

# Expose the port for the Dash application
EXPOSE 8050

# Command to run
CMD ["bash"]