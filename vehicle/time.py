import time
from datetime import datetime


def now_utc_ts():
    now = datetime.utcnow()
    return int(time.mktime(now.timetuple()))
