# Engineering Thought Process

## Human-Driven, AI-Assisted Development

The project followed a human-driven engineering workflow in which AI was used to accelerate implementation and troubleshooting while the architecture, requirements, testing decisions, and final validation remained tied to the actual project behavior.

The reasoning process can be summarized as:

```text
Requirement
    ↓
What must the system do?
    ↓
Which component should perform that responsibility?
    ↓
How should the components communicate?
    ↓
Implement one layer
    ↓
Test the layer
    ↓
Connect it to the next layer
    ↓
Observe real output
    ↓
Debug and refine
    ↓
Validate end-to-end
```

---

## 1. Turning the Requirement into Components

The project statement contains several different responsibilities rather than one single task.

The first design question was:

> What component should perform each responsibility?

This led to the separation:

| Requirement | Component |
| :--- | :--- |
| Collect router/switch metrics | Python Collector |
| Obtain network-device information | SNMP |
| Transport telemetry centrally | gRPC |
| Store historical measurements | PostgreSQL |
| Provide external access | FastAPI |
| Visualize metrics | Grafana |
| Generate controlled test traffic | Python traffic generator |
| Reproduce the laboratory environment | Docker |

This separation prevents one component from becoming responsible for the entire system.

---

## 2. Choosing SNMP for Device Collection

SNMP was selected because the project specifically concerns routers and switches and their operational metrics.

The important observation was that SNMP interface counters are cumulative values rather than instantaneous bandwidth values.

For example:

```text
Sample 1 → 1,000,000 octets
Sample 2 → 1,500,000 octets
```

The difference represents:

```text
500,000 octets transferred
```

Over a known time interval, this can be converted into a rate.

Therefore:

```text
bps = ((current_counter - previous_counter) × 8)
      / elapsed_time
```

This is more meaningful for bandwidth monitoring than treating a single counter value as a bandwidth measurement.

---

## 3. Handling Counter Resets

A counter normally increases:

```text
1000 → 2000 → 3000 → 4000
```

But a restart or counter reset can produce:

```text
3000 → 500
```

A naive calculation would produce a large negative value.

The collector therefore checks:

```text
current < previous
```

When this happens, the previous value is replaced with the current value and the sample is skipped for rate calculation.

This avoids producing a false bandwidth spike.

---

## 4. Choosing SNMPv2c for the Laboratory

SNMPv2c was selected because the project is being demonstrated in a controlled Docker-based environment and requires straightforward metric collection.

The reasoning was:

- Simple configuration
- Easy integration with the simulated SNMP agents
- Sufficient for the required telemetry demonstration
- Less configuration overhead for a laboratory prototype

SNMPv3 is the more appropriate choice for a production deployment because it supports authentication and privacy.

The architecture was kept independent enough that the SNMP access layer can be changed to SNMPv3 later.

---

## 5. Why Docker Is Used

Physical routers and switches are not required to demonstrate the complete software pipeline.

Docker provides simulated SNMP devices that can be controlled and reproduced consistently.

The important distinction is:

```text
Docker = simulation/containerization environment

SNMP = network-device telemetry protocol
```

Docker is therefore not replacing SNMP. It provides the devices on which SNMP can be tested.

---

## 6. Why a User-Defined Bridge Network Is Used

All project containers need to communicate with one another.

A user-defined Docker bridge network provides:

- A dedicated project network
- Container-to-container communication
- Automatic DNS resolution using container names
- Isolation from unrelated containers
- Less dependence on changing container IP addresses

For example:

```text
collector → snmp-device
collector → snmp-device-2
collector → backend
backend   → postgres
api       → postgres
grafana   → postgres
```

Container names are therefore preferable to hard-coded dynamic IP addresses.

---

## 7. Why the Collector Is Separate from the Backend

The collector and backend have different responsibilities.

```text
Collector:
- Talks to network devices
- Polls SNMP
- Calculates metrics
- Measures latency
- Sends telemetry

Backend:
- Receives telemetry
- Provides the central ingestion point
- Stores the measurements
```

This separation makes the architecture modular.

A future deployment could run multiple collectors while keeping a central backend.

---

## 8. Why gRPC Is Used Internally

The collector needs to continuously send structured telemetry to the central backend.

gRPC with Protocol Buffers provides:

- A defined message schema
- Strongly structured data
- Efficient binary serialization
- A clear RPC interface
- A clean service-to-service communication model

The telemetry contract explicitly defines fields such as:

```text
device_name
incoming_bps
outgoing_bps
incoming_utilization
outgoing_utilization
latency_ms
timestamp
```

This avoids loosely structured internal messages.

---

## 9. Why REST Is Also Used

gRPC and REST are not redundant in this architecture.

They serve different purposes:

```text
Collector
   │
   │ gRPC
   ▼
Backend
   │
   ▼
PostgreSQL
   ▲
   │ REST
FastAPI
```

gRPC is used for internal telemetry ingestion.

REST is used to expose stored historical data to external clients.

This allows another application to request telemetry without needing to understand the internal gRPC service.

---

## 10. Why PostgreSQL Is Used

The project requires historical access to collected measurements.

Keeping data only in memory would lose it when the backend stops.

PostgreSQL provides persistent storage for:

