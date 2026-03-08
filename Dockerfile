# =============================================================================
# Dockerfile
# Builds our FastAPI application into a Docker container
# =============================================================================

# Start from an official Python 3.11 slim image (slim = smaller size)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first — Docker caches this layer.
# If requirements don't change, Docker won't re-install packages on every build.
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir keeps the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of our application code into the container
COPY . .

# Tell Docker our app listens on port 8000
EXPOSE 8000

# Start the FastAPI app with uvicorn
# --host 0.0.0.0  = listen on all network interfaces (needed inside Docker)
# --port 8000     = use port 8000
# --reload        = auto-restart when code changes (great for development!)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
