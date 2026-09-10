FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y iputils-ping && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY collector/collector.py .
COPY collector/telemetry_pb2.py .
COPY collector/telemetry_pb2_grpc.py .

RUN pip install pysnmp grpcio protobuf

CMD ["python", "collector.py"]