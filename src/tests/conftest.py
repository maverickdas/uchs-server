import sys
sys.path.append("C:/Users/amit/Dev/uchs-server/src")

import pytest

import main as main
from alarm_manager import Alarm
from main import app


@pytest.fixture(scope="module")
def new_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="module")
def new_alarm():
    alarm = Alarm("r21", "111", "100000", "23.1,22.6", "Fire")
    # assert alarm1.latt == math.radians(23.1) and alarm1.longt == math.radians(22.6)
    yield alarm


@pytest.fixture(scope="module")
def new_conn():
    user, passw, name, conn_name = main.load_env_conf(testing=True)
    params = {
        "db_user": user,
        "db_password": passw,
        "db_name": name,
        "db_connection_name": conn_name
    }
    connx = main.get_db_connection(testing=True, params=params)
    return connx
