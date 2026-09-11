FROM python:3.12-slim

WORKDIR /app

COPY backend/server.py .
COPY backend/api.py .
COPY backend/telemetry_pb2.py .
COPY backend/telemetry_pb2_grpc.py .

RUN pip install --no-cache-dir grpcio protobuf "psycopg[binary]" fastapi uvicorn

CMD ["python", "server.py"]