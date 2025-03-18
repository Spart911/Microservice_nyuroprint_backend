# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application into the container
COPY .. .

# Expose the port that the app runs on
EXPOSE 6666

# Command to run the application with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "6666", "--workers", "4", "--ssl-keyfile", "/ssl/certificate.key.pem", "--ssl-certfile", "/ssl/certificate.crt.pem"]