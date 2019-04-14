import logging


logger = logging.getLogger(__name__)


class SpeedController:

    _zero_speed_times = 0

    def __init__(
            self,
            stopped_threshold,
            stop_speed,
            stop_interval_secs,
            move_interval_secs,
    ):
        super().__init__()
        self.stopped_threshold = stopped_threshold
        self.stop_speed = stop_speed
        self.stop_interval_secs = stop_interval_secs
        self.move_interval_secs = move_interval_secs

    async def process(self, data, hub):
        if 'gps' not in data:
            return
        speed = data['gps']['speed']
        if speed < self.stop_speed:
            self._zero_speed_times += 1
        else:
            self._zero_speed_times = 0
            logger.debug('Moving')
            hub.interval = self.move_interval_secs

        if self._zero_speed_times > self.stopped_threshold:
            logger.debug('Stopped')
            hub.interval = self.stop_interval_secs
