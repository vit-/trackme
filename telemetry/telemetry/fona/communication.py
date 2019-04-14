import logging
import serial
import time


logger = logging.getLogger(__name__)


class CommandError(Exception):
    pass


class ATCommunicator:
    _line_term = '\r\n'
    _cmd_sleep_time = 0.5

    def __init__(self, device, baudrate=115200, timeout=1):
        self._conn = serial.Serial(device, baudrate=baudrate, timeout=timeout)
        self._init_connection()

    def _init_connection(self, tries=5):
        ex = None
        while tries:
            tries -= 1
            try:
                # reset settings
                self.cmd('ATZ')
            except CommandError as e:
                ex = e
            else:
                # turn off echo
                self.cmd('ATE0')
                return
        raise ConnectionError('Cannot establish connection: %r' % ex.message)

    def close(self):
        self._conn.close()

    def cmd(self, command):
        cmd = '{}{}'.format(command, self._line_term)
        self._conn.write(cmd.encode())
        time.sleep(self._cmd_sleep_time)
        resp = self._conn.read_all().decode().strip()
        logger.debug('[%r] %r' % (command, resp))
        lines = [i.strip() for i in resp.split(self._line_term)]
        if lines[-1] != 'OK':
            raise CommandError('Command failed: %r' % resp)
        if len(lines) > 1:
            return lines[0]
        return ''
