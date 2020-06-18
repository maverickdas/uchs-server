import os
import sys
import traceback

import pymysql
import yaml
# from flask import Flask, jsonify, request
from fastapi import FastAPI
# from fastapi.encoders import jsonable_encoder

import utils
import alarm_manager as alm
import user_manager as usm
from message_gen import get_alert_response
from uchs_exceptions import DBError

global db_user, db_password, db_name, db_connection_name, testdb_name
db_user = db_password = db_name = db_connection_name = testdb_name = None


def formatted_err_response(exc: Exception):
    try:
        err = "".join(str(x) + " " for x in exc.args)
    except:
        err = "Error"
    sys_err = sys.exc_info()[0]
    tb_err = traceback.format_exc()
    return {
        "errorMsg": str(err).strip(),
        "errorType": str(sys_err),
        "errorDetails": str(tb_err).splitlines(),
        "status": 0
    }


def load_env_conf(testing=False):
    if not os.environ.get('GAE_ENV') == 'standard':
        app_path = os.path.join(__file__, "..", "app.yaml")
        with open(app_path) as f:
            env = yaml.load(f, Loader=yaml.BaseLoader)["env_variables"]
        for k, v in env.items():
            os.environ[k] = v
    global db_user, db_password, db_name, db_connection_name, testdb_name
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    testdb_name = os.environ.get('TEST_DB_NAME')
    db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
    if testing:
        return {
            "db_user": db_user,
            "db_passw": db_password,
            "db_name": db_name,
            "testdb_name": testdb_name,
            "db_connection_name": db_connection_name
        }
    return None


load_env_conf()
app = FastAPI()


def get_db_connection(testing=False, params=None, is_alt=False):
    # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # set to `standard`
    global db_user, db_password, db_name, db_connection_name, testdb_name
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        conn_db_name = testdb_name if is_alt else db_name
        cnx = pymysql.connect(user=db_user, password=db_password,
                              unix_socket=unix_socket, db=conn_db_name)
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
                testdb_name = params["testdb_name"]
            except Exception as e:
                pass
        host = '127.0.0.1'
        port = 3306
        conn_db_name = testdb_name if is_alt else db_name
        cnx = pymysql.connect(user=db_user, password=db_password,
                              host=host, port=port, db=conn_db_name)
    return cnx


@app.get('/')
async def test():
    response = {"data": "Welcome to UCHS-Server!", "status": "OK"}
    return response


@app.get('/getAllAlarms')
async def see_alarms(alt: bool = False):
    is_alt = alt
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            alarms = alm.get_alarm_list(cursor, is_alt=is_alt)
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        response = {"alarms": [], "status": 1}
        for aid, uid, astatus, atype, _ in alarms:
            response["alarms"].append({
                "alarm_id": aid, "user_id": uid, "status": astatus, "type": atype
            })
    else:
        response.update(err_response)
    return response


@app.route('/raiseAlarm', methods=['GET'])
def raise_alarm():
    user_id = request.args.get('userID')
    alarm_loc = request.args.get('alarmLoc')
    alarm_type = request.args.get('alarmType')
    testing = request.args.get('testing')
    alt_db = request.args.get("alt")
    is_alt = True if alt_db else False
    try:
        connx = get_db_connection(is_alt=is_alt)
        with connx.cursor() as cursor:
            user_check = usm.check_uid_exists(cursor, user_id, utype="user", is_alt=is_alt)
            assert user_check, f"UserID {user_id} has not been registered!"
            stat1, alarm = alm.receive_alarm(cursor, user_id, alarm_loc, alarm_type,
                                             is_alt=is_alt)
            stat2 = alm.start_alert_procedure(cursor, alarm, is_alt=is_alt)
        connx.commit()
        connx.close()
    except Exception as e:
        stat1 = False
        stat2 = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat1 and stat2:
        response = {
            "data": {
                "ACK": f"Received {alarm_type} alarm from {user_id} from {alarm_loc}.",
                "ID": alarm.id
            },
            "status": 1
        }
        if testing:
            response["debug"] = {"id": alarm.id, "user": alarm.user_id}
    else:
        response.update(err_response)
    return jsonify(response)


