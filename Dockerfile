# Python 3.12 slim base
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# System dependencies:
# - libpq-dev for Postgres client libs (psycopg)
# - gcc for building some Python wheels if needed
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better Docker layer caching)
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY app ./app

# Expose Flask port (container-side)
EXPOSE 5000

# Run the Flask app automatically when container starts
# Assumes you have app/main.py with `app = Flask(__name__)`
CMD ["python", "-m", "app.main"]