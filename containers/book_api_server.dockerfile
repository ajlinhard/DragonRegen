# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install curl and other dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*
    
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install the package from the directory
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Make port 5000 available to the world outside this container
# (adjust if your app uses a different port)
EXPOSE 5000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["python", "/app/src/Book_API/app.py"]