@app.get('/checkUserAlerts')
def check_user_alert(uid, alt: bool = False):
    is_alt = alt
    connx = get_db_connection(is_alt=is_alt)
    response = {"data": [], "alarmDetails": [], "status": 0}
    try:
        alarm_id_list = []
        cursor = connx.cursor()
        if usm.check_pending(cursor, uid, is_user=True, is_alt=is_alt):
            alarm_id_list = usm.get_pending_alerts(cursor, uid, is_user=True, is_alt=is_alt)
            if len(alarm_id_list) > 0:
                for aid in alarm_id_list:
                    resp_details = get_alert_response(cursor=cursor, alarm_id=aid, is_alt=is_alt)
                    response["data"].append("Generic Message")
                    response["alarmDetails"].append(resp_details)
                    response["status"] = 1
                alm.update_after_notified(cursor, uid, alarm_id_list,
                                        is_user=True, is_alt=is_alt)
            connx.commit()
            for aid in alarm_id_list:
                alm.check_update_alarm_after_notified(cursor, aid, is_alt=is_alt)
            connx.commit()
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    if stat:
        response["status"] = 1
    else:
        response.update(err_response)
    return response


@app.get('/checkHelplineAlerts')
def check_helpline_alert(hid, alt: bool = False):
    is_alt = alt
    connx = get_db_connection(is_alt=is_alt)
    response = {"data": [], "alarmDetails": [], "status": 0}
    try:
        alarm_id_list = []
        cursor = connx.cursor()
        if usm.check_pending(cursor, hid, is_user=False, is_alt=is_alt):
            alarm_id_list = usm.get_pending_alerts(cursor, hid, is_user=False, is_alt=is_alt)
            if len(alarm_id_list) > 0:
                for aid in alarm_id_list:
                    resp_details = get_alert_response(cursor=cursor, alarm_id=aid, is_alt=is_alt)
                    response["data"].append("Generic Message")
                    response["alarmDetails"].append(resp_details)
                    response["status"] = 1
                alm.update_after_notified(cursor, hid, alarm_id_list,
                                        is_user=False, is_alt=is_alt)
            connx.commit()
            for aid in alarm_id_list:
                alm.check_update_alarm_after_notified(cursor, aid, is_alt=is_alt)
            connx.commit()
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    if stat:
        response["status"] = 1
    else:
        response.update(err_response)
    return response


@app.route('/clientExists', methods=['GET'])
def check_uid_exists():
    utype = request.args.get("type").lower()
    client_ids = request.args.get("IDlist")
    alt_db = request.args.get("alt")
    is_alt = True if alt_db else False
    client_list = client_ids.split(",")
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            valid_ids, invalid_ids = usm.check_uid_list_exists(cursor, client_list, utype=utype, is_alt=is_alt)
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        val = len(invalid_ids)
        response = {"check": 1 if not val else 0, 
        "invalid_IDs": invalid_ids, "valid_IDs": valid_ids, "status": 1}
    else:
        response.update(err_response)
    return jsonify(response)


@app.route('/registerUser', methods=['GET'])
def register_user():
    uid = request.args.get("uid")
    passwd = request.args.get("pass")
    age = request.args.get("age")
    fname = request.args.get("fname")
    lname = request.args.get("lname")
    ccode = request.args.get("ccode")
    phone = request.args.get("phone")
    specz = request.args.get("specz")
    alt_db = request.args.get("alt")
    is_alt = True if alt_db else False
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            usm.register_user(cursor, uid, passwd, fname, lname,
                              age, ccode, phone, specz, is_alt=is_alt)
        connx.commit()
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        response["status"] = 1
    else:
        response.update(err_response)
    return jsonify(response)


