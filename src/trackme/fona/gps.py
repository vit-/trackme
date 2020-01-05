from .communication import ATCommunicator


CGNSINF_FIELDS = (
    ('gps_status', int),
    ('fix_status', int),
    ('utc_timestr', str),
    ('lat', float),
    ('lon', float),
    ('alt', float),  # altitude, meters
    ('speed', float),  # km/h
    ('course', float),  # degrees
    ('fix_mode', int),
    ('_reserved1', str),
    ('hdop', float),
    ('pdop', float),
    ('vdop', float),
    ('_reserved2', str),
    ('gps_sattelites_cnt', int),
    ('gnss_sattelites_cnt', int),
    ('glonass_sattelites_cnt', int),
    ('_reserved3', str),
    ('c_n0_max', int),
    ('hpa', float),
    ('vpa', float),
)


class FonaGPS(ATCommunicator):

    def close(self):
        self.turn_off()
        super().close()

    @staticmethod
    def _remove_prefix(line, prefix):
        if not line.startswith(prefix):
            raise ValueError('Line %r does not start with %r' % (line, prefix))
        return line[len(prefix):]

    def turn_on(self):
        self.cmd('AT+CGNSPWR=1')

    def turn_off(self):
        self.cmd('AT+CGNSPWR=0')

    def is_turned_on(self):
        res = self._remove_prefix(self.cmd('AT+CGNSPWR?'), '+CGNSPWR: ')
        return res == '1'

    def get_status(self):
        res = self._remove_prefix(self.cmd('AT+CGNSINF'), '+CGNSINF: ')
        data = res.split(',')
        return {
            field: (data[idx] and fmt_func(data[idx]) or None)
            for idx, (field, fmt_func) in enumerate(CGNSINF_FIELDS)
        }
