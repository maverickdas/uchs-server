import uchs_exceptions as exs
from alarm import Alarm, AlarmType


def get_alert_response(cursor=None, alarm: Alarm = None, alarm_id=None):
    # print("Generating response..")
    if alarm_id and cursor:
        query = """
        SELECT user_id, alarm_type, latitude, longitude, timestamp
        FROM uchs_db.alarm_status
        WHERE alarm_id = '{}'
        LIMIT 1;
        """.format(alarm_id)
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
