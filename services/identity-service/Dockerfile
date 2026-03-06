FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install service-specific dependencies
COPY services/identity-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code and this service into the image
COPY shared ./shared
COPY services/identity-service ./services/identity-service

WORKDIR /app/services/identity-service

# Run the app as a package module to avoid circular import issues
CMD ["python", "-m", "app.app"]

