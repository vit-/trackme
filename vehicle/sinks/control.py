import logging

from vehicle.core.sink import Sink


logger = logging.getLogger(__name__)


class ControlSink(Sink):

    name = 'control'

    _zero_speed_times = 0

    def __init__(
            self,
            set_update_interval_cb,
            stopped_threshold,
            stop_speed,
            stop_interval_secs,
            move_interval_secs,
    ):
        super().__init__()
        self.set_interval = set_update_interval_cb
        self.stopped_threshold = stopped_threshold
        self.stop_speed = stop_speed
        self.stop_interval_secs = stop_interval_secs
        self.move_interval_secs = move_interval_secs

    async def submit(self, data):
        if not data['sensor'] == 'gps':
            return
        speed = data['measurements']['speed']
        if speed < self.stop_speed:
            self._zero_speed_times += 1
        else:
            self._zero_speed_times = 0
            logger.debug('Moving')
            self.set_interval(self.move_interval_secs)

        if self._zero_speed_times > self.stopped_threshold:
            logger.debug('Stopped')
            self.set_interval(self.stop_interval_secs)
