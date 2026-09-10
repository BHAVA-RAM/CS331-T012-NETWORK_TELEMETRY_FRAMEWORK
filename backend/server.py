from concurrent import futures
import grpc
import psycopg
import telemetry_pb2
import telemetry_pb2_grpc


class TelemetryService(telemetry_pb2_grpc.TelemetryServiceServicer):
    def __init__(self,connection):
        self.connection=connection
    def SendMetrics(self, request, context):
        print("Received telemetry:")
        print("Device:", request.device_name)
        print("Incoming:", request.incoming_bps, "bps")
        print("Outgoing:", request.outgoing_bps, "bps")
        print("Incoming utilization:", request.incoming_utilization, "%")
        print("Outgoing utilization:", request.outgoing_utilization, "%")
        print("Latency:", request.latency_ms, "ms")
        print("Timestamp:", request.timestamp)
        print()
        self.connection.execute(
        """
        INSERT INTO telemetry (
            device_name,
            incoming_bps,
            outgoing_bps,
            incoming_utilization,
            outgoing_utilization,
            latency_ms,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            request.device_name,
            request.incoming_bps,
            request.outgoing_bps,
            request.incoming_utilization,
            request.outgoing_utilization,
            request.latency_ms,
            request.timestamp
        )
        )

        self.connection.commit()

        return telemetry_pb2.TelemetryAck(
            status="Metrics received"
        )


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )
    connection=psycopg.connect(host="postgres",port=5432,dbname="telemetry_db",user="telemetry",password="telemetry123")

    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(
        TelemetryService(connection),
        server
    )

    server.add_insecure_port("[::]:50051")
    server.start()

    print("Telemetry gRPC server started on port 50051")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()