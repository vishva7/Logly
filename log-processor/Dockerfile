FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir kafka-python psycopg2-binary

COPY log_processor.py .

CMD ["python", "log_processor.py"]