- Device identity
- Incoming bandwidth
- Outgoing bandwidth
- Utilization
- Latency
- Timestamp

The database therefore acts as the historical source for both FastAPI and Grafana.

---

## 11. Why FastAPI Is Separate

FastAPI does not collect SNMP data.

Its responsibility is to expose information already stored in PostgreSQL.

For example:

```text
GET /telemetry
```

returns historical records as JSON.

And:

```text
GET /telemetry/export
```

provides CSV export.

This keeps the data-collection mechanism separate from the external API layer.

---

## 12. Why Grafana Is Used

Grafana is responsible for turning stored telemetry into an operational monitoring interface.

The dashboard can show:

- Incoming utilization
- Outgoing utilization
- Latency
- Multiple devices
- Historical trends
- Alert states

Grafana also provides the threshold-based alerting required by the project.

---

## 13. Real-Time vs Near-Real-Time

The collector polls the devices periodically rather than receiving an event for every network packet.

Therefore the technically accurate description is:

> **Near-real-time periodic monitoring.**

With a polling interval of approximately five seconds, the system continuously updates the backend and dashboard with recent measurements.

Calling it “real-time” in the project statement is acceptable in the practical monitoring sense, but the implementation is more precisely periodic near-real-time telemetry.

---

## 14. Debugging Through the Data Path

When an issue occurs, the system is debugged from the source toward the visualization layer:

```text
SNMP
 ↓
Collector
 ↓
gRPC
 ↓
Backend
 ↓
PostgreSQL
 ↓
FastAPI / Grafana
```

For example, if Grafana shows no data, the problem should not immediately be assumed to be Grafana.

The database is checked first.

If the database is empty, the backend is checked.

If the backend receives nothing, the collector is checked.

If the collector cannot obtain values, SNMP is checked.

This layered approach reduces debugging time.

---

## 15. Important Issue: Grafana Timestamp Type

The database stores:

```text
timestamp BIGINT
```

containing Unix epoch time.

Grafana's normal time-filter macro can expand into timestamp values that PostgreSQL treats as date/time values.

Comparing those directly against a BIGINT column causes a type mismatch.

The solution was to use Unix-epoch-aware Grafana macros:

```sql
WHERE timestamp >= $__unixEpochFrom()
  AND timestamp <= $__unixEpochTo()
```

and convert the timestamp for display:

```sql
to_timestamp(timestamp) AS "time"
```

This keeps the stored representation simple while making the query compatible with Grafana.

---

## 16. Testing the System with Generated Traffic

Normal background traffic may be too small to make changes obvious in a demonstration.

A controlled UDP traffic generator was therefore used to produce repeatable traffic toward a simulated device.

The purpose is not to emulate a complete router workload.

It is to create a controlled change in traffic so that:

```text
Traffic increases
      ↓
SNMP counters increase faster
      ↓
Collector calculates higher bps
      ↓
Utilization changes
      ↓
Grafana graph changes
      ↓
Alert threshold can be crossed
```

This provides a visible end-to-end demonstration.

---

## 17. Alerting Strategy

The project requires threshold-based alerting, not necessarily email delivery.

Therefore the implementation focuses on showing the Grafana alert state.

For demonstration, a low threshold can be selected intentionally so that the alert can be triggered reliably.

The important mechanism is:

```text
Metric
  ↓
Query
  ↓
Reduce to latest value
  ↓
Compare with threshold
  ↓
Alert state
```

In a production environment, thresholds would be chosen from meaningful operational limits rather than demonstration-friendly values.

---

## 18. Scalability Considerations

The current implementation supports multiple devices through a device list.

The architecture is modular enough to extend the collector to more devices.

For larger deployments, additional improvements could include:

- Parallel/asynchronous SNMP polling
- Multiple collector instances
- Collector load balancing
- Batched database writes
- Database partitioning or retention policies
- More efficient metric transport
- Additional telemetry protocols
- OpenTelemetry integration

The current project demonstrates the architecture without requiring production-scale infrastructure.

---

## 19. Role of AI in the Engineering Process

AI assistance was primarily useful in four areas:

### Understanding

Explaining unfamiliar technologies such as:

- SNMP
- OIDs
- MIBs
- gRPC
- Protocol Buffers
- FastAPI
- Grafana
- Docker networking
- RFC 9232

### Implementation

Providing starting points and refinements for:

- Python collector logic
- gRPC service definitions
- PostgreSQL schema
- FastAPI endpoints
- Dockerfiles
- Grafana queries

### Debugging

Helping analyze issues such as:

- Incorrect SNMP OIDs
- Docker connectivity
- PostgreSQL verification
- Grafana BIGINT timestamp errors
- Counter-reset behavior

### Documentation

Helping organize:

- Architecture explanations
- Setup instructions
- Testing procedures
- Design rationale
- Presentation material

Generated suggestions were treated as starting points and checked against actual execution results.

---

## 20. Final Engineering Principle

The project was developed component-by-component rather than treating the complete system as one large program.

The central principle was:

```text
Understand → Implement → Run → Observe → Debug → Retest → Integrate
```

This made it possible to verify each layer independently and then demonstrate the complete telemetry path from a network device to the final monitoring dashboard.
