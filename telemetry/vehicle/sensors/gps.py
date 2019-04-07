from fona.gps import FonaGPS
from vehicle.core.sensor import Sensor


class GPSSensor(Sensor):

    name = 'gps'
    _gps = None

    def __init__(self, serial_address):
        super().__init__()
        self._serial_address = serial_address

    async def start(self):
        self._gps = FonaGPS(self._serial_address)
        self._gps.turn_on()

    async def stop(self):
        self._gps.turn_off()
        self._gps.close()

    async def measure(self):
        return self._gps.get_status()
