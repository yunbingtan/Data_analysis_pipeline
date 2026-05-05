# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install only the packages the container actually uses.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Health check to ensure the container is running correctly
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Command to run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
