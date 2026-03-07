FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install service-specific dependencies
COPY services/performance-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code and this service into the image
COPY shared ./shared
COPY services/performance-service ./services/performance-service

WORKDIR /app/services/performance-service

# Run the app as a package module to avoid circular import issues
CMD ["python", "-m", "app.app"]

