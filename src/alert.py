import enum
import uchs_exceptions as exs

class Alert:
    def __init__(self, alarm_id, user_list, helpl_list, msg):
        self.alarm_id = alarm_id
        if isinstance(user_list, list):
            self.user_list = list(set(user_list))
        if isinstance(helpl_list, list):
            self.helpl_list = list(set(helpl_list))
        if isinstance(msg, str):
            self.msg = msg

    def insert_alert(self, cursor):
        try:
            # query = """
            # INSERT INTO uchs_db.alarm_status
            # (alarm_id, alarm_status, user_id, latitude, longitude, alarm_type)
            # VALUES('{}', {}, '{}', {}, {}, '{}');
            # """.format(self.id, self.status.value, self.user_id, self.latt,
            #            self.longt, self.type.name)
            # cursor.execute(query)
            pass
        except Exception as e:
            raise exs.DBError
        return True
