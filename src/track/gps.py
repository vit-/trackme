import asyncio
import logging
import logging.config
from datetime import datetime


logger = logging.getLogger(__name__)


# ^\((?P<device_id>\d+)(?P<command>.{4})(?P<date>\d{6})(?P<validity>[AV])(?P<lat>\d+)(?P<lat_min>\d{2}\.\d+)([NS])(?P<lon>\d+)(?P<lon_min>\d{2}\.\d+)([EW])(?P<speed>\d+\.\d)(?P<time>\d{6})(?P<course>[\d\.]{6})(?:\d+L\d+)\)


async def receive(reader, writer):
    peer = writer.get_extra_info('peername')
    log = logging.LoggerAdapter(logger, dict(peer=peer))

    while True:
        data = await reader.read(1024)
        if not data:
            log.debug('No data received')
            await asyncio.sleep(1)
            continue
        try:
            decoded = data.decode()
        except ValueError:
            log.warning('Cannot decode message: %r', data)
            break
        else:
            log.info('Received data: %s', decoded)
            async for response in handle_data(decoded):
                logger.info('Sending data: %s', response)
                writer.write(response.encode())
            await writer.drain()
    writer.close()


async def handle_data(decoded):
    device_id = decoded[1:13]
    command = decoded[13:17]
    if command == 'BP00':
        yield '({}AP01HSO)'.format(device_id)
        yield '(0{}AP00)'.format(int(device_id) + 1)
        # yield '({}AR0000150005)'.format(device_id)
    elif command == 'BP05':
        yield '({}AP05)'.format(device_id)


async def main():
    server = await asyncio.start_server(
        receive,
        host='0.0.0.0',
        port=50006,
    )

    logger.info('Starting server')
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    logging.config.dictConfig({
        'version': 1,
        'incremental': False,
        'disable_existing_loggers': False,

        'root': {
            'level': 'INFO',
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
