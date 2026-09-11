import csv
from io import StringIO

import psycopg
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "dbname": "telemetry_db",
    "user": "telemetry",
    "password": "telemetry123"
}


def get_connection():
    return psycopg.connect(**DB_CONFIG)


@app.get("/telemetry")
def get_telemetry():

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                device_name,
                incoming_bps,
                outgoing_bps,
                incoming_utilization,
                outgoing_utilization,
                latency_ms,
                timestamp
            FROM telemetry
            ORDER BY id;
            """
        ).fetchall()

    return [
        {
            "id": row[0],
            "device_name": row[1],
            "incoming_bps": row[2],
            "outgoing_bps": row[3],
            "incoming_utilization": row[4],
            "outgoing_utilization": row[5],
            "latency_ms": row[6],
            "timestamp": row[7]
        }
        for row in rows
    ]


@app.get("/telemetry/export")
def export_telemetry():

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                device_name,
                incoming_bps,
                outgoing_bps,
                incoming_utilization,
                outgoing_utilization,
                latency_ms,
                timestamp
            FROM telemetry
            ORDER BY id;
            """
        ).fetchall()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "id",
        "device_name",
        "incoming_bps",
        "outgoing_bps",
        "incoming_utilization",
        "outgoing_utilization",
        "latency_ms",
        "timestamp"
    ])

    writer.writerows(rows)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=telemetry.csv"
        }
    )