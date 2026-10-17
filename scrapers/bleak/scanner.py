"""BLE device discovery helpers."""

from bleak import BleakScanner
from bleak.backends.device import BLEDevice

DISCOVERY_TIMEOUT = 3.0
SCAN_TIMEOUT = 8.0


async def find_device_by_address(address: str) -> BLEDevice | None:
    return await BleakScanner.find_device_by_address(
        address,
        timeout=DISCOVERY_TIMEOUT,
    )


async def scan_devices() -> None:
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover(timeout=SCAN_TIMEOUT)
    if not devices:
        print("No BLE devices found.")
        return

    for device in sorted(devices, key=lambda item: (item.name or "", item.address)):
        print(f"{device.name or '<unnamed>'}\t{device.address}")
