import argparse
import json
import logging
import time
from copy import deepcopy

import requests

from trackme_traccar.conf import configure_logging


logger = logging.getLogger(__name__)


def transform(datapoint: dict, device_id: str) -> dict:
    data = deepcopy(datapoint)
    data['lat'] = data['geo']['lat']
    data['lon'] = data['geo']['lon']
    del data['geo']
    data['id'] = device_id
    return data


def retry(max_tries=5):
    def deco(func):
        def wrapper(*args, **kwargs):
            tries = max_tries
            while tries > 0:
                tries -= 1
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    if tries == 0:
                        raise
                    logger.debug('Exception occurred: %s', ex)
                    time.sleep(1)
        return wrapper
    return deco


@retry()
def submit(endpoint, data):
    response = requests.post(endpoint, data=data)
    response.raise_for_status()


def export(endpoint: str, logs_path: str, state_path: str, device_id: str):
    try:
        with open(state_path, 'r') as f:
            state = json.load(f)
    except OSError:
        logger.warning('State not found, starting new')
        state = {'timestamp': 0}

    with open(logs_path, 'r') as f:
        for line in f:
            try:
                datapoint = json.loads(line)
            except json.JSONDecodeError:
                logger.exception('Failed to parse datapoint')
                continue
            if datapoint['timestamp'] <= state['timestamp']:
                logger.debug('[%s] Old datapoint found, skipping', datapoint['timestamp'])
                continue
            datapoint = transform(datapoint, device_id)
            submit(endpoint, datapoint)
    if datapoint['timestamp'] > state['timestamp']:
        state = {'timestamp': datapoint['timestamp']}
        logger.info('Storing new state: %r', state)
        with open(state_path, 'w') as f:
            json.dump(state, f)


def main(endpoint: str, logs_path: str, state_path: str, device_id: str, interval: int):
    while True:
        export(endpoint, logs_path, state_path, device_id)
        time.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TrackMe Traccar exporter')
    parser.add_argument('endpoint', help='Traccar osmand endpoint')
    parser.add_argument('logs_path', help='Path to read Telemetry logs from')
    parser.add_argument('state_path', help='Path to a file where to store exporter state')
    parser.add_argument('--device_id', default='test', help='Device ID')
    parser.add_argument('--interval', type=int, default=10,
                        help='Telemetry export interval in seconds. Default: 10')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable debug messages')
    args = parser.parse_args()

    configure_logging(args.debug)
    main(args.endpoint, args.logs_path, args.state_path, args.device_id, args.interval)
