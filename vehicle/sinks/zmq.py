import logging
import json
import zlib

from aiozmq import rpc

from vehicle.core.sink import Sink


logger = logging.getLogger(__name__)


class ZMQSink(Sink):

    name = 'zmq'

    def __init__(self, host, port):
        super().__init__()

        self.address = 'tcp://{host}:{port}'.format(
            host=host,
            port=port,
        )
        self.client = None

    async def start(self):
        logger.info('Connecting to %s', self.address)
        self.client = await rpc.connect_rpc(
            connect=self.address
        )

    # async def stop(self):
    #     self.client.clo

    @staticmethod
    def encode(data):
        j = json.dumps(data)
        b = j.encode('utf-8')
        return zlib.compress(b)

    async def submit(self, data):
        await self.client.call.tick(data)
        # encoded = self.encode(data)
        # self.socket.write((
        #     b'data',
        #     b'ask',
        #     encoded,
        # ))
