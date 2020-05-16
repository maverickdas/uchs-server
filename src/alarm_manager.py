import uchs_exceptions as exs
from alarm import Alarm
from alert import Alert


def receive_alarm(cursor, user_id, alarm_loc, alarm_type):
    alarm = Alarm(user_id, alarm_loc, alarm_type)
    stat = alarm.insert_alarm(cursor)
    if stat:
        return True, alarm
    return False, None


def start_alert_procedure(cursor, alarm: Alarm):
    try:
        ## FETCH HELPERS
        user_id = alarm.user_id
        guardian_list = helpline_list = community_list = specialist_list = []

        guardian_query = """
        SELECT *
        FROM uchs_db.user_emergency_contacts_registered
        WHERE user_id = '{}';
        """.format(user_id)
        cursor.execute(guardian_query)
        try:
            guardian_list = [x for x in cursor.fetchone()[1:] if x is not None]
        except Exception:
            pass
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
        try:
            community_list = [x[0] for x in cursor.fetchall()]
        except Exception:
            pass
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
        try:
            helpline_list = [x[0] for x in cursor.fetchall()]
        except Exception:
            pass
        print("Helplines are -")
        print(helpline_list)

        if not helpline_list:
            print(
                "Since no helplines were found, getting specialists within 2km radius.."
            )
            specials_query = """
            select ut.user_id
            from user_live_location ull join user_tbl ut 
            where ut.user_id = ull.user_id
            AND 
            ut.user_id !='{}'
            AND 
            ut.user_specialization ='{}'
            AND 
            acos(sin({}) * sin(ull.latitude) + cos({}) * cos(ull.latitude) * cos(ull.longitude - {})) * 6371 <= 2;
            """.format(user_id, alarm.type.name, alarm.latt, alarm.latt,
                       alarm.longt)
            cursor.execute(specials_query)
            try:
                specialist_list = [x[0] for x in cursor.fetchall()]
            except Exception:
                pass
            print("Specialists are -")
            print(specialist_list)

        ## SEND ALERT
        # message = get_message(alarm)
        message = ""
        alert = Alert(alarm.id,
                      guardian_list + community_list + specialist_list,
                      helpline_list, message)
        send_alerts_to_clients(cursor, alert)
    except Exception as e:
        raise exs.DBError
    return True


def send_alerts_to_clients(cursor, alert: Alert):
    alert.insert_alert(cursor)
    return True


def update_after_notified(cursor, client_id, alarm_id_list, kind="user"):
    ## client_id is same as user/helpline id
    query_upd = ""
    alert_row_vals = "(" + ",".join([f"'{aid}'"
                                     for aid in alarm_id_list]) + ")"
    try:
        if kind == "user":
            query_upd = """
            UPDATE uchs_db.user_alert_status
            SET status=1
            WHERE alarm_id in {} AND user_id='{}';
            """.format(alert_row_vals, client_id)
            cursor.execute(query_upd)
        elif kind == "helpl":
            query_upd = """
            UPDATE uchs_db.helpline_alert_status
            SET status=1
            WHERE alarm_id in {} AND helpline_id='{}';
            """.format(alert_row_vals, client_id)
            cursor.execute(query_upd)
    except Exception:
        raise


def check_update_alarm_after_notified(cursor, alarm_id):
    query_look_user = query_look_helpl = ""
    try:
        u_results = h_results = []
        flag = 0
        query_look_user = """
        SELECT COUNT(alarm_id)
        FROM uchs_db.user_alert_status
        WHERE alarm_id = '{}' AND status=0;
        """.format(alarm_id)
        cursor.execute(query_look_user)
        cnt = cursor.fetchone()[0]
        print("C1: ", cnt)
        if cnt > 0:
            flag = 1

        query_look_helpl = """
        SELECT COUNT(alarm_id)
        FROM uchs_db.helpline_alert_status
        WHERE alarm_id = '{}' AND status=0;
        """.format(alarm_id)
        cursor.execute(query_look_helpl)
        cnt = cursor.fetchone()[0]
        print("C2: ", cnt)
        if cnt > 0:
            flag = 1

        if flag == 0:
            query_upd_alarm = """
            UPDATE uchs_db.alarm_status
            SET alarm_status = 2
            WHERE alarm_id = '{}'
            """.format(alarm_id)
            cursor.execute(query_upd_alarm)
    except Exception:
        raise
