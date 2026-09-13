# AI Prompts Used

## Overview

The following prompts document the types of prompts used during the development of the network telemetry project. They are presented as a single project-level prompt archive without assigning prompts to individual contributors.

---

## Project Understanding & Architecture

- "Explain the project requirements clearly and what each part means."
- "Let's start from the basics and explain the project requirements first."
- "How should we design the architecture for collecting bandwidth and latency from network devices?"
- "Explain each new technology before using it."
- "What should the complete data flow of this project look like?"
- "What components are actually necessary to satisfy the project requirements?"
- "How should the collector, backend, database, REST API and Grafana fit together?"
- "Is this architecture scalable to multiple routers and switches?"
- "Explain why the collector and backend should be separate components."

## SNMP & Network Telemetry

- "Explain SNMP from the basics."
- "What are SNMP agents, managers, OIDs and MIBs?"
- "What are ifDescr, ifInOctets, ifOutOctets, ifSpeed and ifHighSpeed?"
- "Explain how SNMP interface counters can be used to calculate bandwidth."
- "Why are SNMP octet counters multiplied by 8?"
- "How do cumulative counters become bits per second?"
- "What is the difference between Counter32 and Counter64?"
- "How should counter resets or counter wraparound be handled?"
- "What is SNMPv2c and how does it work?"
- "What is the difference between SNMPv2c and SNMPv3?"
- "Why is SNMPv2c suitable for this lab project?"
- "How would the same architecture work with SNMPv3 in a real deployment?"
- "Why did the SNMP OID return no such object?"
- "How can I verify an SNMP device manually using snmpget?"
- "How do I test SNMP connectivity to a Cisco router?"
- "What does an SNMPv3 'Unknown username' response mean?"
- "How should SNMP credentials be obtained for testing a real Cisco router?"

## Docker & Network Simulation

- "How can we simulate network devices using Docker?"
- "How do we create SNMP-enabled Docker containers?"
- "Explain Docker bridge networking and container-to-container communication."
- "Why use a user-defined bridge network?"
- "What is the difference between Docker's default bridge and a user-defined bridge network?"
- "How do containers communicate using service or container names?"
- "How do we create the SNMP devices manually without Docker Compose?"
- "Explain the Docker commands word by word."
- "How should the project containers be connected to the same Docker network?"
- "Why are Docker containers useful for simulating routers or switches in this project?"
- "What are the limitations of using Docker containers instead of real network devices?"

## Python Collector

- "Create a Python collector that polls SNMP metrics periodically."
- "How should the collector support multiple SNMP devices?"
- "Calculate incoming and outgoing bandwidth from cumulative SNMP counters."
- "Calculate interface utilization from bandwidth and interface speed."
- "Add latency measurement using ping."
- "How should the collector handle the first SNMP sample?"
- "How should the collector handle SNMP counter resets?"
- "How frequently should the collector poll the devices?"
- "Explain the collector code step by step."
- "Explain the SNMP OIDs and Python code before using them."
- "Why is the collector calculating a rate using two samples instead of directly reading bandwidth?"

## gRPC & Protocol Buffers

- "Explain gRPC before implementing it."
- "What are Protocol Buffers?"
- "Why use gRPC between the collector and backend?"
- "Create a telemetry.proto definition for the collected network metrics."
- "How should the collector send telemetry to the backend using gRPC?"
- "Create a Python gRPC server that receives telemetry."
- "Explain telemetry_pb2.py and telemetry_pb2_grpc.py."
- "What is the role of port 50051?"
- "Why use gRPC internally and REST externally?"
- "Explain the complete collector-to-backend gRPC data flow."

## PostgreSQL

- "Design a PostgreSQL table for storing network telemetry."
- "What columns are required to store bandwidth, utilization, latency and timestamps?"
- "Why should the telemetry table use a BIGSERIAL primary key?"
- "Why store the timestamp as a Unix epoch value?"
- "Create the SQL initialization script for the telemetry database."
- "How can I verify that telemetry records are being inserted into PostgreSQL?"
- "How can I query the latest telemetry records?"
- "How can I list the distinct devices stored in the database?"
- "Why should there be an index on device_name and timestamp?"

## FastAPI & REST

- "Explain REST APIs before implementing FastAPI."
- "Why do we need FastAPI if the collector already sends data to the backend?"
- "Create a FastAPI endpoint for historical telemetry."
- "Create a REST endpoint that returns telemetry as JSON."
- "Add a CSV export endpoint for historical telemetry."
- "Explain the difference between the collector and the FastAPI service."
- "How does FastAPI retrieve data from PostgreSQL?"
- "How can I test the API using Swagger UI?"
- "What is the role of port 8000?"

## Grafana & Visualization

- "How do I connect Grafana to PostgreSQL?"
- "Create a Grafana query for incoming utilization."
- "Create a Grafana query for outgoing utilization."
- "Create a Grafana query for latency."
- "How should the device dropdown variable be created in Grafana?"
- "Why is Grafana giving an invalid input syntax for type bigint error?"
- "How should Grafana time filters work when timestamps are stored as Unix epoch values?"
- "Create a PostgreSQL query compatible with Grafana Unix epoch time filters."
- "How do I create threshold-based alerts in Grafana?"
- "How should I configure an alert for utilization or latency?"
- "Why use a low threshold during demonstration testing?"
- "How can I show the alert changing to FIRING during the demo?"
- "Do we need SMTP or email configuration for the alert requirement?"

## Testing, Debugging & Validation

- "How can I test the complete data flow from SNMP to Grafana?"
- "How can I verify that the collector is receiving SNMP data?"
- "How can I verify that the backend is receiving gRPC messages?"
- "How can I verify that PostgreSQL is storing the telemetry?"
- "How can I verify the FastAPI historical-data endpoint?"
- "How can I generate traffic to make the bandwidth graph change?"
- "Why are the measured bandwidth values very small without generated traffic?"
- "How can I create a UDP traffic generator for testing?"
- "What should happen when an SNMP counter decreases?"
- "How can I verify that both simulated devices are producing telemetry?"
- "What Docker commands should be used to inspect the running containers?"
- "How can I inspect backend and collector logs?"
- "What ports are used by SNMP, gRPC, PostgreSQL, FastAPI and Grafana?"
- "Explain why HTTP and TCP are different."
- "Which protocol is used at each stage of the project?"

## Project Documentation & Presentation

- "Prepare a professional project report based on the implemented architecture."
- "Create a README explaining the architecture and setup."
- "Prepare a presentation structure for the project."
- "Explain what should be demonstrated during the live demo."
- "What questions might the professor ask about this project?"
- "How should the design choices be justified during the viva?"
- "Why use SNMPv2c instead of SNMPv3?"
- "Why use Docker instead of real routers and switches?"
- "Why use gRPC?"
- "Why use both gRPC and REST?"
- "Why use PostgreSQL?"
- "Why use FastAPI?"
- "Why use Grafana?"
- "What is RFC 9232 and how does it relate to this project?"
- "Is the project really real-time or near-real-time?"
- "How does the system scale to more devices?"
- "What are the limitations of the current implementation?"
