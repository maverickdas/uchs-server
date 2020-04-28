import enum
import math

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
    def __init__(self, user_id, alarm_id, alarm_ts, alarm_loc, alarm_type):
        try:
            self.type = AlarmType[alarm_type]
            self.latt, self.longt = [
                float(x.strip()) for x in alarm_loc.split(",")
            ]
        except Exception as e:
            raise exs.ObjError
        self.user_id = user_id
        self.id = alarm_id
        self.tstamp = alarm_ts
        self.type = AlarmType[alarm_type]
        self.status = AlarmStatusType.Initiated

    def get_status(self):
        return self.type.name

    def set_status(self, alarm_status):
        try:
            self.status = AlarmStatusType[alarm_status]
        except Exception as e:
            raise exs.ObjError

    def insert_alarm(self, cursor):
        try:
            query = """
            INSERT INTO uchs_db.alarm_status
            (alarm_id, alarm_status, user_id, latitude, longitude, alarm_type)
            VALUES('{}', {}, '{}', {}, {}, {});
            """.format(self.id, self.status.value, self.user_id, math.radians(self.latt),
                       math.radians(self.longt), self.type.value)
            cursor.execute(query)
            # for i in cursor.fetchall():
            #     print(i)
        except Exception as e:
            raise exs.DBError
        return True


def receive_alarm(cursor, user_id, alarm_id, alarm_ts, alarm_loc, alarm_type):
    alarm = Alarm(user_id, alarm_id, alarm_ts, alarm_loc, alarm_type)
    stat = alarm.insert_alarm(cursor)
    if stat:
        return True, alarm
    return False, None


def start_alert_procedure(cursor, alarm: Alarm):
    try:
        user_id = alarm.user_id
        query = """
        SELECT *
        FROM uchs_db.user_emergency_contacts_registered
        WHERE user_id = '{}';
        """.format(user_id)
        cursor.execute(query)
        guardian_list = [x for x in cursor.fetchone() if x is not None]
        print(guardian_list)
    except Exception as e:
        raise exs.DBError
    return True