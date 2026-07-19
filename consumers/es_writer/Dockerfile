FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY consumers/es_writer/requirements.txt consumers/es_writer/requirements.txt
RUN pip install --no-cache-dir -r consumers/es_writer/requirements.txt

COPY consumers/es_writer/consumer.py consumers/es_writer/consumer.py

CMD ["python", "consumers/es_writer/consumer.py"]
