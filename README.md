# Team ID=T012

# PROJECT ID =3

# PROJECT TITLE= Network Telemetry Framework

# TEAM

1)Bhava Ram Busa - 24110083

2)Moram Raghavendra Sri Koushik- 24110210

3)Vunnam Thushar Chowdary	 - 24110393

4)Ambati Chaitanya Ram- 24110035

5)Dudekula Mukkesh - 24110114

# Network Telemetry Monitoring System

A Docker-based network telemetry framework for collecting, transporting, storing, visualizing, and monitoring network performance metrics such as bandwidth utilization and latency.

The system uses SNMP-enabled containers to simulate network devices, a Python collector to gather and process telemetry, gRPC for collector-to-backend communication, PostgreSQL for historical storage, FastAPI for REST access, and Grafana for visualization and threshold-based alerting.

## Architecture

```text
                    SNMP
                     |
          +----------+----------+
          |                     |
   snmp-device          snmp-device-2
          |                     |
          +----------+----------+
                     |
                     v
             Python Collector
             collector.py
                     |
                    gRPC
                     |
                     v
              Central Backend
                server.py
                     |
                  SQL INSERT
                     |
                     v
                PostgreSQL
                 telemetry
                /          \
               /            \
              v              v
         FastAPI          Grafana
          api.py          Dashboards
                              |
                              v
                           Alerts
```

## Features

- Periodic collection of interface metrics through SNMP
- Incoming and outgoing bandwidth calculation
- Interface utilization calculation
- Latency measurement using ICMP ping
- Monitoring of multiple SNMP devices
- gRPC-based telemetry transport
- Historical telemetry storage in PostgreSQL
- REST API for historical data access
- CSV export through the REST API
- Grafana dashboards for utilization and latency
- Threshold-based Grafana alerting
- Docker-based isolated components

## Technologies

- Python
- PySNMP
- SNMP
- gRPC
- Protocol Buffers
- FastAPI
- PostgreSQL
- Grafana
- Docker
- ICMP

## Project Structure

```text
CN_PROJECT1/
|
├── collector/
│   ├── collector.py
│   ├── traffic.py
│   ├── Dockerfile
│   ├── telemetry_pb2.py
│   └── telemetry_pb2_grpc.py
│
├── backend/
│   ├── server.py
│   ├── api.py
│   ├── Dockerfile
│   ├── telemetry_pb2.py
│   ├── telemetry_pb2_grpc.py
│   └── proto/
│       ├── telemetry.proto
│       ├── telemetry_pb2.py
│       └── telemetry_pb2_grpc.py
│
├── db/
│   └── init.sql
│
├── snmp/
   └── snmpd.conf/
       └── snmpd.conf

```

## Components

### SNMP Devices

`snmp-device` and `snmp-device-2` run the `polinux/snmpd` image and simulate SNMP-enabled network devices. Their configuration is stored in `snmp/snmpd.conf/snmpd.conf`.

The devices expose standard SNMP objects such as interface counters and interface speed.

### Collector

`collector/collector.py` periodically queries the SNMP devices, measures latency, calculates bandwidth and utilization, and sends the processed telemetry to the backend using gRPC.

The collector currently polls approximately every 5 seconds.

### gRPC Contract

`backend/proto/telemetry.proto` defines the data exchanged between the collector and backend. The main RPC is:

```text
SendMetrics(TelemetryData) -> TelemetryAck
```

The generated Python support files are `telemetry_pb2.py` and `telemetry_pb2_grpc.py`.

### Backend

`backend/server.py` implements the gRPC service. It receives telemetry from the collector and stores the measurements in PostgreSQL.

### REST API

`backend/api.py` provides HTTP endpoints for accessing stored telemetry:

```text
GET /telemetry
GET /telemetry/export
```

`/telemetry` returns historical telemetry as JSON. `/telemetry/export` exports the stored telemetry as CSV.

FastAPI's interactive API documentation is available at:

```text
http://localhost:8000/docs
```

### PostgreSQL

PostgreSQL stores telemetry in the `telemetry` table. The schema is initialized from `db/init.sql` when a new database volume is initialized.

The table contains fields for:

```text
id
device_name
incoming_bps
outgoing_bps
incoming_utilization
outgoing_utilization
latency_ms
timestamp
```

### Grafana

Grafana reads telemetry from PostgreSQL and provides dashboards for:

- Incoming utilization
- Outgoing utilization
- Latency
- Device-based filtering
- Threshold-based alerts

## Metric Calculation

SNMP interface byte counters are cumulative counters. For two consecutive readings:

```text
traffic_bytes = current_counter - previous_counter
```

Bandwidth is calculated as:

```text
bandwidth_bps =
    (current_counter - previous_counter) * 8
    / elapsed_time_seconds
```

Utilization is calculated relative to interface capacity:

```text
utilization_percent =
    bandwidth_bps / interface_capacity_bps * 100
```

