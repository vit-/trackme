import asyncio
import json
import logging

from telemetry.vehicle.time import now_utc_ts


logger = logging.getLogger(__name__)
telemetry_logger = logging.getLogger('vehicle.telemetry')


class Hub:

    _stop = False
    _last_run = 0

    def __init__(self, update_interval_secs):
        self.interval = update_interval_secs

        self._sensors = []
        self._controllers = []

    def register_sensor(self, sensor):
        self._sensors.append(sensor)

    def register_controller(self, controller):
        self._controllers.append(controller)

    async def start(self):
        assert self._sensors, 'At least one sensor must be registered'

        await asyncio.gather(*[i.start() for i in self._sensors])

    async def stop(self):
        self._stop = True

        await asyncio.gather(*[i.stop() for i in self._sensors])

    async def run(self):
        while not self._stop:
            if now_utc_ts() - self._last_run < self.interval:
                await asyncio.sleep(0.1)
                continue
            data = await self._read_sensors()
            self._save(data)
            await self._control(data)
            self._last_run = data['timestamp']

    async def _read_sensors(self):
        measurements = await asyncio.gather(*[
            sensor.read() for sensor in self._sensors
        ])
        data = {'timestamp': now_utc_ts()}
        for m in measurements:
            data.update(m)
        return data

    async def _control(self, data):
        await asyncio.gather(*[
            controller.process(data, self)
            for controller in self._controllers
        ])

    @staticmethod
    def _save(payload):
        telemetry_logger.info(json.dumps(payload))
