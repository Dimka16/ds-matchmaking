# Python 3.12 slim base
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# IMPORTANT: allow top-level imports (app, auth, web)
ENV PYTHONPATH=/app

# Set working directory inside container
WORKDIR /app

# System dependencies (Postgres + optional wheel builds)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL project code (app, auth, web, etc.)
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "-m", "app.main"]
