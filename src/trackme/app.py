import argparse
import json
import logging
import time
from datetime import datetime

from .conf import configure_logging
from .fona.gps import FonaGPS
from .killer import GracefulKiller


logger = logging.getLogger(__name__)
telemetry_logger = logging.getLogger('trackme.telemetry')


def main(device, interval):
    logger.info('Starting app')
    gps = FonaGPS(device)
    gps.turn_on()

    loop(gps, interval)

    gps.close()
    logger.info('Bye!')


def now_utc_ts():
    now = datetime.utcnow()
    return int(time.mktime(now.timetuple()))


def telemetry(data):
    data = {f: v for f, v in data.items() if v != ""}
    data['timestamp'] = now_utc_ts()
    telemetry_logger.info(json.dumps(data))


def format_gps_status(status):
    if status['lat'] and status['lon']:
        status['geo'] = {
            'lat': status['lat'],
            'lon': status['lon'],
        }
    del status['lat']
    del status['lon']
    return status


def loop(gps, interval):
    killer = GracefulKiller()
    while not killer.kill_now:
        next_run = time.monotonic() + interval

        status = format_gps_status(gps.get_status())
        telemetry(status)

        while not killer.kill_now and time.monotonic() < next_run:
            time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trackme telemetry logger')
    parser.add_argument('device', help='FONA device path')
    parser.add_argument('path', help='Path to store Telemetry logs to')
    parser.add_argument('--interval', type=int, default=10,
                        help='Telemetry collection interval in seconds. Default: 10')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable debug messages')
    args = parser.parse_args()

    configure_logging(args.path, args.debug)
    main(args.device, args.interval)
