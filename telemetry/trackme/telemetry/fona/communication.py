import asyncio
import logging

import serial_asyncio


logger = logging.getLogger(__name__)


class CommandError(Exception):
    pass


class ATCommunicator:
    _line_term = '\r\n'
    _cmd_end_codes = ('OK', 'ERROR')

    def __init__(self, device, baudrate=115200):
        self._device = device
        self._baudrate = baudrate

        self._cmd_lock = asyncio.Lock()
        self._reader = None
        self._writer = None

    async def start(self):
        self._reader, self._writer = await serial_asyncio.open_serial_connection(
            url=self._device,
            baudrate=self._baudrate,
        )
        await self._init_connection()

    async def stop(self):
        self._writer.close()

    async def _init_connection(self, tries=5):
        ex = None
        while tries:
            tries -= 1
            try:
                # reset settings
                await self.cmd('ATZ')
            except CommandError as e:
                ex = e
            else:
                # turn off echo
                await self.cmd('ATE0')
                return
        raise ConnectionError('Cannot establish connection: %r' % ex)

    async def cmd(self, command):
        async with self._cmd_lock:
            cmd = '{}{}'.format(command, self._line_term)
            self._writer.write(cmd.encode())
            lines = []
            while True:
                resp = (await self._reader.readline()).decode().strip()
                logger.debug('Received line: %r' % resp)
                lines.append(resp)
                if resp in self._cmd_end_codes:
                    break

        logger.debug('[%r] %r' % (command, lines))

        if lines[-1] != 'OK':
            raise CommandError('Command %r failed: %r' % (command, lines))
        if len(lines) > 1:
            return lines[0]
        return ''
