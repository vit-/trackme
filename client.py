import asyncio
import logging
import logging.config

from vehicle.core.hub import Hub
from vehicle.sensors.gps import GPSSensor
from vehicle.sinks.tcp import TCPSink


logger = logging.getLogger(__name__)


def get_hub():
    hub = Hub(
        uid='dummy',
        interval_secs=10,
    )
    hub.register_sensor(GPSSensor(None))
    hub.register_sink(TCPSink(None))
    return hub


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

    logger.info('Starting app')

    hub = get_hub()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(hub.start())
    try:
        loop.run_until_complete(hub.run())
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Shutting down')
        loop.run_until_complete(hub.stop())
    loop.close()
