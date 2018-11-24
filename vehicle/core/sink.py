import logging


logger = logging.getLogger('trackme.vehicle.sink')


class Sink(object):

    name = None

    def __init__(self, conf):
        assert self.name, 'Name must be set'

        self.conf = conf

    async def start(self):
        pass

    async def stop(self):
        pass

    async def write(self, data):
        logger.debug('[sink: %s] Data: %s',
                     self.name, data)
        await self.submit(data)

    async def submit(self, data):
        raise NotImplementedError()
