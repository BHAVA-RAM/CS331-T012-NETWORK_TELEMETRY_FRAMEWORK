# AI Tools Utilized

## Overview

AI tools were used throughout the development of the network telemetry project as development and technical-assistance tools. The project design, implementation choices, testing, debugging, and validation were carried out iteratively, with AI assistance used where it helped explain concepts, generate or refine code, diagnose errors, and organize documentation.

The AI-assisted work covered the complete development cycle:

- Understanding and breaking down the project requirements
- Learning SNMP, OIDs, MIBs, counters, and telemetry concepts
- Designing the collector–backend–database–visualization architecture
- Writing and refining Python, gRPC, FastAPI, SQL, Docker, and Grafana configurations
- Debugging SNMP, Docker, PostgreSQL, Grafana, and networking issues
- Designing test cases and traffic-generation methods
- Preparing project documentation and presentation material

---

## AI Tools

### 1. OpenAI ChatGPT

**Usage scope:**

- Project requirement analysis
- Architecture planning
- Explanation of networking and telemetry concepts
- SNMP and OID understanding
- Python collector development
- gRPC and Protocol Buffers implementation
- PostgreSQL schema and queries
- FastAPI endpoint development
- Docker and Docker-network troubleshooting
- Grafana dashboard and alert configuration
- Debugging runtime and configuration errors
- Project report, README, and presentation preparation
- Viva-question preparation and explanation of design decisions

**Typical assistance:**

- Explaining a new technology before implementation
- Converting a requirement into an implementation step
- Reviewing code and identifying errors
- Explaining why an implementation decision is appropriate
- Suggesting controlled tests for individual components and the complete pipeline

---

## Technical Development Environment

| Component | Technology / Configuration |
| :--- | :--- |
| Operating environment | Windows + WSL2 Ubuntu |
| Programming language | Python |
| Network telemetry | SNMPv2c |
| SNMP simulation | Docker containers using `polinux/snmpd` |
| Internal communication | gRPC + Protocol Buffers |
| Backend storage | PostgreSQL 17 |
| REST interface | FastAPI |
| Visualization & alerting | Grafana |
| Containerization | Docker |
| Container networking | User-defined Docker bridge network |
| Testing traffic | Python UDP traffic generator |
| API documentation | FastAPI / Swagger UI |

---

## Role of AI in the Development Process

AI was used as an engineering assistant rather than as a replacement for testing or validation.

The general workflow was:

```text
Requirement / Problem
        ↓
Understand the concept
        ↓
Ask AI for explanation or implementation guidance
        ↓
Implement / modify the project
        ↓
Run the system
        ↓
Observe output or error
        ↓
Use AI to diagnose the issue when required
        ↓
Fix and retest
        ↓
Validate the final behavior
```

The final implementation was checked against the actual project requirements and runtime behavior rather than being accepted solely from generated output.
