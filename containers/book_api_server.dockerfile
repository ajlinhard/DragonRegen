# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy the application code to the working directory
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install .

# Expose port 5000 for the Flask application
EXPOSE 5000

RUN python /app/src/Book_API/app.py

# Set environment variables
# ENV FLASK_APP=/app/src/Book_API/app.py
# ENV FLASK_ENV=production

# Command to run the application
# CMD ["flask", "run", "--host=0.0.0.0"]