@app.route('/registerHelpline', methods=['GET'])
def register_helpline():
    hid = request.args.get("hid")
    passwd = request.args.get("pass")
    hname = request.args.get("hname")
    ccode = request.args.get("ccode")
    phone = request.args.get("phone")
    specz = request.args.get("specz")
    location = request.args.get("loc")
    alt_db = request.args.get("alt")
    is_alt = True if alt_db else False
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            usm.register_helpline(cursor, hid, passwd, hname, ccode,
                                  phone, specz, location, is_alt=is_alt)
        connx.commit()
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        response["status"] = 1
    else:
        response.update(err_response)
    return jsonify(response)


@app.route('/login', methods=['GET'])
def login():
    utype = request.args.get("type").lower()
    uid = request.args.get("id")
    passwd = request.args.get("pass")
    alt_db = request.args.get("alt")
    is_alt = True if alt_db else False
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            val, info = usm.login_client(cursor, uid, passwd, utype=utype, is_alt=is_alt)
        connx.commit()
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        response = {"check": 1 if val else 0, "status": 1, "desc": info}
    else:
        response.update(err_response)
    return jsonify(response)


@app.route('/logout', methods=['GET'])
def logout():
    utype = request.args.get("type").lower()
    uid = request.args.get("id")
    alt_db = request.args.get("alt")
    is_alt = True if alt_db else False
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            val, info = usm.logout_client(cursor, uid, utype=utype, is_alt=is_alt)
        connx.commit()
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        response = {"check": 1 if val else 0, "status": 1, "desc": info}
    else:
        response.update(err_response)
    return jsonify(response)


@app.route('/configureSOP', methods=['GET'])
def configure_sop():
    uid = request.args.get("uid")
    guid_list = request.args.get("guid_list").split(",")
    update = request.args.get("update")
    alt_db = request.args.get("alt")
    is_alt = True if alt_db else False
    stat = False
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            if update:
                val, info = usm.update_guardians(cursor, uid, guid_list, is_alt=is_alt)
            else:
                val = usm.insert_guardians(cursor, uid, guid_list, is_alt=is_alt)
        connx.commit()
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        response = {"check": 1 if val else 0, "status": 1, "desc": info}
    else:
        response.update(err_response)
    return jsonify(response)


@app.route('/liveLocation', methods=['GET'])
def update_live_location():
    user_id = request.args.get("uid")
    location = request.args.get("loc")
    alt_db = request.args.get("alt")
    is_alt = True if alt_db else False
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            usm.update_live_location(cursor, user_id, location, is_alt=is_alt)
        connx.commit()
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        response = {"status": 1}
    else:
        response.update(err_response)
    return jsonify(response)


@app.route('/monitorAlert', methods=['GET'])
def monitor_alert():
    aid = request.args.get("aid")
    alt_db = request.args.get("alt")
    is_alt = True if alt_db else False
    users, helplines = [], []
    try:
        assert utils.is_valid_uuid(aid, version_num=1), f"'{aid}' is not a valid UUID1"
        connx = get_db_connection()
        with connx.cursor() as cursor:
            users, helplines = alm.monitor_alerts(cursor, aid, is_alt)
        stat = True
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        response = {"users": {}, "helplines": {}, 
                    "#users": 0, "#helplines":0, "status": 1}
        if users:
            response["users"] = {k: v for (k,v) in users}
            response["#users"] = len(users)
        if helplines:
            response["helplines"] = {k: v for (k,v) in helplines}
            response["#helplines"] = len(helplines)
    else:
        response.update(err_response)
    return jsonify(response)


@app.get('/getGuardians')
async def get_guardians(uid, alt: bool = True):
    is_alt = alt
    guardians = []
    try:
        connx = get_db_connection()
        with connx.cursor() as cursor:
            stat, guardians = usm.get_guardians(cursor, uid, is_alt=is_alt)
        connx.close()
    except Exception as e:
        stat = False
        err_response = formatted_err_response(e)
    response = {"status": 0}
    if stat:
        response = {"guardians": {}, "#guardians":0, "status": 1}
        response["guardians"] = guardians
        response["#guardians"] = len(guardians)
    else:
        response.update(err_response)
    return response


if __name__ == '__main__':
    load_env_conf()
    app.run(host='127.0.0.1', port=8080, debug=True)
