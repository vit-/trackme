import asyncio
import logging
import logging.config


from vehicle.core.hub import Hub
from vehicle.core.sink import Sink
from vehicle.sensors.gps import GPSSensor


logger = logging.getLogger(__name__)


class DummySink(Sink):
    name = 'dummy'

    async def submit(self, data):
        pass


def get_hub():
    hub = Hub(interval_secs=10)
    hub.register_sensor(GPSSensor(None))
    hub.register_sink(DummySink(None))
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
