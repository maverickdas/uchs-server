import enum
import math
from uuid import uuid1

import uchs_exceptions as exs


class AlarmType(enum.Enum):
    Fire = 1
    LostFound = 2
    Medical = 3


class AlarmStatusType(enum.Enum):
    Initiated = 1
    Notified = 2
    Resolved = 3


class Alarm:
    def __init__(self, user_id, alarm_loc, alarm_type):
        try:
            self.type = AlarmType[alarm_type]
            self.latt, self.longt = [
                math.radians(float(x.strip())) for x in alarm_loc.split(",")
            ]
        except Exception as e:
            raise exs.ObjError
        self.user_id = user_id
        self.id = str(uuid1())
        self.type = AlarmType[alarm_type]
        self.status = AlarmStatusType.Initiated

    def get_status(self):
        return self.type.name

    def set_status(self, alarm_status):
        try:
            self.status = AlarmStatusType[alarm_status]
        except Exception as e:
            raise exs.ObjError

    def insert_alarm(self, cursor, is_alt=False):
        try:
            db_name = "uchs_test" if is_alt else "uchs_db"
            query = """
            INSERT INTO {}.alarm_status
            (alarm_id, alarm_status, user_id, latitude, longitude, alarm_type)
            VALUES('{}', {}, '{}', {}, {}, '{}');
            """.format(db_name, self.id, self.status.value, self.user_id,
                       self.latt, self.longt, self.type.name)
            cursor.execute(query)
        except Exception as e:
            raise exs.DBError
        return True
