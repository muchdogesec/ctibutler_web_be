# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django app
COPY . /app/

# Collect static files (optional, if you plan to serve static files via Django)
RUN python manage.py collectstatic --noinput
