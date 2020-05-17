import uchs_exceptions as exs
from alarm import Alarm, AlarmType


def get_alert_response(cursor=None,
                       alarm: Alarm = None,
                       alarm_id=None,
                       is_alt=False):
    # print("Generating response..")
    db_name = "uchs_test" if is_alt else "uchs_db"
    if alarm_id and cursor:
        query = """
        SELECT user_id, alarm_type, latitude, longitude, timestamp
        FROM {}.alarm_status
        WHERE alarm_id = '{}'
        LIMIT 1;
        """.format(db_name, alarm_id)
        cursor.execute(query)
        results = cursor.fetchone()
        uid, a_type, lat, lon, ts = results
        a_type = a_type.capitalize()
        # msg = f"{a_type} alarm raised by {uid}."
        return {
            "user": uid,
            "lat": float(lat),
            "lon": float(lon),
            "tstamp": int(ts.timestamp()),
            "atype": a_type
        }
    else:
        return "Alert message"
