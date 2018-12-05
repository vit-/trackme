import argparse
import asyncio
import logging
import logging.config

import yaml

from vehicle.core.hub import Hub
from vehicle.sensors.gps import GPSSensor
from vehicle.sinks.control import ControlSink
from vehicle.sinks.file import FileSink
from vehicle.sinks.tcp import TCPSink
from vehicle.sinks.zmq import ZMQSink


logger = logging.getLogger(__name__)


def get_hub(conf):
    hub = Hub(
        uid=conf['HUB']['uid'],
        interval_secs=conf['HUB']['interval_secs'],
    )
    hub.register_sensor(GPSSensor())

    tcp_sink_conf = conf['SINKS']['tcp']
    hub.register_sink(TCPSink(
        host=tcp_sink_conf['host'],
        port=tcp_sink_conf['port'],
        connect_retry_timeout_secs=tcp_sink_conf['connect_retry_timeout_secs'],
        buffer_size=tcp_sink_conf['buffer_size'],
    ))

    zmq_sink_conf = conf['SINKS']['zmq']
    hub.register_sink(ZMQSink(
        host=zmq_sink_conf['host'],
        port=zmq_sink_conf['port'],
    ))

    hub.register_sink(FileSink(conf['SINKS']['file']['filename']))

    ctrl_sink_conf = conf['SINKS']['control']
    hub.register_sink(ControlSink(
        set_update_interval_cb=hub.set_interval,
        stopped_threshold=ctrl_sink_conf['stopped_threshold'],
        stop_speed=ctrl_sink_conf['stop_speed'],
        stop_interval_secs=ctrl_sink_conf['stop_interval_secs'],
        move_interval_secs=ctrl_sink_conf['move_interval_secs'],
    ))
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
