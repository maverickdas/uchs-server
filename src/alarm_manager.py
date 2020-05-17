import uchs_exceptions as exs
from alarm import Alarm
from alert import Alert


def receive_alarm(cursor, user_id, alarm_loc, alarm_type, is_alt=False):
    alarm = Alarm(user_id, alarm_loc, alarm_type)
    stat = alarm.insert_alarm(cursor, is_alt=is_alt)
    if stat:
        return True, alarm
    return False, None


def start_alert_procedure(cursor, alarm: Alarm, is_alt=False):
    try:
        ## FETCH HELPERS
        user_id = alarm.user_id
        guardian_list = helpline_list = community_list = specialist_list = []
        db_name = "uchs_test" if is_alt else "uchs_db"

        guardian_query = """
        SELECT *
        FROM {}.user_emergency_contacts_registered
        WHERE user_id = '{}';
        """.format(db_name, user_id)
        cursor.execute(guardian_query)
        try:
            guardian_list = [x for x in cursor.fetchone()[1:] if x is not None]
        except Exception:
            pass
        print("Guardians are -")
        print(guardian_list)

        community_1_query = """
        select ut.user_id
        from {}.user_live_location ull join {}.user_tbl ut 
        where ut.user_id = ull.user_id
        AND 
        ut.user_id !='{}'
        AND 
        acos(sin({}) * sin(ull.latitude) + cos({}) * cos(ull.latitude) * cos(ull.longitude - {})) * 6371 <= 1;
        """.format(db_name, db_name, user_id, alarm.latt, alarm.latt,
                   alarm.longt)
        cursor.execute(community_1_query)
        try:
            community_list = [x[0] for x in cursor.fetchall()]
        except Exception:
            pass
        print("Community is -")
        print(community_list)

        helpline_query = """
        select  ht.helpline_id from {}.helpline_tbl ht join {}.location_tbl lt 
        where ht.helpline_location_id = lt.location_id 
        AND 
        ht.helpline_type ='{}'
        AND 
        acos(sin({}) * sin(lt.latitude) + cos({}) * cos(lt.latitude ) * cos(lt.longitude - {})) * 6371 <= 1;
        """.format(db_name, db_name, alarm.type.name, alarm.latt, alarm.latt,
                   alarm.longt)
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
            from {}.user_live_location ull join {}.user_tbl ut 
            where ut.user_id = ull.user_id
            AND 
            ut.user_id !='{}'
            AND 
            ut.user_specialization ='{}'
            AND 
            acos(sin({}) * sin(ull.latitude) + cos({}) * cos(ull.latitude) * cos(ull.longitude - {})) * 6371 <= 2;
            """.format(db_name, db_name, user_id, alarm.type.name, alarm.latt,
                       alarm.latt, alarm.longt)
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
        send_alerts_to_clients(cursor, alert, is_alt=is_alt)
    except Exception as e:
        raise exs.DBError
    return True


def send_alerts_to_clients(cursor, alert: Alert, is_alt=False):
    alert.insert_alert(cursor, is_alt=is_alt)
    return True


def update_after_notified(cursor,
                          client_id,
                          alarm_id_list,
                          is_user=True,
                          is_alt=False):
    ## client_id is same as user/helpline id
    query_upd = ""
    alert_row_vals = "(" + ",".join([f"'{aid}'"
                                     for aid in alarm_id_list]) + ")"
    db_name = "uchs_test" if is_alt else "uchs_db"
    try:
        if is_user:
            query_upd = """
            UPDATE {}.user_alert_status
            SET status=1
            WHERE alarm_id in {} AND user_id='{}';
            """.format(db_name, alert_row_vals, client_id)
            cursor.execute(query_upd)
        else:
            query_upd = """
            UPDATE {}.helpline_alert_status
            SET status=1
            WHERE alarm_id in {} AND helpline_id='{}';
            """.format(db_name, alert_row_vals, client_id)
            cursor.execute(query_upd)
    except Exception:
        raise


def check_update_alarm_after_notified(cursor, alarm_id, is_alt=False):
    query_look_user = query_look_helpl = ""
    db_name = "uchs_test" if is_alt else "uchs_db"
    try:
        u_results = h_results = []
        flag = 0
        query_look_user = """
        SELECT COUNT(alarm_id)
        FROM {}.user_alert_status
        WHERE alarm_id = '{}' AND status=0;
        """.format(db_name, alarm_id)
        cursor.execute(query_look_user)
        cnt = cursor.fetchone()[0]
        if cnt > 0:
            flag = 1

        query_look_helpl = """
        SELECT COUNT(alarm_id)
        FROM {}.helpline_alert_status
        WHERE alarm_id = '{}' AND status=0;
        """.format(db_name, alarm_id)
        cursor.execute(query_look_helpl)
        cnt = cursor.fetchone()[0]
        if cnt > 0:
            flag = 1

        if flag == 0:
            query_upd_alarm = """
            UPDATE {}.alarm_status
            SET alarm_status = 2
            WHERE alarm_id = '{}'
            """.format(db_name, alarm_id)
            cursor.execute(query_upd_alarm)
    except Exception:
        raise
