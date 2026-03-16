FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY services/api-gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/api-gateway ./services/api-gateway

WORKDIR /app/services/api-gateway

CMD ["python", "app/app.py"]

