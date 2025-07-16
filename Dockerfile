
# Use a lightweight Python image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the backend application code into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the FastAPI application runs on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


