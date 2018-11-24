import asyncio
import json
import logging
import zlib

from async_timeout import timeout

from vehicle.core.sink import Sink


logger = logging.getLogger(__name__)


class ClientProtocol(asyncio.Protocol):

    def __init__(self, connected_cb, disconnected_cb):
        self.connected_cb = connected_cb
        self.diconnected_cb = disconnected_cb

    def connection_made(self, transport):
        self.peer = transport.get_extra_info('peername')

        logger.info('[%s] connected', self.peer)
        self.connected_cb()

    def connection_lost(self, exc):
        logger.info('[%s] disconnected', self.peer)
        self.diconnected_cb()



class TCPSink(Sink):

    name = 'tcp'

    _connected = False

    async def start(self):
        loop = asyncio.get_running_loop()

        self.transport, _ = await loop.create_connection(
            lambda: ClientProtocol(
                connected_cb=self.connection_made,
                disconnected_cb=self.connection_lost,
            ),
            '127.0.0.1', 5000
        )
        async with timeout(10):
            await self.wait_for_connection()

    async def stop(self):
        if not self.transport.is_closing():
            self.transport.close()

    async def wait_for_connection(self):
        while not self._connected:
            await asyncio.sleep(0.1)

    def connection_made(self):
        self._connected = True

    def connection_lost(self):
        self._connected = False

    @staticmethod
    def encode(data):
        j = json.dumps(data)
        b = j.encode('utf-8')
        return zlib.compress(b)

    async def submit(self, data):
        if not self._connected:
            logger.warning('connection lost, not sending')
            return

        encoded = self.encode(data)
        self.transport.write(encoded)
