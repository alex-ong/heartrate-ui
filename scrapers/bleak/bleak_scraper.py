"""BLE heart-rate scraper using the Bluetooth SIG Heart Rate Service."""

import asyncio
import logging
import os

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

from .heart_rate import (
    HEART_RATE_MEASUREMENT_UUID,
    HEART_RATE_SERVICE_UUID,
    parse_heart_rate_measurement,
)
from .scanner import find_device_by_address, scan_devices

logger = logging.getLogger(__name__)

DEVICE_ADDRESS_ENV = "BLEAK_SENSOR_ADDRESS"
RECONNECT_DELAY = 1.0


class Scraper:
    def __init__(self) -> None:
        self.address: str = os.environ.get(DEVICE_ADDRESS_ENV, "").strip()
        self._rate: int = 0
        self._client: BleakClient | None = None
        self._closing: bool = False
        self._missing_device_logged: bool = False
        self._stop_event: asyncio.Event = asyncio.Event()
        self._task: asyncio.Task[None] | None = None

        if not self.address:
            logger.warning(
                "%s is unset; run with '--scraper-args scan' to find a device",
                DEVICE_ADDRESS_ENV,
            )
            return

        self._task = asyncio.create_task(self._run())

    @staticmethod
    async def scan() -> None:
        await scan_devices()

    def get_rate(self) -> int:
        return self._rate

    def _handle_measurement(
        self, _characteristic: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        try:
            self._rate = parse_heart_rate_measurement(data)
        except ValueError as error:
            logger.warning("Ignoring invalid heart-rate notification: %s", error)

    async def _wait_for_disconnect(self, disconnected: asyncio.Event) -> bool:
        stop_task = asyncio.create_task(self._stop_event.wait())
        disconnect_task = asyncio.create_task(disconnected.wait())
        try:
            done, _ = await asyncio.wait(
                (stop_task, disconnect_task),
                return_when=asyncio.FIRST_COMPLETED,
            )
            return disconnect_task in done and not self._closing
        finally:
            for task in (stop_task, disconnect_task):
                if not task.done():
                    task.cancel()
            await asyncio.gather(stop_task, disconnect_task, return_exceptions=True)

    async def _wait_before_retry(self) -> None:
        try:
            await asyncio.wait_for(self._stop_event.wait(), timeout=RECONNECT_DELAY)
        except TimeoutError:
            pass

    async def _find_device(self) -> BLEDevice | None:
        device = await find_device_by_address(self.address)
        if device is None and not self._missing_device_logged:
            logger.warning("BLE heart-rate sensor %s not found; retrying", self.address)
            self._missing_device_logged = True
        elif device is not None:
            self._missing_device_logged = False
        return device

    async def _connect(self, device: BLEDevice) -> None:
        disconnected = asyncio.Event()

        def on_disconnect(_client: BleakClient) -> None:
            disconnected.set()

        async with BleakClient(
            device,
            disconnected_callback=on_disconnect,
            services=[HEART_RATE_SERVICE_UUID],
        ) as client:
            self._client = client
            await client.start_notify(
                HEART_RATE_MEASUREMENT_UUID,
                self._handle_measurement,
            )
            self._rate = 0
            logger.info("Connected to BLE heart-rate sensor %s", self.address)
            if await self._wait_for_disconnect(disconnected):
                logger.warning(
                    "BLE heart-rate sensor %s disconnected; reconnecting",
                    self.address,
                )

    async def _run_attempt(self) -> None:
        device = await self._find_device()
        if device is not None:
            await self._connect(device)

    async def _run(self) -> None:
        while not self._closing:
            try:
                await self._run_attempt()
            except asyncio.CancelledError:
                raise
            except (BleakError, OSError, TimeoutError) as error:
                if not self._closing:
                    logger.warning(
                        "BLE heart-rate connection failed (%s); retrying", error
                    )
            finally:
                self._client = None
                self._rate = 0

            if not self._closing:
                await self._wait_before_retry()

    async def close(self) -> None:
        self._closing = True
        self._stop_event.set()
        if self._task is not None:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
