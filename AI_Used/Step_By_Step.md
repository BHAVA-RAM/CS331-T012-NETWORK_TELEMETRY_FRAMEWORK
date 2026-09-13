# Step-by-Step Development Process

## Project Development Pipeline

The project was developed incrementally so that each major component could be understood, implemented, tested, and then connected to the next component.

```text
Project Requirements
        ↓
Architecture Design
        ↓
SNMP Device Simulation
        ↓
SNMP Metric Verification
        ↓
Python Collector
        ↓
Bandwidth / Utilization / Latency Calculation
        ↓
gRPC Telemetry Transport
        ↓
Central Backend
        ↓
PostgreSQL Storage
        ↓
FastAPI REST Interface
        ↓
Grafana Visualization & Alerts
        ↓
Traffic Generation
        ↓
End-to-End Validation
```

---

## Stage 1: Requirement Analysis

1. Break the project statement into its required functions.
2. Identify the required network metrics:
   - Bandwidth usage
   - Interface utilization
   - Latency
3. Identify the required system capabilities:
   - Periodic collection
   - Central transport
   - Persistent storage
   - Real-time/near-real-time visualization
   - Threshold-based alerting
   - Historical REST access and export
   - Support for multiple devices
4. Identify optional technologies from the project statement and determine where they could fit.

---

## Stage 2: Architecture Design

1. Separate the system into independent components.
2. Use a **collector** for communication with network devices.
3. Use **SNMP** for device metric collection.
4. Use **gRPC** for structured collector-to-backend transport.
5. Use a **backend** to receive telemetry.
6. Use **PostgreSQL** for persistent historical storage.
7. Use **FastAPI** as the external REST interface.
8. Use **Grafana** for visualization and alerting.
9. Use Docker to make the complete laboratory setup reproducible.

The resulting architecture was:

```text
SNMP Devices
     │
     │ SNMP polling
     ▼
Python Collector
     │
     │ gRPC / Protobuf
     ▼
Central Backend
     │
     │ SQL
     ▼
PostgreSQL
   /     \
  /       \
 ▼         ▼
FastAPI   Grafana
 REST     Dashboards
          + Alerts
```

---

## Stage 3: SNMP Device Simulation

1. Create Docker containers representing SNMP-enabled network devices.
2. Use `polinux/snmpd` as the SNMP agent.
3. Configure a read-only SNMP community.
4. Create two simulated devices so that multi-device collection can be demonstrated.
5. Place the containers on a user-defined Docker bridge network.
6. Use container names for communication instead of hard-coding container IP addresses.

The project network was designed as:

```text
network-lab
 ├── snmp-device
 ├── snmp-device-2
 ├── collector
 ├── backend
 ├── postgres
 ├── api
 └── grafana
```

---

## Stage 4: Manual SNMP Verification

Before writing the collector, verify that the SNMP agents actually expose the required information.

1. Test the system description OID.
2. Inspect interface descriptions.
3. Identify the required interface.
4. Verify incoming and outgoing octet counters.
5. Verify interface speed.
6. Verify the high-speed interface value when required.
7. Confirm that the selected OIDs return usable values.

Important OIDs used:

```text
sysDescr
.1.3.6.1.2.1.1.1.0

ifDescr
.1.3.6.1.2.1.2.2.1.2

ifInOctets
.1.3.6.1.2.1.2.2.1.10

ifOutOctets
.1.3.6.1.2.1.2.2.1.16

ifHighSpeed
.1.3.6.1.2.1.31.1.1.1.15
```

The collector uses the high-capacity 64-bit interface counters for bandwidth calculations.

---

## Stage 5: Python Collector

1. Create the Python collector.
2. Store the simulated devices in a device list.
3. Configure SNMP access for each device.
4. Poll the selected interface counters periodically.
5. Store the previous counter values for each device.
6. Calculate the counter difference between two samples.
7. Convert the byte difference to bits by multiplying by 8.
8. Divide by elapsed time to obtain bits per second.
9. Calculate utilization from measured bandwidth and interface speed.
10. Measure latency using `ping`.
11. Add the current timestamp.
12. Repeat the process at a fixed interval.

