import json
import logging

from vehicle.core.db import DBMixin


logger = logging.getLogger(__name__)


class Sync(DBMixin):

    _stop = False
    _last_run = 0

    def __init__(self, uid, db_file, interval_secs, address):
        self.uid = uid
        self.db_file = db_file
        self.interval_secs = interval_secs
        self.address = address
