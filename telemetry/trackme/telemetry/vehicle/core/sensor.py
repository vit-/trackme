class Sensor:

    name = None

    def __init__(self):
        assert self.name, 'Name must be set'

    async def start(self):
        pass

    async def stop(self):
        pass

    async def read(self):
        measurements = await self.measure()
        return {self.name: measurements}

    async def measure(self):
        return NotImplementedError()
