import argparse
import asyncio
import logging
import logging.config

import yaml

from vehicle.controllers.speed import SpeedController
from vehicle.core.hub import Hub
from vehicle.sensors.gps import GPSSensor


logger = logging.getLogger(__name__)


def get_hub(conf):
    hub = Hub(
        update_interval_secs=conf['HUB']['update_interval_secs'],
    )
    hub.register_sensor(GPSSensor(conf['FONA_SERIAL_ADDRESS']))

    ctrl_sink_conf = conf['CONTROLLERS']['speed']
    hub.register_controller(SpeedController(
        stopped_threshold=ctrl_sink_conf['stopped_threshold'],
        stop_speed=ctrl_sink_conf['stop_speed'],
        stop_interval_secs=ctrl_sink_conf['stop_interval_secs'],
        move_interval_secs=ctrl_sink_conf['move_interval_secs'],
    ))

    return hub


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run TrackMe telemetry collector')
    parser.add_argument(
        'config',
        type=str,
        help='path to config file',
    )
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        conf = yaml.full_load(f)

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
