FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY producers/camira_fabrics/requirements.txt producers/camira_fabrics/requirements.txt
RUN pip install --no-cache-dir -r producers/camira_fabrics/requirements.txt

COPY producers/camira_fabrics/producer.py producers/camira_fabrics/producer.py
COPY schemas/camira_fabrics/v1.avsc schemas/camira_fabrics/v1.avsc

CMD ["python", "producers/camira_fabrics/producer.py"]
