import time
import json
import uuid
import socket
import traceback
from typing import Callable, Dict, Any

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from kafka import KafkaProducer


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        kafka_bootstrap_servers: str = "kafka:9092",
        request_topic: str = "request-logs",
        response_topic: str = "response-logs",
        error_topic: str = "error-logs",
    ):
        super().__init__(app)
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.request_topic = request_topic
        self.response_topic = response_topic
        self.error_topic = error_topic
        self.hostname = socket.gethostname()
        self._init_kafka_producer()

    def _init_kafka_producer(self):
        """Initialize the Kafka producer or set to None if connection fails."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda v: v.encode("utf-8") if v else None,
            )
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}")
            self.producer = None

    def _send_to_kafka(self, topic: str, key: str, value: Dict[str, Any]):
        """Send message to Kafka topic with retry logic."""
        if not self.producer:
            try:
                self._init_kafka_producer()
            except Exception:
                print("Still unable to connect to Kafka")
                return

        try:
            if self.producer:
                self.producer.send(topic, key=key, value=value)
                self.producer.flush(timeout=1)
        except Exception as e:
            print(f"Error sending to Kafka: {e}")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()

        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else None,
            "timestamp": start_time,
            "hostname": self.hostname,
        }

        self._send_to_kafka(self.request_topic, request_id, request_info)

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            if response.status_code >= 400:
                error_info = {
                    "request_id": request_id,
                    "error": f"HTTP {response.status_code}",
                    "traceback": "",
                    "processing_time_ms": process_time * 1000,
                    "timestamp": time.time(),
                    "hostname": self.hostname,
                }
                self._send_to_kafka(self.error_topic, request_id, error_info)
            else:
                response_info = {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "processing_time_ms": process_time * 1000,
                    "timestamp": time.time(),
                    "hostname": self.hostname,
                }
                self._send_to_kafka(self.response_topic, request_id, response_info)

            response.headers["X-Process-Time"] = str(process_time)
            return response

        except Exception as exc:
            process_time = time.time() - start_time
            error_info = {
                "request_id": request_id,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "processing_time_ms": process_time * 1000,
                "timestamp": time.time(),
                "hostname": self.hostname,
            }
            self._send_to_kafka(self.error_topic, request_id, error_info)
            raise