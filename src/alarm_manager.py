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
            print("Since no helplines were found, getting specialists within 2km radius..")
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
