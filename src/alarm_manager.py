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
                math.radians(float(x.strip())) for x in alarm_loc.split(",")
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
            VALUES('{}', {}, '{}', {}, {}, '{}');
            """.format(self.id, self.status.value, self.user_id, self.latt,
                       self.longt, self.type.name)
            cursor.execute(query)
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

        guardian_query = """
        SELECT *
        FROM uchs_db.user_emergency_contacts_registered
        WHERE user_id = '{}';
        """.format(user_id)
        cursor.execute(guardian_query)
        guardian_list = [x for x in cursor.fetchone()[1:] if x is not None]
        print("Guardians are -")
        print(guardian_list)

        community_1_query = """
        select ut.user_id
        from user_live_location ull join user_tbl ut 
        where ut.user_id = ull.user_id
        AND 
        ut.user_id !='{}'
        AND 
        acos(sin({}) * sin(ull.latitude) + cos({}) * cos(ull.latitude) * cos(ull.longitude - {})) * 6371 <= 1;
        """.format(user_id, alarm.latt, alarm.latt, alarm.longt)
        cursor.execute(community_1_query)
        community_list = [x[0] for x in cursor.fetchall()]
        print("Community is -")
        print(community_list)

        helpline_query = """
        select  ht.helpline_id from helpline_tbl ht join location_tbl lt 
        where ht.helpline_location_id = lt.location_id 
        AND 
        ht.helpline_type ='{}'
        AND 
        acos(sin({}) * sin(lt.latitude) + cos({}) * cos(lt.latitude ) * cos(lt.longitude - {})) * 6371 <= 1;
        """.format(alarm.type.name, alarm.latt, alarm.latt, alarm.longt)
        cursor.execute(helpline_query)
        helpline_list = [x[0] for x in cursor.fetchall()]
        print("helplines are -")
        print(helpline_list)

        if not helpline_list:
            specials_query = """
            select ut.user_id, ut.user_specialization
            from user_live_location ull join user_tbl ut 
            where ut.user_id = ull.user_id
            AND 
            ut.user_id !='{}'
            AND 
            ut.user_specialization ='{}'
            AND 
            acos(sin({}) * sin(ull.latitude) + cos({}) * cos(ull.latitude) * cos(ull.longitude - {})) * 6371 <= 2;
            """.format(user_id, alarm.type.name, alarm.latt, alarm.latt, alarm.longt)
            cursor.execute(specials_query)
            specialist_list = [(x[0], x[1]) for x in cursor.fetchall()]
            print("Specialists are -")
            print(specialist_list)
    except Exception as e:
        raise exs.DBError
    return True