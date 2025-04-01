import json
import time
import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaConsumer

DB_PARAMS = {
    "host": "postgres",
    "database": "logly_db",
    "user": "logly",
    "password": "logly_password",
}

KAFKA_BOOTSTRAP_SERVERS = ["kafka:9092"]
CONSUMER_GROUP_ID = "log-processor-group"
TOPICS = ["request-logs", "response-logs", "error-logs"]


def create_tables(conn):
    """Create necessary tables if they don't exist."""
    cursor = conn.cursor()

    # Request logs table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS request_logs (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(36) NOT NULL,
            method VARCHAR(10) NOT NULL,
            url TEXT NOT NULL,
            client_host VARCHAR(50),
            timestamp DOUBLE PRECISION NOT NULL,
            hostname VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Response logs table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS response_logs (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(36) NOT NULL,
            status_code INTEGER NOT NULL,
            processing_time_ms DOUBLE PRECISION NOT NULL,
            timestamp DOUBLE PRECISION NOT NULL,
            hostname VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Error logs table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS error_logs (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(36) NOT NULL,
            error TEXT NOT NULL,
            traceback TEXT,
            processing_time_ms DOUBLE PRECISION NOT NULL,
            timestamp DOUBLE PRECISION NOT NULL,
            hostname VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    cursor.close()


def batch_insert_messages(conn, table_name, columns, values):
    """Insert multiple messages into the specified table."""
    cursor = conn.cursor()
    query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES %s
    """

    execute_values(cursor, query, values)
    conn.commit()
    cursor.close()


def process_request_logs(conn, messages):
    """Process and store request logs."""
    columns = ["request_id", "method", "url", "client_host", "timestamp", "hostname"]
    values = []

    for msg in messages:
        data = msg.value
        values.append(
            (
                data["request_id"],
                data["method"],
                data["url"],
                data["client_host"],
                data["timestamp"],
                data["hostname"],
            )
        )

    batch_insert_messages(conn, "request_logs", columns, values)


def process_response_logs(conn, messages):
    """Process and store response logs."""
    columns = [
        "request_id",
        "status_code",
        "processing_time_ms",
        "timestamp",
        "hostname",
    ]
    values = []

    for msg in messages:
        data = msg.value
        values.append(
            (
                data["request_id"],
                data["status_code"],
                data["processing_time_ms"],
                data["timestamp"],
                data["hostname"],
            )
        )

    batch_insert_messages(conn, "response_logs", columns, values)


def process_error_logs(conn, messages):
    """Process and store error logs."""
    columns = [
        "request_id",
        "error",
        "traceback",
        "processing_time_ms",
        "timestamp",
        "hostname",
    ]
    values = []

    for msg in messages:
        data = msg.value
        values.append(
            (
                data["request_id"],
                data["error"],
                data.get("traceback", ""),
                data["processing_time_ms"],
                data["timestamp"],
                data["hostname"],
            )
        )

    batch_insert_messages(conn, "error_logs", columns, values)


def main():
    print("Log processor starting up...")

    max_retries = 10
    retry_interval = 5

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            print("Connected to PostgreSQL database")
            create_tables(conn)
            break
        except Exception as e:
            print(f"Failed to connect to PostgreSQL (attempt {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print("Maximum retries reached. Exiting...")
                return

    # Try to connect to Kafka
    for i in range(max_retries):
        try:
            consumer = KafkaConsumer(
                *TOPICS,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=CONSUMER_GROUP_ID,
                auto_offset_reset="earliest",
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                enable_auto_commit=False,
                max_poll_records=100,
            )
            print("Connected to Kafka")
            break
        except Exception as e:
            print(f"Failed to connect to Kafka (attempt {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print("Maximum retries reached. Exiting...")
                conn.close()
                return

    print("Log processor is running. Waiting for messages...")

    try:
        while True:
            messages = consumer.poll(timeout_ms=1000, max_records=100)

            if not messages:
                continue

            request_logs = []
            response_logs = []
            error_logs = []

            for tp, msgs in messages.items():
                for msg in msgs:
                    if tp.topic == "request-logs":
                        request_logs.append(msg)
                    elif tp.topic == "response-logs":
                        response_logs.append(msg)
                    elif tp.topic == "error-logs":
                        error_logs.append(msg)

            if request_logs:
                process_request_logs(conn, request_logs)
                print(f"Processed {len(request_logs)} request logs")
            if response_logs:
                process_response_logs(conn, response_logs)
                print(f"Processed {len(response_logs)} response logs")
            if error_logs:
                process_error_logs(conn, error_logs)
                print(f"Processed {len(error_logs)} error logs")
            consumer.commit()

    except KeyboardInterrupt:
        print("Shutting down log processor...")
    finally:
        if consumer:
            consumer.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
