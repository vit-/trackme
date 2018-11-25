import asyncio
import json
import logging
import zlib
from collections import deque

from vehicle.core.sink import Sink


logger = logging.getLogger(__name__)


class ClientProtocol(asyncio.Protocol):

    def __init__(self, connected_cb, disconnected_cb):
        self.connected_cb = connected_cb
        self.diconnected_cb = disconnected_cb

    def connection_made(self, transport):
        self.peer = transport.get_extra_info('peername')

        logger.info('[%s] Connected', self.peer)
        self.connected_cb()

    def connection_lost(self, exc):
        logger.info('[%s] Disconnected', self.peer)
        self.diconnected_cb()


class TCPSink(Sink):

    name = 'tcp'

    _connected = False

    def __init__(self, host, port, connect_retry_timeout_secs, buffer_size):
        super().__init__()
        self.host = host
        self.port = port
        self.connect_retry_timeout_secs = connect_retry_timeout_secs
        self.queue = deque(maxlen=buffer_size)

    async def start(self):
        self._ensure_connection_future = asyncio.ensure_future(self.ensure_connection())

    async def stop(self):
        self._ensure_connection_future.cancel()
        if not self.transport.is_closing():
            self.transport.close()

    async def ensure_connection(self):
        loop = asyncio.get_running_loop()

        while True:
            while self._connected and self.queue:
                message = self.queue.popleft()
                self.transport.write(message)
                logger.debug('Message sent: %s', message)

            if self._connected:
                await asyncio.sleep(0.1)
                continue
            try:
                self.transport, _ = await loop.create_connection(
                    lambda: ClientProtocol(
                        connected_cb=self.connection_made,
                        disconnected_cb=self.connection_lost,
                    ),
                    self.host,
                    self.port,
                )
            except ConnectionError as exc:
                logger.error('Failed to connect: %s', exc)
                await asyncio.sleep(self.connect_retry_timeout_secs)

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
        encoded = self.encode(data)
        self.queue.append(encoded)
        logger.debug('Buffer size: %s', len(self.queue))
