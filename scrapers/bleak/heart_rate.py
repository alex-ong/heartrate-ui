"""Bluetooth SIG Heart Rate Service identifiers and packet parsing."""

HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"


def parse_heart_rate_measurement(data: bytes | bytearray) -> int:
    if len(data) < 2:
        raise ValueError("Heart-rate measurement is missing its value")

    flags = data[0]
    if flags & 0x01:
        if len(data) < 3:
            raise ValueError("16-bit heart-rate measurement is truncated")
        return int.from_bytes(data[1:3], byteorder="little")
    return data[1]
