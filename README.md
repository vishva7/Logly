# Logly

Log Analytics Platform is designed to collect, process, and visualize log data in real time. 

It leverages Grafana for visualization, Kafka for real-time log ingestion, and a relational database for storage.

Built for Cloud Computing course mini-project (UE22CS351B).

## Features

The platform visualizes the following metrics in Grafana:
- Request Count per Endpoint: Track the number of requests made to each API endpoint.
- Response Time Trends: Display response time patterns over different time periods.
- Most Frequent Errors in the Application: Identify and highlight recurring errors.
- Real-Time Logs: Provide a live feed of logs for monitoring purposes.

## Technology Stack

- Containerization: Docker
- Simulated server endpoints: FastAPI
- Message Broker: Apache Kafka for log ingestion
- Visualization: Grafana for querying and visualizing log data