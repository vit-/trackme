import asyncio
import logging

from vehicle.time import now_utc_ts


logger = logging.getLogger('trackme.vehicle.hub')


class Hub(object):

    _running = False
    _stop = False
    _last_run = 0

    def __init__(self, uid, interval_secs=300):
        self._sensors = []
        self._sinks = []
        self.uid = uid
        self.interval = interval_secs

    def register_sensor(self, sensor):
        self._sensors.append(sensor)

    def register_sink(self, sink):
        self._sinks.append(sink)

    def set_interval(self, seconds):
        self.interval = seconds

    async def start(self):
        assert self._sensors, 'At least one sensor must be registered'
        assert self._sinks, 'At least one sink must be registered'

        await asyncio.gather(*[i.start() for i in self._sinks])
        await asyncio.gather(*[i.start() for i in self._sensors])

    async def stop(self):
        self._stop = True
        while self._running:
            await asyncio.sleep(0.1)

        await asyncio.gather(*[i.stop() for i in self._sensors])
        await asyncio.gather(*[i.stop() for i in self._sinks])

    async def run(self):
        while not self._stop:
            if now_utc_ts() - self._last_run < self.interval:
                await asyncio.sleep(0.1)
                continue
            await asyncio.gather(*[
                self.read_and_write(sensor) for sensor in self._sensors
            ])
            self._last_run = now_utc_ts()

    async def read_and_write(self, sensor):
        data = await sensor.read()
        data['uid'] = self.uid
        await asyncio.gather(*[
            sink.write(data) for sink in self._sinks
        ])
