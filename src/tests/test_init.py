'''
File: test_init.py
Project: UCHS
File Created: Thursday, 7th May 2020 10:01:41 pm
Author: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
Last Modified: Thursday, 18th June 2020 10:28:29 am
Modified By: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
An Effort By: Team A.V.A.A.S., 2020
'''
import os
import sys
sys.path.append(os.path.join(__file__, "..", ".."))
import math

import pytest
from flask.testing import FlaskClient

import alarm_manager as alm
import main as main
from alarm_manager import Alarm


def test_simple(client):
    resp = client.get('/')
    assert b"Welcome" in resp.data


def test_alarm_init(alarm):
    # alarm1 = Alarm("r21", "111", "100000", "23.1,22.6", "Fire")
    assert (alarm.latt == math.radians(23.1)
            and alarm.longt == math.radians(22.6))


def test_db_init(conn):
    assert True


# if __name__ == "__main__":
#     cl = get_client()
#     test_simple(cl)
