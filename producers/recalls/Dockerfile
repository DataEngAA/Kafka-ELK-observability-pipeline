FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY producers/recalls/requirements.txt producers/recalls/requirements.txt
RUN pip install --no-cache-dir -r producers/recalls/requirements.txt

COPY producers/recalls/producer.py producers/recalls/producer.py
COPY schemas/cpsc_recalls/v1.avsc schemas/cpsc_recalls/v1.avsc

CMD ["python", "producers/recalls/producer.py"]
