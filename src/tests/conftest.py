'''
File: conftest.py
Project: UCHS
File Created: Friday, 8th May 2020 9:27:17 am
Author: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
Last Modified: Thursday, 18th June 2020 10:28:04 am
Modified By: Abhirup Das (abhidash@outlook.com, https://github.com/maverickdas)
-----
An Effort By: Team A.V.A.A.S., 2020
'''
import os
import sys
sys.path.append(os.path.join(__file__, "..", ".."))

import pytest

import main as main
from alarm_manager import Alarm
from main import app


@pytest.fixture(scope="module")
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="module")
def alarm():
    alarm = Alarm("r21", "23.1,22.6", "Fire")
    yield alarm


@pytest.fixture(scope="module")
def conn():
    params = main.load_env_conf(testing=True)
    connx = main.get_db_connection(testing=True, params=params)
    return connx