Latency is measured using ICMP ping.

The collector also handles counter resets by checking whether a newly received counter value is lower than the previous value.

## Running the System Manually

The project can be run manually with Docker .

### Prerequisites

Install Docker and ensure Docker is running.

Run the following commands from the project root unless stated otherwise.

### 1. Create the Docker network

```bash
docker network create network-lab
```

### 2. Start the first SNMP device

```bash
docker run -d \
  --name snmp-device \
  --network network-lab \
  -p 161:161/udp \
  -v "$(pwd)/snmp/snmpd.conf/snmpd.conf:/etc/snmp/snmpd.conf:ro" \
  polinux/snmpd
```

### 3. Start the second SNMP device

```bash
docker run -d \
  --name snmp-device \
  --network network-lab \
  -p 160:161/udp \
  -v "$(pwd)/snmp/snmpd.conf/snmpd.conf:/etc/snmp/snmpd.conf:ro" \
  polinux/snmpd
```


### 4. Start PostgreSQL

```bash
docker run -d \
  --name postgres \
  --network network-lab \
  -e POSTGRES_USER=telemetry \
  -e POSTGRES_PASSWORD=telemetry123 \
  -e POSTGRES_DB=telemetry_db \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  -v "$(pwd)/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" \
  postgres:17
```

Check that PostgreSQL is ready:

```bash
docker exec postgres pg_isready -U telemetry -d telemetry_db
```

Check the initialized tables:

```bash
docker exec -it postgres psql -U telemetry -d telemetry_db -c "\\dt"
```

### 5. Build the backend image

```bash
docker build -f backend/Dockerfile -t telemetry-backend .
```

### 6. Build the collector image

```bash
docker build -f collector/Dockerfile -t network-collector .
```

### 7. Start the backend

```bash
docker run -d \
  --name backend \
  --network network-lab \
  -p 50051:50051 \
  telemetry-backend
```

Check the backend logs:

```bash
docker logs backend
```

The gRPC server listens on port `50051`.

### 8. Start the FastAPI service

The same backend image contains `api.py`.

```bash
docker run -d \
  --name api \
  --network network-lab \
  -p 8000:8000 \
  telemetry-backend \
  uvicorn api:app --host 0.0.0.0 --port 8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

### 9. Start the collector

```bash
docker run -d \
  --name collector \
  --network network-lab \
  network-collector
```

Follow the collector logs:

```bash
docker logs -f collector
```

The collector should periodically report bandwidth, utilization, latency, and the backend acknowledgement.

### 10. Start Grafana

```bash
docker run -d \
  --name grafana \
  --network network-lab \
  -p 3000:3000 \
  grafana/grafana
```

Open:

```text
http://localhost:3000
```

Configure PostgreSQL as a Grafana datasource using:

```text
Host: postgres
Port: 5432
Database: telemetry_db
User: telemetry
Password: telemetry123
```

The hostname is `postgres` because Grafana and PostgreSQL communicate through the Docker network.

## REST API

### Get historical telemetry

```text
GET http://localhost:8000/telemetry
```

Returns the stored telemetry records as JSON.

### Export telemetry

```text
GET http://localhost:8000/telemetry/export
```

Returns the historical telemetry as CSV.

### API documentation

```text
http://localhost:8000/docs
```

## Grafana Configuration

Recommended panels are:

1. Incoming Utilization
2. Outgoing Utilization
3. Latency

Example query for incoming utilization:

```sql
SELECT
    to_timestamp(timestamp) AS "time",
    device_name,
    incoming_utilization
FROM telemetry
WHERE timestamp >= $__unixEpochFrom()
  AND timestamp <= $__unixEpochTo()
ORDER BY timestamp;
```

A dashboard device variable can be populated with:

```sql
SELECT DISTINCT device_name
FROM telemetry
ORDER BY device_name;
```

Threshold-based alert rules can then be configured for utilization and latency metrics.

## Traffic Generation

`collector/traffic.py` is a testing utility for generating UDP traffic toward a simulated device. It can be used to create changing interface traffic and verify that the collector detects the resulting counter changes.

The testing flow is:

```text
Traffic generation
       |
       v
SNMP counters increase
       |
       v
Collector detects counter difference
       |
       v
Bandwidth / utilization changes
       |
       v
PostgreSQL stores new values
       |
       v
Grafana displays the change
```

## Adding More Devices

The collector maintains a configurable list of monitored devices. A new device can be added by providing its name, hostname or IP address, and SNMP port. The same collection and processing logic is reused for the additional device.

## Notes

- The current collector configuration monitors a configured interface index for the interface counters used in bandwidth and utilization calculations.
- The Docker SNMP containers are simulations of SNMP-enabled network devices and can be replaced by authorized physical or virtual devices with suitable SNMP configuration.
- Grafana dashboards and datasource settings are configured through the Grafana interface in the current setup.
