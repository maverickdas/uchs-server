'''
File: message_gen.py
Project: UCHS
File Created: Saturday, 9th May 2020 11:04:27 am
Author: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
Last Modified: Thursday, 18th June 2020 10:26:55 am
Modified By: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
An Effort By: Team A.V.A.A.S., 2020
'''
import uchs_exceptions as exs
from alarm import Alarm, AlarmType


def get_alert_response(cursor=None, alarm: Alarm = None,
                       alarm_id=None, is_alt=False):
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
        return {
            "user": uid,
            "lat": float(lat),
            "lon": float(lon),
            "tstamp": int(ts.timestamp()),
            "atype": a_type
        }
    else:
        return "Alert message"
