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

## Running the Project
 
1. Start the Docker containers: `docker-compose up -d`
 
2. Access the API: API endpoints will be available at http://localhost:8000
 
3. Run the workload simulator (after containers are up):
`python workload_simulator.py --duration 300 --workers 5`
This will simulate traffic for 5 minutes with 5 concurrent workers.
 
4. Monitor Kafka (optional): Access Kafka UI at http://localhost:8080
 
5. View logs and metrics in Grafana: Access Grafana at http://localhost:3000
```language:none
Default credentials: admin/admin
 
You'll need to configure a PostgreSQL data source in Grafana:
Host: postgres:5432
Database: logly_db
User: logly
Password: logly_password
```
 
6. Shut down the project (when finished): `docker-compose down`