The basic bandwidth calculation is:

```text
delta_bytes = current_counter - previous_counter

bits = delta_bytes × 8

bps = bits / elapsed_time
```

Utilization is calculated as:

```text
utilization (%) =
    (measured_bps / interface_speed_bps) × 100
```

Counter-reset protection was added so that an invalid negative delta does not produce an incorrect bandwidth spike.

---

## Stage 6: gRPC Transport

1. Define the telemetry message in `telemetry.proto`.
2. Include:
   - Device name
   - Incoming bps
   - Outgoing bps
   - Incoming utilization
   - Outgoing utilization
   - Latency
   - Timestamp
3. Define the `SendMetrics` RPC.
4. Generate the Python Protocol Buffer and gRPC files.
5. Create the backend gRPC service.
6. Connect the collector to the backend.
7. Send each collected telemetry sample through gRPC.
8. Return an acknowledgement from the backend.

This creates a clear internal contract between the collector and central backend.

---

## Stage 7: PostgreSQL Storage

1. Create the PostgreSQL container.
2. Create the telemetry database and user.
3. Create the `telemetry` table.
4. Store every received telemetry sample.
5. Add a primary key.
6. Store the timestamp with each record.
7. Add an index on device and timestamp.
8. Verify stored records using SQL queries.

The stored data provides the historical layer required by the project.

---

## Stage 8: FastAPI REST Interface

1. Create the FastAPI application.
2. Connect FastAPI to PostgreSQL.
3. Implement `GET /telemetry`.
4. Return historical telemetry as JSON.
5. Implement `GET /telemetry/export`.
6. Convert the stored records to CSV.
7. Test both endpoints using the automatically generated Swagger UI.

The responsibility is separated clearly:

```text
Collector → collects data

Backend → receives and stores data

FastAPI → exposes historical data

Grafana → visualizes and alerts
```

---

## Stage 9: Grafana Dashboards

1. Start Grafana.
2. Add PostgreSQL as a data source.
3. Configure the database connection.
4. Create a device variable using distinct device names.
5. Create an incoming-utilization panel.
6. Create an outgoing-utilization panel.
7. Create a latency panel.
8. Configure the time field correctly.
9. Use Unix-epoch-aware Grafana macros because the database stores timestamps as BIGINT values.
10. Verify that data changes appear on the dashboard.

The Grafana query uses the Unix epoch filter rather than comparing an ISO timestamp directly with a BIGINT column.

---

## Stage 10: Threshold-Based Alerting

1. Select the metric query used by a panel.
2. Reduce the query to the latest value.
3. Define a threshold.
4. Configure the evaluation interval.
5. Configure the pending period.
6. Configure the keep-firing duration.
7. Generate a metric change large enough to cross the threshold.
8. Verify that Grafana changes the alert state to `FIRING`.

For demonstration, a deliberately low threshold can be used so the alert can be triggered reliably.

---

## Stage 11: Traffic Generation

1. Create a small Python UDP traffic generator.
2. Send repeated UDP datagrams toward the second simulated device.
3. Allow the collector to observe the resulting counter changes.
4. Compare the dashboard before and during traffic generation.
5. Stop the traffic generator.
6. Observe the resulting change in the telemetry graph and alert state.

This provides a controlled way to demonstrate that changing traffic affects the collected metrics.

---

## Stage 12: End-to-End Validation

Each layer was checked independently and then as one complete pipeline:

```text
SNMP query works
      ↓
Collector receives counters
      ↓
Collector calculates rates
      ↓
Latency is measured
      ↓
gRPC message reaches backend
      ↓
PostgreSQL stores record
      ↓
FastAPI returns historical record
      ↓
Grafana plots the record
      ↓
Threshold alert reacts to metric
```

This validation approach makes it possible to isolate failures instead of debugging the entire system at once.

---

## Stage 13: Real-Device Consideration

The Docker SNMP containers provide a controlled laboratory environment.

For a real router or switch, the collector would instead use:

```text
Collector
   │
   │ SNMP
   ▼
Router/Switch management IP
   │
   └── UDP port 161
```

The same collection and processing logic can be retained while changing the target device, SNMP version, credentials, and interface information.
