# Dockerfile (FINAL PRODUCTION-READY VERSION)

# Use a specific version for reproducibility
FROM python:3.11.4-slim-bullseye

# Set environment variables for best practices
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents python from writing .pyc files
ENV PYTHONUNBUFFERED 1         # Ensures logs are sent straight to the terminal

# Set the working directory
WORKDIR /app

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel for faster dependency installation
RUN pip install --upgrade pip wheel

# Install Python dependencies
# Copy only the requirements file first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download and cache the AI model during the build process
# Copying the script separately also helps with caching
COPY download_model.py .
RUN python download_model.py

# Copy the rest of the application code
COPY ./app /app/app
COPY ./alembic.ini /app/
COPY ./migrations /app/migrations/

# Change ownership of the app directory to the non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# EXPOSE is not strictly necessary on Koyeb but is good practice
EXPOSE 8000