import os

from flask import Flask, current_app, g
from flask_restful import Api, Resource

from .fona.gps import FonaGPS


def get_env_raise(name):
    val = os.getenv(name)
    if not val:
        raise ValueError('Env {} is not provided'.format(name))
    return val


FONA_DEV = get_env_raise('FONA_DEV')


app = Flask(__name__)
api = Api(app)


def get_gps():
    if 'gps' not in g:
        g.gps = FonaGPS(FONA_DEV)
        g.gps.turn_on()
    return g.gps


def close_gps(e=None):
    gps = g.pop('gps', None)
    if gps is not None:
        gps.turn_off()
        gps.close()


class Gps(Resource):
    def get(self):
        status = get_gps().get_status()
        status['geo'] = {
            'lat': status['lat'],
            'lon': status['lon'],
        }
        del status['lat']
        del status['lon']
        return status


class Health(Resource):
    def get(self):
        gps = get_gps()
        battery = gps._remove_prefix(gps.cmd('AT+CBC'), '+CBC: ').split(',')
        return {
            'alive': 1,
            'battery': {
                'status': int(battery[0]),
                'level': int(battery[1]),
                'voltage': float(battery[2]),
            }
        }


app.teardown_appcontext(close_gps)
api.add_resource(Gps, '/gps')
api.add_resource(Health, '/health')


if __name__ == '__main__':
    app.run(debug=True)

