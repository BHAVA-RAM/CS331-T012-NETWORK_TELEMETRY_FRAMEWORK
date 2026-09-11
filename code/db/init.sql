CREATE TABLE IF NOT EXISTS telemetry (
    id BIGSERIAL PRIMARY KEY,
    device_name TEXT NOT NULL,
    incoming_bps DOUBLE PRECISION NOT NULL,
    outgoing_bps DOUBLE PRECISION NOT NULL,
    incoming_utilization DOUBLE PRECISION NOT NULL,
    outgoing_utilization DOUBLE PRECISION NOT NULL,
    latency_ms DOUBLE PRECISION NOT NULL,
    timestamp BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_telemetry_device_timestamp
ON telemetry (device_name, timestamp);