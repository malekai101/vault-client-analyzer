from datetime import datetime
import time


def convert_to_unix_time(cvt_time: datetime) -> int:
    return int(time.mktime(cvt_time.timetuple()))
