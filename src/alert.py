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

    def insert_alert(self, cursor, is_alt=False):
        db_name = "uchs_test" if is_alt else "uchs_db"
        user_alert_rows = helpl_alert_rows = None
        if len(self.user_list) > 0:
            user_alert_rows = [
                f"('{self.alarm_id}', '{uid}')" for uid in self.user_list
            ]
            try:
                ins_query_user = """
                INSERT INTO {}.user_alert_status
                (alarm_id, user_id)
                VALUES {};
                """.format(db_name, ",".join(user_alert_rows))
                cursor.execute(ins_query_user)
            except Exception:
                raise exs.DBError
        if len(self.helpl_list) > 0:
            helpl_alert_rows = [
                f"('{self.alarm_id}', '{hid}')" for hid in self.helpl_list
            ]
            try:
                ins_query_helpl = """
                INSERT INTO {}.helpline_alert_status
                (alarm_id, helpline_id)
                VALUES {};
                """.format(db_name, ",".join(helpl_alert_rows))
                cursor.execute(ins_query_helpl)
            except Exception:
                raise exs.DBError
        return True
