import argparse
import asyncio
import logging
import logging.config

import yaml

from vehicle.core.hub import Hub
from vehicle.sensors.gps import GPSSensor
from vehicle.sinks.tcp import TCPSink


logger = logging.getLogger(__name__)


def get_hub(conf):
    hub = Hub(
        uid=conf['HUB']['uid'],
        interval_secs=conf['HUB']['interval_secs'],
    )
    hub.register_sensor(GPSSensor())

    tcp_sink_conf = conf['SINKS']['tcp']
    hub.register_sink(TCPSink(tcp_sink_conf['host'], tcp_sink_conf['port']))
    return hub


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run TrackMe client')
    parser.add_argument(
        'config',
        type=str,
        help='path to config file',
    )
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        conf = yaml.load(f)

    logging.config.dictConfig(conf['LOGGING'])

    logger.info('Starting app')

    hub = get_hub(conf)

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
