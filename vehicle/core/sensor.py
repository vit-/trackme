import logging

from vehicle.time import now_utc_ts


logger = logging.getLogger('trackme.vehicle.sensor')


class Sensor(object):

    name = None

    def __init__(self):
        assert self.name, 'Name must be set'

    async def start(self):
        pass

    async def stop(self):
        pass

    async def read(self):
        measurements = await self.measure()

        logger.debug('[sensor: %s] Measurements: %s',
                     self.name, measurements)

        return {
            'sensor': self.name,
            'timestamp': now_utc_ts(),
            'measurements': measurements,
        }

    async def measure(self):
        return NotImplementedError()
