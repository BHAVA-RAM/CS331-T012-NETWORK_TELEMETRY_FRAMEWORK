import asyncio
import time
import subprocess

import grpc

import telemetry_pb2
import telemetry_pb2_grpc

from pysnmp.hlapi.v1arch.asyncio import (
    SnmpDispatcher,
    CommunityData,
    UdpTransportTarget,
    ObjectType,
    ObjectIdentity,
    get_cmd,
)


devices = [
    {
        "name": "snmp-device",
        "host": "snmp-device",
        "port": 161
    },
    {
        "name": "snmp-device-2",
        "host": "snmp-device-2",
        "port": 161
    }
]


# Retrieve cumulative 64-bit counter for incoming traffic
async def get_in_octets(device):
    with SnmpDispatcher() as snmpDispatcher:
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public"),
            await UdpTransportTarget.create(
                (device["host"], device["port"])
            ),
            ObjectType(
                # ifHCInOctets for interface 2
                ObjectIdentity("1.3.6.1.2.1.31.1.1.1.6.2")
            ),
        )

        if errorIndication:
            print("SNMP error:", errorIndication)
            return None

        elif errorStatus:
            print("SNMP error:", errorStatus)
            return None

        else:
            for varBind in varBinds:
                return int(varBind[1])


# Retrieve interface bandwidth
async def get_high_speed(device):
    with SnmpDispatcher() as snmpDispatcher:
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public"),
            await UdpTransportTarget.create(
                (device["host"], device["port"])
            ),
            ObjectType(
                ObjectIdentity("1.3.6.1.2.1.31.1.1.1.15.2")
            ),
        )

        if errorIndication:
            print("SNMP error:", errorIndication)
            return None

        elif errorStatus:
            print("SNMP error:", errorStatus)
            return None

        else:
            for varBind in varBinds:
                return int(varBind[1])


# Retrieve cumulative 64-bit counter for outgoing traffic
async def get_out_octets(device):
    with SnmpDispatcher() as snmpDispatcher:
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public"),
            await UdpTransportTarget.create(
                (device["host"], device["port"])
            ),
            ObjectType(
                # ifHCOutOctets for interface 2
                ObjectIdentity("1.3.6.1.2.1.31.1.1.1.10.2")
            ),
        )

        if errorIndication:
            print("SNMP error:", errorIndication)
            return None

        elif errorStatus:
            print("SNMP error:", errorStatus)
            return None

        else:
            for varBind in varBinds:
                return int(varBind[1])


# Measure latency using ping
def get_latency(device):
    result = subprocess.run(
        ["ping", "-c", "1", device["host"]],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():
        if "time=" in line:
            latency = line.split("time=")[1].split()[0]
            return float(latency)

    return None


async def main():

    # Connect collector to backend
    channel = grpc.insecure_channel("backend:50051")

    stub = telemetry_pb2_grpc.TelemetryServiceStub(channel)

    # Store previous readings separately for every device
    previous_data = {}

    while True:

        # Process every device in the devices list
        for device in devices:

            device_name = device["name"]

            # Get interface speed
            interface_speed_mbps = await get_high_speed(device)

            if interface_speed_mbps is None:
                print(
                    "Could not retrieve interface speed for",
                    device_name
                )
                continue

            interface_speed_bps = interface_speed_mbps * 1_000_000

            # Get current readings
            current_in = await get_in_octets(device)
            current_out = await get_out_octets(device)
            current_time = time.time()

            # Measure latency
            latency = get_latency(device)

            if current_in is not None and current_out is not None:

                # Check whether this device has a previous reading
                if device_name in previous_data:

                    previous_in = previous_data[device_name]["in"]
                    previous_out = previous_data[device_name]["out"]
                    previous_time = previous_data[device_name]["time"]

                    # If counter becomes smaller, it was reset or wrapped.
                    # Do not calculate a negative bandwidth from this reading.
                    if current_in < previous_in:
                        print(
                            "Incoming counter reset/wrapped for",
                            device_name
                        )

                        previous_data[device_name] = {
                            "in": current_in,
                            "out": current_out,
                            "time": current_time
                        }

                        continue

                    # Same protection for outgoing counter
                    if current_out < previous_out:
                        print(
                            "Outgoing counter reset/wrapped for",
                            device_name
                        )

                        previous_data[device_name] = {
                            "in": current_in,
                            "out": current_out,
                            "time": current_time
                        }

                        continue

                    elapsed_time = current_time - previous_time

                    incoming_bps = (
                        (current_in - previous_in) * 8
                    ) / elapsed_time

                    outgoing_bps = (
                        (current_out - previous_out) * 8
                    ) / elapsed_time

                    incoming_utilization = (
                        incoming_bps / interface_speed_bps
                    ) * 100

                    outgoing_utilization = (
                        outgoing_bps / interface_speed_bps
                    ) * 100

                    metrics = telemetry_pb2.TelemetryData(
                        device_name=device_name,
                        incoming_bps=incoming_bps,
                        outgoing_bps=outgoing_bps,
                        incoming_utilization=incoming_utilization,
                        outgoing_utilization=outgoing_utilization,
                        latency_ms=latency if latency is not None else 0.0,
                        timestamp=int(time.time())
                    )

                    response = stub.SendMetrics(metrics)

                    print(
                        "Device:",
                        device_name
                    )
                    print(
                        "Backend response:",
                        response.status
                    )
                    print(
                        "Incoming:",
                        round(incoming_bps, 2),
                        "bps"
                    )
                    print(
                        "Outgoing:",
                        round(outgoing_bps, 2),
                        "bps"
                    )
                    print(
                        "Incoming utilization:",
                        round(incoming_utilization, 8),
                        "%"
                    )
                    print(
                        "Outgoing utilization:",
                        round(outgoing_utilization, 8),
                        "%"
                    )
                    print(
                        "Latency:",
                        latency,
                        "ms"
                    )
                    print(
                        "Elapsed:",
                        round(elapsed_time, 2),
                        "seconds"
                    )
                    print()

                else:
                    print(
                        "First reading collected for",
                        device_name
                    )
                    print()

                # Save current reading for this device
                previous_data[device_name] = {
                    "in": current_in,
                    "out": current_out,
                    "time": current_time
                }

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())