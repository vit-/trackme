import argparse
import asyncio
import json
import logging
import logging.config
import zlib

import yaml


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


async def main(host, port):
    logger.info('Serving at %s:%s', host, port)

    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: ServerProtocol(received_cb),
        host,
        port,
    )
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run TrackMe server')
    parser.add_argument(
        'config',
        type=str,
        help='path to config file',
    )
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        conf = yaml.load(f)

    logging.config.dictConfig(conf['LOGGING'])
    server_conf = conf['PLAIN_SERVER']
    asyncio.run(main(server_conf['host'], server_conf['port']))
