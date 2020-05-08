import os
import sys
import traceback

import pymysql
import yaml
import json
from flask import Flask, jsonify, request

from alarm_manager import receive_alarm, start_alert_procedure
from getloc import get_loc
from uchs_exceptions import DBError

global db_user, db_password, db_name, db_connection_name


def load_env_conf(testing=False):
    if not os.environ.get('GAE_ENV') == 'standard':
        app_path = os.path.join(__file__, "..", "app.yaml")
        with open(app_path) as f:
            env = yaml.load(f, Loader=yaml.BaseLoader)["env_variables"]
        for k, v in env.items():
            os.environ[k] = v
    global db_user, db_password, db_name, db_connection_name
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
    if testing:
        return (db_user, db_password, db_name, db_connection_name)
    return None


load_env_conf()
app = Flask(__name__)


def get_db_connection(testing=False, params=None):
    # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # set to `standard`
    global db_user, db_password, db_name, db_connection_name
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user,
                              password=db_password,
                              unix_socket=unix_socket,
                              db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        if testing and params:
            try:
                db_user = params["db_user"]
                db_password = params["db_password"]
                db_name = params["db_name"]
            except Exception as e:
                pass
        host = '127.0.0.1'
        port = 3306
        cnx = pymysql.connect(user=db_user,
                              password=db_password,
                              host=host,
                              port=port,
                              db=db_name)
    return cnx


@app.route('/')
def test():
    response = {"data": "Welcome to UCHS-Server!", "status": "OK"}
    return jsonify(response)


@app.route('/raiseAlarm', methods=['GET'])
def raise_alarm():
    user_id = request.args.get('userID')
    # TODO: use UUId to generate alarm ID
    # alarm_id = request.args.get('alarmID')
    alarm_ts = request.args.get('alarmTS')
    alarm_loc = request.args.get('alarmLoc')
    alarm_type = request.args.get('alarmType')
    testing = request.args.get('testing')
    geoloc = alarm_loc
    # print("=====================")
    # print(alarm_loc)
    # if len(alarm_loc.split(",")) == 2:
    #     loc = get_loc(alarm_loc)
    #     if loc:
    #         geoloc = loc
    # print(geoloc)
    err = ""
    sys_err = ""
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            stat1, alarm = receive_alarm(cursor, user_id, alarm_ts, alarm_loc,
                                         alarm_type)
            stat2 = start_alert_procedure(cursor, alarm)
        connx.commit()
        connx.close()
    except Exception as e:
        stat1 = False
        stat2 = False
        try:
            err = "".join(str(x) + " " for x in e.args)
        except:
            err = "Error"
        sys_err = sys.exc_info()[0]
        tb_err = traceback.format_exc()

    if stat1 and stat2:
        response = {
            "data": {
                "ACK":
                f"Received {alarm_type} alarm from {user_id} at {alarm_ts} from {geoloc}."
            },
            "status": 1
        }
        if testing:
            response["debug"] = {
                "id": alarm.id, "user": alarm.user_id
            }

    else:
        response = {
            "errorMsg": str(err) + " => " + str(sys_err),
            "errorDetails": str(tb_err).splitlines(),
            "status": 0
        }
    return jsonify(response)


if __name__ == '__main__':
    load_env_conf()
    app.run(host='127.0.0.1', port=8080, debug=True)
