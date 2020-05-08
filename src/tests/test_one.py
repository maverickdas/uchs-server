import math
import sys
sys.path.append("C:/Users/amit/Dev/uchs-server/src")

import pytest
from flask.testing import FlaskClient

import alarm_manager as alm
import main as main
from alarm_manager import Alarm


def test_simple(new_client):
    resp = new_client.get('/')
    print(resp)
    assert b"Welcome" in resp.data


def test_alarm_init(new_alarm):
    # alarm1 = Alarm("r21", "111", "100000", "23.1,22.6", "Fire")
    assert new_alarm.latt == math.radians(
        23.1) and new_alarm.longt == math.radians(22.6)


def test_db_init(new_conn):
    assert True


# if __name__ == "__main__":
#     cl = get_client()
#     test_simple(cl)
