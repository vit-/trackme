import asyncio
import json
import logging

from vehicle.core.db import DBMixin
from vehicle.time import now_utc_ts


logger = logging.getLogger(__name__)


class Hub(DBMixin):

    _stop = False
    _last_run = 0

    def __init__(self, db_file, interval_secs):
        self.db_file = db_file
        self.interval = interval_secs

        self._sensors = []

    def register_sensor(self, sensor):
        self._sensors.append(sensor)

    async def start(self):
        assert self._sensors, 'At least one sensor must be registered'

        self.init_db()
        await asyncio.gather(*[i.start() for i in self._sensors])

    async def stop(self):
        self._stop = True

        await asyncio.gather(*[i.stop() for i in self._sensors])

    def init_db(self):
        with self.db as conn:
            conn.execute(
                'CREATE TABLE IF NOT EXISTS measurements '
                '(id  INTEGER CONSTRAINT id_key PRIMARY KEY AUTOINCREMENT , '
                'data TEXT, '
                'synced BOOLEAN DEFAULT false)'
            )
            conn.commit()

    async def run(self):
        while not self._stop:
            if now_utc_ts() - self._last_run < self.interval:
                await asyncio.sleep(0.1)
                continue
            await asyncio.gather(*[
                self.read_and_write(sensor) for sensor in self._sensors
            ])
            self._last_run = now_utc_ts()

    async def read_and_write(self, sensor):
        data = await sensor.read()
        with self.db as conn:
            conn.execute(
                'INSERT INTO measurements '
                '(data) '
                'VALUES '
                '(?)',

                (json.dumps(data), ),
            )
            conn.commit()
