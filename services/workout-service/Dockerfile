FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install service-specific dependencies
COPY services/workout-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code and this service into the image
COPY shared ./shared
COPY services/workout-service ./services/workout-service

WORKDIR /app/services/workout-service

# Run the app as a package module to avoid circular import issues
CMD ["python", "-m", "app.app"]

