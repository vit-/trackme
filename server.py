import asyncio
import json
import logging
import logging.config
import zlib


logger = logging.getLogger(__name__)


class ServerProtocol(asyncio.Protocol):

    def __init__(self, received_cb):
        self.received_cb = received_cb

    def connection_made(self, transport):
        self.transport = transport
        self.peer = transport.get_extra_info('peername')

        logger.info('[%s] connected', self.peer)

    def connection_lost(self, exc):
        logger.debug('[%s] disconnected exc: %s', self.peer, exc)
        logger.info('[%s] disconnected', self.peer)

    def data_received(self, data):
        logger.debug('[%s] received %s bytes: %r', self.peer, len(data), data)
        self.received_cb(self.peer, data)


def received_cb(peer, data):
    try:
        b = zlib.decompress(data)
        j = b.decode('utf-8')
        decoded = json.loads(j)
    except ValueError:
        logger.warning(
            '[%s] invalid data received: %r',
            peer,
            data,
        )
    else:
        logger.info('[%s] received: %r', peer, decoded)


async def main():
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: ServerProtocol(received_cb),
        '127.0.0.1', 5000
    )
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    logging.config.dictConfig({
        'version': 1,
        'incremental': False,
        'disable_existing_loggers': False,

        'root': {
            'level': 'DEBUG',
            'handlers': [
                'console',
            ]
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            }
        },
        'formatters': {
            'default': {
                'format': '%(asctime)s %(name)-s[%(process)d]: %(levelname)-8s %(message)s',
            }
        }
    })
    asyncio.run(main())
