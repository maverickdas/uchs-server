import os
import sys
sys.path.append(os.path.join(__file__, "..", ".."))
import math
import json

import pytest
from flask.testing import FlaskClient

import alarm_manager as alm
import main as main
from alarm_manager import Alarm


def get_users(cursor):
    query = """
    SELECT user_id
    FROM uchs_db.user_tbl;
    """
    cursor.execute(query)
    return [x[0] for x in cursor.fetchall()]


def test_raise_alarm(client):
    userID = "Thakuma"
    alarmTS = "1000000"
    alarmLoc = "22.3, 88.9"
    alarmType = "Fire"
    url = "/raiseAlarm?userID={}&alarmTS={}&alarmLoc={}&alarmType={}&testing=True".format(
        userID, alarmTS, alarmLoc, alarmType
    )
    resp = client.get(url)
    # print(resp.data)
    check_words = f"Received {alarmType} alarm from {userID}"
    assert check_words.encode("UTF-8") in resp.data


def test_new_user(conn, client):
    with conn.cursor() as cursor:
        users = get_users(cursor)
    unseen_user = "ABCDE"
    if unseen_user in users:
        print(f"Need to update the set 'unseen user' {unseen_user} in test-case.")
    else: 
        print(f"Testing raiseAlarm for unknown userID: {unseen_user}")
        alarmTS = "1000000"
        alarmLoc = "22.3, 88.9"
        alarmType = "Fire"
        url = "/raiseAlarm?userID={}&alarmTS={}&alarmLoc={}&alarmType={}&testing=True".format(
            unseen_user, alarmTS, alarmLoc, alarmType
        )
        resp = client.get(url)
        resp_dict = json.loads(str(resp.data, "utf-8"))
        assert resp_dict["status"] == 0
    conn.commit()
    conn.close()

