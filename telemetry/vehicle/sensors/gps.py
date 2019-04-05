from vehicle.core.sensor import Sensor


class GPSSensor(Sensor):

    name = 'gps'

    async def measure(self):
        return {
            'lat': 50.12345,
            'lon': 30.12345,
            'speed': 0,
        }
